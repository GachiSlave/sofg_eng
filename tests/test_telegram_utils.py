import os
import sys
import unittest
from unittest.mock import patch, mock_open

# Добавление пути к родительской директории
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telegram_utils import send_message, send_photo


class TestTelegramUtils(unittest.TestCase):
    @patch('telegram_utils.open', new_callable=mock_open, read_data='data')
    @patch('requests.post')
    def test_send_photo(self, mock_post, mock_file):
        """Проверка функции отправки фото парковки"""
        send_photo('dummy_token', 'dummy_chat_id', 'dummy_path')
        self.assertTrue(mock_post.called)
        mock_file.assert_called_with('dummy_path', 'rb')

    @patch('requests.get')
    def test_send_message(self, mock_get):
        """Проверка функции отправки сообщения"""
        send_message('dummy_token', 'dummy_chat_id', 'dummy_message')
        self.assertTrue(mock_get.called)


if __name__ == '__main__':
    unittest.main()
