from utils.logging import Logger

logger = Logger(__name__)


class GPIO:
    def __init__(self, config=None):
        self._config = config

    def set_pin(self, value):
        raise NotImplementedError

    def get_pin(self):
        raise NotImplementedError


class SPI:
    def __init__(self, config=None):
        self._config = config

    def write_bytes(self, data):
        raise NotImplementedError

    def read_bytes(self, count):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class I2C:
    def __init__(self, config=None):
        self._config = config

    def write_bytes(self, addr, reg, data):
        raise NotImplementedError

    def read_bytes(self, addr, reg, nbytes):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class MCU:
    def __init__(self, hw_config=None):
        logger.info(f"MCU Config:\n{hw_config}")

        self._spi = dict()
        self._i2c = dict()
        self._gpio = dict()

        self.init_spi(hw_config.get("SPI", dict()))
        self.init_i2c(hw_config.get("I2C", dict()))
        self.init_gpio(hw_config.get("GPIO", dict()))

    @property
    def spi(self):
        return self._spi

    @property
    def i2c(self):
        return self._i2c

    @property
    def gpio(self):
        return self._gpio

    @staticmethod
    def sleep_ms(ms):
        raise NotImplementedError

    @staticmethod
    def ticks_ms():
        raise NotImplementedError

    @staticmethod
    def ticks_diff(start, end):
        raise NotImplementedError

    @classmethod
    def get_spi_impl(cls):
        raise

    @classmethod
    def get_i2c_impl(cls):
        raise

    @classmethod
    def get_gpio_impl(cls):
        raise

    def init_spi(self, spi_config=None):
        for spi_id, conf in spi_config.items():
            self._spi[spi_id] = self.get_spi_impl()(config=conf)

    def init_i2c(self, i2c_config=None):
        for i2c_id, conf in i2c_config.items():
            self._i2c[i2c_id] = self.get_i2c_impl()(config=conf)

    def init_gpio(self, gpio_config=None):
        for gpio_id, conf in gpio_config.items():
            self._gpio[gpio_id] = self.get_gpio_impl()(config=conf)

    def close(self):
        for spi_id, spi in self._spi.items():
            spi.close()

        for i2c_id, i2c in self._i2c.items():
            i2c.close()
