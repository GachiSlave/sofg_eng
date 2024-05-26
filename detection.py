import cv2
import numpy as np


# Расчет IoU
def calculate_iou(box, boxes, box_area, boxes_area):
    y1 = np.maximum(box[0], boxes[:, 0])
    y2 = np.minimum(box[2] + box[0], boxes[:, 2] + boxes[:, 0])
    x1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[3] + box[1], boxes[:, 3] + boxes[:, 1])
    intersection = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
    union = box_area + boxes_area[:] - intersection[:]
    iou = intersection / union
    return iou


# Расчет пересечения рамок
def compute_overlaps(boxes1, boxes2):
    area1 = boxes1[:, 2] * boxes1[:, 3]
    area2 = boxes2[:, 2] * boxes2[:, 3]
    overlaps = np.zeros((boxes1.shape[0], boxes2.shape[0]))
    for i in range(overlaps.shape[1]):
        box2 = boxes2[i]
        overlaps[:, i] = calculate_iou(box2, boxes1, area2[i], area1)
    return overlaps


# Отрисовка рамок
def draw_bbox(image, x, y, w, h, text, color=(0, 0, 255)):
    start, end = (x, y), (x + w, y + h)
    cv2.rectangle(image, start, end, color, 2)
    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
    return image
