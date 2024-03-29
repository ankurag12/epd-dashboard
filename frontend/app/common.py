from utils.logging import Logger

logger = Logger(__name__)


class BaseApp:
    def __init__(self, display_platform, **kwargs):
        self._display_platform = display_platform
        self._mcu = display_platform.mcu

    def run(self):
        raise NotImplementedError
