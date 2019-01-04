# coding: utf-8
from polyglot.downloader import downloader
print(downloader.supported_languages_table("morph2"))
print(downloader.supported_languages_table("morph2.en"))
import polyglot
polyglot download morph2.en morph2.ar
polyglot.downloader('morph2.en')
polyglot.downloader.download_gui
get_ipython().run_cell_magic(u'bash', u'', u'    polyglot download morph2.en morph2.ar\n')
from polyglot.text import Text, Word
words = ["preprocessing", "processor", "invaluable", "thankful", "crossed"]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
get_ipython().magic(u'ls ')
get_ipython().magic(u'ls ')
get_ipython().magic(u'pwd ')
get_ipython().magic(u'cd /data1/struct2text/wikiparse/wikiparse/')
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
get_ipython().magic(u'ls ')
get_ipython().magic(u'cat lemmatization.py')

import spacy
nlp = spacy.load('en_core_web_sm')
f=open('output_train.txt')
x=f.readlines()
x
xclean=[e.strip() for e in x]
xclean
get_ipython().magic(u'cat lemmatization.py')
polyglot download embeddings2.en pos2.en
get_ipython().run_cell_magic(u'bash', u'', u'polyglot download embeddings2.en pos2.en\n')
words = ["preprocessing", "processor", "invaluable", "thankful", "crossed"]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
xclean[0]
xclean[0].split()
xcleantokenlist=[[token.text for token in nlp(s)] for s in xclean]
xcleantokenlist=[[token.text for token in nlp(unicode(s,'utf-8'))] for s in xclean]
xcleantokenlist=[[token.text for token in nlp(unicode(s,'utf-8'))] for s in xclean[:100]]
xcleantokenlist[0]
words=xcleantokenlist[0]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
xcleantokenlist[1]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
words=xcleantokenlist[1]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
xcleanlemmas = [[(token.text,token.lemma_,token.tag_) for token in nlp(unicode(s,'utf-8'))] for s in xclean]
xcleanlemmas = [[(token.text,token.lemma_,token.tag_) for token in nlp(unicode(s,'utf-8'))] for s in xclean[:100]]
xcleanlemmas
l=xcleanlemmas[99]
l
from nltk.corpus import wordnet
def get_wordnet_pos(treebank_tag):
    
        if treebank_tag.startswith('J'):
                return wordnet.ADJ
        elif treebank_tag.startswith('V'):
                return wordnet.VERB
        elif treebank_tag.startswith('N'):
                return wordnet.NOUN
        elif treebank_tag.startswith('R'):
                return wordnet.ADV
        else:
                return ''
ltag=[(e[1],get_wordnet_pos(e[2])) for e in l]
ltag
def get_wordnet_pos(treebank_tag):
    
        if treebank_tag.startswith('J'):
                return wordnet.ADJ
        elif treebank_tag.startswith('V'):
                return wordnet.VERB
        elif treebank_tag.startswith('N'):
                return wordnet.NOUN
        elif treebank_tag.startswith('R'):
                return wordnet.ADV
        else:
                return wordnet.NOUN
    
ltag=[(e[1],get_wordnet_pos(e[2])) for e in l]
ltag
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
llem=[(k,lemmatizer.lemmatize(k,v)) for k,v in ltag]
llem
words=[k for k,v in llem]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
xclean
xcleanlemmas
l=[(u'Brock', u'brock', u'NNP'),
  (u'Lesnar', u'lesnar', u'NNP'),
  (u'married', u'marry', u'VBD'),
  (u'Randy', u'randy', u'NNP'),
  (u'Couture', u'couture', u'NNP'),
  (u'.', u'.', u'.')]
ltag=[(e[1],get_wordnet_pos(e[2])) for e in l]
llem=[(k,lemmatizer.lemmatize(k,v)) for k,v in ltag]
llem
words=[k for k,v in llem]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
get_ipython().magic(u'cat lemmatization.py')
f=open('lemmas_output_train.pkl','rb')
import cPickle as cp
xcleanlemmas=cp.load(f)
len(xcleanlemmas)
xcleanlemmas[10]
get_ipython().magic(u'cat lemmatization.py')
import spacy
nlp = spacy.load('en_core_web_sm')
f=open('output_train.txt')
x=f.readlines()
xclean=[e.strip() for e in x]
xcleanlemmas = [[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(unicode(s,'utf-8'))] for s in xclean]
xcleanlemmas[0]
f=open('lemmas_output_train_2.pkl','wb')
cp.dump(xcleanlemmas,f)
xnopunct=[]
for e in xnopunct:
    el=[]
    for z in e:
        if z[2]=='PUNCT':
            continue
        el.append(z)
    xnopunct.append(el)
    
xnopunct[0]
for e in xcleanlemmas:
    el=[]
    for z in e:
        if z[2]=='PUNCT':
            continue
        el.append(z)
    xnopunct.append(el)
    
xnopunct[0]
xnopunct[1]
f=open('lemmas_output_train_2_nopunct.pkl','wb')
cp.dump(xnopunct,f)
from nltk.corpus import stopwords
sw = stopwords.words("english")
sw
len(sw)
xnostop=[]
for e in xnopunct:
    el=[]
    for z in e:
        if z[1] in sw:
            continue
        el.append(z)
    xnostop.append(el)
    
xnostop
xnostop[0]
xnostop[1]
xnostop[2]
xcleanlemmas[2]
xnostop[3]
xnostop[4]
xnostop[5]
xnostop[6]
xspacytags=[[ent for ent in nlp(unicode(s,'utf-8')).ents] for s in xclean[:10]]
xspacytags
xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in nlp(unicode(s,'utf-8')).ents] for s in xclean[:10]]
xspacytags
xclean[2]
xclean[4]
xclean[5]
xcleantagged=[]
s=xclean[0]
t=[(u'Nikolaj Coster-Waldau', 0, 21, u'PERSON'),
  (u'the Fox Broadcasting Company', 34, 62, u'ORG')]
t
s
s1=s
s1=s[21:]
s1
s1=s1[:13]+s1[41:]
s1
diff=0
def return_range(t):
    diff=0
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
    pairs=[]
    for i in range(len(l)-1):
        pairs.add((l[i][0],l[i+1][0]))
    return pairs
pairs=return_range(t)
def return_range(t):
    diff=0
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
    pairs=[]
    for i in range(len(l)-1):
        pairs.append((l[i][0],l[i+1][0]))
    return pairs
pairs=return_range(t)
pairs
def return_range(t):
    diff=0
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
    pairs=[]
    for i in range(len(l)-1):
        pairs.append((l[i][0],l[i+1][0]))
    pairs.append(l[-1])return pairs
    
def return_range(t):
        if len(t)==0:
                return (0,-1)
        l=[]
        for e in t:
                l.append((e[2],-1))
            pairs=[]
            for i in range(len(l)-1):
                    pairs.append((l[i][0],l[i+1][0]))
                pairs.append(l[-1])
                return pairs
        
get_ipython().magic(u'paste')
def return_range(t):
    diff=0
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
    pairs=[]
    for i in range(len(l)-1):
        pairs.append((l[i][0],l[i+1][0]))
    pairs.append(l[-1])return pairs
    
def return_range(t):
def return_range(t):
        if len(t)==0:
                return (0,-1)
        l=[]
        for e in t:
                l.append((e[2],-1))
            pairs=[]
            for i in range(len(l)-1):
                    pairs.append((l[i][0],l[i+1][0]))
                pairs.append(l[-1])
    return (0,-1)
def return_range(t):
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
        pairs=[]
        for i in range(len(l)-1):
            pairs.append((l[i][0],l[i+1][0]))
            pairs.append(l[-1])
    return pairs
def return_range(t):
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
    pairs=[]
    pairs=[]
    for i in range(len(l)-1):
        pairs.append((l[i][0],l[i+1][0]))
    pairs.append(l[-1])
    return pairs
pairs=return_range(t)
pairs
xspacytags
t=[(u'number two', 18, 28, u'CARDINAL'),
  (u'the Billboard Hot 100', 32, 53, u'ORG'),
  (u'2003', 57, 61, u'DATE')]
pairs=return_range(t)
pairs
def return_range(t):
    if len(t)==0:
        return (0,-1)
    l=[]
    for e in t:
        l.append((e[2],-1))
    pairs=[]
    pairs=[]
    for i in range(len(l)-1):
        pairs.append((l[i][1],l[i+1][0]))
    pairs.append(l[-1])
    return pairs
pairs=return_range(t)
pairs
def return_range(t):
    if len(t)==0:
        return (0,-1)
    pairs=[]
    for i in range(len(t)-1):
        pairs.append((t[i][2],t[i+1][1]))
    pairs.append((t[-1][2],-1))
    return pairs
pairs=return_range(t)
pairs
t
xclean[6]
xcleanlemmas[6]
def return_range(t):
    if len(t)==0:
        return (0,-1)
    pairs=[(0,t[0][1])]
    for i in range(len(t)-1):
        pairs.append((t[i][2],t[i+1][1]))
    pairs.append((t[-1][2],-1))
    return pairs
pairs=return_range(t)
t
pairs
t=xspacytags[0]
t
pairs=return_range(t)
pairs
def substring(s,pairs):
    s1=''
    for st,en in pairs:
        s1=s1+s[st:en]
    return s1
s1=substring(xclean[0],return_range(xspacytags[0]))
s1
xclean[0]
def return_range(t):
    if len(t)==0:
        return (0,-1)
    pairs=[(0,t[0][1])]
    tags=[t[0][3]]
    for i in range(len(t)-1):
        pairs.append((t[i][2],t[i+1][1]))
        tags.append(t[i+1][3])
    pairs.append((t[-1][2],-1))
    return pairs
def return_range(t):
    if len(t)==0:
        return (0,-1)
    pairs=[(0,t[0][1])]
    tags=[t[0][3]]
    for i in range(len(t)-1):
        pairs.append((t[i][2],t[i+1][1]))
        tags.append(t[i+1][3])
    pairs.append((t[-1][2],-1))
    return pairs,tags
pairs,tags=return_range(xspacytags[0])
pairs,tags
pairs,tags=return_range(xspacytags[6])
pairs,tags
def substring(s,pairs,tags):
    s1=''
    for st,en in pairs:
        s1=s1+s[st:en]
    return s1
def substring(s,pairs,tags):
    s1=''
    for i in range(len(tags)):
        st,en=pairs[i]
        s1=s1+s[st:en]+tags[i]
    return s1
s=xclean[6]
s1=substring(s,pairs,tags)
s1
s
s=xclean[0]
pairs,tags=return_range(xspacytags[0])
pairs,tags
s1=substring(s,pairs,tags)
s1
s1=substring(s,return_range(xspacytags[0]))
xtag=[(xclean[i],substring(xclean[i],k,v)) for k,v in return_range(xspacytags[i]) for i in range(10)]
xtag=[(k,v) for k,v in return_range(xspacytags[i]) for i in range(10)]
xtag=[i for i in range(10)]
xtag
xtag=[return_range(xspacytags[i]) for i in range(10)]
xtag
xtag=[return_range(xspacytags[i]) for i in range(10)]
xtag=[(k,v) for k,v in list(return_range(xspacytags[i])) for i in range(10)]
xtag=[]
for i in range(10):
    s=xclean[i]
    pairs=return_range(xspacytags[i])
    pairs,tags=return_range(xspacytags[i])
    xtag.append(substring(s,pairs,tags))
    
for i in range(10):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    pairs,tags=return_range(xspacytags[i])
    xtag.append(substring(s,pairs,tags))
    
xtag=[]
for i in range(10):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append(substring(s,pairs,tags))
    
def return_range(t):
    if len(t)==0:
        return [(0,-1)],['']
    pairs=[(0,t[0][1])]
    tags=[t[0][3]]
    for i in range(len(t)-1):
        pairs.append((t[i][2],t[i+1][1]))
        tags.append(t[i+1][3])
    pairs.append((t[-1][2],-1))
    return pairs,tags
for i in range(10):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append(substring(s,pairs,tags))
    
xtag
xtag=[]
for i in range(10):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
xtag
xclean[:10]
xspacytags[:10]
pairs,tags=return_range(xspacytags[1])
pairs,tags
s1=substring(xclean[1],pairs,tags)
s1
def substring(s,pairs,tags):
    s1=''
    for i in range(len(tags)):
        st,en=pairs[i]
        s1=s1+s[st:en]+tags[i]
    return s1+pairs[-1]
s1=substring(xclean[1],pairs,tags)
pairs[-1]
def substring(s,pairs,tags):
    s1=''
    for i in range(len(tags)):
        st,en=pairs[i]
        s1=s1+s[st:en]+tags[i]
    return s1+s[pairs[-1][0],pairs[-1][1]]
s1=substring(xclean[1],pairs,tags)
def substring(s,pairs,tags):
    s1=''
    for i in range(len(tags)):
        st,en=pairs[i]
        s1=s1+s[st:en]+tags[i]
    return s1+s[pairs[-1][0]:pairs[-1][1]]
s1=substring(xclean[1],pairs,tags)
s1
xtag=[]
for i in range(10):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
xtag
s=xclean[4]
s
pairs,tags=return_range(xspacytags[4])
pairs,tags
def return_range(t):
    if len(t)==0:
        return [(0,-1)],[]
    pairs=[(0,t[0][1])]
    tags=[t[0][3]]
    for i in range(len(t)-1):
        pairs.append((t[i][2],t[i+1][1]))
        tags.append(t[i+1][3])
    pairs.append((t[-1][2],-1))
    return pairs,tags
xtag=[]
for i in range(10):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
xtag
xcleanlemmas[:10]
xtag=[]
for i in range(len(xclean)):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
len(xclean)
len(xspacytags)
xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in nlp(unicode(s,'utf-8')).ents] for s in xclean]
