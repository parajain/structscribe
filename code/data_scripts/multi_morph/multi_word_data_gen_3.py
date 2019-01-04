# coding: utf-8
f=open('output_train.txt','r')
x=f.readlines()
xclean=[e.strip() for e in x]
len(x)
len(xclean)
import spacy
nlp = spacy.load('en_core_web_sm')
xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in nlp(unicode(s,'utf-8')).ents] for s in xclean]
xspacytags[0]
xtag=[]
for i in range(len(xclean)):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
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
def substring(s,pairs,tags):
    s1=''
    for i in range(len(tags)):
        st,en=pairs[i]
        s1=s1+s[st:en]+tags[i]
    return s1+s[pairs[-1][0]:pairs[-1][1]]
xtag
for i in range(len(xclean)):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
def substring(s,pairs,tags):
    s1=''
    for i in range(len(tags)):
        st,en=pairs[i]
        s1=s1+s[st:en]+tags[i]
    return s1+s[pairs[-1][0]:pairs[-1][1]]
xtag
len(xtag)
xtag
xclean[91]
xclean=[unicode(e.strip(),'utf-8') for e in x]
xclean[91]
xtag
xtag=[]
for i in range(len(xclean)):
    s=xclean[i]
    pairs,tags=return_range(xspacytags[i])
    xtag.append((s,substring(s,pairs,tags)))
    
len(xtag)
xtag
f=open('lemmas_output_train_2.pkl','rb')
import cPickle as cp
xcleanlemmas=cp.load(f)
xcleanlemmas[0]
f=open('lemmas_output_train_2_nopunct.pkl','rb')
xnopunct=cp.load(f)
xnopunct[0]
xnostop=[]
get_ipython().magic(u'ls ')
get_ipython().magic(u'cat multi_word_data_gen.py')
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
        
for e in xnopunct:
    el=[]
    for z in e:
        if z[1] in sw:
            continue
        el.append(z)
    xnostop.append(el)
    
xnostop[0]
xtag[0]
xtag[1]
xnostop[1]
fout=open('lemma_output_train_2_nopunct_nostop.pkl','wb')
cp.dump(xnostop,fout)
get_ipython().magic(u'ls ')
get_ipython().magic(u'ls -lart')
xtagxtag
xtag[:10]
len(xtag)
xindices = [i for i in range(len(xtag)) if len(xtag[i][1].split()) <= 10]
xindices
len(xindices)
xindices[0]
xindices[:20]
xtag[2]
xtag[5]
xtag[11]
xtag[10]
xtag[0]
xtag[1]
xtag[3]
xtag[:23]
xnostop[:23]
xtag[:23]
xnostop[6]
xnostop[22]
xinput = []
for t in xnostop:
    l=[]
    for a,b,c,d in t:
        l.append(a)
        l.append(d)
    xinput.append(' '.join(l))
    
xinput
xinput[0],xtag[0],xnostop[0]
s1='worked'
s2='work'
s1.split(s2)
xinput[1],xtag[1],xnostop[1]
s1='Nikolaj'
s2='nikolaj'
s1.split(s2)
xmorph=[]
for t in xnostop:
    l=[]
    for a,b,c,d in t:
        e=''.join(a.lower().split(b))
        l.append((a,b,c,d,e))
    xmorph.append(l)
    
xinput[0],xtag[0],xnostop[0]
xinput[0],xtag[0],xnostop[0],xmorph[0]
s1=u'Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.'
t=[(u'Nikolaj', u'nikolaj', u'PROPN', u'NNP', u''),
  (u'Coster', u'coster', u'PROPN', u'NNP', u''),
  (u'Waldau', u'waldau', u'PROPN', u'NNP', u''),
  (u'worked', u'work', u'VERB', u'VBD', u'ed'),
  (u'Fox', u'fox', u'PROPN', u'NNP', u''),
  (u'Broadcasting', u'broadcasting', u'PROPN', u'NNP', u''),
  (u'Company', u'company', u'PROPN', u'NNP', u'')])
t=[(u'Nikolaj', u'nikolaj', u'PROPN', u'NNP', u''),
  (u'Coster', u'coster', u'PROPN', u'NNP', u''),
  (u'Waldau', u'waldau', u'PROPN', u'NNP', u''),
  (u'worked', u'work', u'VERB', u'VBD', u'ed'),
  (u'Fox', u'fox', u'PROPN', u'NNP', u''),
  (u'Broadcasting', u'broadcasting', u'PROPN', u'NNP', u''),
  (u'Company', u'company', u'PROPN', u'NNP', u'')]
s2
s2
s1
nlp
doc=nlp(s1)
for token in doc:
    print token.text
    
xnopunct[0]
xmorph[0]
xoutput=[]
for i in range(len(xnopunct)):
    t=[]
    t1=xnopunct[i]
    t2=xmorph[i]
    t2map={}
    for a,b,c,d,e in t2:
        if a not in t2map:
            t2map[a]=a
        if len(e) != 0:
            t2map[a]=(b,e)
    for a,b,c,d in t1:
        if a not in t2map:
            t.append(a)
        else:
            if isinstance(t2map[a], tuple):
                t.append(t2map[a][0])
                t.append(t2map[a][1])
            else:
                t.append(a)
    xoutput.append(' '.join(t))
    
xoutput[0]
xinput[0]
len(xinput),len(xoutput)
len(xindices)
xinputfinal=[xinput[i] for i in xindices]
xoutputfinal=[xoutput[i] for i in xindices]
len(xinputfinal),len(xoutputfinal)
f1=open('lemmax_seq2seq.src','w')
f1.writelines('\n'.join(xinputfinal))
xinputfinal=[xinput[i]+'\n' for i in xindices]
xoutputfinal=[xoutput[i]+'\n' for i in xindices]
f1.writelines(xinputfinal)
xinputfinal[0]
xinout=[]
for i in range(len(xinputfinal)):
    xinout.append((xinputfinal[i],xoutputfinal[i]))
    
xinout[:20]
xinout[:30]
xnopunct[:8]
xinout[:30]
xnopunct[:8]
xnopunct[:9]
xinout[:30]
get_ipython().magic(u'ls -lart')
get_ipython().magic(u'save 1-122 multi_word_data_gen_2')
get_ipython().magic(u'save multi_word_data_gen_2 1-122')
xinout[:30]
get_ipython().run_cell_magic(u'bash', u'', u'polyglot download morph2.en morph2.ar\n')
from polyglot.text import Text, Word
words = ["preprocessing", "processor", "invaluable", "thankful", "crossed"]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
words = ["sold"]
for w in words:
      w = Word(w, language="en")
      print("{:<20}{}".format(w, w.morphemes))
    
xinout[:30]
xnopunct[1]
from nltk.stem.wordnet import WordNetLemmatizer
lem=WordNetLemmatizer('creator','n')
lem=WordNetLemmatizer.lemmatize('creator','n')
nltk.stem.WordNetLemmatizer().lemmatize('loving', 'v')
import nltk
nltk.stem.WordNetLemmatizer().lemmatize('loving', 'v')
nltk.stem.WordNetLemmatizer().lemmatize('creator','n')
nltk.stem.WordNetLemmatizer().lemmatize('stranger','n')
nltk.stem.WordNetLemmatizer().lemmatize('stranger','NN')
nltk.stem.WordNetLemmatizer().lemmatize('stranger',nltk.stem.wordnet.NOUN)
xinout[:30]
xcleanlemmas[:26]
xinout[:30]
xspacytags[:20]
xspacytags[:30]
xinout[:30]
f1.writelines(xinputfinal)
xinputfinal=[xinput[i].decode('utf-8')+'\n' for i in xindices]
xinputfinal=[xinput[i]+'\n' for i in xindices]
xinputfinal[:30]
for e in xinputfinal:
    f1.write(e)
    
for e in xinputfinal:
    f1.write(e,'utf-8')
    
for e in xinputfinal:
    f1.write(e.decode('utf-8'))
    
for e in xinputfinal:
    f1.write(e.decode('ascii'))
    
for e in xinputfinal:
    f1.write(e.decode('ascii','ignore'))
    
for e in xinputfinal:
    f1.write(e.decode('utf-8'))
    
for e in xinputfinal:
    f1.write(e)
    
for e in xinputfinal:
    f1.write(e.encode('utf-8'))
    
f1.close()
len(xinputfinal),len(xoutputfinal)
f1=open('lemmax_seq2seq.tgt','w')
for e in xoutputfinal:
    f1.write(e.encode('utf-8'))
    
f1.close()
len(xinout)
xinout[:30]
f1=open('lemmax_seq2seq.src','w')
f2=open('lemmax_seq2seq.tgt','w')
for k,v in xinout:
    f1.write(k.encode('utf-8'))
    f2.write(v.encode('utf-8'))
    
f1.close()
f2.close()
xinout[:30]
xspacytags[:30]
xtag
xtag[:30]
xinout[:30]
xtag[:30]
xinput[:30]
xinout=[]
for i in range(len(xinput)):
    xinout.append((xinput[i],xoutput[i]))
    
xinout[:30]
xinoutfinal=[xinout[i] for i in xindices]
len(xinout)
len(xinoutfinal)
xinoutfinal[:30]
xtag[:30]
s=u'Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.'
stag=u'PERSON worked with ORG'
snostop=xnostop[0]
snostop
snopunct=xnopunct[0]
snopunct
stag
s
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(unicode(s,'utf-8'))] for k,s in xtag]
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(s)] for k,s in xtag]
snopunct
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(s)] for k,s in xtag[:5]]
xtagpos
sclean=xclean[:10]
sclean
stag=xtag[:10]
stag
snopunct=xnopunct[:10]
snopunct[:2]
snostop=xnostop[:10]
snostop[:2]
sspacytags=xspacytags[:10]
sspacytags[:2]
sspacytags[:2]
spacylist=['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','UNK']
stag[:2]
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(s)] for k,s in xtag[:10]]
xtagpos[:2]
snopunct[:2]
xtagpos[2:4]
xnopunct[2:4]
stagpos[4:6]
xtagpos[4:6]
xnopunct[4:6]
xtagpos[6:8]
xnopunct[6:8]
xtagpos[8:-1]
xtagpos[8:10]
xnopunct[8:10]
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(s)] for k,s in xtag]
xtagpos[8:10]
xnopunct[8:10]
xtag[8:10]
xmorph[8:10]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtag[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
xtag[:5]
xnopunct[:5]
xtag[:5]
xspacytags[:5]
xnopunct[:5]
xtag[:5]
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(s)] for k,s in xtag[:10]]
xtagpos[:5]
xtag[:5]
xnopunct[:5]
xtag[6:10]
stag=xtag[6]
stag
snopunct=xnopunct[6]
snopunct
stagtokens=stag[1].split()
stagtokens
xmorph[6]
snopunct
stagtokens
xtag[:5]
s=u'History of art includes architecture, dance, sculpture, music, painting, poetry literature, theatre, narrative, film, photography and graphic arts.'
t=s.translate(None, string.punctuation)
import string
t=s.translate(None, string.punctuation)
table = string.maketrans("","")
t=s.translate(table, string.punctuation)
t=s.translate(string.punctuation)
t
table
t=s.translate(string.punctuation)
t
import re
def test_re(s):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    return regex.sub('', s)
t=test_re(s)
t
xtag[:5]
xtagnopunct=[(test_re(k),test_re(v)) for k,v in xtag]
xtagnopunct[:5]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
spacylist
spacylist.append('WORKOFART')
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
spacylist
string.punctuation
spacylist=['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','UNK']
puncts='!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~'
xtagnopunct=[(test_re(k),test_re(v)) for k,v in xtag]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
def test_re(s):
    regex = re.compile('[%s]' % re.escape(puncts))
    return regex.sub('', s)
xtagnopunct=[(test_re(k),test_re(v)) for k,v in xtag]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
xtagnopunct[:30]
xtagnopunct[:40]
xnopunct[35]
xnopunct[34]
xnopunct[33]
xnopunct[:10]
xnopunct[:5]
xnopunct[5:10]
xcommonwords=[]
for t in xnopunct:
    for a,b,c,d in t:
        xcommonwords.append(a)
        
len(xcommonwords)
xcommonwords[0]
xcommonwords[1]
xcommonwords[2]
xcommonwords[3]
xcommonwords[4]
len(xnopunct),len(xcommonwords)
from collections import Counter
xwords=[]
for t in xnopunct:
    for a,b,c,d in t:
        xwords.append(a)
        
xcommonwords=Counter(xwords)
xcommonwords.most_common(10)
len(xcommonwords)
xcommonwords.most_common(100)
xwords=[]
for t in xnopunct:
    for a,b,c,d in t:
        xwords.append(a.lower())
        
xcommonwords=Counter(xwords)
len(xcommonwords)
xcommonwords.most_common(100)
xcommonwords.most_common(1000)
xcommonwords.most_common(10000)
xnopunct[5:10]
sw
xnopunct[5:10]
xtag[5:10]
xtag[30:40]
xnopunct[30:35]
xtagnopunct[30:35]
xtag[30:35]
'Whoopi Goldberg co-produced an American dance tournament.'.replace('-',' ')
def test_re(s):
    regex = re.compile('[%s]' % re.escape(puncts))
    return regex.sub('', s)
xtagnopunct=[(test_re(k.replace('-',' ')),test_re(v.replace('-',' '))) for k,v in xtag]
xtag[30:35]
xtagnopunct[30:35]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
xnopunct[57]
xtag[57]
xtagnopunct[57]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[a]=test_re(d)
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
xtagnopunct[57]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[test_re(a)]=d
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[test_re(a)]=d
    print i
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
puncts='!"#$%&\()*+,-./:;<=>?@[\\]^`{|}~'
xtagnopunct=[(test_re(k.replace('-',' ')),test_re(v.replace('-',' '))) for k,v in xtag]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[test_re(a)]=d
    print i
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
def replace_string(s):
    return s.replace('-',' ').replace('\'',' \'')
replace_string("dog's")
xtagnopunct=[(test_re(replace_string(k)),test_re(replace_string(v))) for k,v in xtag]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[test_re(a)]=d
    print i
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
spacylist
xtag[85]
spacylist.append('FAC')
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[test_re(a)]=d
    print i
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
replace_string("isn't")
xtag[215]
replace_string(u"Dolly Parton isn't an actress.")
replace_string(u"PERSON isn't an actress")
xtagnopunct[215]
xtagpos=[]
for i in range(len(xnopunct)):
    tags=xtagnopunct[i][1]
    tagstokens=tags.split()
    tmap={}
    for a,b,c,d in xnopunct[i]:
        if a not in tmap:
            tmap[test_re(a)]=d
    print i
    l=[]
    for tok in tagstokens:
        if tok in spacylist:
            l.append((tok,'NER'))
        else:
            l.append((tok,tmap[tok]))
    xtagpos.append(l)
    
tkns=xtagnopunct[215][1].split()
tkns
xnopunct[215]
xtagpos=[[(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(s)] for k,s in xtag]
xtagpos[215]
xnopunct[215]
xnostop[215]
xtagnopunct[215]
xtagpos[:5]
xnostop[:5]
xtagpos[5:10]
xtagposunk=[]
for tlist in xtagpos:
    l=[]
    for a,b,c,d in tlist:
        if d==u'NNP' or d==u'NNPS':
            if a not in spacylist:
                a=u'UNK'
        l.append((a,b,c,d))
    xtagposunk.append(l)
    
xtagposunk[5:10]
xtagposunk[:5]
xtagposunk[10:15]
xtagposunk[15:20]
xtagposunk[20:25]
xtagposunk[:5]
xtagposunknopunct=[]
for tlist in xtagposunk:
    l=[]
    for a,b,c,d in xtagposunknopunct:
        if c==u'PUNCT':
            continue
        l.append((a,b,c,d))
    xtagposunknopunct.append(l)
    
for tlist in xtagposunk:
    l=[]
    for a,b,c,d in tlist:
        if c==u'PUNCT':
            continue
        l.append((a,b,c,d))
    xtagposunknopunct.append(l)
    
xtagposunknopunct[:5]
xtagposunk[:5]
xtagposunknopunct=[]
for tlist in xtagposunk:
    l=[]
    for a,b,c,d in tlist:
        if c==u'PUNCT':
            continue
        l.append((a,b,c,d))
    xtagposunknopunct.append(l)
    
xtagposunknopunct[:5]
len(xtagpos),len(xtagposunk),len(xtagposunknopunct)
xtagposunknostop=[]
for tlist in xtagposunknopunct:
    l=[]
    for a,b,c,d in tlist:
        if a in sw:
            continue
        l.append((a,b,c,d))
    xtagposunknostop.append(l)
    
xtagposunknostop[:5]
xtagposunknostop[5:10]
xtagposunknostop[10:15]
xtagposunknostop[15:20]
xtag[15:20]
xtagposunknopunct[15:20]
xtagposunknostop[15:20]
spacylist
xtagposunknostopmerge[]
xtagposunknostopmerge=[]
'person' in spacylist
def merge_entity(a,b):
    x,z,w=a[0],a[2],a[3]
    if a[0]==u'UNK':
        x,z,w=b[0],b[2],b[3]
    y=a[1]+'_'+b[1]
    return (x,y,z,w)
for tlist in xtagposunknostop:
    flag=True
    l=[]
    while flag:
        flag=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist:
                l.append(merge_entity(tlist[i],tlist[i+1]))
            	  flag=True
            for e in tlist[i+2:]:
                l.append(e)
        tlist=l
        l=[]
    xtagposunknostopmerge.append(tlist)
    
for tlist in xtagposunknostop:
    flag=True
    l=[]
    while flag:
        flag=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist:
                l.append(merge_entity(tlist[i],tlist[i+1]))
            	  flag=True
            for e in tlist[i+2:]:
                l.append(e)
        tlist=l
        l=[]
    xtagposunknostopmerge.append(tlist)
    
xtagposunknostopmerge=[]
for tlist in xtagposunknostop:
    flag=True
    l=[]
    while flag:
        flag=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist:
                l.append(merge_entity(tlist[i],tlist[i+1]))
                flag=True
            for e in tlist[i+2:]:
                l.append(e)
            break
        tlist=l
        l=[]
    xtagposunknostopmerge.append(tlist)
    
xtagposunknostopmerge[:5]
xtagposunknostopmerge=[]
get_ipython().magic(u'paste')
get_ipython().magic(u'cpaste')
xtagposunknostopmerge[:5]
xtagposunknostop[:5]
xtagposunknostopmerge=[]
get_ipython().magic(u'cpaste')
xtagposunknostopmerge=[]
get_ipython().magic(u'cpaste')
xtagposunknostopmerge=[]
get_ipython().magic(u'cpaste')
xtagposunknostop[:5]
xtagposunknostop[45:50]
xtagposunknostopmerge[45:50]
xtagposunknostopmerge=[]
get_ipython().magic(u'cpaste')
xtagposunknostopmerge[45:50]
xtagposunknostop[45:50]
xtagposunknostop[:5]
xtagposunknostopmerge[:5]
xtagposunknostop[5:10]
xtagposunknostopmege[5:10]
xtagposunknostopmerge[5:10]
xtagposunknostop[50:55]
xtagposunknostopmerge[50:55]
xtagposunknopunct[50:55]
xtag[50:55]
xtagposunknostop[100:105]
xtagposunknostopmerge[100:105]
xtagposunknostopmerge=[]
get_ipython().magic(u'cpaste')
xtagposunknostopmerge=[]
get_ipython().magic(u'cpaste')
xtagposunknostopmerge[100:105]
xtagposunknostop[100:105]
xtag[100:105]
xtagposunknostop[50:55]
xtagposunknostopmerge[50:55]
xtagposunknostopmerge[500:505]
xtagposunknostop[500:505]
xtag[500:505]
xnopunct[500:505]
xtagposunknostop[500:505]
xtagposunknostop[5000:5005]
xtagposunknostopmerge[5000:5005]
xtagposunknopunct[5000:5005]
xtagposunknostopmerge[5000:5005]
xinputtagged=[]
for tlist in xtagposunknostopmerge:
	l=[]
	for a,b,c,d in tlist:
		l.append(a)
		l.append(d)
	xinputtagged.append(' '.join(l))
len(xinputtagged)
xinputtagged[5000:5005]
xinputtaggedfinal=[xinputtagged[i] for i in xindices]
xinputtaggedfinal[:50]
xtagposunknostop[:10]
xtagposunknostopmerge[:10]
xtagposunknostopmerge[5:10]
xtagposunknopunct[5:10]
xtagposunknostopmerge[5:10]
xtagposunknostopmerge[5]
xtagposunknopunct[5]
len(xinputtaggedfinal)
for i,j in zip(range(4),range(5)):
	print i,j
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
import sys
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
xtag[14]
xtagposunknostop[14]
xtagposunknostopmerge[14]
xtagposunknopunct[14]
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'tb')
xclean[1706]
x[1706]
x[1706]
x[1706]
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
len(sw)
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
get_ipython().magic(u'cpaste')
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i
i=0
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i=1
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i=2
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i=4
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i=5
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i=50
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
i=500
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
xtagposwithstop[:5]
xtagposwithstop[5:10]
xtagposwithstop[10:15]
xtagposwithstop[15:20]
xtagposwithstop[18]
i=18
xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
xtagposunknostop[i],xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
get_ipython().magic(u'pwd ')
get_ipython().magic(u'save multi_word_data_gen_3 1-547')
i=18
xtagposunknostop[i],xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
xtagposunknostopmerge=[]
for tlist in xtagposunknostop[i]:
    flag=True
    l=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                l.append(merge_entity(tlist[i],tlist[i+1]))
                flag=True
                if i==len(tlist)-2:
                	isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
        	l.append(tlist[-1])
        tlist=l
        l=[]
    xtagposunknostopmerge.append(tlist)
xtagposunknostopmerge
xtagposunknostopmerge=[]
for tlist in xtagposunknostop:
    flag=True
    l=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                l.append(merge_entity(tlist[i],tlist[i+1]))
                flag=True
                if i==len(tlist)-2:
                	isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
        	l.append(tlist[-1])
        tlist=l
        l=[]
    xtagposunknostopmerge.append(tlist)
xtagposwithstop=[]
for i in range(len(xtagposunknopunct)):
	l1=xtagposunknostopmerge[i]
	l2=xtagposunknopunct[i]
	ind=[]
	q=0
	for j in range(len(l1)-1):
		try:
			p,q=search_l2(l2[q:],l1[j][0],l1[j+1][0],q)
		except:
			print 'i='+str(i)
			print l1
			print l2
			sys.exit()
		if j==0 and p>0:
			ind.append((0,p))
		ind.append((p,q))
	print 'i='+str(i)
	print ind
	l3=[l2[0]]
	for k,v in ind:
		allstop=True
		slist=[]
		j=k+1
		while j<=v-1:
			slist.append(l2[j])
			allstop = allstop and (l2[j][0] in sw)
			j+=1
		if allstop:
			l3.extend(slist)
		l3.append(l2[v])
	xtagposwithstop.append(l3)
i=18
xtagposunknostop[i],xtagposunknostopmerge[i],xtagposunknopunct[i],xtagposwithstop[i]
tlist=[(u'PERSON', u'person', u'NOUN', u'NN'),
  (u'UNK', u'fiction', u'PROPN', u'NNP'),
  (u'film', u'film', u'NOUN', u'NN')]
flag=True
l=[]
while flag:
    flag=False
    isend=False
    for i in range(len(tlist)-1):
        if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
            l.append(merge_entity(tlist[i],tlist[i+1]))
            flag=True
            if i==len(tlist)-2:
            	isend=True
        else:
            l.append(tlist[i])
            continue
        for e in tlist[i+2:-1]:
            l.append(e)
        break
    if len(tlist) < 2 or not isend:
    	l.append(tlist[-1])
    tlist=l
    l=[]
tlist
xtagposunknostop[18]
xtagposunknopunct[18]
xtagposunknostop[18]
def search(l2,a,b,offset):
	ai,bi=0,0
	for x in range(len(l2)):
		if l2[x][0]==a:
			ai=x
			break
	for y in range(len(l2)):
		if y<=ai:
			continue
		if l2[y][0]==b:
			bi=y
			break
	assert ai<bi
	return ai+offset,bi+offset
xtagposunknostopmerge=[]
xtagposwithstop=[]
for j in range(len(xtagposunknopunct)):
	tlist=xtagposunknostop[j]
	l2=xtagposunknopunct[j]
    flag=True
    l=[]
    q=0
    ind=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
            	ment=merge_entity(tlist[i],tlist[i+1])
                l.append(ment)
                p,q=search(l2[q:],tlist[i][0],tlist[i+1][0],q)
				ind.append((p,q,ment))
		        flag=True
                if i==len(tlist)-2:
                	isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
        	l.append(tlist[-1])
        tlist=l
        l=[]
    l3=[]
    for i in range(len(ind)):
    	p,q,ment=ind[i][0],ind[i][1],ind[i][2]
    	if i==0 and p>0:
    		l3.append(l2[:p])
    	l3.append(ment)
    	l3.append(l2[q+1:])
    if not ind:
    	xtagposwithstop.append(l2)
    else
    	xtagposwithstop.append(l3)
    xtagposunknostopmerge.append(tlist)
xtagposunknostopmerge=[]
xtagposwithstop=[]
for j in range(len(xtagposunknopunct)):
    tlist=xtagposunknostop[j]
    l2=xtagposunknopunct[j]
    flag=True
    l=[]
    q=0
    ind=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                ment=merge_entity(tlist[i],tlist[i+1])
                l.append(ment)
                p,q=search(l2[q:],tlist[i][0],tlist[i+1][0],q)
                ind.append((p,q,ment))
                flag=True
                if i==len(tlist)-2:
                    isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
            l.append(tlist[-1])
        tlist=l
        l=[]
    l3=[]
    for i in range(len(ind)):
        p,q,ment=ind[i][0],ind[i][1],ind[i][2]
        if i==0 and p>0:
            l3.append(l2[:p])
        l3.append(ment)
        l3.append(l2[q+1:])
    if not ind:
        xtagposwithstop.append(l2)
    else
        xtagposwithstop.append(l3)
    xtagposunknostopmerge.append(tlist)
xtagposunknostopmerge=[]
xtagposwithstop=[]
for j in range(len(xtagposunknopunct)):
    tlist=xtagposunknostop[j]
    l2=xtagposunknopunct[j]
    flag=True
    l=[]
    q=0
    ind=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                ment=merge_entity(tlist[i],tlist[i+1])
                l.append(ment)
                p,q=search(l2[q:],tlist[i][0],tlist[i+1][0],q)
                ind.append((p,q,ment))
                flag=True
                if i==len(tlist)-2:
                    isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
            l.append(tlist[-1])
        tlist=l
        l=[]
    l3=[]
    for i in range(len(ind)):
        p,q,ment=ind[i][0],ind[i][1],ind[i][2]
        if i==0 and p>0:
            l3.append(l2[:p])
        l3.append(ment)
        l3.append(l2[q+1:])
    if not ind:
        xtagposwithstop.append(l2)
    else:
        xtagposwithstop.append(l3)
    xtagposunknostopmerge.append(tlist)
xtagposunknostopmerge=[]
xtagposwithstop=[]
for j in range(len(xtagposunknopunct)):
    tlist=xtagposunknostop[j]
    l2=xtagposunknopunct[j]
    flag=True
    l=[]
    q=0
    ind=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                ment=merge_entity(tlist[i],tlist[i+1])
                l.append(ment)
                try:
                    p,q=search(l2[q:],tlist[i][0],tlist[i+1][0],q)
                except:
                    print 'j='+str(j)
                    print tlist
                    print l2
                    sys.exit()
                ind.append((p,q,ment))
                flag=True
                if i==len(tlist)-2:
                    isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
            l.append(tlist[-1])
        tlist=l
        l=[]
    l3=[]
    for i in range(len(ind)):
        p,q,ment=ind[i][0],ind[i][1],ind[i][2]
        if i==0 and p>0:
            l3.append(l2[:p])
        l3.append(ment)
        l3.append(l2[q+1:])
    if not ind:
        xtagposwithstop.append(l2)
    else:
        xtagposwithstop.append(l3)
    xtagposunknostopmerge.append(tlist)
def search(l2,a,b,offset):
    ai,bi=0,0
    for x in range(len(l2)):
        if l2[x][0]==a:
            ai=x
            break
    for y in range(len(l2)):
        if y<=ai:
            continue
        if l2[y][0]==b:
            bi=y
            break
    print l2
    print a,b
    print offset
    print ai,bi
    assert ai<bi
    return ai+offset,bi+offset
for j in range(len(xtagposunknopunct)):
    tlist=xtagposunknostop[j]
    l2=xtagposunknopunct[j]
    flag=True
    l=[]
    q=0
    ind=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                ment=merge_entity(tlist[i],tlist[i+1])
                l.append(ment)
                try:
                    p,q=search(l2[q:],tlist[i][0],tlist[i+1][0],q)
                except:
                    print 'j='+str(j)
                    print tlist
                    print l2
                    sys.exit()
                ind.append((p,q,ment))
                flag=True
                if i==len(tlist)-2:
                    isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
            l.append(tlist[-1])
        tlist=l
        l=[]
    l3=[]
    for i in range(len(ind)):
        p,q,ment=ind[i][0],ind[i][1],ind[i][2]
        if i==0 and p>0:
            l3.append(l2[:p])
        l3.append(ment)
        l3.append(l2[q+1:])
    if not ind:
        xtagposwithstop.append(l2)
    else:
        xtagposwithstop.append(l3)
    xtagposunknostopmerge.append(tlist)
get_ipython().magic(u'tb')
xtagposunknostopmerge=[]
xtagposwithstop=[]
for j in range(len(xtagposunknopunct)):
    tlist=xtagposunknostop[j]
    l2=xtagposunknopunct[j]
    flag=True
    l=[]
    q=0
    ind=[]
    while flag:
        flag=False
        isend=False
        for i in range(len(tlist)-1):
            if tlist[i][0] in spacylist and tlist[i+1][0] in spacylist and (tlist[i][0]==u'UNK' or tlist[i+1][0]==u'UNK'):
                ment=merge_entity(tlist[i],tlist[i+1])
                l.append(ment)
                try:
                    p,q=search(l2[q:],tlist[i][0],tlist[i+1][0],q)
                except:
                    print 'j='+str(j)
                    print tlist
                    print l2
                    print tlist[i]
                    print tlist[i+1]
                    sys.exit()
                ind.append((p,q,ment))
                flag=True
                if i==len(tlist)-2:
                    isend=True
            else:
                l.append(tlist[i])
                continue
            for e in tlist[i+2:-1]:
                l.append(e)
            break
        if len(tlist) < 2 or not isend:
            l.append(tlist[-1])
        tlist=l
        l=[]
    l3=[]
    for i in range(len(ind)):
        p,q,ment=ind[i][0],ind[i][1],ind[i][2]
        if i==0 and p>0:
            l3.append(l2[:p])
        l3.append(ment)
        l3.append(l2[q+1:])
    if not ind:
        xtagposwithstop.append(l2)
    else:
        xtagposwithstop.append(l3)
    xtagposunknostopmerge.append(tlist)
get_ipython().magic(u'tb')
def merge_entity(a,b):
    x,z,w=a[0],a[2],a[3]
    if a[0]==u'UNK':
        x,z,w=b[0],b[2],b[3]
    y=a[1]+'_'+b[1]
    return (x,y,z,w)
merge_entity((u'DATE', u'date_wta', u'NOUN', u'NN'),(u'UNK', u'finals', u'PROPN', u'NNPS'))
xtag[:30]
