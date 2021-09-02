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
d = {
    'code': 200,
    'response': 'Ok',
    'connection_header': 'Closed',
    'content_type_header': 'text/html'
}


class Server(object):
    def __init__(self):
        pass

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
            print("[CONNECT] New connection!")
            self.authentication(conn, addr)

    def authentication(self, conn, addr):
        """

        :param conn:
        :param addr:
        :return: None
        :raises: generic exception
        """
        try:
            request = Request(conn.recv(2048).decode())
            print(request)

            if request.method == 'GET':
                # todo do get
                generic_http_response_result = generic_http_response.substitute(d)
                generic_html_response_result = generic_html_response.substitute(d)
                generic_http_response_result += generic_html_response_result
                conn.sendall(generic_http_response_result.encode())
            elif request.method == 'PUT':
                # todo put
                pass
            elif request.method == 'POST':
                # todo post
                pass
            else:
                # todo either raise and exception or send an error response
                pass
        except Exception as e:
            print("[EXCEPTION]", e)
            conn.close()


if __name__ == '__main__':
    server = Server()
    # Launch a thread binded to a socket and listen all requests
    t = threading.Thread(target=server.connection_handler)
    t.start()
