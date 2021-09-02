class Request(object):
    def __init__(self, raw_request):
        self.raw_request = raw_request
        self.parse_request(self.raw_request)


    def parse_request(self, raw_request):
        print("Parsing request...")
        pass
