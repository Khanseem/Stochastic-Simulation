import heapq
import copy


class Vehicle:

    def __init__(self, arrTime, stations, forgetCityPass, impatiencyTime, vehicleVars, typRNG):
        self.arrTime = arrTime
        self.forgetCityPass = forgetCityPass
        self.impatiencyTime = impatiencyTime
        self.gateWaitTime = 0
        self.stationArrTime = 0
        self.stationWaitTime = 0
        self.serviced = False
        self.stations = stations
        self.upcomingStations = copy.copy(stations)
        heapq.heapify(self.upcomingStations)
        self.currentStation = 0
        self.vehicleTypes = dict({})
        for i in range(len(vehicleVars)):
            self.vehicleTypes[list(vehicleVars.keys())[i]] = i
        self.type = 0
        self.typRNG = typRNG
        while self.typRNG > vehicleVars[list(vehicleVars.keys())[self.type]]:
            self.typRNG -= vehicleVars[list(vehicleVars.keys())[self.type]]
            self.type += 1
        if self.type == self.vehicleTypes["VAN"]:
            self.size = 2
        else:
            self.size = 1
        if self.type == self.vehicleTypes["PEDESTRIAN"] or self.type == self.vehicleTypes["BIKE"]:
            self.priority = 1
        else:
            self.priority = 2

    def setDepTime(self, depTime):
        self.depTime = depTime

    def nextStation(self):
        self.currentStation = heapq.heappop(self.upcomingStations)
        return self.currentStation

    def noStationsLeft(self):
        return len(self.upcomingStations) == 0

    def __lt__(self, other):
        if self.priority < other.priority:
            return True
        return self.arrTime <= other.arrTime
