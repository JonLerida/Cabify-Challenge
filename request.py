from string import Template


class Request(object):
    def __init__(self, raw_request):
        self.raw_request = raw_request
        self.parse_request(self.raw_request)

        self.headers = None
        # todo fix this
        self.method = 'GET'

    def parse_request(self, raw_request):
        raw_request.split('\r\n')
        pass

    def __str__(self):
        return ''

    def __repr__(self):
        return str(self)
