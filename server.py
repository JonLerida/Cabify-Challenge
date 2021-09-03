import socket
import threading
from string import Template
from request import Request
import json
import datetime

from car import Car
from group import Group
# TODO move this to a new method | class


class Server(object):
    def __init__(self):
        # TODO create here variables needed (such as lists)
        self.journey_counter = 0
        self._reset_cars()  # Creates self.cars = []
        self.available_cars = []
        self.used_cars = []
        self.groups = []

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
            print('[EXCEPTION] ', e)

        print("[LOG] Server running in port %d" % server_port)

        # Backlog argument limites the number of queued requests
        s.listen()
        while True:
            conn, addr = s.accept()
            print("[CONNECT] New connection")
            self.request_handler(conn, addr)
            conn.close()

    def request_handler(self, conn, addr):
        """

        :param conn:
        :param addr:
        :return: None
        :raises: generic exception
        """
        try:
            # Parses the HTTP request
            data = conn.recv(1024).decode('utf8', 'strict')
            if not data:
                print("Empty data received")
                return

            request = Request(data)
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
            print("[EXCEPTION]", type(e).__name__, e)
            # todo do we wanna actually close the socket?
            conn.close()

    @staticmethod
    def _fill_date_header():
        days_abbr = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
        weekday = datetime.datetime.today().weekday()
        now = datetime.datetime.now()
        date_info = now.strftime("%d %b %Y %H:%M:%S")
        date_header = '%s, %s GMT+2' % (
            weekday, date_info
        )

        return date_header

    def _fill_response(self, body:bool, http_dict, body_dict=None):
        """
        hace

        :param body: bool
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

        if body:
            with open('response_template.html', 'r') as f:
                html_string = Template(f.read())

            d['html_response'] = html_string.safe_substitute(body_dict)
        else:
            d['html_response'] = ''

        d['content_length_header'] = len(d['html_response'].encode())

        response = http_response.safe_substitute(d)

        return response

    def do_GET_status(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """

        d = {
            'code': 200,
            'response': 'Ok',
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
            'server_message': "SERVER'S UP"
        }

        response = self._fill_response(body=False, http_dict=d)
        conn.sendall(response.encode())
        print("[LOG] GET status resource")

    def do_GET_invalid(self, conn, request):
        """

        :param conn:
        :param request:
        :return:
        """

        d = {
            'code': 404,
            'response': 'Not Found',
            'connection_header': 'Closed',
            'content_type_header': 'text/html',
        }

        response = self._fill_response(body=False, http_dict=d)
        conn.sendall(response.encode())
        print("[LOG] GET status resource")

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
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] POST journey invalid Content-Type")
            return

        if not request.body:
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] POST journey empty body")
            return
        
        try:
            group = json.loads(request.body)
            self.groups.append(Group(id=group['id'], people=group['people']))
            d = {
                'code': 202,
                'response': 'Accepted',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }
            print("[LOG] POST journey successfully created the group")

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())

        except Exception as e:
            print('[EXCEPTION]', type(e).__name__, e)
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())


    def do_POST_dropoff(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """
        pass

    def do_POST_locate(self, conn, request):
        """
        Handles the POST /locate request

        200 Ok if...

        404 Not Found if

        400 Bad Request if...

        204 No Content if...

        :param conn: socket
        :param request: Request
        """
        pass

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

        response = self._fill_response(body=False, http_dict=d)
        conn.sendall(response.encode())
        print("[LOG] PUT invalid resource")

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

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] PUT cars invalid Content-Type")
            return

        if not request.body:  # 404
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] PUT cars empty body")
            return

        try:
            cars_json = json.loads(request.body)
            self._reset_cars()  # Delete previous existing cars
            # todo should i delete the whole file if there's a single error?
            for car in cars_json:
                car_object = Car(id=car['id'], seats=car['seats'])
                self.cars.append(car_object)

            d = {
                'code': 200,
                'response': 'Ok',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())
            print("[LOG] PUT cars successfully created CARS")

            print(self.cars)
        except Exception as e:
            print('[EXCEPTION]', type(e).__name__, e)
            d = {
                'code': 400,
                'response': 'Bad Request',
                'connection_header': 'Closed',
                'content_type_header': 'text/html',
            }

            response = self._fill_response(body=False, http_dict=d)
            conn.sendall(response.encode())

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

        response = self._fill_response(body=False, http_dict=d)
        conn.sendall(response.encode())

    def _reset_cars(self):
        """
        Resets the cars list.

        This method should be called ONLY at the start of the server
        and when receiving a successful PUT /cars request

        """
        self.cars = []
if __name__ == '__main__':

    server = Server()
    # Launch a thread binded to a socket and listen all requests
    t = threading.Thread(target=server.connection_handler)
    t.start()
