import cv2
from tracker import *

# Create tracker object
tracker = EuclideanDistTracker()

cap = cv2.VideoCapture('../../Videos/2NS.mp4')
history = 320 # количество кадров для предварительной обработки
# создание маски (для стабильной камеры)
object_detector = cv2.createBackgroundSubtractorKNN(history=history, dist2Threshold=100, detectShadows=True)
#object_detector = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=80, detectShadows=False)

percent = 70 # уменьшение видео (значение в процентах)

fourcc = cv2.VideoWriter_fourcc(*'XVID') # для записи видео
out = cv2.VideoWriter('output3.avi', fourcc, 30.0, (1920,1080))


def resize_window(frame):                           # для уменьшения окна вывода
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    frame_re = cv2.resize(frame, dim)
    return frame_re


frames = 0 # кол-во обработанных кадров

mask_road = cv2.imread('../../Videos/mask.png', cv2.IMREAD_GRAYSCALE) # маска для обработки только необходимого створа
thresh = 80
mask_road = cv2.threshold(mask_road, thresh, 255, cv2.THRESH_BINARY)[1] # преобразование img в оттенки серого в двоичном коде

count = 0 # счетчик кадров

while True:
    ret, frame = cap.read()

    if frames < history:
        frames += 1
        continue

    if ret:

        mask = object_detector.apply(frame)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_and(mask, mask_road) # наложение маски

        # обработка кадров для получения контуров
        th = cv2.threshold(mask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
        th = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
        dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=5)
        # cv2.imshow('Dron-View2', th)
        # cv2.imshow('Dron-View1', dilated)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        # print(contours[0])  # вывод обработанного кадра
        detections = []

        for cont in contours:
            # расчет области для каждого объекта
            area = cv2.contourArea(cont)
            if 10_000 > area > 300:
                x, y, w, h = cv2.boundingRect(cont)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                detections.append([x, y, w, h])

        frame_re = resize_window(frame)
        mask = resize_window(mask)

        count += 1
        cv2.putText(frame, ("frame: " + str(count)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        boxes_ids = tracker.update(detections, count) # засунули всю информацию о объектах
        print(count, ':', *list(map(lambda x: f'(id:{x[4]}, x:{x[0]}, y:{x[1]})' if x[4] < 7 else'', boxes_ids)))

        for box_id in boxes_ids: # id на кадре
            x, y, w, h, id = box_id
            cv2.putText(frame, str(id), (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        cv2.imshow('Dron-View', frame) # вывод обработанного кадра
        cv2.imshow('Mask', mask) # вывод маски
        out.write(frame) # сохранение обработанного видео
        cv2.imwrite(f'frame/frame-{count}.jpg', frame)
        cv2.imwrite(f'mask/mask-{count}.jpg', mask)

    else:
        print('Can\'t receive frame from file. Exiting...')
        break

    if cv2.waitKey(30) == ord('q'):
        print('Keyboard exiting...')
        print(count)
        break




cap.release()
cv2.destroyAllWindows()