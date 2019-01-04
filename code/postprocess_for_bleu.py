import spacy
import sys
from os import path

infile = sys.argv[1]
outfile = sys.argv[2]

if path.exists(outfile):
    print('Output file ' + str(outfile) + ' already exist')
    sys.exit(0)

lines = open(infile, 'r').readlines()
lines = [l.rstrip() for l in lines]

outfile = open(outfile, 'w')
nlp = spacy.load('en_core_web_sm')

for line in lines:
    line = line.decode('unicode-escape')
    line.replace(u'\xe2\x80\x99',u'\'')
    doc = nlp(line)
    words = [token.text for token in doc]
    oline = ' '.join(words)
    print(oline)
    outfile.write(oline.rstrip().lower().encode('unicode-escape') + '\n')

outfile.close()
