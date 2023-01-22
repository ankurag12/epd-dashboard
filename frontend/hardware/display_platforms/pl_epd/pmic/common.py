class Pmic:
    def __init__(self, i2c_id, i2c_addr):
        self._i2c_id = i2c_id
        self._i2c_addr = i2c_addr

    def load_timings(self):
        raise NotImplementedError

    def configure(self):
        raise NotImplementedError

    def set_vcom_regiter(self):
        raise NotImplementedError

    def set_vcom_voltage(self):
        raise NotImplementedError

    def wait_pok(self):
        raise NotImplementedError

    def temp_enable(self):
        raise NotImplementedError

    def temp_disable(self):
        raise NotImplementedError

    def temp_measure(self):
        raise NotImplementedError