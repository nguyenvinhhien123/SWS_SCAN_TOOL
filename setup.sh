#!/bin/bash

# Hiển thị tiêu đề
echo "====================================================="
echo "   SWS SCAN TOOL SETUP     "
echo "====================================================="

# 1. Cập nhật Repository và sửa lỗi kết nối
sudo sed -i 's/vn.archive.ubuntu.com/archive.ubuntu.com/g' /etc/apt/sources.list
sudo apt update --fix-missing

# 2. Cài đặt các công cụ hệ thống có sẵn
echo "[+] Đang cài đặt Nmap, Nikto, Wapiti, Golang, Docker..."
sudo apt --fix-broken install -y
sudo apt install -y nmap nikto wapiti golang-go docker.io python3-pip git curl

# 3. Thiết lập Docker
sudo systemctl start docker
sudo systemctl enable docker

# 4. Cài đặt Katana (ProjectDiscovery) - Xử lý lỗi GOPATH
echo "[+] Đang cài đặt Katana..."
export GO111MODULE=on
export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

go install github.com/projectdiscovery/katana/cmd/katana@latest

# Kiểm tra và copy Katana vào hệ thống
if [ -f "$HOME/go/bin/katana" ]; then
    sudo cp $HOME/go/bin/katana /usr/local/bin/
else
    # Thử cách cài cũ nếu go version thấp
    go get -u github.com/projectdiscovery/katana/cmd/katana
    sudo cp ~/go/bin/katana /usr/local/bin/ 2>/dev/null
fi

# 5. Cài đặt XSStrike (Tải về cùng thư mục với tool)
echo "[+] Đang kiểm tra XSStrike..."
if [ ! -d "XSStrike" ]; then
    git clone https://github.com/s0md3v/XSStrike.git
    cd XSStrike && pip3 install -r requirements.txt
    cd ..
fi

# 6. Cấp quyền thực thi cho tool
chmod +x pentestsws.py

echo "====================================================="
echo "        CÀI ĐẶT HOÀN TẤT! BẮT ĐẦU QUÉT"
echo "  Sử dụng: sudo python3 pentestsws.py"
echo "====================================================="
