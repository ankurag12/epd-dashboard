# Base class for a generic display platform.
# It could be EPD, LCD, whatever

class DisplayPlatform:
    def __init__(self, mcu, **kwargs):
        self._mcu = mcu

    @property
    def mcu(self):
        return self._mcu

    def clear(self):
        raise NotImplementedError

    def show_image(self, img_path, **kwargs):
        raise NotImplementedError
