class Logger:
    def __init__(self, name):
        self._name = name
        self._log_file = "/log.txt"

    def error(self, s):
        self.add_log("ERROR", s)

    def info(self, s):
        self.add_log("INFO", s)

    def warning(self, s):
        self.add_log("WARNING", s)

    def add_log(self, level, s):
        line = f"{self._name} [{level}]: {s}"
        print(line)
        with open(self._log_file, "at") as f:
            f.write(line)
            f.write("\n")
