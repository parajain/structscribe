import SimpleXMLRPCServer
from cnngender.gender_predict import predict_gender


class Gender:
    def determine_gender(self, name):
        return predict_gender(name)


if __name__ == "__main__":
    print('--------------------------------------------')
    port_n = 18902
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port_n))
    server.register_instance(Gender())
    print "Registered instance on localhost@" + str(port_n)
    server.serve_forever()

