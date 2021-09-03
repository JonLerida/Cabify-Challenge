from io import StringIO
import email
import re
import exceptions
class Request(object):
    def __init__(self, raw_request):
        self.raw_request = raw_request
        self.headers = None
        self.method = None
        self.full_path = None
        self.resource = None
        self.protocol = None
        self.headers = None
        self.first_line = None
        self.arguments = None
        self.body = None

        self.parse_request(self.raw_request)
        if self.get_header_value('Content-Type') == 'application/x-www-form-urlencoded':
            self._parse_form_body(self.body)


    def _parse_form_body(self, body):
        """

        :param body: str
        :return:
        :raises Exception
        """
        key, value = body.split('=')
        if key:
            self.arguments[key] = value.strip()

    def _parse_path(self, path):
        if '?' in path:
            self.resource, arguments = path.split('?', 1)
            arguments = arguments.replace('=', ':')
            aux = email.message_from_file(StringIO(arguments))
            self.arguments = dict(aux.items())
        else:
            self.resource = path.strip()
            self.arguments = {}


    def _parse_first_line(self, first_line):
        parts = first_line.split(' ')
        self.path = parts[1]
        self._parse_path(self.path)
        self.method = parts[0]
        self.protocol = parts[2]

    def _parse_headers(self, headers):
        pass

    def _parse_headers_and_body(self, h_a_b):
        try:
            headers, body = h_a_b.split('\r\n\r\n', 1)
        except ValueError: # no body
            headers = h_a_b
            body = ''

        return headers, body

    def parse_request(self, raw_request):
        self.first_line, headers_and_body = raw_request.split('\r\n', 1)

        self._parse_first_line(self.first_line)
        headers, self.body = self._parse_headers_and_body(headers_and_body)

        # construct a message from the request string
        message = email.message_from_file(StringIO(headers))

        # construct a dictionary containing the headers
        self.headers = dict(message.items())

    def __str__(self):
        return 'request object'

    def __repr__(self):
        return str(self)

    def get_header_value(self, header_name):
        """
        returns the value of the header_name. Returns none if no header with that name
        :param header_name: str
        :return: str
        """
        return self.headers.get(header_name, '')

    def get_argument_value(self, argument_name):
        """
        returns the value of the argument asked
        :param argument_name: str
        :return: str
        """
        return self.arguments[argument_name]