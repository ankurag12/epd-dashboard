# stoic-dashboard

**Dashboard that displays a new Stoic thought everyday!**

<p align="middle">
  <img align="top" src="../media/media/IMG_1015.jpeg?raw=true" height="400" />
  <img align="top" src="../media/media/IMG_1020.jpeg?raw=true" height="400" /> 
</p>

The main components of the project are:

- [Plastic Logic's Electrophoretic Display (EPD)](https://www.plasticlogic.com/product/parrot-msp430-for-10-7-display/):
  Similar to an E-ink display; it's optimal for this application as it consumes energy only when the image is updated.
- [Adafruit HUZZAH32-ESP32](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather): An ESP32 board. This runs the
  firmware for the dashboard in MicroPython, and provides functionality like connecting to a WiFi network, pulling image
  from the server, and sending it to the EPD controller.
- [ESP32-EPD Adapter](designs): The original eval-kit from Plastic Logic is powered by an MSP430 MCU. However, I wanted
  to run it using an ESP32 for features like WiFi connectivity and Python compatibility. So I made this adapter board
  that stacks on top of the Adafruit HUZZAH32-ESP32 and connects to the FPC that goes to the EPD controller board (Raven), replacing the MSP430 board (Parrot).
- [RaspberryPi](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/): It acts as a server that runs 24x7,
  maintaining a repository of images by pulling from Instagram
  account [@dailystoic](https://www.instagram.com/dailystoic/) and serving it to ESP32.

Other accessories include

- 3.7V LiPo battery
- [FFC/FPC extenders](https://www.adafruit.com/search?q=0.5mm+FFC+%2F+FPC+Extender) + [Flex cables](https://www.amazon.com/dp/B00W8W9PZO)
  to make connecting different boards easier after framing
- Frame using [foam-board](https://www.michaels.com/product/20-x-30-white-foam-board-10110205)
  and [leather sheet](https://www.amazon.com/gp/product/B08XJW7ZDR) (because I didn't have access to woodworking tools!)

This repo contains the ESP32 firmware ([frontend](frontend)), RPi server code ([backend](backend)) and design files for
the ESP32-EPD adapter ([designs](designs)).

## backend

Run this code on a permanently powered and internet connected system like a RaspberryPi. If a RaspberryPi isn't
available, any computer running Python can be used as a server. Just make sure to update the URL
in [main.py](frontend/main.py).

To setup, create a Python venv and install dependencies

```commandline
cd backend
python -m venv .env
source ./.env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

and run the server indefinitely.

```commandline
nohup python server.py &
```

After a few seconds, there should be images downloaded in `backend/image_repo`. You can verify that the server is
working well by visiting http://raspberrypi.local:8080 in your browser.

The server maintains a queue of available images from `image_repo`, popping one out whenever client (ESP32) queries. If
the size of the queue drops below a threshold (default=10), it executes another pull from Instagram to
update `image_repo` and the queue.

To avoid repeating images, it also maintains a history of previously served images as `history.pkl`. Delete that file to
recycle old images.

## frontend

This is a MicroPython port of the
original [MSP430 firmware from PlasticLogic](https://github.com/plasticlogic/pl-mcu-epd) (written in C) with some modifications like
pulling the image to display from a server on the network instead of reading from an SD-card.

If not done already, follow the steps here to
prepare [ESP32 for MicroPython](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html).

Create a Python3.7 venv and install dependencies

```commandline
cd frontend
python3.7 -m venv .env
source ./.env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Change WiFi and SSID and password in [wifi.json](frontend/wifi.json), and run `run.sh`

```commandline
./run.sh
```

This will transfer all frontend code and configs to the ESP32, pull an image from the server, display it on the EPD, and
go to [deep sleep](https://lastminuteengineers.com/esp32-deep-sleep-wakeup-sources/) for approx 24 hours. On wake-up, it
will pull and display a new image.

Before running `run.sh`, make sure that the server is running, else the frontend code will crash because
it can't find server! If that happens, perform a hard reset

```commandline
ampy --port /dev/cu.SLAB_USBtoUART reset --hard
```

#### Changing an image on demand

If you want to change the current image (and understandably don't want to wait 24 hours), ESP32 has a way to wake-up
from deep sleep
using [touch](https://docs.micropython.org/en/latest/esp32/quickref.html?highlight=deep_sleep#capacitive-touch). ESP32
has several capacitive touch-enabled pins; I'm using GPIO #14 that I fly-wired to a corner of the dashboard. Touching
that corner wakes up the ESP32 and updates the image. It could take ~20s, but still pretty cool! 

## designs
I used KiCad for designing the adapter board.

## Why Stoic?
Because I find it interesting 🤷

But yeah, technically, it's a generic dashboard, and one can add any number of Instagram accounts as `SOURCES` in [server.py](backend/server.py) :) 