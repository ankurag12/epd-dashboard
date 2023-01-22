class Logger:
    def __init__(self, name):
        self._name = name

    def error(self, s):
        print(f"{self._name} [ERROR]: {s}")

    def info(self, s):
        print(f"{self._name} [INFO]: {s}")

    def warning(self, s):
        print(f"{self._name} [WARNING]: {s}")