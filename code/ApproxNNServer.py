# Server code

import SimpleXMLRPCServer
from ApproxNN import *
import sys
import os.path
from os import path
import json

class ANNFunctions:
    def __init__(self, config):
        print('Initializing ApproxNN Server ', config)
        self.approxNN = ApproxNN(config)
        print('Init done ApproxNN..')
        

    def _privateFunction(self):
        # This function cannot be called through XML-RPC because it
        # starts with an '_'
        pass
    
    def generate(self, astr, use_string_match):
        return self.approxNN.generate(astr, use_string_match)

    
config_file = sys.argv[1]
if not path.exists(config_file):
  print('Unable to read file ', config_file)
  sys.exit(0)

config = json.load(open(config_file))
print('Configuration:')
print(json.dumps(config, indent=4, sort_keys=True))
print('--------------------------------------------')
port = config['ann_port']


server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port))
server.register_instance(ANNFunctions(config))
server.register_function(lambda astr: '_' + astr, '_string')
server.serve_forever()
# Client code
'''
import xmlrpclib

server = xmlrpclib.Server('http://localhost:8001')
print server.chop_in_half('I am a confidant guy')
print server.repeat('Repetition is the key to learning!\n', 5)
print server._string('<= underscore')
print server.python_string.join(['I', 'like it!'], " don't ")
print server._privateFunction() # Will throw an exception
'''
