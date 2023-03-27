from utils.logging import Logger
from hardware.display_platforms.pl_epd.pmic.common import PMIC
from collections import OrderedDict

logger = Logger(__name__)


class Max17135(PMIC):
    I2C_ADDRESS = 0x48
    PROD_ID = 0x4D

    HVPMIC_TIMING_SEQ = {
        # HVPMIC MAX17135 timings for Type4 Display (Maxim Drivers)
        0: OrderedDict({
            "UP_VGNEG": 24,
            "UP_VSNEG": 7,
            "UP_VSPOS": 2,
            "UP_VGPOS": 12,
            "DOWN_VGPOS": 7,
            "DOWN_VSPOS": 14,
            "DOWN_VSNEG": 12,
            "DOWN_VGNEG": 2
        }),
        # HVPMIC MAX17135 timings for Type11 Display (ST Drivers)
        1: OrderedDict({
            "UP_VGNEG": 12,
            "UP_VSNEG": 7,
            "UP_VSPOS": 2,
            "UP_VGPOS": 23,
            "DOWN_VGPOS": 2,
            "DOWN_VSPOS": 14,
            "DOWN_VSNEG": 12,
            "DOWN_VGNEG": 7
        })
    }

    class Register:
        HVPMIC_REG_EXT_TEMP = 0x00
        HVPMIC_REG_CONF = 0x01
        HVPMIC_REG_INT_TEMP = 0x04
        HVPMIC_REG_TEMP_STAT = 0x05
        HVPMIC_REG_PROD_REV = 0x06
        HVPMIC_REG_PROD_ID = 0x07
        HVPMIC_REG_DVR = 0x08
        HVPMIC_REG_ENABLE = 0x09
        HVPMIC_REG_FAULT = 0x0A
        HVPMIC_REG_PROG = 0x0C
        HVPMIC_REG_TIMING_1 = 0x10
        HVPMIC_REG_TIMING_2 = 0x11
        HVPMIC_REG_TIMING_3 = 0x12
        HVPMIC_REG_TIMING_4 = 0x13
        HVPMIC_REG_TIMING_5 = 0x14
        HVPMIC_REG_TIMING_6 = 0x15
        HVPMIC_REG_TIMING_7 = 0x16
        HVPMIC_REG_TIMING_8 = 0x17

    def __init__(self, i2c, i2c_addr=None):
        super().__init__(i2c, i2c_addr=i2c_addr)
        if not i2c_addr:
            self._i2c_addr = Max17135.I2C_ADDRESS
        self._cal = None
        self._timings = dict()
        self._prod_rev = None
        self._prod_id = None

    def load_timings(self):
        reg = Max17135.Register.HVPMIC_REG_TIMING_1
        i = 0
        for key, val in self._timings.items():
            self._i2c.write_byte_numeric(self._i2c_addr, reg + i, val)
            i += 1

    def configure(self, vcom_cal, power_sequence):
        self._cal = vcom_cal
        self._timings = Max17135.HVPMIC_TIMING_SEQ[power_sequence]

        self._prod_rev = self._i2c.read_byte_numeric(self._i2c_addr, Max17135.Register.HVPMIC_REG_PROD_REV)
        self._prod_id = self._i2c.read_byte_numeric(self._i2c_addr, Max17135.Register.HVPMIC_REG_PROD_ID)

        logger.info(f"PMIC rev: {self._prod_rev} , id: {self._prod_id}")

        if self._prod_id != Max17135.PROD_ID:
            raise ValueError(f"Invalid Prod ID")

        return self.load_timings()

    def set_vcom_register(self):
        raise

    def set_vcom_voltage(self, mv):
        dac_value = self.vcom_calculate(self._cal, mv)

        if dac_value < 0:
            dac_value = 0
        elif dac_value > 255:
            dac_value = 255

        self._i2c.write_byte_numeric(self._i2c_addr, Max17135.Register.HVPMIC_REG_DVR, dac_value)

    def wait_pok(self):
        raise

    def temp_enable(self):
        raise

    def temp_disable(self):
        raise

    def temp_measure(self):
        raise
