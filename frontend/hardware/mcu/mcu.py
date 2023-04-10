from utils.logging import Logger

logger = Logger(__name__)


class GPIO:
    def __init__(self, config=None):
        self._config = config

    def set_pin(self, value):
        raise NotImplementedError

    def get_pin(self):
        raise NotImplementedError


class Touch:
    def __init__(self, config=None):
        self._config = config

    def read(self):
        raise NotImplementedError

    def config(self, val):
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


class Network:
    def __init__(self, config=None):
        self._config = config

    def connect(self, ssid, password):
        raise NotImplementedError


class Power:
    def __init__(self, config=None):
        self._config = config

    def light_sleep(self, time_ms=-1):
        """
        Maintains the state and continues from where left off
        :return:
        """
        raise NotImplementedError

    def deep_sleep(self, time_ms=-1):
        """
        Equivalent to waking up from reset
        :return:
        """
        raise NotImplementedError

    def wake_on_touch(self, wake):
        raise NotImplementedError


class MCU:
    def __init__(self, hw_config=None):
        logger.info(f"MCU Config:\n{hw_config}")

        self._spi = dict()
        self._i2c = dict()
        self._gpio = dict()
        self._touch = dict()
        self._power = None
        self._network = None

        self._init_spi(hw_config.get("SPI", dict()))
        self._init_i2c(hw_config.get("I2C", dict()))
        self._init_gpio(hw_config.get("GPIO", dict()))
        self._init_touch(hw_config.get("TOUCH", dict()))
        self._init_power(hw_config.get("POWER", dict()))
        self._init_network(hw_config.get("NETWORK", dict()))

    @property
    def spi(self):
        return self._spi

    @property
    def i2c(self):
        return self._i2c

    @property
    def gpio(self):
        return self._gpio

    @property
    def touch(self):
        return self._touch

    @property
    def power(self):
        return self._power

    @property
    def network(self):
        return self._network

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

    @classmethod
    def get_touch_impl(cls):
        raise

    @classmethod
    def get_power_impl(cls):
        raise

    @classmethod
    def get_network_impl(cls):
        raise

    def _init_spi(self, spi_config=None):
        for spi_id, conf in spi_config.items():
            self._spi[spi_id] = self.get_spi_impl()(config=conf)

    def _init_i2c(self, i2c_config=None):
        for i2c_id, conf in i2c_config.items():
            self._i2c[i2c_id] = self.get_i2c_impl()(config=conf)

    def _init_gpio(self, gpio_config=None):
        for gpio_id, conf in gpio_config.items():
            self._gpio[gpio_id] = self.get_gpio_impl()(config=conf)

    def _init_touch(self, touch_config=None):
        for touch_id, conf in touch_config.items():
            self._touch[touch_id] = self.get_touch_impl()(config=conf)

    def _init_power(self, power_config=None):
        self._power = self.get_power_impl()(config=power_config)

    def _init_network(self, network_config=None):
        self._network = self.get_network_impl()(config=network_config)

    def close(self):
        for spi_id, spi in self._spi.items():
            spi.close()

        for i2c_id, i2c in self._i2c.items():
            i2c.close()
