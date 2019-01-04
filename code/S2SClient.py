import xmlrpclib

class S2SClient:
    def __init__(self, port_n):
        addr = 'http://localhost:' + str(port_n)
        self.server = xmlrpclib.Server(addr)
    
  
    def generate_with_classifier(self, astr):
        return self.server.generate_with_classifier(astr)
    
    def generate_without_classifier(self, astr):
        return self.server.generate_without_classifier(astr)

    def generate_with_multiword(self, astr):
        return self.server.generate_with_multiword(astr)

    def generate_with_singleword(self, astr):
        return self.server.generate_with_singleword(astr)

    def generate_multiword_morph_simple(self, astr):
        return self.server.generate_multiword_morph_simple(astr)

    def generate_multiword_morph_merge(self, astr):
        return self.server.generate_multiword_morph_merge(astr)


if __name__ == '__main__':
    import time
    s2sClient = S2SClient(9911)
    tick1 = time.time()
    s = 'PERSON NOUN date NOUN birth NOUN DATE NOUN'
    o = s2sClient.generate_multiword_morph_simple(s)
    tick2 = time.time()    
    print(tick1)
    print(tick2)
    print(tick2 - tick1)
    print(o)
