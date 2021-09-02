"""

"""


class Car(object):
    def __init__(self, id, seats):
        self.id = id
        self.seats = seats
        self.travelling = None # todo may not be needed


    def get_id(self):
        return self.id

    def get_seats(self):
        return self.seats

    def __str__(self):
        return f'Car #{self.id} with {self.seats} total seats'

    def __repr__(self):
        return str(self)
