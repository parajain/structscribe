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
