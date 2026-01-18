#!/bin/bash


sudo apt update


sudo apt install -y nmap nikto wapiti docker.io golang-go


go install github.com/projectdiscovery/katana/cmd/katana@latest
sudo cp ~/go/bin/katana /usr/local/bin/


chmod +x pentestsws.py

echo "done."
