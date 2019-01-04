import re
import spacy
nlp = spacy.load('en_core_web_sm')

f=open('output_train.txt','r')
x=f.readlines()
xclean=[s.decode('unicode-escape').strip() for s in x]

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
    return s1+s[pairs[-1][0]:]

puncts='!"#$%&\()*+,-./:;<=>?@[\\]^`{|}~'
def test_re(s):
    regex = re.compile('[%s]' % re.escape(puncts))
    return regex.sub('', s)
def replace_string(s):
    return s.replace('-',' ').replace('\'',' \'')

xcleannopunct=[]
xcleannopunct=[test_re(replace_string(s)) for s in xclean]

def ner_tag(xlist):
	xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in nlp(s).ents] for s in xlist]
	xtag=[]
	for i in range(len(xlist)):
	    s=xlist[i]
	    pairs,tags=return_range(xspacytags[i])
	    xtag.append((s,substring(s,pairs,tags)))
	return xtag

xtag=ner_tag(xcleannopunct)

xtagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(s)] for k,s in xtag]
def remove_stop(xtagparse):
	xtagparsenostop=[]
	for t in xtagparse:
		l=[]
		for tup in t:
			if tup[4]:
				continue
			l.append(tup)
		xtagparsenostop.append(l)
	return xtagparsenostop
xtagparsenostop=remove_stop(xtagparse)

def create_input(xlist):
	inl=[]
	for t in xlist:
		l=[]
		for tup in t:
			l.extend([tup[0],tup[2]])
		inl.append(' '.join(l))
	return inl

def create_output(xlist):
	outl=[]
	for t in xlist:
		l=[]
		for tup in t:
			if tup[2]==u'VERB':
				l.extend([tup[1],tup[3]])
			else:
				l.append(tup[0])
		outl.append(' '.join(l))
	return outl

xin1=create_input(xtagparsenostop)
xout1=create_output(xtagparse)

def remove_caps(s):
    l=s.split(' ')
    ll=[]
    for e in l:
        if (not e.isupper() and not e.islower()) or (len(e)==1 and e.isupper()) :
            ll.append(e.lower())
            ll.append('CAPS')
        else:
            ll.append(e)
    return ' '.join(ll)

xin1=[remove_caps(s) for s in xin1]
xout1=[remove_caps(s) for s in xout1]

xindices = [i for i in range(len(xtag)) if len(xtag[i][1].split()) <= 10]
xin1=[xin1[i] for i in xindices]
xout1=[xout1[i] for i in xindices]

xdump1=(xin1,xout1)
fout=open('simple_tagged_output_train.pkl','wb')
import cPickle as cp
cp.dump(xdump1,fout)
fout.close()

def transform_input(s):
	sclean=s.decode('unicode-escape').strip()
	scleannopunct=test_re(replace_string(sclean))
	stag=ner_tag([scleannopunct])
	stagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(s)] for k,s in stag]
	stagparsenostop=remove_stop(stagparse)
	sin1=create_input(stagparsenostop)
	return remove_caps(sin1[0])

if __name__ == '__main__':
    s='Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.\r\n'
    print transform_input(s)
