#!/bin/bash

# Initial
#sudo apt install python3-dev python3-pip python3-numpy libfreetype6-dev libjpeg-dev build-essential python3-venv libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev
#git clone git@github.com:drewski3420/barcode_scanner.git
#python -m venv .venv
#source .venv/bin/activate
#pip3 install -r requirements.txt

# subsequent
sudo cp barcode_scanner.service /etc/systemd/system/.
sudo systemctl daemon-reload
sudo systemctl enable barcode_scanner
sudo systemctl start barcode_scanner
