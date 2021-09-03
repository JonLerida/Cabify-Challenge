"""
Stores the group and car ID of every journey
"""


class Journey(object):
    def __init__(self, group, car, ID):

        self.group = group
        self.car = car
        self.ID = ID

    def get_group(self):
        """

        :return:
        """
        return self.group

    def get_car(self):
        """

        :return:
        """
        return self.car

    def get_id(self):
        """

        :return:
        """
        return self.ID

    def __str__(self):
        return f'[Journey object] with id {self.ID}'

    def __repr__(self):
        return str(self)
