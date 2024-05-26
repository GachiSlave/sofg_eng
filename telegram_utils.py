import requests


# Отправка фото в телеграм
def send_photo(token, chat_id, img_path):
    files = {'photo': open(img_path, 'rb')}
    requests.post(f'https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}', files=files)

# Отправка сообщения в телеграм
def send_message(token, chat_id, message):
    requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}')
