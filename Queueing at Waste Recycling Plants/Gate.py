from collections import deque
import numpy as np
from GateQueue import *

rng = np.random.default_rng()


class Gate:

    def __init__(self, capacity, serviceTimeVars):
        self.capacity = capacity
        self.occupation = deque()
        self.queue = GateQueue()
        self.serviceTimeVars = serviceTimeVars

    def add(self, vehicle):
        if not self.isFull():
            self.occupation.append(vehicle)
        else:
            self.queue.add(vehicle)

    def queueToGate(self):
        vehicle = self.queue.next()
        self.occupation.append(vehicle)
        return vehicle

    def remove(self, vehicle):
        self.occupation.remove(vehicle)

    def isFull(self):
        return len(self.occupation) == self.capacity

    def fill(self):
        fill = 0
        for i in range(len(self.occupation)):
            fill += self.occupation[i].size
        return fill

    def relativeFill(self):
        return len(self.occupation) / self.capacity

    def returnQueueLen(self):
        return self.queue.length()

    def genServiceTime(self):
        serviceTime = rng.gamma(self.serviceTimeVars[0], self.serviceTimeVars[1])
        return serviceTime
