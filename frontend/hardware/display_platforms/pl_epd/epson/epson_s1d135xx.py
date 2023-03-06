import struct
from utils.logging import Logger
import os
from hardware.display_platforms.utils import pnm_read_header

logger = Logger(__name__)


class S1D135xx:
    TEMP_MASK = 0x00FF

    DATA_BUFFER_LENGTH = 512

    XMASK = 0x0FFF
    YMASK = 0x0FFF
    INIT_CODE_CHECKSUM_OK = (1 << 15)
    PWR_CTRL_UP = 0x8001
    PWR_CTRL_DOWN = 0x8002
    PWR_CTRL_BUSY = 0x0080
    PWR_CTRL_CHECK_ON = 0x2200

    class Register:
        REV_CODE = 0x0002
        SOFTWARE_RESET = 0x0008
        SYSTEM_STATUS = 0x000A
        I2C_CLOCK = 0x001A
        PERIPH_CONFIG = 0x0020
        HOST_MEM_PORT = 0x0154
        I2C_TEMP_SENSOR_VALUE = 0x0216
        I2C_STATUS = 0x0218
        PWR_CTRL = 0x0230
        SEQ_AUTOBOOT_CMD = 0x02A8
        DISPLAY_BUSY = 0x0338
        INT_RAW_STAT = 0x033A

    RotMode = {
        0: 0,
        90: 1,
        180: 2,
        270: 3
    }

    class CMD:
        INIT_SET = 0x00
        RUN = 0x02
        STBY = 0x04
        SLEEP = 0x05
        INIT_STBY = 0x06
        INIT_ROT_MODE = 0x0B
        READ_REG = 0x10
        WRITE_REG = 0x11
        BST_RD_SDR = 0x1C
        BST_WR_SDR = 0x1D
        BST_END_SDR = 0x1E
        LD_IMG = 0x20
        LD_IMG_AREA = 0x22
        LD_IMG_END = 0x23
        WAIT_DSPE_TRG = 0x28
        WAIT_DSPE_FREND = 0x29
        UPD_INIT = 0x32
        UPDATE_FULL = 0x33
        UPDATE_FULL_AREA = 0x34
        EPD_GDRV_CLR = 0x37

    def __init__(self, mcu, wflib_file=None):
        self._wflib = wflib_file
        self._mcu = mcu
        self._spi = mcu.spi["EPSON"]
        self._hdc = mcu.gpio.get("EPSON_HDC")
        self._hrdy = mcu.gpio.get("HRDY")
        self._cs = mcu.gpio.get("CS_0")
        self._reset = mcu.gpio.get("RESET")
        self._clk_en = mcu.gpio.get("CLK_EN")
        self._vcc_en = mcu.gpio.get("VCC_EN")
        self._hrdy_mask = None
        self._hrdy_result = None
        self.xres = None
        self.yres = None
        self._measured_temp = None
        self._init_code_file = f"{os.getcwd()}hardware/display_platforms/pl_epd/epson/bin/Ecode.bin"
        self._flags_needs_update = 0
        self._temp_mode = None
        self._manual_temp = 0

        if self._hrdy:
            logger.info("Using HRDY GPIO")
        if self._hdc:
            logger.info("Using HDC GPIO")

    def _get_hrdy(self):
        if self._hrdy:
            return self._hrdy.get_pin()

        status = self._read_reg(S1D135xx.Register.SYSTEM_STATUS)
        return (status & self._hrdy_mask) == self._hrdy_result

    def _do_fill(self, area, bpp, g):
        if bpp == 4:
            val16 = g & 0xF0
            val16 |= val16 >> 4
            val16 |= val16 << 8
            pixels = area["width"] // 4
        elif bpp == 8:
            val16 = g | (g << 8)
            pixels = area["width"] // 2
        else:
            raise ValueError(f"Unsupported bpp {bpp}")

        lines = area["height"]

        self._wait_idle()

        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.WRITE_REG)
        self._send_param(S1D135xx.Register.HOST_MEM_PORT)

        while lines:
            self._send_params([val16] * pixels)
            lines -= 1
        logger.info(f"Filled all")

        self._set_cs(1)
        self._wait_idle()
        self._send_cmd_cs(S1D135xx.CMD.LD_IMG_END)
        self._wait_idle()

    def _wflib_wr(self, data):
        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.WRITE_REG)
        self._send_param(S1D135xx.Register.HOST_MEM_PORT)
        self._transfer_data(data)
        self._set_cs(1)

    def _transfer_file(self, file):
        chunk = file.read(S1D135xx.DATA_BUFFER_LENGTH)
        while chunk:
            self._transfer_data(chunk)
            chunk = file.read(S1D135xx.DATA_BUFFER_LENGTH)

    def _transfer_image(self, file, area, left, top, width):
        if width < area["width"] or width < (left + area["width"]):
            raise ValueError("Invalid combination of width/left/area")

        with open(file, "rb") as f:
            # First ignore the top cropped area
            f.seek(top * width)
            for line in range(area["height"], -1, -1):
                # Find the first relevant pixel (byte) on this line
                f.seek(left + f.tell())

                # Transfer data of interest in chunks
                chunk = f.read(S1D135xx.DATA_BUFFER_LENGTH)
                while chunk:
                    self._transfer_data(chunk)
                    chunk = f.read(S1D135xx.DATA_BUFFER_LENGTH)

                # Move file pointer to end of line
                f.seek(f.tell() + width - (left + area["width"]))

    def _transfer_data(self, data):
        # Data is a byte array in little endian. Target wants word array in big endian
        data = struct.pack(f"<{len(data)//2}H", *struct.unpack(f">{len(data)//2}H", data))
        self._spi.write_bytes(data)

    def _send_cmd_area(self, cmd, mode, area):
        args = [
            mode,
            area["left"] & S1D135xx.XMASK,
            area["top"] & S1D135xx.YMASK,
            area["width"] & S1D135xx.XMASK,
            area["height"] & S1D135xx.YMASK
        ]
        self._send_cmd(cmd)
        self._send_params(args)

    def _send_cmd_cs(self, cmd):
        self._set_cs(0)
        self._send_cmd(cmd)
        self._set_cs(1)

    def _send_cmd(self, cmd):
        cmd = cmd.to_bytes(2, "big")
        self._set_hdc(0)
        self._spi.write_bytes(cmd)
        self._set_hdc(1)

    def _send_params(self, params):
        params = b''.join([param.to_bytes(2, "big") for param in params])
        self._spi.write_bytes(params)

    def _send_param(self, param):
        # param is an integer
        param = param.to_bytes(2, "big")
        self._spi.write_bytes(param)

    def _set_cs(self, state):
        self._cs.set_pin(state)

    def _set_hdc(self, state):
        if self._hdc:
            self._hdc.set_pin(state)

    @classmethod
    def _wf_mode(cls, wf):
        return (wf << 8) & 0x0F00

    def _wait_idle(self, timeout_ms=1000):
        start = self._mcu.ticks_ms()
        while not self._get_hrdy():
            if self._mcu.ticks_diff(self._mcu.ticks_ms(), start) > timeout_ms:
                raise RuntimeError(f"HRDY timeout")
            self._mcu.sleep_ms(1)

    def _early_init(self):
        raise

    def _hard_reset(self):
        if not self._reset:
            logger.warning(f"No Hard Reset")
            return
        self._reset.set_pin(0)
        self._mcu.sleep_ms(4)
        self._reset.set_pin(1)
        self._mcu.sleep_ms(10)

    def _soft_reset(self):
        self._write_reg(S1D135xx.Register.SOFTWARE_RESET, 0xFF)
        self._wait_idle()

    def _check_prod_code(self, ref_code):
        prod_code = self._read_reg(S1D135xx.Register.REV_CODE)
        logger.info(f"Product code : {prod_code}")

        if prod_code != ref_code:
            raise ValueError(f"Invalid product code, expected {ref_code}")

    def _load_init_code(self):
        self._wait_idle()
        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.INIT_SET)
        with open(self._init_code_file, "rb") as f:
            self._transfer_file(f)

        self._set_cs(1)
        self._wait_idle()

        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.INIT_STBY)
        self._send_param(0x0500)
        self._set_cs(1)

        self._mcu.sleep_ms(100)
        self._wait_idle()

        checksum = self._read_reg(S1D135xx.Register.SEQ_AUTOBOOT_CMD)
        logger.info(f"Checksum = {checksum}")

        if not (checksum & S1D135xx.INIT_CODE_CHECKSUM_OK):
            raise ValueError(f"Init code checksum error")

    def _load_wflib(self, wflib, addr):
        # os.stat returns a tuple. 7th element is the size
        size2 = os.stat(wflib)[6] // 2

        self._wait_idle()

        params = [
            addr & 0xFFFF,
            (addr >> 16) & 0xFFFF,
            size2 & 0xFFFF,
            (size2 >> 16) & 0xFFFF
        ]

        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.BST_WR_SDR)
        self._send_params(params)
        self._set_cs(1)

        # Original code is more generic to support loading wflib from FatFS or EEPROM
        # Here we simplify it by assuming wflib is available as a file
        # So we just read wflib file and transfer it
        with open(wflib, "rb") as f:
            chunk = f.read(S1D135xx.DATA_BUFFER_LENGTH)
            while chunk:
                self._wflib_wr(chunk)
                chunk = f.read(S1D135xx.DATA_BUFFER_LENGTH)

        self._wait_idle()
        self._send_cmd_cs(S1D135xx.CMD.BST_END_SDR)
        self._wait_idle()

    def _init_gate_drv(self):
        self._send_cmd_cs(S1D135xx.CMD.EPD_GDRV_CLR)
        self._wait_idle()

    def _wait_dspe_trig(self):
        self._send_cmd_cs(S1D135xx.CMD.WAIT_DSPE_TRG)
        self._wait_idle()

    def clear_init(self):
        self._send_cmd_cs(S1D135xx.CMD.UPD_INIT)
        self._wait_idle()
        return self._wait_dspe_trig()

    def _fill(self, mode, bpp, area, grey):
        self._set_cs(0)

        if area:
            self._send_cmd_area(S1D135xx.CMD.LD_IMG_AREA, mode, area)
            fill_area = area
        else:
            self._send_cmd(S1D135xx.CMD.LD_IMG)
            self._send_param(mode)
            fill_area = {
                "top": 0,
                "left": 0,
                "width": self.xres,
                "height": self.yres
            }

        self._set_cs(1)
        return self._do_fill(fill_area, bpp, grey)

    def _pattern_check(self, height, width, checker_size, mode):
        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.LD_IMG)
        self._send_param(mode)
        self._set_cs(1)
        self._wait_idle()

        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.WRITE_REG)
        self._send_param(S1D135xx.Register.HOST_MEM_PORT)

        for i in range(height):
            k = i // checker_size
            for j in range(0, width, 2):
                if (k + (j // checker_size)) % 2:
                    val = 0xFFFF
                else:
                    val = 0x0
                self._send_param(val)

        self._set_cs(1)
        self._wait_idle()

        self._send_cmd_cs(S1D135xx.CMD.LD_IMG_END)

    def _load_image(self, path, mode, bpp, area=None, left=0, top=0):
        with open(path, "rb") as img_file:
            hdr = pnm_read_header(img_file)

            self._set_cs(0)

            if area:
                self._send_cmd_area(S1D135xx.CMD.LD_IMG_AREA, mode, area)
            else:
                self._send_cmd(S1D135xx.CMD.LD_IMG)
                self._send_param(mode)

            self._set_cs(1)
            self._wait_idle()
            self._set_cs(0)
            self._send_cmd(S1D135xx.CMD.WRITE_REG)
            self._send_param(S1D135xx.Register.HOST_MEM_PORT)

            if not area:
                self._transfer_file(img_file)
            else:
                self._transfer_image(img_file, area, left, top, hdr["width"])

            self._set_cs(1)

        self._wait_idle()

        self._send_cmd_cs(S1D135xx.CMD.LD_IMG_END)
        self._wait_idle()

    def _update(self, wfid, area=None):
        self._set_cs(0)

        if area:
            self._send_cmd_area(S1D135xx.CMD.UPDATE_FULL_AREA, self._wf_mode(wfid), area)
        else:
            self._send_cmd(S1D135xx.CMD.UPDATE_FULL)
            self._send_param(self._wf_mode(wfid))

        self._set_cs(1)
        self._wait_idle()
        self._wait_dspe_trig()

    def wait_update_end(self):
        self._send_cmd_cs(S1D135xx.CMD.WAIT_DSPE_FREND)
        self._wait_idle(timeout_ms=5000)

    def _set_power_state(self, state):
        self._set_cs(1)
        self._set_hdc(1)
        self._vcc_en.set_pin(1)
        self._clk_en.set_pin(1)

        self._wait_idle()

        if state.upper() == "RUN":
            self._send_cmd_cs(S1D135xx.CMD.RUN)
            self._wait_idle()
        elif state.upper() == "STANDBY":
            self._send_cmd_cs(S1D135xx.CMD.STBY)
            self._wait_idle()
        elif state.upper() == "SLEEP":
            self._send_cmd_cs(S1D135xx.CMD.STBY)
            self._wait_idle()
            self._clk_en.set_pin(0)
        elif state.upper() == "OFF":
            self._send_cmd_cs(S1D135xx.CMD.SLEEP)
            self._wait_idle()
            self._clk_en.set_pin(0)
            self._vcc_en.set_pin(0)
            self._set_hdc(0)
            self._set_cs(0)

    def set_epd_power(self, on):
        if on:
            arg = S1D135xx.PWR_CTRL_UP
        else:
            arg = S1D135xx.PWR_CTRL_DOWN

        self._wait_idle()

        self._write_reg(S1D135xx.Register.PWR_CTRL, arg)
        tmp = self._read_reg(S1D135xx.Register.PWR_CTRL)
        while tmp & S1D135xx.PWR_CTRL_BUSY:
            tmp = self._read_reg(S1D135xx.Register.PWR_CTRL)

        if on and (tmp & S1D135xx.PWR_CTRL_CHECK_ON) != S1D135xx.PWR_CTRL_CHECK_ON:
            raise IOError(f"Failed to turn the EPDC power on")

    def _cmd(self, cmd, params):
        self._set_cs(0)
        self._send_cmd(cmd)
        self._send_params(params)
        self._set_cs(1)

    def _read_reg(self, reg):
        self._set_cs(0)
        self._send_cmd(S1D135xx.CMD.READ_REG)
        self._send_param(reg)
        # Not sure why the original C code has it twice
        val = self._spi.read_bytes(2)
        val = self._spi.read_bytes(2)
        self._cs.set_pin(1)
        return int.from_bytes(val, "big")

    def _write_reg(self, reg, val):
        self._cs.set_pin(0)
        self._send_cmd(S1D135xx.CMD.WRITE_REG)
        reg = reg.to_bytes(2, 'big')
        val = val.to_bytes(2, "big")
        self._spi.write_bytes(reg + val)
        self._cs.set_pin(1)

    def _load_register_overrides(self):
        return
