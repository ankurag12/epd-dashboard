from utils.logging import Logger

logger = Logger(__name__)


class PMIC:
    def __init__(self, i2c, i2c_addr=None):
        self._i2c = i2c

    def load_timings(self):
        raise NotImplementedError

    def configure(self, vcom_cal, power_sequence):
        raise NotImplementedError

    def set_vcom_register(self):
        raise NotImplementedError

    def set_vcom_voltage(self, mv):
        raise NotImplementedError

    def wait_pok(self):
        raise NotImplementedError

    def temp_enable(self):
        raise NotImplementedError

    def temp_disable(self):
        raise NotImplementedError

    def temp_measure(self):
        raise NotImplementedError

    @staticmethod
    def vcom_calculate(vcom_cal, input_mv):
        scaled_mv = round(input_mv * vcom_cal["swing"] / vcom_cal["swing_ideal"])
        dac_value = round((scaled_mv - vcom_cal["dac_offset"]) * vcom_cal["dac_dx"] / vcom_cal["dac_dy"])
        logger.info(f"Input: {input_mv} , scaled: {scaled_mv} , DAC reg: {hex(dac_value)}")
        return dac_value

    @staticmethod
    def vcom_init(vcom_info):
        vcom_cal = dict()
        vcom_cal["dac_dx"] = vcom_info["dac_x2"] - vcom_info["dac_x1"]
        vcom_cal["dac_dy"] = vcom_info["dac_y2"] - vcom_info["dac_y1"]
        vcom_cal["dac_offset"] = vcom_info["dac_y1"] - round(
            vcom_info["dac_x1"] * vcom_cal["dac_dy"] / vcom_cal["dac_dx"])
        vcom_cal["swing"] = vcom_info["vgpos_mv"] - vcom_info["vgneg_mv"]
        vcom_cal["swing_ideal"] = vcom_info["swing_ideal"]
        vcom_cal["dac_step_mv"] = round(vcom_cal["dac_dy"] / vcom_cal["dac_dx"])
        return vcom_cal
