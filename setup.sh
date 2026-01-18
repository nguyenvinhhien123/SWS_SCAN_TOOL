#!/bin/bash

# Thiết lập màu sắc để dễ theo dõi
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}[*] Bắt đầu thiết lập môi trường cho SWS_SCAN_TOOL...${NC}"

# 1. Cập nhật Repository (Tự động đổi mirror nếu lỗi)
echo -e "${GREEN}[1/5] Cập nhật danh sách gói phần mềm...${NC}"
sudo apt update --fix-missing

# 2. Sửa lỗi "Held packages" và "Dependencies" (Đặc biệt cho Docker)
echo -e "${GREEN}[2/5] Xử lý xung đột gói và cài đặt công cụ nền...${NC}"
sudo apt --fix-broken install -y
sudo apt install -y curl wget git python3-pip nmap nikto wapiti golang-go

# 3. Cài đặt Docker (Xử lý riêng lỗi containerd trên Ubuntu/Debian)
echo -e "${GREEN}[3/5] Cài đặt Docker Engine...${NC}"
sudo apt install -y containerd.io || sudo apt install -y containerd
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# 4. Cài đặt Katana (Xử lý lỗi Go version cũ/mới)
echo -e "${GREEN}[4/5] Cài đặt Katana (ProjectDiscovery)...${NC}"
export GO111MODULE=on
export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Thử cài bằng go install (cho Go 1.16+)
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Nếu go install không thành công (cho Go cũ hơn), thử dùng go get
if [ ! -f "$HOME/go/bin/katana" ]; then
    echo -e "${RED}[!] go install thất bại, đang thử dùng go get...${NC}"
    go get -u github.com/projectdiscovery/katana/cmd/katana
fi

# Đưa Katana vào hệ thống để máy nào cũng nhận diện được lệnh
if [ -f "$HOME/go/bin/katana" ]; then
    sudo cp $HOME/go/bin/katana /usr/local/bin/
    echo -e "${GREEN}[+] Katana cài đặt thành công!${NC}"
else
    echo -e "${RED}[!] Không thể cài Katana. Vui lòng kiểm tra lại kết nối mạng.${NC}"
fi

# 5. Cài đặt XSStrike (Tải trực tiếp về thư mục dự án)
echo -e "${GREEN}[5/5] Kiểm tra XSStrike...${NC}"
if [ ! -d "XSStrike" ]; then
    git clone https://github.com/s0md3v/XSStrike.git
    cd XSStrike && pip3 install -r requirements.txt
    cd ..
fi

# Cấp quyền thực thi cho script chính
chmod +x pentestsws.py

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}   HOÀN TẤT CÀI ĐẶT TRÊN TẤT CẢ CÁC MÁY   ${NC}"
echo -e "1. Chạy tool: ${GREEN}sudo python3 pentestsws.py${NC}"
echo -e "2. Kiểm tra Docker: ${GREEN}sudo docker ps${NC}"
echo -e "${GREEN}==========================================${NC}"
