import heapq


class GateQueue:

    def __init__(self):
        self.queue = []

    def add(self, vehicle):
        heapq.heappush(self.queue, vehicle)

    def next(self):
        return heapq.heappop(self.queue)

    def isEmpty(self):
        return len(self.queue) == 0

    def length(self):
        return len(self.queue)

    def remove(self, vehicle):
        self.queue.remove(vehicle)
        heapq.heapify(self.queue)