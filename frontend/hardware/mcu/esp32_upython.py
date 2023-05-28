import json
import time

import esp32
import machine
import network
import ntptime

from hardware.mcu import mcu
from utils.logging import Logger

logger = Logger(__name__)


# TODO: We can use more low-level commands (if available) for speed


class ESP32GPIO(mcu.GPIO):
    _mode_map = {
        "IN": machine.Pin.IN,
        "OUT": machine.Pin.OUT,
        "OPEN_DRAIN": machine.Pin.OPEN_DRAIN,
        -1: -1
    }
    _pull_map = {
        None: None,
        "PULL_UP": machine.Pin.PULL_UP,
        "PULL_DOWN": machine.Pin.PULL_DOWN,
        -1: -1
    }

    def __init__(self, config=None):
        super().__init__(config=config)
        self._pin = machine.Pin(config["pin"],
                                mode=ESP32GPIO._mode_map.get(config.get("mode"), -1),
                                pull=ESP32GPIO._pull_map.get(config.get("pull"), -1),
                                value=config.get("value"))

    def configure_pin(self, config):
        self._pin.init(mode=ESP32GPIO._mode_map[config.get("mode", -1)],
                       pull=ESP32GPIO._pull_map[config.get("pull")],
                       value=config.get("value"))

    def set_pin(self, value):
        self._pin(value)

    def get_pin(self):
        return self._pin()


class ESP32Touch(mcu.Touch):
    def __init__(self, config=None):
        super().__init__(config=config)
        self._pin = machine.TouchPad(machine.Pin(config["pin"]))
        self._pin.config(config["thresh"])

    def read(self):
        return self._pin.read()

    def config(self, val):
        return self._pin.config(val)


class ESP32Power(mcu.Power):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.wake_on_touch(config.get("wake_on_touch", False))

    def deep_sleep(self, time_ms=-1):
        if time_ms > 0:
            logger.info(f"Going to deep sleep for {time_ms / 1000} seconds", to_file=True)
            return machine.deepsleep(time_ms)
        else:
            logger.info(f"Going to deep sleep indefinitely", to_file=True)
            return machine.deepsleep()

    def light_sleep(self, time_ms=-1):
        if time_ms > 0:
            logger.info(f"Going to light sleep for {time_ms / 1000} seconds")
            return machine.lightsleep(time_ms)
        else:
            logger.info(f"Going to light sleep indefinitely")
            return machine.lightsleep()

    def wake_on_touch(self, wake):
        esp32.wake_on_touch(wake)

    def reset_cause(self):
        reset_causes = {
            machine.DEEPSLEEP: "DEEPSLEEP",
            machine.HARD_RESET: "HARD_RESET",
            machine.PWRON_RESET: "PWRON_RESET",
            machine.SOFT_RESET: "SOFT_RESET",
            machine.DEEPSLEEP_RESET: "DEEPSLEEP_RESET"
        }
        reset_cause = machine.reset_cause()
        logger.info(f"Reset Cause: {reset_cause}", to_file=True)
        return reset_causes.get(reset_cause, "UNKNOWN")


class ESP32Network(mcu.Network):
    def __init__(self, config=None):
        super().__init__(config=config)
        self._wlan = network.WLAN(network.STA_IF)
        self._retries = 0
        if config.get("auto_connect"):
            wifi_cred = config.get("wifi_credentials")
            if wifi_cred:
                if isinstance(wifi_cred, str):
                    with open(wifi_cred, "r") as f:
                        wifi_cred = json.load(f)
                self.connect(wifi_cred.get("SSID"), wifi_cred.get("Password"))
            else:
                self.connect()

    def connect(self, ssid=None, password=None):
        self._wlan.active(True)
        if not self._wlan.isconnected():
            logger.info(f'Connecting to network {ssid}...')
            try:
                if ssid and password:
                    self._wlan.connect(ssid, password)
                else:
                    self._wlan.connect()
                while not self._wlan.isconnected():
                    time.sleep(0.1)
            except OSError as e:
                if self._retries > 3:
                    logger.error(f"Could not connect to network {ssid}")
                    return
                self._retries += 1
                self.disconnect()
                self.connect(ssid=ssid, password=password)

        logger.info(f"Network config:\n{self._wlan.ifconfig()}", to_file=True)
        self._retries = 0

    def disconnect(self):
        self._wlan.disconnect()
        self._wlan.active(False)


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
        self._i2c = machine.I2C(config["id"],
                                freq=config["frequency"],
                                scl=machine.Pin(config.get("scl", ESP32I2C._default_io_pins[config["id"]]["scl"])),
                                sda=machine.Pin(config.get("sda", ESP32I2C._default_io_pins[config["id"]]["sda"])))

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

        self._spi = machine.SPI(config["id"],
                                config["baudrate"],
                                sck=machine.Pin(config.get("sck", ESP32SPI._default_io_pins[config["id"]]["sck"])),
                                mosi=machine.Pin(config.get("mosi", ESP32SPI._default_io_pins[config["id"]]["mosi"])),
                                miso=machine.Pin(config.get("miso", ESP32SPI._default_io_pins[config["id"]]["miso"])))

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
        ntptime.settime()
        self._rtc = machine.RTC()

    @classmethod
    def get_gpio_impl(cls):
        return ESP32GPIO

    @classmethod
    def get_spi_impl(cls):
        return ESP32SPI

    @classmethod
    def get_i2c_impl(cls):
        return ESP32I2C

    @classmethod
    def get_touch_impl(cls):
        return ESP32Touch

    @classmethod
    def get_power_impl(cls):
        return ESP32Power

    @classmethod
    def get_network_impl(cls):
        return ESP32Network

    @staticmethod
    def ticks_ms():
        return time.ticks_ms()

    @staticmethod
    def ticks_diff(start, end):
        return time.ticks_diff(start, end)

    @staticmethod
    def sleep_ms(ms):
        return time.sleep_ms(ms)

    def rtc_time(self, *args):
        dt = self._rtc.datetime(*args)
        # Return a formatted string and in California timezone
        return f"{dt[0]}-{dt[1]}-{dt[2]} {dt[4] - 7}:{dt[5]}:{dt[6]}.{dt[7]}"
