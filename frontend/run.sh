rm -rf -- **/__pycache__
rm -rf -- **/.DS_Store
ampy --port /dev/cu.SLAB_USBtoUART put app
ampy --port /dev/cu.SLAB_USBtoUART put hardware
ampy --port /dev/cu.SLAB_USBtoUART put utils
ampy --port /dev/cu.SLAB_USBtoUART put wifi.json
ampy --port /dev/cu.SLAB_USBtoUART put main.py
ampy --port /dev/cu.SLAB_USBtoUART reset --hard