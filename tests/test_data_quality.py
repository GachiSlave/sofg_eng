import cv2
import os
import subprocess
import sys
import unittest


class TestDataQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Убедитесь, что видеофайл загружен перед запуском тестов"""
        video_path = './video.mp4'
        if not os.path.exists(video_path):
            print("Видео не найдено. Попытка скачать через wget...")
            try:
                result = subprocess.run(
                    ['wget', '-O', video_path,
                     'https://drive.google.com/uc?export=download&id=1Bv8pKIf10KoDqw_QTOEQjeJPV0scNpLy'],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120  # Устанавливаем таймаут в 2 минуты
                )
                print(result.stdout.decode('utf-8'))
                print(result.stderr.decode('utf-8'), file=sys.stderr)
            except subprocess.TimeoutExpired:
                print("Тайм-аут: wget занял слишком много времени", file=sys.stderr)
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"Ошибка: {e.stderr.decode('utf-8')}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
                sys.exit(1)

    def test_video_readability(self):
        """Тест считывание файла с видео"""
        if not os.path.exists('./video.mp4'):
            self.fail("Видео отсутствует.")
        cap = cv2.VideoCapture('./video.mp4')
        ret, frame = cap.read()
        cap.release()
        self.assertTrue(ret)

    def test_frame_size(self):
        """Проверка размеров кадров видео"""
        if not os.path.exists('./video.mp4'):
            self.fail("Видео отсутствует.")
        cap = cv2.VideoCapture('./video.mp4')
        ret, frame = cap.read()
        cap.release()
        if ret:
            height, width, _ = frame.shape
            self.assertGreater(height, 0)
            self.assertGreater(width, 0)

    def test_video_duration(self):
        """Проверка длительности видео (больше 1 секунды)"""
        if not os.path.exists('./video.mp4'):
            self.fail("Видео отсутствует.")
        cap = cv2.VideoCapture('./video.mp4')
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        duration = frame_count / fps
        self.assertGreater(duration, 1)


if __name__ == '__main__':
    unittest.main()
