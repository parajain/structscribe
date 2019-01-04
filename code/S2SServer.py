# Server code

import SimpleXMLRPCServer
from S2SModel import *
import json
import sys
import os.path
from os import path

class S2SFunctions:
    def __init__(self, config):
        #withClassifierS2SModelFile = config['withClassifierS2SModel']
        withoutClassifierS2SModelFile = config['withoutClassifierS2SModel']
        withoutClassifierMultiWordS2SModelFile = config['withoutClassifierMultiWordS2SModel']
        withoutClassifierSingleWordS2SModelFile = config['withoutClassifierSingleWordS2SModel']
        multiWordSimpleS2SModelFile = config['multiWordSimpleS2SModel']
        multiWordMergeS2SModelFile = config['multiWordMergeS2SModel']
        #self.withClassifierS2SModel = Seq2Seq(modelfile=withClassifierS2SModelFile)
        self.withoutClassifierS2SModel = Seq2Seq(modelfile=withoutClassifierS2SModelFile)
        self.withoutClassifierMultiWordS2SModel = Seq2Seq(modelfile=withoutClassifierMultiWordS2SModelFile)
        self.withoutClassifierSingleWordS2SModel = Seq2Seq(modelfile=withoutClassifierSingleWordS2SModelFile)
        self.multiWordSimpleS2SModel = Seq2Seq(modelfile=multiWordSimpleS2SModelFile)
        self.multiWordMergeS2SModel = Seq2Seq(modelfile=multiWordMergeS2SModelFile)
        print('Loaded s2s models ..')
        

    def _privateFunction(self):
        # This function cannot be called through XML-RPC because it
        # starts with an '_'
        pass
    
    #def generate_with_classifier(self, astr):
    #    return self.withClassifierS2SModel.generate(astr)
    
    def generate_without_classifier(self, astr):
        return self.withoutClassifierS2SModel.generate(astr)

    def generate_with_multiword(self, astr):
        return self.withoutClassifierMultiWordS2SModel.generate(astr)

    def generate_with_singleword(self, astr):
        return self.withoutClassifierSingleWordS2SModel.generate(astr)

    def generate_multiword_morph_simple(self, astr):
        return self.multiWordSimpleS2SModel.generate(astr)
    
    def generate_multiword_morph_merge(self, astr):
        return self.multiWordMergeS2SModel.generate(astr)


if __name__ == "__main__":
    config_file = sys.argv[1]
    if not path.exists(config_file):
      print('Unable to read file ', config_file)
      sys.exit(0)

    config = json.load(open(config_file))
    print('Configuration:')
    print(json.dumps(config, indent=4, sort_keys=True))
    print('--------------------------------------------')
    port_n = config['s2s_port']    
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port_n))
    server.register_instance(S2SFunctions(config))
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
