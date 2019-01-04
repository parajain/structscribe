from owlready2 import *

fname = "C:\\Users\\IBM_ADMIN\\Downloads\\dbpedia_2014onto\\dbpedia_2014.owl"
f = open(fname, 'r')


from ontology_alchemy import Ontology, Session
ontology = Ontology.load("dbpedia_ontology.ttl")
