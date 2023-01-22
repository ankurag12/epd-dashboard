rm -rf -- **/__pycache__
ampy --port /dev/cu.SLAB_USBtoUART put app
ampy --port /dev/cu.SLAB_USBtoUART put hardware
ampy --port /dev/cu.SLAB_USBtoUART put boot.py
ampy --port /dev/cu.SLAB_USBtoUART run main.py