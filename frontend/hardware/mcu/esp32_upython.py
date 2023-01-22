from hardware.mcu import mcu
from machine import Pin, SPI, I2C

# TODO: We can use more low-level commands (if available) for speed

class ESP32GPIO(mcu.GPIO):
    _mode_map = {
        "IN": Pin.IN,
        "OUT": Pin.OUT
    }

    def __init__(self, config=None):
        super().__init__(config=config)
        self._pin = Pin(config["pin"], mode=self._mode_map[config["mode"]])

    def configure_pin(self, config):
        self._pin = Pin.init(config["pin"], mode=self._mode_map[config["mode"]])

    def set_pin(self, value):
        self._pin(value)

    def get_pin(self):
        return self._pin()


class ESP32I2C(mcu.I2C):
    def __init__(self, config=None):
        super().__init__(config=config)

    def read_bytes(self):
        raise

    def write_bytes(self):
        raise

    def close(self):
        raise


class ESP32SPI(mcu.SPI):
    def __init__(self, config=None):
        super().__init__(config=config)

    def read_bytes(self, count):
        raise

    def write_bytes(self, data, count):
        raise

    def close(self):
        raise


class ESP32uPy(mcu.MCU):
    def __init__(self, hw_config):
        super().__init__(hw_config=hw_config)

    @classmethod
    def get_gpio_impl(cls):
        return ESP32GPIO

    @classmethod
    def get_spi_impl(cls):
        return ESP32SPI

    @classmethod
    def get_i2c_impl(cls):
        return ESP32I2C


