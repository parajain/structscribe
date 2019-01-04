import spacy
from dbpedia_ner import *
import sys, codecs

nlp = spacy.load('en')

def get_spacy_ner(s):
  #s_unicode = s.decode('utf8')
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
    print(s)
    tag = getTag(s)
    if tag is not None:
        tag = tag.upper()
    return tag


def get_root(txt):
	#txt = txt.decode("unicode-escape")
	doc = nlp(txt)
	for tok in doc:
		if "ROOT" in tok.dep_:
			return tok.text
	return None

def tag_input_file(inputfilename, outputfilename):
    inputlines = codecs.open(inputfilename, 'r', encoding="utf-8").readlines()
    outputlines = codecs.open(outputfilename, 'r', encoding="utf-8").readlines()
    ioutfile = codecs.open(inputfilename + '.tagged', 'w', 'utf-8')
    ooutfile = codecs.open(outputfilename + '.tagged', 'w', 'utf-8')
    for iline, oline in zip(inputlines, outputlines):
        o1, r, o2 = iline.rstrip().split('||')
        oline = oline.rstrip()
        o1 = o1.strip()
        o2 = o2.strip()
        r = r.strip()
        tag1 = None
        tag2 = None
        stag1 = get_spacy_ner(o1)
        if stag1 is not None:
            tag1 = stag1
        else:
            tag1 = get_dbpedia_ner(o1)
        stag2 = get_spacy_ner(o2)
        if stag2 is not None:
            tag2 = stag2
        else:
            tag2 = get_dbpedia_ner(o2)

        if tag1 is None:
            tag1 = get_root(o1)
        if tag2 is None:
            tag2 = get_root(o2)

        #print(line + '\n')
        #print(tag1, tag2)
        #outfile.write(line.rstrip() + '\n')
        ioutfile.write(tag1 + ' || ' + r  + ' || ' + tag2  + '\n')
        #print(iline, oline)
        oline = oline.replace(o1, tag1)
        oline = oline.replace(o2, tag2)
        ooutfile.write(oline + '\n')




def main():
    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    tag_input_file(inputfilename, outputfilename)

def test():
  s = 'Apple is looking at buying U.K. startup for $1 billion'
  s =  'Massachusetts Institute of Technology'
  #s = 'United States'
  #nertext, start, end, lable = get_dbpedia_ner(s)
  print(get_dbpedia_ner(s))

if __name__ == '__main__':
  test()
