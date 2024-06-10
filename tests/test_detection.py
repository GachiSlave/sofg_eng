import numpy as np
import os
import sys
import unittest

# Добавление пути к родительской директории
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detection import calculate_iou, compute_overlaps


class TestDetection(unittest.TestCase):
    def test_calculate_iou(self):
        """Тестирование расчета IoU между рамками"""
        box = [0, 0, 10, 10]
        boxes = np.array([[0, 0, 10, 10], [10, 10, 10, 10]])
        box_area = 100
        boxes_area = np.array([100, 100])
        iou = calculate_iou(box, boxes, box_area, boxes_area)
        self.assertEqual(iou[0], 1.0)
        self.assertEqual(iou[1], 0.0)

    def test_compute_overlaps(self):
        """Тест на вычисление перекрытий между несколькими рамками"""
        boxes1 = np.array([[0, 0, 10, 10], [10, 10, 10, 10]])
        boxes2 = np.array([[0, 0, 10, 10], [10, 10, 10, 10]])
        overlaps = compute_overlaps(boxes1, boxes2)
        self.assertEqual(overlaps[0, 0], 1.0)
        self.assertEqual(overlaps[1, 1], 1.0)
        self.assertEqual(overlaps[0, 1], 0.0)
        self.assertEqual(overlaps[1, 0], 0.0)


if __name__ == '__main__':
    unittest.main()
