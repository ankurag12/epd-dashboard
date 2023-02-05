from app.common import BaseApp


class StoicDashboard(BaseApp):
    def __init__(self, display_platform=None, **kwargs):
        super().__init__(display_platform=display_platform, **kwargs)
        pass

    def run(self):
        self._display_platform.clear()
