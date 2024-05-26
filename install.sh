#!/bin/bash
if ! command -v python3 &> /dev/null
then
    exit
fi

if ! dpkg -l | grep -q python3.10-venv; then
    sudo apt-get update
    sudo apt-get install -y python3.10-venv

    if ! dpkg -l | grep -q python3.10-venv; then
        exit
    fi
fi

python3 -m venv venv

if [ ! -d "venv" ]; then
    exit
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -O yolov8n.pt
