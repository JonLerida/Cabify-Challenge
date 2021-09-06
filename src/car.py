"""
Car class

Store the ID, # of seats and a boolean variable (travelling)
author: Jon Lérida García (jon.lerida.garcia@gmail.com)
"""
import json


class Car(object):
    def __init__(self, ID, seats):
        self.ID = int(ID)
        self.seats = int(seats)
        self.travelling = False

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
        JSON representation of the instance

        :return: str
        """
        d = {
            'id': self.get_ID(),
            'seats': self.get_seats()
        }
        return json.dumps(d, indent=4)
