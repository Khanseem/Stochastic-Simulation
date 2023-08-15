import numpy as np
from collections import deque
import Car 
import Event
import SimResults 
import FES 
import numpy as np
from collections import deque

rng = np.random.default_rng()

class CyclicSimulation:

    def __init__(self, lanes, alphaLst, muLst, b, s, vm, x0):
        self.lanes = lanes
        self.alphaLst = alphaLst
        self.muLst = muLst
        self.b = b
        self.s = s
        self.minT = x0 / vm
        self.nrCars = 0

    def simulate(self, totalCars):
        queue = [deque()] * self.lanes
        table = np.zeros((totalCars, 3))
        res = []
        z = 0
        t = 0
        currentLane = 0
        fes = [[]] * (self.lanes + 1)
        fes[self.lanes] = FES()
        #create FES for each lane
        for lane in range(self.lanes):
            res.append(SimResults()) #simulation results
            fes[lane] = FES()
            arrTime = t + self.b + rng.exponential(scale = 1/self.muLst[lane]) * self.alphaLst[lane]
            car = Car(arrTime, lane)
            arr = Event(Event.ARRIVAL, car)
            fes[self.lanes].add(arr)

        while self.nrCars < totalCars:
            for l in range(self.lanes):
                res[l].registerQueueLength(t, len(queue[l])) #register queue lengths for all lanes

            prevLane = currentLane
            notAllEmpty = 0
            for lane in range(self.lanes):
                #check which lane is empty
                notAllEmpty += not fes[lane].isEmpty()
            if fes[currentLane].isEmpty() and bool(notAllEmpty):
                #if current lane is empty and there are cars in other lanes, change to other lanes
                while fes[currentLane].isEmpty(): 
                    currentLane += (currentLane + 1) % self.lanes
                    if prevLane == currentLane:
                        break
                    #if all lanes are empty return to inital current lane
                car = queue[currentLane][0]#get first car in lane
                depTime = max(t + self.s, car.arrTime + self.minT) #add departure event of car
                car.setDepTime(depTime)
                dep = Event(Event.DEPARTURE, car)
                fes[currentLane].add(dep)
                oldCar = car
                if len(queue[currentLane]) > 1: #if there are more cars in the lane schedhule departure events of all teh cars
                    for carEntry in range(1, len(queue[currentLane])):
                        car = queue[currentLane][carEntry]
                        depTime = max(oldCar.depTime + self.b, car.arrTime + self.minT)
                        car.setDepTime(depTime)
                        dep = Event(Event.DEPARTURE, car)
                        fes[currentLane].add(dep)
                        oldCar = car

            if not bool(notAllEmpty) or fes[self.lanes].events[0].time < fes[currentLane].events[0].time:
                # if there are no cars or there are events that occur before the current lane, 
                e = fes[self.lanes].next()
                t = e.time
                car = e.car
                lane = car.lane
                queue[lane].append(car)
                if lane == currentLane and len(queue[lane]) == 1:
                    #if same lane and there is only one car, schedhule departure of the car
                    depTime = t + self.minT
                    car.setDepTime(depTime)
                    dep = Event(Event.DEPARTURE, car)
                    fes[lane].add(dep)
                arrTime = t + self.b + rng.exponential(scale=1 / self.muLst[lane]) * self.alphaLst[lane]
                #create arrival of car
                car = Car(arrTime, lane)
                arr = Event(Event.ARRIVAL, car)
                fes[self.lanes].add(arr)

            else:
                e = fes[currentLane].next()
                t = e.time
                oldCar = e.car
                res[oldCar.lane].registerWaitingTime(t - oldCar.arrTime)
                queue[currentLane].remove(oldCar)
                table[self.nrCars, 0] = oldCar.lane
                table[self.nrCars, 1] = oldCar.arrTime
                table[self.nrCars, 2] = oldCar.depTime
                self.nrCars += 1

                if len(queue[currentLane]) > 0:
                    car = queue[currentLane][0]
                    waitTime = self.b
                    depTime = max((car.arrTime + self.minT), (oldCar.depTime + waitTime))
                    car.setDepTime(depTime)
                    dep = Event(Event.DEPARTURE, car)
                    fes[currentLane].add(dep)

        return table,res