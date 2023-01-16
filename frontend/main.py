import time
import sys
import machine

pin = machine.Pin(13, machine.Pin.OUT)
print("Hello")

BUFFER_SIZE = 7


class RxTx:
    def __init__(self, uart_id=2, baudrate=115200):
        self._uart = machine.UART(uart_id, baudrate=baudrate)
        self._dp = DataPacketGenerator()
        self._response_map = {
            0: "UNKNOWN",
            1: "ACK_SEND_NEXT",
            2: "ERROR_SEND_PACKET_AGAIN",
            3: "ERROR_RESTART_COMM"
        }

    def send(self):
        self._uart.write(self._dp.get_data_packet())
        while True:
            resp = self._uart.read(1)
            while not resp:
                print("waiting")
                time.sleep(1)
                resp = self._uart.read(1)

            print(f"resp = {resp}")
            next_action = self._response_map[resp[0]]
            print(f"next_action = {next_action}")
            if next_action == "ACK_SEND_NEXT":
                self._uart.write(self._dp.get_data_packet())


class DataPacketGenerator:
    def __init__(self, size=BUFFER_SIZE):
        self._dp = bytearray(size)
        self._cmd_map = {
            "DO_NOTHING": 0,
            "CLEAR_DISPLAY": 1,
            "INIT_FILE_TRANSFER": 2,
            "READ_DATA_PACKET": 3,
            "END_FILE_TRANSFER": 4
        }
        self._tail_map = {
            "DO_NOTHING": 0,
        }
        self._counter = 0

    def get_data_packet(self):
        if self._counter == 0:
            cmd = "INIT_FILE_TRANSFER"
        elif 0 < self._counter < 5:
            cmd = "READ_DATA_PACKET"
        elif self._counter == 5:
            cmd = "END_FILE_TRANSFER"
        else:
            cmd = "DO_NOTHING"
            sys.exit()

        self._dp[0] = self._cmd_map[cmd]

        if cmd == "READ_DATA_PACKET":
            self._dp[1:-1] = bytes([i for i in range(65, 70)])

        self._dp[-1] = self._tail_map["DO_NOTHING"]
        print(f"Data packet = {self._dp}, self._counter = {self._counter}")
        self._counter += 1
        return self._dp


if __name__ == "__main__":
    rxtx = RxTx()
    rxtx.send()
# dp_generator = DataPacketGenerator()
# uart.write(dp_generator.get_data_packet("INIT_FILE_TRANSFER"))
# # TODO: use Interrupts
# resp = uart.read(1)
# while not resp:
#     time.sleep(1)
#     print("waiting")
#     resp = uart.read(1)
#
#
# while True:
#     pin.on()
#     for i in range(65, 70):
#         print(f"Sending {chr(i)}")
#         uart.write(chr(i))
#        time.sleep(0.1)
#     while not uart.read(1):
#         time.sleep(1)
#         print("waiting")
#     pin.off()
#    time.sleep(5)
