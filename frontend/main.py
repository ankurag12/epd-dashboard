import os
from app.IoTDashboard import IoTDashboard
from hardware.display_platforms.pl_epd.pl_epd import PlEpd
from hardware.mcu.esp32_upython import ESP32uPy
from utils.misc import load_config

if __name__ == "__main__":
    config_file = f"{os.getcwd()}hardware/configs/config_esp32upy.json"
    config = load_config(config_file)
    mcu = ESP32uPy(hw_config=config["MCU"])
    display_platform = PlEpd(mcu=mcu)
    app = IoTDashboard(display_platform=display_platform)
    app.test()
    mcu.close()
