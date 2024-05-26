# Сервис для мониторинга и анализа состояния парковочных мест в реальном времени
Суть проекта состоит на безмасочном обнаружении парковочных мест, на основе детекции стоящих автомобилей при помощи предварительно обученной модели YOLOv8. Результаты обнаружения освободившегося/занятого парковочного места оповещается при помощи Telegram-бота.
## Документация по запуску проекта

1. Клонирование репозитория:
```
git clone https://github.com/GachiSlave/sofg_eng
cd sofg_eng
```

2. Установка зависимостей и запуск виртуальной среды
* на Linux:
```
chmod +x install.sh
./install.sh
source venv/bin/activate
```

* на Windows
```
install.bat
```

3. Настройка конфигурации:

Откройте файл config.yaml и замените chat_id на ваш Telegram chat ID, если Вы используете свой бот, то так же замените TOKEN. Узнать chat_id интересующего чата, а так же воспользоваться готовым ботом можно при помощи https://t.me/freeparkingcar_bot (в этом случае TOKEN менять не нужно).

4. Запуск проекта:
```
python main.py
```

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&duration=2000&pause=1000&color=1141f7&random=false&width=600&lines=You're+breathtaking!+%E2%9C%A8)](https://git.io/typing-svg)
