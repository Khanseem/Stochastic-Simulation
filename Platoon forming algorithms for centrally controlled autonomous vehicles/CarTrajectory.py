#class to create cars and output their trajectory when asked, see below for creating and outputing an example
import numpy as np


class CarTrajectory:

    def __init__(self, arr, dep, am, vm, x0, stopDist = 13, prevCarXFullEnd = None):
        self.arr = arr
        self.dep = dep
        self.am = am
        self.vm = vm
        self.x0 = x0
        self.delta = dep - arr

        self.dTAcc = vm / am # assuming full stop of dt = 0
        self.xAcc = 1/2 * self.vm ** 2 / self.am
        self.dTFull = self.delta - 2 * self.dTAcc
        self.xFull = self.dTFull * vm
        if (self.xFull + 2 * self.xAcc) > self.x0:
            self.xFull = self.x0 - 2 * self.xAcc
            self.dTFull = self.xFull / self.vm
            self.dTStop = self.delta - self.dTFull - 2 * self.dTAcc
        else:
            self.dTStop = 0
            if (self.xFull + 2 * self.xAcc) < self.x0:
                self.dTAcc = np.sqrt((self.delta * self.vm - x0) / self.am)
                self.xAcc = -1/2 * self.am * self.dTAcc ** 2 + self.vm * self.dTAcc
                self.dTFull = self.delta - 2 * self.dTAcc
                self.xFull = self.dTFull * self.vm
        if prevCarXFullEnd != None:
            self.xFullEnd = prevCarXFullEnd + stopDist
            self.dTFullEnd = self.xFullEnd / self.vm
            self.xFullStart = self.xFull - self.xFullEnd
            self.dTFullStart = self.dTFull - self.dTFullEnd
        else:
            self.xFullEnd = 0
            self.dTFullEnd = 0
            self.xFullStart = self.xFull
            self.dTFullStart = self.dTFull


    def trajectory(self, stepSize):
        timePoints = np.linspace(self.arr, self.dep, int(np.ceil(self.delta/stepSize)) + 1)
        xPoints = np.zeros(np.alen(timePoints))
        dTimePoints = timePoints - self.arr
        for i in range(np.alen(timePoints)):
            if dTimePoints[i] <= self.dTFullStart:
                xPoints[i] = - self.x0 + dTimePoints[i] * self.vm
            elif dTimePoints[i] <= (self.dTFullStart + self.dTAcc):
                subT = dTimePoints[i] - self.dTFullStart
                xPoints[i] = - self.x0 + self.xFullStart + self.vm * subT - 1/2 * self.am * subT ** 2
            elif dTimePoints[i] <= (self.dTFullStart + self.dTAcc + self.dTStop):
                xPoints[i] = - self.xFullEnd - self.xAcc
            elif dTimePoints[i] <= (self.dTFullStart + 2 * self.dTAcc + self.dTStop):
                subT = dTimePoints[i] - self.dTFullStart - 2 * self.dTAcc - self.dTStop
                xPoints[i] = - self.xFullEnd + self.vm * subT + 1/2 * self.am * subT ** 2
            else:
                xPoints[i] = (timePoints[i] - self.dep) * self.vm
        return timePoints, xPoints