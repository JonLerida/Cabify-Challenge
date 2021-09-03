"""

"""


class Car(object):
    def __init__(self, id, seats):
        self.id = int(id)
        self.seats = int(seats)

        self.travelling = False # todo may not be needed


    def get_id(self):
        return self.id

    def get_seats(self):
        return self.seats

    def __str__(self):
        return f'[Car_object] with id {self.id}, seats {self.seats}'

    def __repr__(self):
        return str(self)
