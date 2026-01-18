#!/bin/bash

echo "[+] Dang cap nhat he thong..."
sudo apt update

echo "[+] Dang sua loi dependencies va cai dat cong cu..."
# Cai dat tung buoc de tranh loi docker
sudo apt install -y containerd
sudo apt install -y docker.io nmap nikto wapiti golang-go

echo "[+] Dang cai dat Katana..."
# Su dung duong dan day du cua Go
export GOPATH=$HOME/go
export PATH=$PATH:/usr/lib/go/bin:$GOPATH/bin

go install github.com/projectdiscovery/katana/cmd/katana@latest

# Kiem tra va copy file thuc thi
if [ -f "$HOME/go/bin/katana" ]; then
    sudo cp $HOME/go/bin/katana /usr/local/bin/
    echo "[+] Da cai dat Katana thanh cong."
else
    echo "[!] Khong tim thay file katana sau khi build."
fi

chmod +x pentestsws.py
echo "--- XONG ---"
