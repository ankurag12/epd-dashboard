from app.stoic_dashboard import StoicDashboard
from hardware.display_platforms.pl_epd.pl_epd import PlEpd
from hardware.mcu.esp32_upython import ESP32uPy

def load_config():
    config = {
        "GPIO": {
            "LED": {
                "pin": 13,
                "mode": "OUT"
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

    mcu.gpio["LED"].set_pin(0)
