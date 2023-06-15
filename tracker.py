import math

check2 = {} # объекты которые мы потеряли на текущем кадре


class EuclideanDistTracker:
    def __init__(self):
        # сохранение центральных положений объектов
        self.center_points = {} #словарь: id - x, y
        # подсчет id
        # каждый раз, когда обнаруживается новый id, id_count++
        self.id_count = 0


    def update(self, objects_rect, count):

        objects_bbs_ids = []
        check = {} # объекты которые мы нашли на текущем кадре

        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2  # округляет до целых, центр бокса
            cy = (y + y + h) // 2

            # Поиск пропавших авто
            for id, pt in list(check2.items()):  # цикл по элементам словаря
                dist = math.hypot(cx - pt[0], cy - pt[1])  # евклидова норма между точками

                if (0 < cy < 80) or (1000 < cy < 1080) or (1850 < cx< 1920): # перестаем отслеживать
                    del check2[id]
                    break

                if dist < 45:
                    self.center_points[id] = (cx, cy)
                    del check2[id]
                    objects_bbs_ids.append([cx, y, w, h, id])
                    break

        # выичсления центра bbx
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2 # округляет до целых, центр бокса
            cy = (y + y + h) // 2

            # Определим, был ли этот объект уже обнаружен
            same_object_detected = False
            for id, pt in self.center_points.items(): # цикл по элементам словаря
                dist = math.hypot(cx - pt[0], cy - pt[1]) # евклидова норма между точками

                if dist < 35: #объект с прошлого кадра
                    self.center_points[id] = (cx, cy)
                    check[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # обнаружен новый объект, которому мы присваиваем идентификатор
            if same_object_detected is False and (700 < cx < 780):
                self.center_points[self.id_count] = (cx, cy)
                check[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        for id, pt in self.center_points.items(): # в check2 добавляем все утерянные объекты
            if id not in check.keys():
                check2[id] = pt

        #print(count)
        #print('найденные', check)
        #print('утерянные', check2)
        #print()

        # очистка словаря по центральным точкам, чтобы удалить идентификаторы, которые больше не используются
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # обновить словарь с удаленными неиспользуемыми идентификаторами
        self.center_points = new_center_points.copy()
        return objects_bbs_ids