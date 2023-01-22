from hardware.display_platforms import S1D135xx

class S1D13524(S1D135xx):
    def __init__(self):
        super().__init__()
        raise NotImplementedError

    def clear_init(self):
        raise NotImplementedError

    def load_wflib(self):
        raise NotImplementedError

    def set_temp_mode(self):
        raise NotImplementedError

    def update_temp(self):
        raise NotImplementedError

    def fill(self):
        raise NotImplementedError

    def pattern_check(self):
        raise NotImplementedError

    def load_image(self):
        raise NotImplementedError

    def early_init(self):
        raise NotImplementedError

    def check_rev(self):
        raise NotImplementedError

    def init_clocks(self):
        raise NotImplementedError

    def init_ctlr_mode(self):
        raise NotImplementedError




