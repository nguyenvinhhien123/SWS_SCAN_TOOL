#!/bin/bash
set -e

echo "========================================"
echo "   ILOVEYOURWEB AUTO SETUP SCRIPT"
echo "========================================"

# -------- CHECK ROOT --------
if [[ $EUID -ne 0 ]]; then
   echo "[!] Please run as root: sudo ./setup.sh"
   exit 1
fi

# -------- UPDATE SYSTEM --------
echo "[+] Updating system..."
apt update && apt upgrade -y

# -------- INSTALL BASE TOOLS --------
echo "[+] Installing base packages..."
apt install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    nmap \
    sqlmap \
    jq \
    tmux \
    build-essential \
    net-tools

# -------- INSTALL KATANA --------
if ! command -v katana &> /dev/null; then
    echo "[+] Installing Katana..."
    go install github.com/projectdiscovery/katana/cmd/katana@latest
    export PATH=$PATH:$HOME/go/bin
else
    echo "[✔] Katana already installed"
fi

# -------- INSTALL NUCLEI --------
if ! command -v nuclei &> /dev/null; then
    echo "[+] Installing Nuclei..."
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    export PATH=$PATH:$HOME/go/bin
    nuclei -update-templates
else
    echo "[✔] Nuclei already installed"
fi

# -------- INSTALL PYTHON LIBS --------
echo "[+] Installing python libraries..."
pip3 install --upgrade pip
pip3 install requests colorama

# -------- INSTALL XSStrike --------
XS_PATH="/home/kali/swit-scanner/apps/XSStrike"

if [ ! -d "$XS_PATH" ]; then
    echo "[+] Cloning XSStrike..."
    mkdir -p /home/kali/swit-scanner/apps
    git clone https://github.com/s0md3v/XSStrike.git "$XS_PATH"
    cd "$XS_PATH"
    pip3 install -r requirements.txt
else
    echo "[✔] XSStrike already exists"
fi

# -------- PERMISSION --------
echo "[+] Setting executable permissions..."
chmod +x ILOVEYOURWEB.py
chmod +x setup.sh

# -------- FINISH --------
echo ""
echo "========================================"
echo "[✔] Setup completed successfully!"
echo ""
echo "Run tool:"
echo "   python3 ILOVEYOURWEB.py"
echo ""
echo "Optional:"
echo "   export OPENAI_API_KEY='YOUR_API_KEY'"
echo "========================================"
