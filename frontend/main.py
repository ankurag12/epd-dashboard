import machine
import time

pin = machine.Pin(13, machine.Pin.OUT)
print("Hello")
while True:
    pin.on()
    time.sleep(1)
    pin.off()
    time.sleep(1)
