class Event:

    ARRIVAL = 0
    STATIONMOVE = 1
    DEPARTURE = 2
    IMPATIENT = 3

    def __init__(self, typ, vehicle, time):
        self.type = typ
        self.vehicle = vehicle
        self.time = time

    def __lt__(self, other): # due to events possibly taking place at the same time, also sort them by type
        if self.time == other.time:
            if self.type == self.IMPATIENT or other.type == self.IMPATIENT:
                if self.type == self.IMPATIENT and other.type == self.IMPATIENT:
                    return self.vehicle.arrTime < other.vehicle.arrTime
                return self.type == self.IMPATIENT

            if self.type == self.DEPARTURE or other.type == self.DEPARTURE:
                if self.type == self.DEPARTURE and other.type == self.DEPARTURE:
                    return self.vehicle.arrTime < other.vehicle.arrTime
                return self.type == self.DEPARTURE

            if self.type == self.ARRIVAL or other.type == self.ARRIVAL:
                return self.type == self.ARRIVAL

            if self.vehicle.currentStation == 0 or other.vehicle.currentStation == 0:
                if self.vehicle.currentStation == 0 and other.vehicle.currentStation == 0:
                    if self.vehicle.priority == other.vehicle.priority:
                        return self.vehicle.arrTime < other.vehicle.arrTime
                    return self.vehicle.priority < other.vehicle.priority
                return other.vehicle.currentStation == 0

            if self.vehicle.currentStation.order == other.vehicle.currentStation.order:
                return self.vehicle.arrTime < other.vehicle.arrTime
            return self.vehicle.currentStation.order > other.vehicle.currentStation.order

        return self.time < other.time
