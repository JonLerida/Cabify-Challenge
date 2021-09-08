"""
Group class. Store the ID,# of people and a boolean variable (travelling or not)

author: Jon Lérida García (jon.lerida.garcia@gmail.com)
"""


class Group(object):
    def __init__(self, ID, people):
        self.ID = int(ID)
        self.people = int(people)
        self.travelling = False

    def get_ID(self):
        return self.ID

    def get_people(self):
        return self.people

    def __str__(self):
        return f'[Group object] with id {self.ID}, people {self.people}'

    def __repr__(self):
        return str(self)
