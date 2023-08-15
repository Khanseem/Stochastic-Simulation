import numpy as np
from collections import deque
import Car 
import Event
import SimResults 
import FES 

rng = np.random.default_rng()

class FCFSSimulation:

    def __init__(self, lanes, alphaLst, muLst, b, s, vm, x0):
        self.lanes = lanes
        self.alphaLst = alphaLst
        self.muLst = muLst
        self.b = b
        self.s = s
        self.minT = x0 / vm
        self.nrCars = 0

    def simulate(self, totalCars):
        laneQueue = [] #Queues for each lane
        table = np.zeros((totalCars, 3))
        res = []
        crossingQueue = deque() #Queue for all lanes at crossing
        previousDepartureTime = 0

        for lane in range(self.lanes):
          laneRes = SimResults () # simulation results
          res.append(laneRes)
          laneQueue.append(deque())

        t = 0
        fes = FES()
        firstCarArrTime = 1000 #set random high number 
        for lane in range(self.lanes):
            arrTime = t + self.b + rng.exponential(scale = 1/self.muLst[lane]) * self.alphaLst[lane]
            car = Car(arrTime, lane)
            arr = Event(Event.ARRIVAL, car)
            fes.add(arr)
            if arrTime < firstCarArrTime : #get first lane car moves from
                firstCarArrTime = arrTime
                currentLane = lane
            

        while self.nrCars < totalCars:
            e = fes.next()
            t = e.time
            lane = e.car.lane
            
            for l in range(self.lanes):
                res[l].registerQueueLength(t, len(laneQueue[l])) #register queue lengths for all lanes

            if e.type == Event.ARRIVAL:
                oldCar = e.car
                laneQueue[lane].append(oldCar)
                crossingQueue.append(oldCar)
                if len(crossingQueue) == 1: #only one lane can have cars moving so there is only 1 server 
                    #if there is a free server, 
                    res[lane].registerWaitingTime(t - oldCar.arrTime) #register car waiting time when car departs , if q is 0 waiting time shd be 0
                    if oldCar.lane == currentLane :
                        if oldCar.arrTime - previousDepartureTime <1: #if moving from same lane, time must be more than or equal to 1
                            depTime = previousDepartureTime +1
                        else:
                            depTime = t 
                        car.setDepTime(depTime)
                        dep =Event(Event.DEPARTURE, oldCar) 
                        previousDepartureTime = t 
                    else:
                        if oldCar.arrTime - previousDepartureTime <2.4: #if moving from a different lane, time must be more than or equal to 2.4
                            depTime = previousDepartureTime +2.4
                        else:
                            depTime = t 
                        oldCar.setDepTime(depTime)
                        dep =Event(Event.DEPARTURE, oldCar)  
                        previousDepartureTime = depTime 
                        currentLane =  oldCar.lane
                    fes.add(dep)

                if len(crossingQueue) != 0:
                    arrTime = t + rng.exponential(scale=1 / self.muLst[lane]) * self.alphaLst[lane]
                    car = Car(arrTime, lane)
                    arr = Event(Event.ARRIVAL, car)
                    fes.add(arr)

            elif e.type == Event.DEPARTURE:
                
                previousDepartureTime = t 
                oldCar = e.car
                laneQueue[oldCar.lane].remove(oldCar)
                crossingQueue.remove(oldCar)
                res[oldCar.lane].registerWaitingTime(t - oldCar.arrTime) #car has moved off, so register its waiting time and remove it from queue

                table[self.nrCars, 0] = oldCar.lane
                table[self.nrCars, 1] = oldCar.arrTime
                table[self.nrCars, 2] = oldCar.depTime
                self.nrCars += 1

                if len(crossingQueue) > 0:
                    car = crossingQueue[0] 
                    
                    if car.lane == currentLane:
                        depTime = previousDepartureTime+self.b
                    else:
                        depTime = previousDepartureTime+self.s                
                    car.setDepTime(depTime)

                    dep = Event(Event.DEPARTURE, car) 
                    fes.add(dep)
                    currentLane = car.lane
                    previousDepartureTime = t

        return table , res