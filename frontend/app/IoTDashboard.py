import time

from app.common import BaseApp
from utils.logging import Logger

logger = Logger(__name__)


class IoTDashboard(BaseApp):
    def __init__(self, display_platform=None, **kwargs):
        super().__init__(display_platform=display_platform, **kwargs)
        self._mcu = self._display_platform.mcu

    def run(self, img_path="http://macbook-pro.local/the_image.pgm:8080", update_interval_sec=86400, **kwargs):
        # Ideally we'd like to clear screen only for selected cases like PWRON_RESET, but we see ghosting in
        # image display so better to clear for every case (or remove if condition)
        if self._mcu.power.reset_cause() in ("PWRON_RESET", "SOFT_RESET", "HARD_RESET", "DEEPSLEEP_RESET"):
            self.clear()
        while True:
            self._display_platform.show_image(img_path, **kwargs)
            logger.info(f"Updated Image", to_file=True)
            self._mcu.network.disconnect()
            self._mcu.power.deep_sleep(update_interval_sec * 1000)
            # Waking up from deep sleep starts the program from very beginning. If we're here then it was light sleep
            logger.info(f"Just woke-up from light sleep")
            self._mcu.network.connect()

    def clear(self):
        self._display_platform.clear()
        time.sleep(5)

    def test_image(self, img_path, **kwargs):
        self._display_platform.show_image(img_path, **kwargs)
