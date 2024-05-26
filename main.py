import cv2
import numpy as np
import requests
from ultralytics import YOLO
import yaml

# Загрузка конфигурации телеграм-бота и видео
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

TOKEN = config['telegram']['TOKEN']
chat_id = config['telegram']['chat_id']
video_path = config['video']['path']

# Загрузка предварительно обученной YOLOv8 модели
model = YOLO('yolov8n.pt')


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


# Отправка сообщения в телеграм
def send_message(token, chat_id, message):
    requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}')


# Отправка фото в телеграм
def send_photo(token, chat_id, img_path):
    files = {'photo': open(img_path, 'rb')}
    requests.post(f'https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}', files=files)


video_capture = cv2.VideoCapture(video_path)
check_det_frame = None
final_image = 0
first_frame_parking_spaces = None
free_parking_timer = 0
free_parking_timer_bag1 = 0
first_frame_parking_score = 0
free_parking_space = False
free_parking_space_box = None
telegram_message = False
x_free, y_free, w_free, h_free = 0, 0, 0, 0

# Работа модели с отображением результатов на видео, пока не нажата клавиша q
while video_capture.isOpened():
    ret, image_to_process = video_capture.read()

    height, width, _ = image_to_process.shape

    # Определение класса машин ("2") в COCO
    results = model.track(image_to_process, persist=False)
    detections = results[0].boxes
    class_indexes, class_scores, boxes = ([] for i in range(3))
    for class_index in detections:
        if class_index.cls.numpy() == 2:
            box = class_index.xywh.numpy().astype(int)[0].tolist()
            box = [box[0] - box[2] // 2, box[1] - box[3] // 2,
                   box[2], box[3]]
            boxes.append(box)
            class_scores.append(float(class_index.conf))

    # Предполагаем, что под каждой стоячей машиной будет парковочное место
    if not first_frame_parking_spaces:
        first_frame_parking_spaces = boxes
        first_frame_parking_score = class_scores

    else:
        chosen_cars_boxes = cv2.dnn.NMSBoxes(boxes, class_scores, 0.0, 0.4)
        cars_area = []

        # Распознавание машин
        for box_index in chosen_cars_boxes:
            car_box = boxes[box_index]
            cars_area.append(car_box)

            x, y, w, h = car_box
            parking_text = 'Car'
            final_image = draw_bbox(image_to_process, x, y, w, h, parking_text, (255, 255, 0))
        cars_boxes = cars_area

        # IoU
        overlaps = compute_overlaps(np.array(first_frame_parking_spaces), np.array(cars_boxes))

        for parking_space_one, area_overlap in zip(first_frame_parking_spaces, overlaps):

            max_IoU = max(area_overlap)
            sort_IoU = np.sort(area_overlap[area_overlap > 0])[::-1]

            if not free_parking_space:
                if 0.0 < max_IoU < 0.4:

                    # Количество парковочных мест по первому условию: 0.0 < IoU < 0.4
                    len_sort = len(sort_IoU)

                    # Количество парковочных мест по второму условию: IoU > 0.15
                    sort_IoU_2 = sort_IoU[sort_IoU > 0.15]
                    len_sort_2 = len(sort_IoU_2)

                    # Проверка двух условий для подсчета кадров с освободившимся местом
                    if (check_det_frame == parking_space_one) & (len_sort != len_sort_2):
                        free_parking_timer += 1

                    elif check_det_frame is None:
                        check_det_frame = parking_space_one

                    else:
                        # Фильтр от багов со "скачком" свободного парковочного места
                        free_parking_timer_bag1 += 1
                        if free_parking_timer_bag1 == 2:
                            # Обнуление счётчика
                            check_det_frame = parking_space_one
                            free_parking_timer = 0

                    # Условие освободившегося места (10 кадров подряд)
                    if free_parking_timer == 10:
                        # Помечаем свободное место
                        free_parking_space = True
                        free_parking_space_box = parking_space_one
                        # Отрисовка рамки освободившегося парковочного места
                        x_free, y_free, w_free, h_free = parking_space_one

            else:
                # Освободившееся место заняли
                overlaps = compute_overlaps(np.array([free_parking_space_box]), np.array(cars_boxes))
                for area in overlaps:
                    max_IoU = max(area)
                    if max_IoU > 0.6:

                        free_parking_space = False
                        telegram_message = False

                        # Отправка сообщения телеграмм-ботом о занятом месте
                        screenshot_parking_space = final_image
                        message = 'Где ты ездишь??? Место уже занято :('
                        path = './image_test_not_free.png'
                        send_message(TOKEN, chat_id, message)
                        cv2.imwrite(path, screenshot_parking_space)
                        send_photo(TOKEN, chat_id, path)

    # Распознавание парковочных мест
    chosen_boxes = cv2.dnn.NMSBoxes(first_frame_parking_spaces,
                                    first_frame_parking_score, 0.0, 0.4)
    parking_spaces = []

    for box_index in chosen_boxes:
        box = first_frame_parking_spaces[box_index]
        # Отрисовка освободившегося места
        if free_parking_space:

            if box == [x_free, y_free, w_free, h_free]:
                parking_text = 'FREE SPACE!!!'
                final_image = draw_bbox(image_to_process, x_free, y_free, w_free, h_free, parking_text, (0, 255, 0))

                # Отправка сообщения телеграмм-ботом о свободном месте
                if not telegram_message:
                    # Скриншот свободного места
                    screenshot_parking_space = final_image
                    message = 'Свободное место! Давай, жми скорее!!!'
                    path = './image_test_free.png'
                    send_message(TOKEN, chat_id, message)
                    cv2.imwrite(path, screenshot_parking_space)
                    send_photo(TOKEN, chat_id, path)

                    telegram_message = True
            else:
                # Координаты и размеры парковочного места
                x, y, w, h = box
                parking_text = 'No parking'
                final_image = draw_bbox(image_to_process, x, y, w, h, parking_text)

        else:
            # Координаты и размеры парковочного места
            x, y, w, h = box
            parking_text = 'No parking'
            final_image = draw_bbox(image_to_process, x, y, w, h, parking_text)

        # Координаты парковочных мест, обнаруженных на первом кадре
        parking_spaces.append(box)
    # Отображение результатов работы модели
    cv2.imshow("Parking Space", final_image)

    # Прерывание отображения клавишей q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Закрытие всех окон с кадрами после завершения
video_capture.release()
cv2.destroyAllWindows()
