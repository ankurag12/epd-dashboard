class DisplayPlatform:
    def __init__(self, hw_config=None):
        self._hw_config = hw_config

    def clear(self):
        raise NotImplementedError

    def show_image(self):
        raise NotImplementedError