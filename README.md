# Сервис для мониторинга и анализа состояния парковочных мест в реальном времени
Суть проекта состоит на безмасочном обнаружении парковочных мест, на основе детекции стоящих автомобилей при помощи предварительно обученной модели YOLOv8. Результаты обнаружения освободившегося/занятого парковочного места оповещается при помощи Telegram-бота.
## Документация по запуску проекта
1. Клонирование репозитория:
```
git clone https://github.com/GachiSlave/sofg_eng
cd sofg_eng
```
2. Установка зависимостей и запуск виртуальной среды
```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Настройка конфигурации:

Откройте файл config.yaml и замените chat_id на ваш Telegram chat ID
4. Запуск проекта:
```
python main.py
```

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&duration=2000&pause=1000&color=1141f7&random=false&width=600&lines=You're+breathtaking!+%E2%9C%A8)](https://git.io/typing-svg)
