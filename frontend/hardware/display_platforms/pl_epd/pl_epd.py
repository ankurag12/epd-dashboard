from hardware.display_platforms.common import DisplayPlatform
from utils.logging import Logger
from hardware.display_platforms.pl_epd.pl.epdpsu import EpdPsuGPIO, EpdPsuEPDC
from hardware.display_platforms.pl_epd.pmic.max17135 import Max17135
from hardware.display_platforms.pl_epd.epson.epson_s1d13524 import S1D13524
import os

logger = Logger(__name__)


class PlEpd(DisplayPlatform):
    _HW_INFO_DEFAULT = {
        "version": 1,
        "vcom": {
            "dac_x1": 63,
            "dac_y1": 4586,
            "dac_x2": 189,
            "dac_y2": 9800,
            "vgpos_mv": 27770,
            "vgneg_mv": -41520,
            "swing_ideal": 70000},
        "board": {
            "board_type": "Raven",
            "board_ver_maj": 1,
            "board_ver_min": 0,
            "vcom_mode": 0,
            "hv_pmic": "HV_PMIC_MAX17135",
            "vcom_dac": 0,
            "vcom_adc": 0,
            "io_config": 0,
            "i2_mode": "CONFIG_DEFAULT_I2C_MODE",
            "temp_sensor": "TEMP_SENSOR_LM75",
            "frame_buffer": 0,
            "epdc_ref": "EPDC_S1D13524",
            "adc_scale_1": 1,
            "adc_scale_2": 1
        },
        "crc": 0xFFFF
    }

    _DISP_INFO_DEFAULT = {
        "vermagic": {
            "magic": 0x46574C50,
            "version": 1
        },
        "info": {
            "panel_id": "",
            "panel_type": "Type11",
            "vcom": 3983,
            "waveform_md5": bytearray(b'\xFF' * 16),
            "waveform_full_length": 0,
            "waveform_lzss_length": 0,
            "waveform_id": "",
            "waveform_target": ""
        },
        "info_crc": 0xFFFF
    }

    # This covers all the "probe" calls in main.c
    def __init__(self, mcu, hw_info=None, disp_info=None, wflib_file=None):
        super().__init__(mcu=mcu)

        if not hw_info:
            hw_info = PlEpd._HW_INFO_DEFAULT

        if not disp_info:
            disp_info = PlEpd._DISP_INFO_DEFAULT

        if not wflib_file:
            wflib_file = f"{os.getcwd()}hardware/display_platforms/pl_epd/waveform.wbf"
        self._wflib_file = wflib_file

        self._hw_info = hw_info
        self._disp_info = disp_info

        self._init_pmic()
        self._init_epdc()
        self._init_psu()

    def _init_pmic(self):
        if self._hw_info["board"]["hv_pmic"] == "HV_PMIC_MAX17135":
            self._pmic = Max17135(self._mcu.i2c["EPSON"])
            vcom_cal = Max17135.vcom_init(self._hw_info["vcom"])
            self._pmic.configure(vcom_cal=vcom_cal, power_sequence=1)
            self._pmic.set_vcom_voltage(self._disp_info["info"]["vcom"])

        elif self._hw_info["board"]["hv_pmic"] == "HV_PMIC_TPS65185":
            raise NotImplementedError

        else:
            raise ValueError(f"Invalid HV-PMIC id : {self._hw_info['board']['hv_pmic']}")

    def _init_psu(self):
        if self._hw_info["board"]["board_type"] == "Raven":
            self._psu = EpdPsuEPDC(self._epdc)
        else:
            self._psu = EpdPsuGPIO(self._mcu)
        logger.info(f"Initialized EPD PSU")

    def _init_epdc(self):
        if self._hw_info["board"]["epdc_ref"] == "EPDC_S1D13524":
            self._epdc = S1D13524(self._mcu, wflib_file=self._wflib_file)
        else:
            raise NotImplementedError

        logger.info("Loading wflib")
        self._epdc.load_wflib()

        logger.info(f"Ready {self._epdc.xres}x{self._epdc.yres}")

        logger.info(f"Initialized EPDC")

    def show_image(self, img_path, area=None, left=0, top=0):
        self._epdc.load_image(img_path, area=area, left=left, top=top)
        self._epdc.update_temp()
        self._psu.on()
        self._epdc.update("refresh", area=area)
        self._epdc.wait_update_end()
        self._psu.off()

    def clear(self):
        logger.info(f"Clearing the screen")
        self._epdc.fill(None, 255)
        self._epdc.clear_init()
        self._psu.on()
        self._epdc.update("init", area=None)
        self._epdc.wait_update_end()
        self._psu.off()
