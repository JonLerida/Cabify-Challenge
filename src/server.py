"""
Main thread. Server side of the application.
Open a socket in 0.0.0.0 addr and wait for connections
in an infinite loop.

Pipe new requests to the handler, which calls the Request class to parse http messages

Response client side with HTTP messages, based on the request

author: Jon Lérida García (jon.lerida.garcia@gmail.com)
"""

import socket
import threading
from string import Template
import json
import datetime
import time

from request import Request
from car import Car
from group import Group
from journey import Journey
import exceptions


class Server(object):
    def __init__(self, verbose: bool = False):
        self.journey_counter = 1

        self._reset_cars()  # Creates self.available_cars = self.used_cars = []
        self._reset_jorneys()  # Creates self.journeys = []

        self.pending_groups = []
        self.served_groups = []
        self.verbose = verbose

    """
    Static methods
    """

    # noinspection PyBroadException
    @staticmethod
    def recv_timeout(conn: socket.socket, timeout: float = 1):
        """
        This methods receives the socket incoming data

        Read data until a timeout is over or until the socket has new data

        This method is needed because the http requests size is not stated (large json in the PUT /cars method)

        :param conn:
        :type conn: socket.socket
        :param timeout:
        :type timeout: float
        :return:
        """
        conn.setblocking(False)
        total_data = []
        data = ''
        begin = time.time()
        while True:
            if total_data and time.time() - begin >= timeout:
                break
            elif time.time() - begin >= timeout * 2:
                break
            try:
                data = conn.recv(2048)
                if data:
                    total_data.append(data)
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        return b''.join(total_data)

    @staticmethod
    def _parse_request_arguments(request: Request):
        """
        Reparse the request arguments and assert the formulary requirements

        If everything is ok, return the formulary ID (id=x)

        Raise exceptions.IncorrectForm in other case

        :param request:
        :type request: Request
        :return: int
        :raises IncorrectForm
        :returns the form ID
        """

        if len(request.arguments) > 1:
            raise exceptions.IncorrectForm

        if 'ID' not in request.arguments.keys():
            raise exceptions.IncorrectForm
        try:
            id = int(request.arguments['ID'])
            return id
        except ValueError:
            raise exceptions.IncorrectForm

    @staticmethod
    def _fill_date_header():
        """
        Get the current date, time and timezone in a pretty format

        :return: str
        """

        days_abbr = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
        weekday = days_abbr[datetime.datetime.today().weekday()]
        now = datetime.datetime.now()
        date_info = now.strftime("%d %b %Y %H:%M:%S")
        date_header = '%s, %s GMT+2' % (
            weekday, date_info
        )
        return date_header

    """
    Auxiliar methods
    """

    def _fill_response(
            self,
            http_body: bool,
            http_dict: dict,
            body_dict: dict = None
    ):
        """
        Fill the HTTP response using some dictionaries.

        Uses the 'http_response_template.txt' file in the static folder

        :param http_body: does the response include body?
        :param http_dict: dictionary to fill the HTTP template
        :param body_dict:
        :return: str
        """
        valid_http_keys = [
            'code',
            'response',
            'date_header',
            'content_length_header',
            'connection_header',
            'content_type_header',
        ]

        d = {v: http_dict.get(v, '') for v in valid_http_keys}
        d['date_header'] = self._fill_date_header()
        f = open("./static/http_response_template.txt", "r")
        http_response = Template(f.read())
        f.close()

        if http_body:
            if d['content_type_header'] == 'text/html':
                f = open('./static/response_template.html', 'r')
                html_string = Template(f.read())
                f.close()
                d['http_body'] = html_string.safe_substitute({**d, **body_dict})

            elif d['content_type_header'] == 'application/json':
                d['http_body'] = body_dict['content']
        else:
            d['http_body'] = ''

        d['content_length_header'] = len(d['http_body'].encode())

        if d['content_type_header']:
            d['content_type_header'] = 'Content-Type: %s' % d['content_type_header']

        response = http_response.safe_substitute(d)
        return response.strip()

    def _reset_cars(self):
        """
        Resets the cars list.

        This method should be called ONLY at the start of the server
        and when receiving a successful PUT /cars request

        """
        self.available_cars = []
        self.used_cars = []

    def _reset_jorneys(self):
        """
        Resets the journeys list.

        This method should be called ONLY at the start of the server
        and when receiving a successful PUT /cars request

        """
        self.journeys = []

    """
    Class methods
    """

    def connection_handler(self):
        """
        Creates the socket and listens for new connections

        New connections are piped to the authentication method

        :return:
        """
        server_ip = "0.0.0.0"
        server_port = 9091  # stated in challenge description

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((server_ip, server_port))
        except socket.error as e:
            if self.verbose:
                print("[server exception]", type(e).__name__, e)

        print("[LOG] Server running in (%s, %s)" % (server_ip, server_port))

        # Backlog argument limites the number of queued requests
        s.listen()
        while True:
            conn, addr = s.accept()
            self.request_handler(conn, addr)
            # conn.shutdown(socket.SHUT_RDWR)
            conn.close()

    def request_handler(self, conn, addr):
        """
        Handless HTTP requests, piping them to concrete method handlers

        :param conn: socket object
        :type conn: socket.socket
        :param addr: str
        :type addr:str
        :raises: generic exception
        """
        try:
            data = self.recv_timeout(conn, timeout=1).decode()
            if not data:
                return
            request = Request(data)

            socket_info = (conn, addr)
            if request.method == 'GET':
                self.do_GET(socket_info, request)
            elif request.method == 'PUT':
                self.do_PUT(socket_info, request)
            elif request.method == 'POST':
                self.do_POST(socket_info, request)
            else:
                self.do_DEFAULT(socket_info, request)
        except Exception as e:
            if self.verbose:
                print("[server exception]", type(e).__name__, e)

    """
    Do Get
    """
    def do_GET(self, socket_info, request):
        """
        bnla bla

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        :return:
        """
        if request.resource == '/status':
            self.do_GET_status(socket_info, request)
        else:
            self.do_GET_invalid_resource(socket_info, request)

    def do_GET_status(self, socket_info, request):
        """
        Handless the GET /status requests

        Responses 200 OK when ready to accept new requests

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        """

        self.send_2xx_response(socket_info, request, code=200, msg='OK')

    def do_GET_invalid_resource(self, socket_info, request):
        """

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        :return:
        """

        self.send_4xx_response(socket_info, request, code=404, msg='Not Found')

    """
    Do Post
    """

    def do_POST(self, socket_info, request):
        """
        hace...

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        :return: None
        """
        if request.resource == '/journey':
            self.do_POST_journey(socket_info, request)
        elif request.resource == '/dropoff':
            self.do_POST_dropoff(socket_info, request)
        elif request.resource == '/locate':
            self.do_POST_locate(socket_info, request)
        else:
            self.do_POST_invalid_resource(socket_info, request)

    def do_POST_journey(self, socket_info, request):
        """
        hace

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        :return:
        """

        if request.get_header_value('Content-Type') != 'application/json':
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')
            if self.verbose:
                print("[LOG] invalid Content-Type")
            return

        if not request.body:
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')
            if self.verbose:
                print("[LOG] empty body")
            return

        try:
            group = json.loads(request.body)
            if self.get_group(group['id']) and self.verbose:
                print("[LOG] group already exists, ignoring...")
            else:
                self.pending_groups.append(Group(ID=group['id'], people=group['people']))

            self.send_2xx_response(socket_info, request, code=202, msg='Accepted')
            self.check_queues()

        except Exception as e:
            if self.verbose:
                print('[server exception]', type(e).__name__, e)
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')

    def do_POST_invalid_resource(
            self,
            socket_info: (socket.socket, str),
            request: Request
    ):
        """
        Handles all the POST invaslid resource requests

        :param socket_info:
        :param request:
        """
        self.send_4xx_response(socket_info, request, code=404, msg='Not Found')

    def do_POST_locate(self, socket_info, request):
        """
        Handles the POST /locate request

        200 Ok  and car as payload is group is travelling

        204 No Content if group is waiting

        404 Not Found if group doesn't exist

        400 Bad Request if other error

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        """
        try:
            group_ID = int(request.get_argument_value('ID'))
            group = self.get_group(group_ID)
            if group:
                journey = self.get_journey(group)
                if journey:
                    body_dict = {
                        'Content-Type': 'application/json',
                        'content': journey.car.as_json()
                    }
                    self.send_2xx_response(socket_info, request, code=200, msg='OK', body_dict=body_dict)
                else:
                    # Response
                    self.send_2xx_response(socket_info, request, code=204, msg='No Content')
            else:
                self.send_4xx_response(socket_info, request, code=404, msg='Not Found')

        except (KeyError, ValueError):
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')

    def do_POST_dropoff(
            self,
            socket_info: (socket.socket, str),
            request: Request
    ):
        """
        hace

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        :return:
        """
        try:
            group_ID = self._parse_request_arguments(request)
            group = self.get_group(group_ID)
            if group:
                self.dropoff(group)

                # Check if new groups can be served now
                self.check_queues()

                # Response
                self.send_2xx_response(socket_info, request, code=204, msg='No Content')
            else:
                self.send_4xx_response(socket_info, request, code=404, msg='Not Found')

        except (KeyError, ValueError, exceptions.IncorrectForm):
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')

    def dropoff(self, group: Group):
        """
        Hace

        :param group: Group
        :return:
        """
        journey = self.get_journey(group)
        if journey:
            # End the journey
            self.journeys.remove(journey)

            # Mark the group as 'served'
            self.served_groups.append(group)
            group.travelling = False

            # Free the used car
            self.available_cars.append(journey.car)
            self.used_cars.remove(journey.car)
        else:
            # TODO I assumed the group wants to be deleted from the pending queue (such a cancel travel request)
            self.pending_groups.remove(group)
        if self.verbose:
            self.print_stats()

    """
    Do Put
    """

    def do_PUT(
            self,
            socket_info: (socket.socket, str),
            request: Request
    ):
        """
        First handler for PUT requests

        :param socket_info
        :param request
        """
        if request.resource == '/cars':
            self.do_PUT_cars(socket_info, request)
        else:
            self.do_PUT_invalid(socket_info, request)

    def do_PUT_cars(
            self,
            socket_info: (socket.socket, str),
            request: Request
    ):
        """
        JSON should come in the body of the request

        :param socket_info:
        :type socket_info:(socket.socket, str)
        :param request:
        :raises Exception
        :return:
        """

        if request.get_header_value('Content-Type') != 'application/json':
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')
            if self.verbose:
                print("[LOG] invalid Content-Type")
            return

        if not request.body:
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')
            if self.verbose:
                print("[LOG] empty body")
            return

        try:
            cars_json = json.loads(request.body)
            self._reset_cars()  # Delete previous existing cars
            self._reset_jorneys()  # Delete previous existing journeys
            for car in cars_json:
                car_object = Car(ID=car['id'], seats=car['seats'])
                self.available_cars.append(car_object)

            self.check_queues()
            self.send_2xx_response(socket_info, request, code=200, msg='OK')
        except Exception as e:
            if self.verbose:
                print('[server exception]', type(e).__name__, e)
            self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')

    def do_PUT_invalid(
            self,
            socket_info: (socket.socket, str),
            request: Request
    ):
        """
        Handles all the invalid PUT requests.json

        Respond a 404 Not Found

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        """

        self.send_4xx_response(socket_info, request, code=404, msg='Not Found')
        if self.verbose:
            print("[LOG] invalid resource")

    """
    Do default
    """

    def do_DEFAULT(
            self,
            socket_info: (socket.socket, str),
            request: Request
    ):
        """
        hace

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :return:
        """
        self.send_4xx_response(socket_info, request, code=400, msg='Bad Request')

    def get_group(self, ID):
        """
        Returns the group object given the ID. Searchs in both pending and journeys queues

        :param ID:
        :type ID: int
        :return: Group
        """
        group = next((g for g in self.pending_groups if g.ID == ID), None)

        if group is None:
            group = next((j.group for j in self.journeys if j.group.ID == ID), None)

        return group

    def get_journey(self, group: Group):
        """
        Search a journey by group

        :param group
        :type group:Group
        :return: Journey
        :returns: Journey
        """
        return next((j for j in self.journeys if j.group == group), None)

    """
    Responses
    """

    def send_4xx_response(
            self,
            socket_info: (socket.socket, str),
            request: Request,
            code: int,
            msg: str,
            body_dict: dict = None
    ):
        """
        Sends 4xx HTTP responses


        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :type request: Request
        :param code:
        :type code: int
        :param msg:
        :type msg: str
        :param body_dict:
        :type body_dict: dict
        """
        conn, addr = socket_info
        d = {
            'code': code,
            'response': msg,
            'connection_header': 'Closed',
        }
        http_body = False
        if body_dict:
            d['content_type_header'] = body_dict['Content-Type']
            http_body = True
        response = self._fill_response(http_body=http_body, http_dict=d, body_dict=body_dict)
        conn.sendall(response.encode())
        print('%s - - [%s] "%s" %s -' % (addr[0], self._fill_date_header(), request.first_line, code))

    def send_2xx_response(
            self,
            socket_info: (socket.socket, str),
            request: Request,
            code: int,
            msg: str,
            body_dict: dict = None
    ):
        """
        Sends 2xx HTTP responses

        :param socket_info:
        :type socket_info: (socket.socket, str)
        :param request:
        :param code:
        :param msg: str
        :param body_dict: dict
        """
        conn, addr = socket_info
        d = {
            'code': code,
            'response': msg,
            'connection_header': 'Closed',
        }
        http_body = False
        if body_dict:
            d['content_type_header'] = body_dict['Content-Type']
            http_body = True
        response = self._fill_response(http_body=http_body, http_dict=d, body_dict=body_dict)
        conn.sendall(response.encode())
        print('%s - - [%s] "%s" %s -' % (addr[0], self._fill_date_header(), request.first_line, code))

    def create_new_journey(self, group: Group, car: Car):
        """
        Creates a new Journey(group, car) object

        Marks both car and group travelling attribute as True

        :param group:
        :param car:
        :return:
        """
        car.travelling = True
        group.travelling = True
        self.journeys.append(Journey(group=group, car=car, ID=self.journey_counter))
        self.journey_counter += 1

    def check_queues(self):
        """
        Checks all the pending groups and tries to assign a new journey.

        Search for all the available cars and choose the one with the least empty seats (seats >= people)

        :return: None
        """
        # Store the assigned groups in an auxiliar variable
        assigned_groups = []
        for group in self.pending_groups:
            # Available cars with enough empty seats
            valid_cars = [c for c in self.available_cars if c.seats >= group.people]
            if valid_cars:
                # In order to optimize the space...
                sorted_cars_by_seat = sorted(valid_cars, key=lambda x: x.seats, reverse=False)
                chosen_car = sorted_cars_by_seat[0]

                # Create the new Journey
                self.create_new_journey(group, chosen_car)

                # Update the available | used cars queue
                self.available_cars.remove(chosen_car)
                self.used_cars.append(chosen_car)

                # Update the assigned groups list
                assigned_groups.append(group)

        # Once all the groups have been checked, proceed to update the pending group list
        [self.pending_groups.remove(x) for x in assigned_groups]

        if self.verbose:
            self.print_stats()

    def print_stats(self):
        print("\t---Active journeys: %d ---" % len(self.journeys))
        print("\t---Total cars: %d---" % (len(self.used_cars) + len(self.available_cars)))
        print("\t---Available cars: %d---" % len(self.available_cars))
        print("\t---Pending groups: %d---" % len(self.pending_groups))
        print("\t---Served groups: %d---" % len(self.served_groups))


if __name__ == '__main__':
    server = Server(verbose=False)
    # Launch a new thread to handle incoming requests
    t = threading.Thread(target=server.connection_handler)
    t.start()
