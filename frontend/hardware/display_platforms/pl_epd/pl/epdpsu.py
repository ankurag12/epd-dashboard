class EPDPSU:
    def __init__(self):
        self._state = 0

    def on(self):
        raise NotImplementedError

    def off(self):
        raise NotImplementedError


class EpdPsuGPIO(EPDPSU):
    def __init__(self, mcu, timeout_ms=300, on_delay_ms=5, off_delay_ms=100):
        super().__init__()
        self._mcu = mcu
        self._timeout_ms = timeout_ms
        self._on_delay_ms = on_delay_ms
        self._off_delay_ms = off_delay_ms

    def on(self):
        if self._state == 1:
            return

        self._mcu["GPIO"]["PMIC_EN"].set_pin(1)

        start = self._mcu.ticks_ms()

        while self._mcu["GPIO"]["PMIC_POK"].get_pin() != 1:
            if self._mcu.ticks_diff(self._mcu.ticks_ms(), start) > self._timeout_ms:
                self._mcu["GPIO"]["PMIC_EN"].set_pin(0)
                raise TimeoutError(f"Timeout waiting for PMIC_OK")
            self._mcu.sleep_ms(1)

        self._mcu["GPIO"]["HVSW_CTRL"].set_pin(1)
        self._mcu.sleep_ms(self._on_delay_ms)

        self._state = 1

    def off(self):
        self._mcu["GPIO"]["HVSW_CTRL"].set_pin(0)
        self._mcu["GPIO"]["PMIC_EN"].set_pin(0)
        self._mcu.sleep_ms(self._off_delay_ms)
        self._state = 0


class EpdPsuEPDC(EPDPSU):
    def __init__(self, epdc):
        super().__init__()
        self._epdc = epdc

    def on(self):
        if not self._state:
            self._epdc.set_epd_power(1)
            self._state = 1

    def off(self):
        if self._state:
            self._epdc.set_epd_power(0)
            self._state = 0
