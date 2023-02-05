from hardware.display_platforms.pl_epd.epson.epson_s1d135xx import S1D135xx

from utils.logging import Logger

logger = Logger(__name__)


class S1D13524(S1D135xx):
    PROD_CODE = 0x004F
    STATUS_HRDY = (1 << 5)
    PLLCFG0 = 0x340F
    PLLCFG1 = 0x0300
    PLLCFG2 = 0x1680
    PLLCFG3 = 0x1880
    I2C_CLOCK_DIV = 7  # 400 kHz
    I2C_DELAY = 3
    AUTO_RETRIEVE_ON = 0x0000
    AUTO_RETRIEVE_OFF = 0x0001
    LD_IMG_4BPP = (0 << 4)
    LD_IMG_8BPP = (1 << 4)
    LD_IMG_16BPP = (2 << 4)
    WF_CHECKSUM_ERROR = 0x1F00
    CTLR_AUTO_WFID = 0x0200
    CTLR_NEW_AREA_PRIORITY = 0x4000
    CTLR_PROCESSED_SINGLE = 0x0000
    CTLR_PROCESSED_DOUBLE = 0x0001
    CTLR_PROCESSED_TRIPLE = 0x0002

    class Register:
        POWER_SAVE_MODE = 0x0006,
        FRAME_DATA_LENGTH = 0x0300,
        LINE_DATA_LENGTH = 0x0306,
        TEMP_AUTO_RETRIEVE = 0x0320,
        TEMP = 0x0322,
        WF_ADDR_0 = 0x0390,
        WF_ADDR_1 = 0x0392

    class CMD:
        INIT_PLL = 0x01,
        INIT_CTLR_MODE = 0x0E,
        RD_WF_INFO = 0x30

    wf_table = {
        "init": 0,
        "refresh": 2,
        "delta": 3,
        "delta/mono": 4,
        "refresh/mono": 1,
        None: -1
    }

    def __init__(self, mcu, wflib_file):
        super().__init__(mcu=mcu, wflib_file=wflib_file)

        # self._temp_mode = None
        # self._measured_temp = None

        self.early_init()
        self._load_init_code()
        self._load_register_overrides()

        # Loading the init code turns the EPD power on as a side effect
        self.set_epd_power(0)

        self._set_power_state("RUN")
        self._init_gate_drv()
        self._wait_dspe_trig()
        self.init_ctlr_mode()
        self.xres = self._read_reg(S1D13524.Register.LINE_DATA_LENGTH)
        self.yres = self._read_reg(S1D13524.Register.FRAME_DATA_LENGTH)
        self.set_temp_mode("EXTERNAL")

    def clear_init(self):
        params = [0x0500]
        self._cmd(0x32, params)
        self._wait_idle()
        self.init_ctlr_mode()
        # TODO: find out why the first image state goes away
        self._fill(S1D13524.LD_IMG_4BPP, 4, None, 0xFF)

    def load_wflib(self):
        addr16 = [
            self._read_reg(S1D13524.Register.WF_ADDR_0),
            self._read_reg(S1D13524.Register.WF_ADDR_1)
        ]
        addr32 = addr16[1] << 16 | addr16[0]
        self._write_reg(0x0260, 0x8001)
        self._load_wflib(self._wflib, addr32)
        self._cmd(S1D13524.CMD.RD_WF_INFO, addr16)

        self._wait_idle()

        busy = self._read_reg(S1D135xx.Register.DISPLAY_BUSY)

        if busy & S1D13524.WF_CHECKSUM_ERROR:
            raise ValueError(f"Waveform checksum error")

    def set_temp_mode(self, mode):
        if mode.upper() == "MANUAL":
            self._write_reg(S1D13524.Register.TEMP_AUTO_RETRIEVE, S1D13524.AUTO_RETRIEVE_OFF)
        elif mode.upper() == "EXTERNAL":
            self._write_reg(S1D13524.Register.TEMP_AUTO_RETRIEVE, S1D13524.AUTO_RETRIEVE_ON)
        elif mode.upper() == "INTERNAL":
            raise ValueError(f"Unsupported temperature mode")
        else:
            raise ValueError("Invalid temperature mode")

        self._temp_mode = mode.upper()

    def update_temp(self):
        if self._temp_mode.upper() == "MANUAL":
            self._write_reg(S1D13524.Register.TEMP, self._manual_temp)
            new_temp = self._manual_temp
        elif self._temp_mode.upper() == "EXTERNAL":
            new_temp = self._read_reg(S1D13524.Register.TEMP)
        else:
            raise ValueError("Invalid temperature mode")

        self._measured_temp = new_temp

    def fill(self, area, grey):
        return self._fill(S1D13524.LD_IMG_4BPP, 4, area, grey)

    def pattern_check(self, size):
        return self._pattern_check(self.yres, self.xres, size, S1D13524.LD_IMG_8BPP)

    def load_image(self, path, area, left, top):
        return self._load_image(path, S1D13524.LD_IMG_8BPP, 8, area, left, top)

    def early_init(self):
        self._hrdy_mask = S1D13524.STATUS_HRDY
        self._hrdy_result = 0
        self._measured_temp = -127
        self._hard_reset()

        self._soft_reset()
        self.check_rev()

        self._write_reg(S1D135xx.Register.I2C_STATUS, S1D13524.I2C_DELAY)
        self.init_clocks()
        self._set_power_state("RUN")

    def check_rev(self):
        self._check_prod_code(S1D13524.PROD_CODE)

        rev = self._read_reg(0x0000)
        conf = self._read_reg(0x0004)
        logger.info(f"Rev: {rev}, conf: {conf}")

        if rev != 0x0100 or conf != 0x001F:
            raise ValueError(f"Invalid ref/conf values")

    def init_clocks(self):
        params = [
            S1D13524.PLLCFG0, S1D13524.PLLCFG1, S1D13524.PLLCFG2, S1D13524.PLLCFG3
        ]
        self._cmd(S1D13524.CMD.INIT_PLL, params)
        self._wait_idle()
        self._write_reg(S1D13524.Register.POWER_SAVE_MODE, 0x0)
        self._write_reg(S1D135xx.Register.I2C_CLOCK, S1D13524.I2C_CLOCK_DIV)

    def init_ctlr_mode(self):
        params = [
            S1D13524.CTLR_AUTO_WFID, (S1D13524.CTLR_NEW_AREA_PRIORITY | S1D13524.CTLR_PROCESSED_SINGLE)
        ]
        self._cmd(S1D13524.CMD.INIT_CTLR_MODE, params)
        self._wait_idle()

    def update(self, wfid, area=None):
        wfid = S1D13524.wf_table.get(wfid)
        super()._update(wfid, area=area)
