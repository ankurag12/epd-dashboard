from hardware.display_platforms.common import DisplayPlatform
from utils.logging import Logger


logger = Logger(__name__)

class PlEpd(DisplayPlatform):
    def __init__(self, hw_config=None):
        super().__init__(hw_config=hw_config)
        pass

    def init_hardware(self):
        # TODO: Instantiate epdc and PSU
        raise NotImplementedError

    def _init_gpio(self):
        gpio_config = self._hw_config.get("GPIO")
        if not gpio_config:
            logger.warning("No GPIO config defined")
            return

        for pin_name, conf in gpio_config.items():
            pass

    def show_image(self):
        raise NotImplementedError

    def clear(self):
        logger.info(f"Clearing the screen")
        self._epdc.fill(None, COLOR.WHITE)

        self._epdc.clear_init()

        self._psu.on()

        self._epdc.update()

        self._epdc.wait_update_end()

        self._psu.off()