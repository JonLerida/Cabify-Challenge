"""

"""

import json
class Car(object):
    def __init__(self, ID, seats):
        self.ID = int(ID)
        self.seats = int(seats)

        self.travelling = False # todo may not be needed

    def get_ID(self):
        return self.ID

    def get_seats(self):
        return self.seats

    def __str__(self):
        return f'[Car_object] with id {self.ID}, {self.seats} seats'

    def __repr__(self):
        return str(self)

    def as_json(self):
        """

        :return: str
        """
        d = {
            'id': self.get_ID(),
            'seats': self.get_seats()
        }
        return json.dumps(d, indent=4)
