#Библиотеки
import cv2
import numpy as np
import pandas as pd
from art import tprint
import matplotlib.pylab as plt
import requests
from ultralytics import YOLO

#Это необходимо заполнить для работы с telegram ботом
TOKEN = "YOUR_TOKEN"
chat_id = "YOUR_CHAT_ID"

# load yolov8 model
model = YOLO('yolov8n.pt')

# ##### Пути до конфигурации и весов модели
# path_conf = "./yolov4-tiny.cfg"
# path_weights = "./yolov4-tiny.weights"

#Классы которые распознает YOLO
path_coco_names = "./coco.names.txt"

#Тестовое видео
video_path = './video.mp4'

#Функции для подсчета Intersection over Union (IoU)
def calculate_iou(box, boxes, box_area, boxes_area):
    #Считаем IoU
    y1 = np.maximum(box[0], boxes[:, 0])
    y2 = np.minimum(box[2]+box[0], boxes[:, 2]+boxes[:, 0])
    x1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[3]+box[1], boxes[:, 3]+boxes[:, 1])
    intersection = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
    union = box_area + boxes_area[:] - intersection[:]
    iou = intersection / union
    return iou

#Функция для расчета персечения всех со всеми через IoU
def compute_overlaps(boxes1, boxes2):
    #Areas of anchors and GT boxes
    area1 = boxes1[:, 2] * boxes1[:, 3]
    area2 = boxes2[:, 2] * boxes2[:, 3]
    overlaps = np.zeros((boxes1.shape[0], boxes2.shape[0]))
    for i in range(overlaps.shape[1]):
        box2 = boxes2[i]
        overlaps[:, i] = calculate_iou(box2, boxes1, area2[i], area1)
    return overlaps


# Функция для отрисовки Bounding Box в кадре
def draw_bbox(x, y, w, h, parking_text, parking_color=(0, 255, 0)):
    start = (x, y)
    end = (x + w, y + h)
    color = parking_color
    width = 2
    final_image = cv2.rectangle(image_to_process, start, end, color, width)

    # Подпись BB
    start = (x, y - 10)
    font_size = 0.4
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 1
    text = parking_text
    final_image = cv2.putText(final_image, text, start, font, font_size, color, width, cv2.LINE_AA)
    return final_image


#Функция для отправки фото в телеграм
def send_photo_file(chat_id, img):
    files = {'photo': open(img, 'rb')}
    requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}', files=files)

#Функция для отправки сообщения в телеграм
def send_telegram_message(message):
    requests.get(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}').json()


#Определяем параметры модели
#Загружаем конфигурацию и веса модели скаченные ранее
#https://docs.opencv.org/4.x/d6/d0f/group__dnn.html#gae11aaf57b3f2bbdaf99ea6e4957d8384
#Считывает модель сети, хранящуюся в файлах моделей Darknet.

# net = cv2.dnn.readNetFromDarknet(path_conf, path_weights)
# layer_names = net.getLayerNames()

#https://docs.opencv.org/3.4/db/d30/classcv_1_1dnn_1_1Net.html#ae62a73984f62c49fd3e8e689405b056a
#Возвращает индексы слоев с неподключенными выходами.

# out_layers_indexes = net.getUnconnectedOutLayers()
# out_layers = [layer_names[index - 1] for index in out_layers_indexes]

#Парковочные места
first_frame_parking_spaces = None

free_parking_timer = 0
free_parking_timer_bag1 = 0
free_parking_count = 0
first_parking_timer = 0
free_parking_space = False
free_parking_space_box = None
check_det_frame = None

#Сообщение в телеграм?
telegram_message = False

# Инициализируем работу с видео
video_capture = cv2.VideoCapture(video_path)

# Пока не нажата клавиша q функция будет работать
# isOpened() Возвращает true, если захват видео уже инициализирован.
while video_capture.isOpened():

    # Захват, декодирование и возврат следующего видеокадра
    # https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#a473055e77dd7faa4d26d686226b292c1
    ret, image_to_process = video_capture.read()

    # Препроцессинг изображения и работа YOLO
    height, width, _ = image_to_process.shape
    # Создает 4-мерный блоб из изображения
    """
      blobFromImage

      #https://docs.opencv.org/4.x/d6/d0f/group__dnn.html#ga29f34df9376379a603acd8df581ac8d7          
      image	  входное изображение (с 1-, 3- или 4-канальным)..

      scalefactor	множитель для значений изображений.

      size	  пространственный размер выходного изображения

      mean	  скаляр со средними значениями, которые вычитаются из каналов. 
              Значения должны располагаться в порядке (mean-R, mean-G, mean-B), 
              если изображение имеет порядок BGR и значение swapRB равно true.

      swapRB	флаг, указывающий, что необходимо поменять местами первый и 
              последний каналы в 3-канальном изображении.


      crop	  флаг, указывающий, будет ли изображение обрезано 
              после изменения размера или нет

      ddepth	Глубина выходного объекта. Выберите CV_32F или CV_8U.
    """
    # blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (608, 608),
    #                              (0, 0, 0), swapRB=True, crop=False)
    """
    setInput

    https://docs.opencv.org/3.4/db/d30/classcv_1_1dnn_1_1Net.html#a5e74adacffd6aa53d56046581de7fcbd

    Устанавливает новое входное значение для сети.
    """
    # net.setInput(blob)
    results = model.track(image_to_process, persist=True)
    frame_ = results[0].plot()
    # https://docs.opencv.org/3.4/db/d30/classcv_1_1dnn_1_1Net.html#a98ed94cb6ef7063d3697259566da310b
    # Выполняет прямой проход для вычисления выхода слоя с именем outputName.
    # Иницилизация пустыми []
    class_indexes, class_scores, boxes = ([] for i in range(3))

    # # Обнаружение объектов в кадре
    # for out in outs:
    #     print(out)
    #     for obj in out:
    #         print(obj)
    #         scores = obj[5:]
    #         print(scores)
    #         class_index = np.argmax(scores, 1)
    #         # В классе 2 (car) только автомобили
    #         if class_index == 2:
    #             class_score = scores[class_index]
    #             print('class_index')
    #             if class_score > 0:
    #                 center_x = int(obj[0] * width)
    #                 center_y = int(obj[1] * height)
    #                 obj_width = int(obj[2] * width)
    #                 obj_height = int(obj[3] * height)
    #                 box = [center_x - obj_width // 2, center_y - obj_height // 2,
    #                        obj_width, obj_height]
    #
    #                 # BBoxes
    #                 boxes.append(box)
    #                 class_indexes.append(class_index)
    #                 class_scores.append(float(class_score))
    #                 print('class_score')
    #
    # ###ПЕРВЫЙ КАДР ОПРЕДЕЛЯЕМ ПАРКОМЕСТА
    # if not first_frame_parking_spaces:
    #     # Предполагаем, что под каждой машиной будет парковочное место
    #     first_frame_parking_spaces = boxes
    #     first_frame_parking_score = class_scores
    #     print('first_frame_parking_spaces')
    #
    # else:
    #     chosen_cars_boxes = cv2.dnn.NMSBoxes(boxes, class_scores, 0.0, 0.4)
    #     cars_area = []
    #
    #     ###МАШИНЫ
    #     for box_index in chosen_cars_boxes:
    #         car_box = boxes[box_index]
    #         cars_area.append(car_box)
    #
    #         x, y, w, h = car_box
    #         parking_text = 'Car'
    #         print('box_index')
    #         final_image = draw_bbox(x, y, w, h, parking_text, (255, 255, 0))
    #
    #     # Теперь зная парковочные места, определим когда место освободится
    #     cars_boxes = cars_area
    #
    #     ###IoU
    #     overlaps = compute_overlaps(np.array(parking_spaces), np.array(cars_boxes))
    #
    #     for parking_space_one, area_overlap in zip(parking_spaces, overlaps):
    #
    #         max_IoU = max(area_overlap)
    #         sort_IoU = np.sort(area_overlap[area_overlap > 0])[::-1]
    #
    #         if free_parking_space == False:
    #             print('free_parking_space')
    #             if 0.0 < max_IoU < 0.4:
    #                 print('max_IoU')
    #                 # Количество паркомест по условию 1: 0.0 < IoU < 0.4
    #                 len_sort = len(sort_IoU)
    #
    #                 # Количество паркомест по условию 2: IoU > 0.15
    #                 sort_IoU_2 = sort_IoU[sort_IoU > 0.15]
    #                 len_sort_2 = len(sort_IoU_2)
    #
    #                 # Смотрим чтобы удовлятворяло условию 1 и условию 2
    #                 if (check_det_frame == parking_space_one) & (len_sort != len_sort_2):
    #                     # Начинаем считать кадры подряд с пустыми координатами
    #                     free_parking_timer += 1
    #                     print('check_det_frame')
    #
    #                 elif check_det_frame == None:
    #                     check_det_frame = parking_space_one
    #
    #                 else:
    #                     # Фильтр от чехарды мест (если место чередуется, то "скачет")
    #                     free_parking_timer_bag1 += 1
    #                     if free_parking_timer_bag1 == 2:
    #                         # Обнуляем счётчик, если паркоместо "скачет"
    #                         check_det_frame = parking_space_one
    #                         free_parking_timer = 0
    #
    #                 # Если более 10 кадров подряд, то предполагаем, что место свободно
    #                 if free_parking_timer == 10:
    #                     # Помечаем свободное место
    #                     free_parking_space = True
    #                     free_parking_space_box = parking_space_one
    #                     # Отрисовываем рамку парковочного места
    #                     x_free, y_free, w_free, h_free = parking_space_one
    #
    #         else:
    #             # Если место занимают, то помечается как отсутствие свободных мест
    #             overlaps = compute_overlaps(np.array([free_parking_space_box]), np.array(cars_boxes))
    #             for area_overlap in overlaps:
    #                 max_IoU = max(area_overlap)
    #                 if max_IoU > 0.6:
    #
    #                     free_parking_space = False
    #                     telegram_message = False
    #
    #                     # Отправка сообщения боту в телеграмм
    #                     if not telegram_message:
    #                         screenshot_parking_space = final_image
    #                         # отправим в телеграм
    #                         message_tel = 'Где ты ездишь??? Место уже занято :('
    #                         send_telegram_message(message_tel)
    #                         cv2.imwrite('./image_test_not_free.png', screenshot_parking_space)
    #                         send_photo_file(chat_id, './image_test_not_free.png')
    #
    #                         telegram_message = True
    #
    # ###ПАРКОВОЧНЫЕ МЕСТА
    # # Отрисовка BB парковочных мест
    # chosen_boxes = cv2.dnn.NMSBoxes(first_frame_parking_spaces,
    #                                 first_frame_parking_score, 0.0, 0.4)
    # parking_spaces = []
    # print('first_frame_parking_spaces2')
    # for box_index in chosen_boxes:
    #     box = first_frame_parking_spaces[box_index]
    #     # Если определилось пустое место, то отрисуем его в кадре
    #     if free_parking_space:
    #         if box == [x_free, y_free, w_free, h_free]:
    #             parking_text = 'FREE SPACE!!!'
    #             print('$')
    #             final_image = draw_bbox(x_free, y_free, w_free, h_free, parking_text, (0, 0, 255))
    #         else:
    #             x, y, w, h = box
    #             parking_text = 'No parking'
    #             print('$')
    #             final_image = draw_bbox(x, y, w, h, parking_text)
    #
    #         # Отправка сообщения боту в телеграмм
    #         if not telegram_message:
    #             # Скриншот свободного места, отправим в телеграм
    #             screenshot_parking_space = final_image
    #             message_tel = 'Свободное место! Давай, жми скорее!!!'
    #             send_telegram_message(message_tel)
    #             cv2.imwrite('./image_test_free.png', screenshot_parking_space)
    #             send_photo_file(chat_id, './image_test_free.png')
    #
    #             telegram_message = True
    #
    #     else:
    #         # Координаты и размеры BB
    #         x, y, w, h = box
    #         parking_text = 'No parking'
    #         final_image = draw_bbox(x, y, w, h, parking_text)
    #
    #     # Координаты парковочных мест с первого кадры
    #     parking_spaces.append(box)
    # # Показать результат работы
    # cv2.imshow("Parking Space", final_image)
    #
    # # Прерывание работы клавишей q
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     # Очищаем всё после завершения.
    #     video_capture.release()
    #     cv2.destroyAllWindows()
    #     break

# visualize
    cv2.imshow('frame', frame_)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
