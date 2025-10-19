put some instructions here on how to install

1. Install the dependencies `sudo apt install python3-dev python3-pip python3-venv build-essential`
1. Clone the repo, cd into the folder
2. Create a venv. `python -m venv .venv`
3. Activate the venv `source .venv/bin/activate`
4. Install the modules `pip3 install -r requirements.txt`
5. Create the service `cp barcode_scanner.service /etc/systemd/system/.`
6. Reload the daemon `sudo systemctl daemon-reload`
7. Enable the service `sudo systemctl enable barcode_scanner`
8. Start it `sudo systemctl start myservice`
9. check it `sudo systemctl status myservice`
