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
    img_path = "http://macbook-pro.local/sample_image.pgm:8080"
    # img_path = f"{os.getcwd()}hardware/display_platforms/sample_images/01_eyes_128x96_n.pgm"
    app.test_image(img_path,
                   area={"left": 1280 // 2 - 128 // 2,
                         "top": 960 // 2 - 96 // 2,
                         "height": 96,
                         "width": 128},
                   left=0,
                   top=0)
    mcu.close()
