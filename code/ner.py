import spacy
from lookupner.dbpedia_ner import *
import sys, codecs

nlp = spacy.load('en_core_web_lg')
logfile = open('ologs.txt', 'a')

def log_something(sometext, somevalue):
    lstr = sometext + ': ' + str(somevalue)
    logfile.write('############## \n')
    logfile.write(lstr + '\n')
    #return_logs = self.return_logs + '\n' + lstr
    #print(lstr + '\n')

def get_spacy_ner(s):
    #if not isinstance(s, unicode):
    #Python 3 renamed the unicode type to str, the old str type has been replaced by bytes.
    if not isinstance(s, unicode):
        s_unicode = s.decode('utf8')
    else:
        s_unicode = s
    doc = nlp(s_unicode)
    l = len(doc.ents)
    if l > 1 or l < 1:
        return None
    else:
        ent = doc.ents[0]
        if ent.end_char < len(s): # fully text is not the whole entity
            return None

        return ent.label_


def get_dbpedia_ner(s):
    #print(s)
    tag = getTag(s)
    if tag is not None:
        tag = tag.upper()
    return tag


def get_root(txt):
	txt = txt.decode("unicode-escape")
	doc = nlp(txt)
	for tok in doc:
		if "ROOT" in tok.dep_:
			return tok.text
	return None
def capitalize_phrase(phrase):
    #Makes each word in the phrase capitalized
    new_phrase = ""
    for w in phrase.split():
        new_w = w[0].upper()+w[1:]
        new_phrase+=new_w +" "
    new_phrase = new_phrase.strip()
    return new_phrase

def tagTriple(triple):
    o1, r, o2 = triple[0], triple[1], triple[2]
    #######################################################
    #We are capitalizing each and every term for the entities
    o1_temp = capitalize_phrase(o1)
    o2_temp = capitalize_phrase(o2)

    #########################################################

    tag1 = None
    tag2 = None
    stag1 = get_spacy_ner(o1_temp)
    log_something('Spacy tag for ' + str(o1_temp) + ' ', str(stag1))
    if stag1 is not None:
        tag1 = stag1
    else:
        tag1 = get_dbpedia_ner(o1_temp)
    stag2 = get_spacy_ner(o2_temp)
    if stag2 is not None:
        tag2 = stag2
    else:
        tag2 = get_dbpedia_ner(o2_temp)

    if tag1 is None:
        tag1 = 'UNK'#get_root(o1)
    if tag2 is None:
        tag2 = 'UNK'#get_root(o2)

    #print(line + '\n')
    #print(tag1, tag2)
    tagged = [tag1, r, tag2]
    tag_map_list = []
    tag1map = {}
    tag1map[tag1] = o1 #Store original words
    tag2map = {}
    tag2map[tag2] = o2 #Store original words
    tag_map_list.append(tag1map)
    tag_map_list.append(tag2map)

    return tagged, tag_map_list


def test():
  s = 'Apple is looking at buying U.K. startup for $1 billion'
  s =  'Massachusetts Institute of Technology'
  s = 'United States'
  #nertext, start, end, lable = get_dbpedia_ner(s)
  print(get_dbpedia_ner(s))
  print(spacy_ner(s))

if __name__ == '__main__':
  test()
