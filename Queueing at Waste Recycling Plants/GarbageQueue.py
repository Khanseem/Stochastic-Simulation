from collections import deque


class GarbageQueue:

    def __init__(self):
        self.queue = deque()

    def remove(self, vehicle):
        self.queue.remove(vehicle)

    def add(self, vehicle):
        self.queue.append(vehicle)

    def isEmpty(self):
        return len(self.queue) == 0

    def length(self):
        return len(self.queue)