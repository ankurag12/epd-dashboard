import time


class Logger:
    def __init__(self, name):
        self._name = name
        self._log_file = "/log.txt"

    def error(self, s):
        self.add_log("ERROR", s, to_file=True)

    def info(self, s, to_file=False):
        self.add_log("INFO", s, to_file=to_file)

    def warning(self, s):
        self.add_log("WARNING", s, to_file=True)

    def add_log(self, level, s, to_file=False):
        line = f"{self.get_time()} {self._name} [{level}]: {s}"
        print(line)
        if to_file:
            with open(self._log_file, "at") as f:
                f.write(line)
                f.write("\n")

    @staticmethod
    def get_time():
        dt = time.localtime()
        return f"{dt[0]}-{dt[1]}-{dt[2]} {dt[3] - 7}:{dt[4]}:{dt[5]}"
