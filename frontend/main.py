from app.stoic_dashboard import StoicDashboard
from hardware.display_platforms.pl_epd.pl_epd import PlEpd
from hardware.mcu.esp32_upython import ESP32uPy
import time
def load_config():
    config = {
        "GPIO": {
            "LED": {
                "pin": 13,
                "mode": "OUT"
            }
        },
        "SPI": {
            "EPSON": {
                "id": 2,
                "baudrate": 10000000,
                "sck": 5,
                "mosi": 18,
                "miso": 19
            }
        }
    }
    return config


if __name__ == "__main__":
    # display_platform = PlEpd(hw_config=load_config())
    # app = StoicDashboard(display_platform=display_platform)
    # app.run()
    hw_config = load_config()
    mcu = ESP32uPy(hw_config=hw_config)

    # mcu.gpio["LED"].set_pin(0)

    while True:
        try:
            mcu.gpio["LED"].set_pin(0)
            mcu.spi["EPSON"].write_bytes(b"ABCDEFGHIJ")
        finally:
            time.sleep(0.5)
            mcu.gpio["LED"].set_pin(1)



        # try:
        #     mcu.gpio["LED"].set_pin(0)
        #     rxdata = mcu.spi["EPSON"].read_bytes(1)
        # finally:
        #     mcu.gpio["LED"].set_pin(1)
        # print(f"rxdata={rxdata}")
        time.sleep(1)
