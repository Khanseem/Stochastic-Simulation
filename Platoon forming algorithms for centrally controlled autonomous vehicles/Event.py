class Event:

    ARRIVAL = 0
    DEPARTURE = 1

    def __init__(self, typ, car):
        self.type = typ
        self.car = car
        if self.type == self.ARRIVAL:
            self.time = self.car.arrTime
        elif self.type == self.DEPARTURE:
            self.time = self.car.depTime

    def __lt__(self, other):
        return self.time < other.time