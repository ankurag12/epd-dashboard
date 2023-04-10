import os
from app.IoTDashboard import IoTDashboard
from hardware.display_platforms.pl_epd.pl_epd import PlEpd
from hardware.mcu.esp32_upython import ESP32uPy
from utils.misc import load_config
from utils.logging import Logger

logger = Logger(__name__)

if __name__ == "__main__":
    config_file = f"{os.getcwd()}hardware/configs/config_esp32upy.json"
    config = load_config(config_file)
    mcu = ESP32uPy(hw_config=config["MCU"])
    display_platform = PlEpd(mcu=mcu)
    app = IoTDashboard(display_platform=display_platform)
    try:
        app.run(img_path="http://macbook-pro.local/the_image.pgm:8080", update_interval_sec=86400)
    except Exception as e:
        logger.error(f"Exception raised:\n{e}")
        mcu.close()
