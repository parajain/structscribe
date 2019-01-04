import xmlrpclib

class ApproxNNClient:
    def __init__(self, port_n):
        addr = 'http://localhost:' + str(port_n)
        self.server = xmlrpclib.Server(addr)
        #self.server = xmlrpclib.Server('http://localhost:8003')
    
    def generate(self, s, use_string_match):
        o = self.server.generate(s, use_string_match)
        #print(o)
        return o

if __name__ == '__main__':
    client = ApproxNNClient()
    s = 'PERSON located GPE'
    use_string_match = False
    o = client.generate(s, use_string_match)
    print(o)
