# -*- coding: utf-8 -*-

#Parag Jain
import xml.etree.ElementTree as ET
import string, os, re, sys
import urllib2 # python2
#import urllib.request as urllib2  # python3
#from urllib.parse import urlparse
#import urllib.request
#import urllib.parse
from numbers import Number
import xml.etree.ElementTree as ET
from dateutil.parser import parse
import requests
import json
import sys
#from urlparse import urlparse

here = os.path.dirname(os.path.abspath(__file__))
#print('Here ', here)
sys.path.append(here)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
#print('filed ', file_dir)

dbpedia_search_link_web = 'http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString='
dbpedia_search_link_prefix = 'http://irlbxph017.irl.in.ibm.com:1111/api/search/PrefixSearch?QueryClass=&MaxHits=5&QueryString='
dbpedia_search_link = 'http://irlbxph017.irl.in.ibm.com:1111/api/search/KeywordSearch?QueryClass=&MaxHits=5&QueryString='

#dirpath = os.getcwd()
#print('655555555', dirpath)
mappings = json.load(open(os.path.join(here, 'ner_class_mappings.txt')))

def filter_string(string_inp):
    fs = filter(lambda x: x in string.printable, string_inp)
    return fs

def is_url(x):
    try:
        result = urlparse(x)
        return result.scheme and result.netloc and result.path
        #return True
    except:
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def is_date(s):
    s = s.strip().replace('"', '')
    try:
        parse(s)
        return True
    except ValueError:
        return False

def check_dbpedia(s):
    s = filter_string(s)
    #s = urllib2.quote(s) # python 2
    #s = dbpedia_search_link + s
    #u = dbpedia_search_link + s
    u  = dbpedia_search_link + urllib2.quote(s)
    #print('Checking -- ', u)
    all_labels = []
    try:
        req = urllib2.Request(u)
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        #print(req)
        a = urllib2.urlopen(req, timeout=6).read()
        #print(a)
        xmlp = ET.XMLParser(encoding="utf-8")
        root = ET.fromstring(a, parser=xmlp)
        results = root.findall('{http://lookup.dbpedia.org/}Result')
        for result in results:
            classes = result.find('{http://lookup.dbpedia.org/}Classes')
            labels = []
            for c in classes.findall('{http://lookup.dbpedia.org/}Class'):
                label = c.find('{http://lookup.dbpedia.org/}Label').text
                labels.append(label)

            #print(labels)
            all_labels.extend(labels)
    except:
        pass
        #print("Unexpected error:", sys.exc_info()[0])
    return all_labels


def split_and_check(s):
    if '_' in s:
        sarr = s.split('_')
    else:
        sarr = s.split(' ')
    l = len(sarr)
    for i in range(l):
        ss = ' '.join(sarr[:l-i])
        t = check_dbpedia(ss.strip(','))
        if t is not None:
            return t
    return None

def get_entity_type(s):
    s = s.strip().replace('"', '')
    if is_url(s):
        return ['url']
    #if is_date(s):
    #    return 'date'
    #if is_number(s):
    #    return 'number'
    t = check_dbpedia(s)
    if t is None:
        t = split_and_check(s)
        if t is not None:
            return t
    else:
        return t
    return 'thing'

def getTag(s):
  dbpediatags = get_entity_type(s)
  #print(dbpediatags)
  ner_tags = []
  for key, value in mappings.items():
    for t in dbpediatags:
      t = t.replace(" ", "")
      if t in value:
        if key not in ner_tags:
          ner_tags.append(key)

  if len(ner_tags) > 0:
      return ner_tags[0]
  else:
      return None

def main():
  s =  'Massachusetts Institute of Technology'
  s = 'United states'
  t = getTag(s)
  print(t)

if __name__ == '__main__':
  main()
