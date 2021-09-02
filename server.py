import socket
import threading
from io import StringIO
import email
from string import Template


from request import Request

with open('http_response_template.txt.', 'r') as f:
    generic_http_response = Template(f.read())


with open('response_template.html', 'r') as f:
    generic_html_response = Template(f.read())


# TODO move this to a new method | class



class Server(object):
    def __init__(self):
        # TODO create here variables needed (such as lists)
        self.journey_counter = 0

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
            print("[EXCEPTION]", e)
            # todo do we wanna actually close the socket?
            conn.close()

    def do_GET_status(self, conn, request):
        """

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

        generic_http_response_result = generic_http_response.substitute(d)
        generic_html_response_result = generic_html_response.substitute(d)
        generic_http_response_result += generic_html_response_result
        conn.sendall(generic_http_response_result.encode())
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
            # 'server_message': 'SERVER UP'
        }

        generic_http_response_result = generic_http_response.safe_substitute(d)
        generic_html_response_result = generic_html_response.safe_substitute(d)
        generic_http_response_result += generic_html_response_result
        conn.sendall(generic_http_response_result.encode())
        print("[LOG] GET invalid resource")

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
        pass

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
        hace

        :param conn:
        :param request:
        :return:
        """
        pass

    def do_POST_invalid(self, conn, request):
        """
        ghace

        :param conn:
        :param request:
        :return:
        """
        pass

    def do_PUT(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """
        if request.resource == '/cars':
            self.do_PUT_cars(conn, request)
        else:
            self.do_PUT_invalid(conn, request)

    def do_PUT_invalid(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """
        pass

    def do_PUT_cars(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """
        pass

    def do_DEFAULT(self, conn, request):
        """
        hace

        :param conn:
        :param request:
        :return:
        """
        pass


if __name__ == '__main__':

    server = Server()
    # Launch a thread binded to a socket and listen all requests
    t = threading.Thread(target=server.connection_handler)
    t.start()
