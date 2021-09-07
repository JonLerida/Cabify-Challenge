"""
HTTP request parser

author: Jon Lérida García (jon.lerida.garcia@gmail.com)
"""
from io import StringIO
import email


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
        self.body = ''

        self.parse_request(self.raw_request)
        # We don't need more cases for this challenge
        if self.get_header_value('Content-Type') == 'application/x-www-form-urlencoded':
            self._parse_form_body(self.body)

    def _parse_form_body(self, body):
        """
        Parse the http body when content-type is a formulary
        Store key-value pairs in the self.arguments dictionary

        :param body:
        :type body:str
        :return:
        """
        key, value = body.split('=')
        if key:
            self.arguments[key] = value.strip()

    def _parse_path(self, path):
        """
        Parses the request path searching for url key-value pairs

        :param path:
        :type path: str
        """
        if '?' in path:
            self.resource, arguments = path.split('?', 1)
            arguments = arguments.replace('=', ':')
            aux = email.message_from_file(StringIO(arguments))
            self.arguments = dict(aux.items())
        else:
            self.resource = path.strip()
            self.arguments = {}

    def _parse_first_line(self, first_line):
        """
        Parses HTTP request first line

        Search for the http method, protocol (and version) and full path

        :param first_line:
        :type first_line: str
        """
        parts = first_line.split(' ')
        self.path = parts[1]
        self._parse_path(self.path)
        self.method = parts[0]
        self.protocol = parts[2]

    @staticmethod
    def _parse_headers_and_body(h_a_b):
        """
        Parse HTTP request (except first line)

        Look for HTTP headers and the request body

        :param h_a_b: headers and body
        :type h_a_b: str
        :return:
        """
        try:
            headers, body = h_a_b.split('\r\n\r\n', 1)
        except ValueError:  # no body
            headers = h_a_b
            body = ''

        return headers, body

    def parse_request(self, raw_request):
        """
        Parse the HTTP request

        Look for HTTP separators (\r\n) and try to get first_line, headers and body

        :param raw_request: HTTP incoming request
        :type raw_request: str
        """

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
        Returns the value of the header_name string.

        Returns empty string ('') if there's no header with such name in the http request

        :param header_name:
        :type header_name: str
        :return: str
        """
        return self.headers.get(header_name, '')

    def get_argument_value(self, argument_name):
        """
        Returns the value of the argument string.

        Returns empty string ('') if there's no argume with such name in the http request

        :param argument_name:
        :type argument_name: str
        :return: str
        :raises: KeyError
        """
        return self.arguments[argument_name]
