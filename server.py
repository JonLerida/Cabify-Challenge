import socket
import threading
from io import StringIO
import email

from request import Request

# class HTTPRequest(BaseHTTPRequestHandler):
#     def __init__(self, request):
#         self.rfile = BytesIO(request)
#         self.raw_requestline = self.rfile.readline()
#         self.error_code = self.error_message = None
#         self.parse_request()
#
#     def send_error(self, code, message):
#         self.error_code = code
#         self.error_message = message


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
        try:
            request = Request(conn.recv(2048).decode())
            # lines = self.parse_request(request)
            # construct a message from the request string
            request = email.message_from_file(StringIO(lines))
            print(request)
        except Exception as e:
            print("[EXCEPTION]", e)
            conn.close()


if __name__ == '__main__':
    server = Server()
    # Launch a thread binded to a socket and listen all requests
    t = threading.Thread(target=server.connection_handler)
    t.start()
