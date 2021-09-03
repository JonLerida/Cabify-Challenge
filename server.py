import socket
import threading
from string import Template
from request import Request
import json
import datetime
import exceptions
import re

from car import Car
from group import Group
from journey import Journey
# TODO move this to a new method | class


class Server(object):
    def __init__(self):
        # TODO create here variables needed (such as lists)
        self.journey_counter = 1

        self._reset_cars()  # Creates self.available_cars = []
        self._reset_jorneys()  # Creates self.journeys = []

        self.used_cars = []
        self.pending_groups = []
        self.groups = []
        self.served_groups = []

    def _parse_request_arguments(self, request):
        """
        Reparse the request arguments to fill the formulary requirements

        :param request: Request
        :return: int
        :raises Exception
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

    def connection_handler(self):
        """
        Creates the socket and listens for new connections.
        New connections are piped to the authentication method
        :return:
        """
        server_ip = ""
        server_port = 60000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((server_ip, server_port))
        except socket.error as e:
            print('[server exception] ', e)

        print("[LOG] Server running in port %d" % server_port)

        # Backlog argument limites the number of queued requests
        s.listen()
        while True:
            conn, addr = s.accept()
            # print("\n\n[CONNECT] New connection")
            self.request_handler(conn, addr)
            conn.close()

    def request_handler(self, conn, addr):
        """
        Handless HTTP requests, piping them to concrete method handlers

        :param conn: socket
        :param addr: tuple (ip, port)
        :raises: generic exception
        """
        try:
            # Parses the HTTP request
            data = conn.recv(1024).decode('utf8', 'strict')
            if not data:
                print("Empty data received")
                return
            try:
                request = Request(data)
            except exceptions.IncorrectForm as e:
                self.send_error_response(conn, code=400, msg='Bad Request')
                print("[LOG] IncorrectForm")
                return

            print('[REQUEST] %s from %s' % (request.first_line, addr))

            if request.method == 'GET':
                self.do_GET(conn, request)
            elif request.method == 'PUT':
                # todo put
                self.do_PUT(conn, request)
            elif request.method == 'POST':
                # todo post
                self.do_POST(conn, request)
            else:
                # todo either raise and exception or send an error response
                self.do_DEFAULT(conn, request)
        except Exception as e:
            print("[server exception]", type(e).__name__, e)
            # todo do we wanna actually close the socket?
            conn.close()

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

    def _fill_response(self, http_body: bool, http_dict: dict, body_dict: dict = None):
        """
        Fill the HTTP response using some dictionaries.

        Uses the 'http_response_template.txt' file

        :param http_body: bool
        :param http_dict: dict
        :param body_dict: dict
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

        with open('http_response_template.txt.', 'r') as f:
            http_response = Template(f.read())

        if http_body:
            if d['content_type_header'] == 'text/html':
                with open('response_template.html', 'r') as f:
                    html_string = Template(f.read())

                d['http_body'] = html_string.safe_substitute({**d, **body_dict})
            elif d['content_type_header'] == 'application/json':
                d['http_body'] = body_dict['json']
        else:
            # No body
            d['http_body'] = ''

        d['content_length_header'] = len(d['http_body'].encode())

        response = http_response.safe_substitute(d)
        return response

    def do_GET_status(self, conn, request):
        """
        Handless the GET /status requests

        Responses 200 OK when ready to accept new requests

        :param conn:
        :param request:
        """

        d = {
            'code': 200,
            'response': 'Ok',
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
        }

        response = self._fill_response(http_body=False, http_dict=d)
        conn.sendall(response.encode())

    def do_GET_invalid(self, conn, request):
        """

        :param conn:
        :param request:
        :return:
        """

        self.send_error_response(conn, code=404, msg='Not Found')

    def do_GET(self, conn, request):
        """
        bnla bla

        :param conn:
        :param request:
        :return:
        """
        # todo do get
        if request.resource == '/status':
            self.do_GET_status(conn, request)
        else:
            self.do_GET_invalid(conn, request)

    def do_POST(self, conn, request):
        """
        hace...

        :param conn: socket
        :param request: Request
        :return: None
        """
        if request.resource == '/journey':
            self.do_POST_journey(conn, request)
        elif request.resource == '/dropoff':
            self.do_POST_dropoff(conn, request)
        elif request.resource == '/locate':
            self.do_POST_locate(conn, request)
        else:
            self.do_POST_invalid(conn, request)

    def do_POST_journey(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """

        if request.get_header_value('Content-Type') != 'application/json':
            self.send_error_response(conn, code=400, msg='Bad Request')
            print("[LOG] invalid Content-Type")
            return

        if not request.body:
            self.send_error_response(conn, code=400, msg='Bad Request')
            print("[LOG] empty body")
            return
        
        try:
            group = json.loads(request.body)
            if self.get_group(group['id']):
                print("[LOG] group already exists, ignoring...")
            else:
                self.pending_groups.append(Group(ID=group['id'], people=group['people']))
                print("[LOG] successfully created the group")
            d = {
                'code': 202,
                'response': 'Accepted',
                'connection_header': 'Closed',
            }
            response = self._fill_response(http_body=False, http_dict=d)
            conn.sendall(response.encode())
            self.check_queues()

        except Exception as e:
            print('[server exception]', type(e).__name__, e)
            self.send_error_response(conn, code=400, msg='Bad Request')

    def dropoff(self, group):
        """

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
            # TODO I'll assume the group wants to be deleted from the waiting queue
            self.pending_groups.remove(group)

    def do_POST_dropoff(self, conn, request):
        """
        "
        hace

        :param conn:
        :param request:
        :return:
        """
        try:
            group_ID = self._parse_request_arguments(request)
            group = self.get_group(group_ID)
            if group:
                print("EXISTS")
                self.dropoff(group)

                # Check if new groups can be served now
                self.check_queues()

                # Response
                d = {
                    'code': 204,
                    'response': 'No content',
                    'connection_header': 'Closed',
                    'content_type_header': 'text/html',
                }

                response = self._fill_response(http_body=False, http_dict=d)
                conn.sendall(response.encode())
            else:
                self.send_error_response(conn, code=404, msg='Not Found')

        except (KeyError, ValueError, exceptions.IncorrectForm):
            self.send_error_response(conn, code=400, msg='Bad Request')

    def get_group(self, ID):
        """
        Returns the group object given the ID. Searchs in both pending and journeys queues

        :param ID: int
        :return: Group
        """
        group = next((g for g in self.pending_groups if g.ID == ID), None)

        if group is None:
            group = next((j.group for j in self.journeys if j.group.ID == ID), None)
            
        return group

    def get_journey(self, group):
        return next((j for j in self.journeys if j.group == group), None)


    def send_2XX(self, conn, code, msg, payload):
        d = {
            'code': code,
            'response': msg,
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
        }

        response = self._fill_response(http_body=False, http_dict=d)
        conn.sendall(response.encode())
    def send_error_response(self, conn, code, msg):
        d = {
            'code': code,
            'response': msg,
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
        }

        response = self._fill_response(http_body=False, http_dict=d)
        conn.sendall(response.encode())

        print("[RESPONSE] %s %s" % (code, msg))

    def do_POST_locate(self, conn, request):
        """
        Handles the POST /locate request

        200 Ok  and car as payload is group is travelling

        204 No Content if group is waiting

        404 Not Found if group doesn't exist

        400 Bad Request if other error

        :param conn: socket
        :param request: Request
        """
        try:
            group_ID = int(request.get_argument_value('ID'))
            group = self.get_group(group_ID)
            if group:
                journey = self.get_journey(group)
                if journey:
                    # Response
                    d = {
                        'code': 200,
                        'response': 'Ok',
                        'connection_header': 'Closed',
                        'content_type_header': 'application/json',
                    }

                    body_dict = {
                        'json': journey.car.as_json()
                    }

                    response = self._fill_response(http_body=True, http_dict=d, body_dict=body_dict)
                    conn.sendall(response.encode())
                else:
                    # Response
                    d = {
                        'code': 204,
                        'response': 'No Content',
                        'connection_header': 'Closed',
                        'content_type_header': 'text/html',
                    }

                    response = self._fill_response(http_body=False, http_dict=d)
                    conn.sendall(response.encode())
            else:
                self.send_error_response(conn, code=404, msg='Not Found')

        except (KeyError, ValueError):
            self.send_error_response(conn, code=400, msg='Bad Request')

    def do_POST_invalid(self, conn, request):
        """
        ghace

        :param conn: socket
        :param request: Request
        :return:
        """
        pass

    def do_PUT(self, conn, request):
        """
        First handler for PUT requests

        :param conn: socket
        :param request: Request
        """
        if request.resource == '/cars':
            self.do_PUT_cars(conn, request)
        else:
            self.do_PUT_invalid(conn, request)

    def do_PUT_invalid(self, conn, request):
        """
        Handles all the invalid PUT requests.json

        Respond a 404 Not Found

        :param conn:
        :param request:
        """
        d = {
            'code': 404,
            'response': 'Not Found',
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
        }

        response = self._fill_response(http_body=False, http_dict=d)
        conn.sendall(response.encode())
        print("[LOG] invalid resource")

    def do_PUT_cars(self, conn, request):
        """
        JSON should come in the body of the request

        :param conn:
        :param request:
        :raises Exception
        :return:
        """

        if request.get_header_value('Content-Type') != 'application/json':  # 404
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(http_body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] invalid Content-Type")
            return

        if not request.body:  # 404
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(http_body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] empty body")
            return

        try:
            cars_json = json.loads(request.body)
            self._reset_cars()  # Delete previous existing cars
            # todo should i delete the whole file if there's a single error?
            for car in cars_json:
                car_object = Car(ID=car['id'], seats=car['seats'])
                self.available_cars.append(car_object)

            self.check_queues()

            d = {
                'code': 200,
                'response': 'Ok',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(http_body=False, http_dict=d)
            conn.sendall(response.encode())
            # print("[LOG] PUT cars successfully created CARS")
        except Exception as e:
            print('[server exception]', type(e).__name__, e)
            self.send_error_response(conn, code=400, msg='Bad Request')

    def do_DEFAULT(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """
        d = {
            'code': 400,
            'response': 'Bad Request',
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
        }

        response = self._fill_response(http_body=False, http_dict=d)
        conn.sendall(response.encode())

    def _reset_cars(self):
        """
        Resets the cars list.

        This method should be called ONLY at the start of the server
        and when receiving a successful PUT /cars request

        """
        self.available_cars = []

    def _reset_jorneys(self):
        """
        Resets the journeys list.

        This method should be called ONLY at the start of the server
        and when receiving a successful PUT /cars request

        """
        self.journeys = []

    def create_new_journey(self, group, car):
        """

        :param group: Group
        :param car: Car
        :return:
        """
        # print('[JOURNEY CREATED]', group, car)
        self.journeys.append(Journey(group=group, car=car, ID=self.journey_counter))
        self.journey_counter += 1

    def check_queues(self):
        """

        :return:
        """

        for group in self.pending_groups:
            # Available cars with enough empty seats
            valid_cars = [c for c in self.available_cars if c.seats >= group.people]
            if valid_cars:
                # In order to optimize the space...
                sorted_cars_by_seat = sorted(valid_cars, key=lambda x: x.seats, reverse=False)
                chosen_car = sorted_cars_by_seat[0]
                chosen_car.travelling = True
                group.travelling = True
                self.available_cars.remove(chosen_car)
                self.used_cars.append(chosen_car)
                self.pending_groups.remove(group)
                self.create_new_journey(group, chosen_car)

        self.print_stats()

    def print_stats(self):
        print("stats:")
        print("\tPending groups: %d" % len(self.pending_groups))
        print("\tAvailable cars: %d"% len(self.available_cars))
        print("\tUsed cars: %d"% len(self.used_cars))
        print("\tServed groups: %d"% len(self.served_groups))
        print("\tActive journeys: %d" % len(self.journeys))

if __name__ == '__main__':

    server = Server()
    # Launch a thread binded to a socket and listen all requests
    t = threading.Thread(target=server.connection_handler)
    t.start()
