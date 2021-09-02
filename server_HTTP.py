"""
This version uses HTTP server and overrides baseHTTPRequestHandler
MAIN file
runs the threads, manages the requests and provides authentication
"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # todo rewrite this
        print(self.path)

        # self.send_response(200)
        # self.send_header('content-type', 'text/html')
        # self.end_headers()
        # self.wfile.write(self.path.encode())
        # self.wfile.write('this is a get'.encode())
        pass

    def do_POST(self):
        # todo rewrite this
        # self.send_response(200)
        # self.send_header('content-type', 'text/html')
        # self.end_headers()
        # self.wfile.write(self.path.encode())
        # self.wfile.write('this is a post'.encode())
        pass

    def do_PUT(self):
        # todo rewrite this
        pass


def run_HTTP_server():
    PORT = 60000
    server = HTTPServer(('', PORT), RequestHandler)
    print('server running on port %d' % PORT)
    server.serve_forever()


if __name__ == '__main__':
    run_HTTP_server()