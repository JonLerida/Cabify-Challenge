"""
Stores the group and car ID of every journey
"""


class Journey(object):
    def __init__(self, group, car, id):

        self.group = group
        self.car = car
        self.id = id

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
        return self.id
