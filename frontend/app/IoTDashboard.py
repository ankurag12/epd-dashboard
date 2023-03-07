from app.common import BaseApp
import time
import os


class IoTDashboard(BaseApp):
    def __init__(self, display_platform=None, **kwargs):
        super().__init__(display_platform=display_platform, **kwargs)
        pass

    def run(self):
        self._display_platform.clear()

    def test(self):
        self._display_platform.clear()
        time.sleep(2)
        self._display_platform.show_image(f"{os.getcwd()}hardware/display_platforms/sample_images/01_eyes_128x96_n.pgm",
                                          area={"left": 1280 // 2 - 128 // 2,
                                                "top": 960 // 2 - 96 // 2,
                                                "height": 96,
                                                "width": 128},
                                          left=0,
                                          top=0)
