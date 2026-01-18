#!/bin/bash

echo "[+] Dang sua loi ket noi va cap nhat..."
sudo apt update --fix-missing

echo "[+] Dang cai dat dependencies..."
sudo apt install -y --fix-missing nmap nikto wapiti golang

echo "[+] Dang cai dat Katana..."
# Thiết lập môi trường tạm thời để nhận lệnh go ngay lập tức
export GOPATH=$HOME/go
export PATH=$PATH:/usr/lib/go/bin:$GOPATH/bin

go install github.com/projectdiscovery/katana/cmd/katana@latest

if [ -f "$HOME/go/bin/katana" ]; then
    sudo cp $HOME/go/bin/katana /usr/local/bin/
    echo "[+] Da cai dat Katana."
fi

chmod +x pentestsws.py
echo "--- HOAN TAT ---"
