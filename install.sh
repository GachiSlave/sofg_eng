#!/bin/bash
# Проверка наличия python3
if ! command -v python3 &> /dev/null
then
    echo "python3 не установлен. Установите python3 и повторите попытку."
    exit
fi

# Проверка наличия пакета python3.10-venv
if ! dpkg -l | grep -q python3.10-venv; then
    echo "Пакет python3.10-venv не установлен. Устанавливаем..."
    sudo apt-get update
    sudo apt-get install -y python3.10-venv

    # Проверка успешности установки
    if ! dpkg -l | grep -q python3.10-venv; then
        echo "Не удалось установить пакет python3.10-venv. Установите его вручную и повторите попытку."
        exit
    fi
fi

# Создаем и активируем виртуальную среду
python3 -m venv venv

# Проверка успешности создания виртуального окружения
if [ ! -d "venv" ]; then
    echo "Не удалось создать виртуальное окружение. Убедитесь, что у вас установлен пакет python3-venv."
    exit
fi

# Активируем виртуальное окружени
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Скачиваем модель yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -O yolov8n.pt

echo "Виртуальная среда настроена и зависимости установлены. Модель YOLOv8n загружена."
