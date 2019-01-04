# -*- coding: utf-8 -*-

#Parag Jain
import xml.etree.ElementTree as ET
import string, os, re, sys
#import urllib2 # python2
import urllib.request as urllib2  # python3
from urllib.parse import urlparse

from numbers import Number
import xml.etree.ElementTree as ET
from dateutil.parser import parse
import requests


#in order
grounded_entities = ['person', 'country','city', 'place', 'book', 'food', 'institute','university','organisation', 'thing']
entity_word_map = {'person': '<person>',
                   'place': '<place>',
                   'book': '<book>',
                   'food':'<food>',
                   'institute':'<organization>',
                    'university':'<organisation>',
                   'organisation':'<organisation>',
                   'thing':'<thing>',
                   'country':'<country>',
                   'city':'<city>',
                   'date':'<date>',
                   'number': '<number>'}
dbpedia_search_link = 'http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString='
url_s = 'http://lookup.dbpedia.org/api/search/KeywordSearch'

def filter_string(string_inp):
    print('99999999999999999999 ', string_inp)
    fs = filter(lambda x: x in string.printable, string_inp)
    return fs
    
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

def check_dbpedia2(s):
    #s = filter_string(s)
    #s = urllib2.quote(s) python 2
    s = urllib2.parse.quote(s)
    u = dbpedia_search_link+s
    print(u)
    #_params = {'QueryString',s}
    #r = requests.get(url=url_s, params=_params)
    #print('888888', r)

    #u = urllib2.Request(u)
    #print(u)
    #resp = requests.get(u)
    #print('resp' + resp)

    req = urllib2.Request(u)
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    a = urllib2.urlopen(req, timeout=6).read()

    xmlp = ET.XMLParser(encoding="utf-8")
    root = ET.fromstring(a, parser=xmlp)
    result = root.find('{http://lookup.dbpedia.org/}Result')
    classes = result.find('{http://lookup.dbpedia.org/}Classes')
    labels = []
    for c in classes.findall('{http://lookup.dbpedia.org/}Class'):
        label = c.find('{http://lookup.dbpedia.org/}Label').text
        labels.append(label)
    print(labels)
    for grounded_entity in grounded_entities:
        for label in labels:
            if grounded_entity in label:
                return grounded_entity
    #    print("Unexpected error:", sys.exc_info()[0])
    return None

def check_dbpedia(s):
    #s = filter_string(s)
    #s = urllib2.quote(s) # python 2
    s = urlparse(dbpedia_search_link + s)
    #u = dbpedia_search_link + s
    #print(u)
    try:
        req = urllib2.Request(u)
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        a = urllib2.urlopen(req, timeout=6).read()
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
            for grounded_entity in grounded_entities:
                for label in labels:
                    #print(label, grounded_entity)
                    if grounded_entity in label:
                        return grounded_entity
    except:
        pass
        #print("Unexpected error:", sys.exc_info()[0])
    return None


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
    if is_date(s):
        return 'date'
    if is_number(s):
        return 'number'
    t = check_dbpedia(s)
    if t is None:
        t = split_and_check(s)
        if t is not None:
            return t
    else:
        return t
    return 'thing'


def test():
    s = 'Massachusetts Institute of Technology, sc asasa'
    s = 'cake'
    t = get_entity_type(s)
    print(t)

def test_lcs():
    s1 = 'Massachusetts Institute of Technology, sc asasa'
    s2 = 'Technolgy'
    s = common_string(s1, s2)
    if s is not None:
        print('asaASASAS   ' + s)
    else:
        print('None')

if __name__ == '__main__':
  test()