import math
from collections import deque

class Tracker:
    def __init__(self, max_distance=50, max_history=5):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        self.id_count = 0
        # Maximum distance to consider an object the same
        self.max_distance = max_distance
        # History of points to estimate velocity
        self.history = {}
        # Maximum history length for velocity estimation
        self.max_history = max_history

    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, x2, y2 = rect
            w = x2 - x
            h = y2 - y
            cx = (x + x2) // 2
            cy = (y + y2) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < self.max_distance:
                    # Update center point
                    self.center_points[id] = (cx, cy)
                    # Update history for velocity estimation
                    if id in self.history:
                        self.history[id].append((cx, cy))
                        if len(self.history[id]) > self.max_history:
                            self.history[id].popleft()
                    else:
                        self.history[id] = deque([(cx, cy)], maxlen=self.max_history)
                    
                    objects_bbs_ids.append([x, y, x2, y2, id])
                    same_object_detected = True
                    break

            # New object is detected, assign the ID to that object
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                self.history[self.id_count] = deque([(cx, cy)], maxlen=self.max_history)
                objects_bbs_ids.append([x, y, x2, y2, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDs not used anymore
        new_center_points = {}
        new_history = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center
            new_history[object_id] = self.history[object_id]

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points
        self.history = new_history
        
        return objects_bbs_ids

    def predict_next_position(self, object_id):
        # Predict the next position of an object based on its velocity
        if object_id in self.history and len(self.history[object_id]) > 1:
            # Calculate the average velocity
            dx = 0
            dy = 0
            history = list(self.history[object_id])
            for i in range(1, len(history)):
                dx += history[i][0] - history[i-1][0]
                dy += history[i][1] - history[i-1][1]
            dx /= (len(history) - 1)
            dy /= (len(history) - 1)
            # Predict next position
            last_position = history[-1]
            predicted_position = (last_position[0] + dx, last_position[1] + dy)
            return predicted_position
        else:
            return None
