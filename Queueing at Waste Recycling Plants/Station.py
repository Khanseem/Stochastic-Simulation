from collections import deque
import numpy as np
from GarbageQueue import *

rng = np.random.default_rng()


class Station:

    def __init__(self, name, order, capacity, serviceTimeVars):
        self.name = name
        self.order = order
        self.capacity = capacity
        self.occupation = deque()
        self.queue = GarbageQueue()
        self.serviceTimeVars = serviceTimeVars

    def __lt__(self, other):
        return self.order < other.order

    def fill(self):
        fill = 0
        for i in range(len(self.occupation)):
            fill += self.occupation[i].size
        return fill

    def fits(self, size):
        return (self.capacity - self.fill()) >= size

    def add(self, vehicle):
        if self.fits(vehicle.size) and self.queue.isEmpty():
            self.occupation.append(vehicle)
        else:
            self.queue.add(vehicle)

    def queueFits(self):
        return self.fits(self.queue.queue[0].size)

    def queueToStation(self):
        vehicle = self.queue.queue[0]
        self.queue.remove(vehicle)
        self.occupation.append(vehicle)
        return vehicle

    def remove(self, vehicle):
        self.occupation.remove(vehicle)

    def isFull(self):
        return self.fill() == self.capacity

    def relativeFill(self):
        return self.fill() / self.capacity

    def returnQueueLen(self):
        return self.queue.length()

    def genServiceTime(self):
        serviceTime = rng.gamma(self.serviceTimeVars[0], self.serviceTimeVars[1])
        return serviceTime
