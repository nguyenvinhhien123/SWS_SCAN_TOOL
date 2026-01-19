#!/bin/bash

echo "[*] Đang cập nhật hệ thống..."
sudo apt-get update -y

echo "[*] Cài đặt các công cụ cơ bản (Nmap, Nikto, Python3)..."
sudo apt-get install -y nmap nikto python3 python3-pip git

echo "[*] Cài đặt Golang (cần thiết cho các công cụ ProjectDiscovery)..."
sudo apt-get install -y golang

echo "[*] Cài đặt Katana và Nuclei từ ProjectDiscovery..."
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Đưa tool Go vào đường dẫn hệ thống
sudo cp ~/go/bin/* /usr/local/bin/

echo "[*] Đang kiểm tra thư mục apps..."
mkdir -p apps
cd apps

if [ ! -d "XSStrike" ]; then
    echo "[*] Đang tải XSStrike..."
    git clone https://github.com/s0md3v/XSStrike.git
    cd XSStrike
    pip3 install -r requirements.txt
    cd ..
fi

echo "[*] Cài đặt thư viện Python cho tool chính..."
cd ..
pip3 install -r requirements.txt

echo "[✔] CÀI ĐẶT HOÀN TẤT!"
echo "[!] Lưu ý: Hãy đảm bảo XSSTRIKE_PATH trong file .py khớp với: $PWD/apps/XSStrike/xsstrike.py"
