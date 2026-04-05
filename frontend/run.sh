rm -rf -- **/__pycache__
rm -rf -- **/.DS_Store
mpremote cp -r app/ :
mpremote cp -r hardware/ :
mpremote cp -r utils/ :
mpremote cp wifi.json :
mpremote cp main.py :
mpremote reset