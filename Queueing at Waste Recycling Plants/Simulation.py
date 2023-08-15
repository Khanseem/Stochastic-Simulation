import numpy as np
import FES
import Event
import GarbageQueue
import Gate
import GateQueue
import Station
import Vehicle
rng = np.random.default_rng()


class Simulation:

    def simulate(self, startTime, openTime, closeTime, stations, arrTimeVars, gateTimeVars, impatiencyVars, vehicleVars, gateEntrances = 1, forgetChance = 0.05, disableImpatiency = False):
        t = startTime
        fes = FES()

        stationLst = []
        for n in range(len(stations)):
            stationLst.append(Station(stations[n][0], stations[n][1], stations[n][2], stations[n][3]))
        gate = Gate(gateEntrances, gateTimeVars)

        self.createArrival(t, startTime, closeTime, arrTimeVars, impatiencyVars, stationLst, stations, forgetChance, vehicleVars, fes)

        queueLog = []
        impatientLog = []
        vehicleLog = []
        self.logQueues(queueLog, t, gate, stationLst)

        run = True
        while run:
            event = fes.next()
            t = event.time
            vehicle = event.vehicle
            if event.type == Event.ARRIVAL:
                gate.add(vehicle)
                if gate.queue.isEmpty():
                    # plan move to station
                    self.planGateMove(t, openTime, vehicle, gate, fes)
                elif not disableImpatiency:
                    # plan leaving due to impatiency
                    event = Event(Event.IMPATIENT, vehicle, vehicle.impatiencyTime)
                    fes.add(event)
                # plan next arrival
                self.createArrival(t, startTime, closeTime, arrTimeVars, impatiencyVars, stationLst, stations, forgetChance, vehicleVars, fes)

            elif event.type == Event.STATIONMOVE:
                oldStation = vehicle.currentStation
                if oldStation == 0: # the old station was the gate
                    allSpace = True # check if all stations have space
                    for n in range(len(stationLst)):
                        if not stationLst[n].fits(vehicle.size):
                            allSpace = False
                    if allSpace:
                        newStation = vehicle.nextStation()
                        # move to next station
                        newStation.add(vehicle)
                        if newStation.queue.isEmpty():
                            # instantly serviced at new station
                            self.planStationMove(t, vehicle, newStation, fes)
                        # manage situation at old location (gate)
                        gate.remove(vehicle)
                        if not gate.queue.isEmpty():
                            newVehicle = gate.queueToGate()
                            self.planGateMove(t, openTime, newVehicle, gate, fes)
                    else: # no space for vehicle so reinsert this event directly after the next time someone moves from a station
                        nextEventType = Event.ARRIVAL
                        nextEventStation = 0
                        i = -1
                        while not ((nextEventType == Event.DEPARTURE or nextEventType == Event.STATIONMOVE) and not nextEventStation == 0):
                            i += 1
                            nextEventType = fes.events[i].type
                            nextEventStation = fes.events[i].vehicle.currentStation
                        event.time = fes.events[i].time
                        vehicle.gateWaitTime += event.time - t
                        fes.add(event)
                else:
                    newStation = vehicle.nextStation()
                    # move to next station
                    newStation.add(vehicle)
                    if newStation.queue.isEmpty():
                        # instantly serviced at new station
                        self.planStationMove(t, vehicle, newStation, fes)
                    # manage situation at old location (station)
                    self.updateOldStation(t, vehicle, oldStation, fes)

            elif event.type == Event.DEPARTURE:
                oldStation = vehicle.currentStation
                if oldStation == 0:
                    # manage situation at old location (gate)
                    gate.remove(vehicle)
                    if not gate.queue.isEmpty():
                        newVehicle = gate.queueToGate()
                        self.planGateMove(t, openTime, newVehicle, gate, fes)
                else:
                    # manage situation at old location (station)
                    self.updateOldStation(t, vehicle, oldStation, fes)
                self.logVehicle(vehicleLog, vehicle)

            elif event.type == Event.IMPATIENT and not vehicle.serviced:
                gate.queue.remove(vehicle)
                self.logImpatient(impatientLog, t, vehicle, gate)

            self.logQueues(queueLog, t, gate, stationLst)
            if fes.isEmpty():
                run = False
        return queueLog, impatientLog, vehicleLog

    def createArrival(self, t, startTime, closeTime, arrTimeVars, impatiencyVars, stationLst, stations, forgetChance, vehicleVars, fes):
        halfHourOfService = np.floor(t / 30 / 60) - np.floor(startTime / 30 / 60) # find correct vehicle arrival density
        beta = 1 / (arrTimeVars[int(halfHourOfService)] / 30 / 60)
        arrRNG = rng.exponential(scale = beta)
        emptyTimeslots = 0
        if arrRNG > 30 * 60 * (emptyTimeslots + 1): # with extremely sparse arrivals, a first arrival might take ages
            emptyTimeslots += 1                     # so it'll select the next density after half an hour
            beta = 1 / (arrTimeVars[int(halfHourOfService + emptyTimeslots)] / 30 / 60)
            arrRNG = emptyTimeslots * 30 * 60 + rng.exponential(scale=beta) / emptyTimeslots
        arrTime = t + arrRNG
        if arrTime <= closeTime: # as long as vehicles are allowed to arrive, create a new one
            impatiencyTime = arrTime + rng.gamma(impatiencyVars[0], impatiencyVars[1])
            typRNG = rng.uniform()
            vehicleStations = [] # generate stations to be visited and list cannot be empty
            while len(vehicleStations) == 0:
                for n in range(len(stationLst)):
                    if rng.uniform() <= stations[n][4]:
                        vehicleStations.append(stationLst[n])
            forgetCityPass = rng.uniform() <= forgetChance
            vehicle = Vehicle(arrTime, vehicleStations, forgetCityPass, impatiencyTime, vehicleVars, typRNG)
            event = Event(Event.ARRIVAL, vehicle, arrTime)
            fes.add(event)

    def planGateMove(self, t, openTime, vehicle, gate, fes):
        vehicle.gateWaitTime = t - vehicle.arrTime
        vehicle.serviced = True
        serviceTime = max(t, openTime) + gate.genServiceTime()
        if vehicle.forgetCityPass:
            vehicle.setDepTime(serviceTime)
            event = Event(Event.DEPARTURE, vehicle, serviceTime)
        else:
            vehicle.stationArrTime = serviceTime
            event = Event(Event.STATIONMOVE, vehicle, serviceTime)
        fes.add(event)

    def planStationMove(self, t, vehicle, station, fes):
        if vehicle.noStationsLeft():
            #plan departure
            serviceTime = t + station.genServiceTime()
            vehicle.setDepTime(serviceTime)
            event = Event(Event.DEPARTURE, vehicle, serviceTime)
            fes.add(event)
        else:
            #plan stationmove
            serviceTime = t + station.genServiceTime()
            vehicle.stationArrTime = serviceTime
            event = Event(Event.STATIONMOVE, vehicle, serviceTime)
            fes.add(event)

    def updateOldStation(self, t, vehicle, oldStation, fes):
        oldStation.remove(vehicle)
        if not oldStation.queue.isEmpty():
            if oldStation.queueFits():
                newVehicle = oldStation.queueToStation()
                newVehicle.stationWaitTime += (t - newVehicle.stationArrTime)
                self.planStationMove(t, newVehicle, oldStation, fes)

    def logQueues(self, log, t, gate, stationLst):
        logEntry = [t, len(gate.occupation), gate.fill(), gate.returnQueueLen()]
        for n in range(len(stationLst)):
            logEntry.append(len(stationLst[n].occupation))
            logEntry.append(stationLst[n].fill())
            logEntry.append(stationLst[n].returnQueueLen())
        log.append(logEntry)
        # print(logEntry)

    def logImpatient(self, log, t, vehicle, gate):
        logEntry = [t, vehicle.impatiencyTime - vehicle.arrTime, gate.returnQueueLen() + len(gate.occupation)]
        log.append(logEntry)

    def logVehicle(self, log, vehicle):
        logEntry = [vehicle.type, vehicle.arrTime, vehicle.depTime, vehicle.gateWaitTime, vehicle.stationWaitTime]
        if vehicle.forgetCityPass:
            subLogEntry = [0]
        else:
            subLogEntry = []
            for i in range(len(vehicle.stations)):
                subLogEntry.append(vehicle.stations[i].name)
        logEntry.append(subLogEntry)
        log.append(logEntry)
