"""
Journey class
For every journey, store the group, car and ID

author: Jon Lérida García (jon.lerida.garcia@gmail.com)
"""


class Journey(object):
    def __init__(self, group, car, ID):
        self.group = group
        self.car = car
        self.ID = ID

    def get_group(self):
        return self.group

    def get_car(self):
        return self.car

    def get_id(self):
        return self.ID

    def __str__(self):
        return f'[Journey object] with id {self.ID}'

    def __repr__(self):
        return str(self)
