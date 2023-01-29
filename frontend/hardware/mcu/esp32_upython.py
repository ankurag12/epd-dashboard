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
        self._pin = Pin(config["pin"], mode=ESP32GPIO._mode_map[config["mode"]])

    def configure_pin(self, config):
        self._pin = Pin.init(config["pin"], mode=ESP32GPIO._mode_map[config["mode"]])

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

    def read_bytes(self, count):
        return self._spi.read(count)

    def write_bytes(self, data):
        return self._spi.write(data)

    def close(self):
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


