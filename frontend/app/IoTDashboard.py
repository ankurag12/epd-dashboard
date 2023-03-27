from app.common import BaseApp

import time


class IoTDashboard(BaseApp):
    def __init__(self, display_platform=None, **kwargs):
        super().__init__(display_platform=display_platform, **kwargs)

    def run(self):
        self._display_platform.clear()

    def clear(self):
        self._display_platform.clear()

    def test_image(self, img_path, **kwargs):
        self._display_platform.show_image(img_path, **kwargs)
