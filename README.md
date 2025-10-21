# INSTALLATION INSTRUCTIONS

1. Install the dependencies `sudo apt install python3-dev python3-pip python3-numpy libfreetype6-dev libjpeg-dev build-essential python3-venv libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev`
1. Clone the repo, cd into the folder
1. Create a venv. `python -m venv .venv`
1. Activate the venv `source .venv/bin/activate`
1. Install the modules `pip3 install -r requirements.txt`
1. Create the service `sudo cp barcode_scanner.service /etc/systemd/system/.`
1. Reload the daemon `sudo systemctl daemon-reload`
1. Enable the service `sudo systemctl enable barcode_scanner`
1. Start it `sudo systemctl start barcode_scanner`
1. check it `sudo systemctl status barcode_scanner`
