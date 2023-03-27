from hardware.mcu import mcu
from machine import Pin, SPI, I2C
import time
from utils.logging import Logger

logger = Logger(__name__)

# TODO: We can use more low-level commands (if available) for speed

class ESP32GPIO(mcu.GPIO):
    _mode_map = {
        "IN": Pin.IN,
        "OUT": Pin.OUT,
        "OPEN_DRAIN": Pin.OPEN_DRAIN
    }
    _pull_map = {
        None: None,
        "PULL_UP": Pin.PULL_UP,
        "PULL_DOWN": Pin.PULL_DOWN
    }

    def __init__(self, config=None):
        super().__init__(config=config)
        self._pin = Pin(config["pin"],
                        mode=ESP32GPIO._mode_map.get(config.get("mode"), -1),
                        pull=ESP32GPIO._pull_map.get(config.get("pull"), -1),
                        value=config.get("value"))

    def configure_pin(self, config):
        self._pin = Pin.init(config["pin"],
                             mode=ESP32GPIO._mode_map[config.get("mode", -1)],
                             pull=ESP32GPIO._pull_map[config.get("pull")],
                             value=config.get("value"))

    def set_pin(self, value):
        self._pin(value)

    def get_pin(self):
        return self._pin()


class ESP32I2C(mcu.I2C):
    _default_io_pins = {
        0: {
            "scl": 18,
            "sda": 19
        },
        1: {
            "scl": 25,
            "sda": 26
        }
    }

    def __init__(self, config=None):
        super().__init__(config=config)
        self._i2c = I2C(config["id"],
                        freq=config["frequency"],
                        scl=Pin(config.get("scl", ESP32I2C._default_io_pins[config["id"]]["scl"])),
                        sda=Pin(config.get("sda", ESP32I2C._default_io_pins[config["id"]]["sda"])))

    def read_bytes(self, addr, reg, nbytes):
        if reg:
            return self._i2c.readfrom_mem(addr, reg, nbytes)
        else:
            return self._i2c.readfrom(addr, nbytes)

    def read_byte_numeric(self, addr, reg):
        return self.read_bytes(addr, reg, 1)[0]

    def write_bytes(self, addr, reg, data):
        if reg:
            return self._i2c.writeto_mem(addr, reg, data)
        else:
            return self._i2c.writeto(addr, data)

    def write_byte_numeric(self, addr, reg, data):
        """Write a numeric value"""
        if not isinstance(data, int):
            raise ValueError(f"data should be of type int")
        # byteorder doesn't matter for 1 byte but is required position argument
        data = data.to_bytes(1, "big")
        self.write_bytes(addr, reg, data)

    def scan(self):
        return self._i2c.scan()

    def close(self):
        logger.info(f"Closing I2C")
        return


class ESP32SPI(mcu.SPI):
    _default_io_pins = {
        1: {
            "sck": 14,
            "mosi": 13,
            "miso": 12
        },
        2: {
            "sck": 18,
            "mosi": 23,
            "miso": 19
        }
    }

    def __init__(self, config=None):
        super().__init__(config=config)

        self._spi = SPI(config["id"],
                        config["baudrate"],
                        sck=Pin(config.get("sck", ESP32SPI._default_io_pins[config["id"]]["sck"])),
                        mosi=Pin(config.get("mosi", ESP32SPI._default_io_pins[config["id"]]["mosi"])),
                        miso=Pin(config.get("miso", ESP32SPI._default_io_pins[config["id"]]["miso"])))

    def read_bytes(self, nbytes):
        return self._spi.read(nbytes)

    def write_bytes(self, data):
        return self._spi.write(data)

    def close(self):
        logger.info(f"Closing SPI")
        self._spi.deinit()


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

    @staticmethod
    def ticks_ms():
        return time.ticks_ms()

    @staticmethod
    def ticks_diff(start, end):
        return time.ticks_diff(start, end)

    @staticmethod
    def sleep_ms(ms):
        return time.sleep_ms(ms)
