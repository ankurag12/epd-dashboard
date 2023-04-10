from app.common import BaseApp
from utils.logging import Logger

import time

logger = Logger(__name__)


class IoTDashboard(BaseApp):
    def __init__(self, display_platform=None, **kwargs):
        super().__init__(display_platform=display_platform, **kwargs)
        self._mcu = self._display_platform.mcu

    def run(self, img_path="http://macbook-pro.local/the_image.pgm:8080", update_interval_sec=86400, **kwargs):
        self._display_platform.clear()
        time.sleep(3)
        while True:
            self._display_platform.show_image(img_path, **kwargs)
            logger.info(f"Updated Image")
            self._mcu.network.disconnect()
            self._mcu.power.light_sleep(update_interval_sec * 1000)
            logger.info(f"Just woke-up from light sleep")
            self._mcu.network.connect()

    def clear(self):
        self._display_platform.clear()

    def test_image(self, img_path, **kwargs):
        self._display_platform.show_image(img_path, **kwargs)
