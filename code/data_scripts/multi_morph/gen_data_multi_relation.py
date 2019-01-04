import sys
import re
import spacy
import cPickle as cp
import en

nlp = spacy.load('en_core_web_sm')
spacylist=['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','UNK', 'FAC']

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

def ner_tag(xlist):
    xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in document.ents] for document in nlp.pipe(xlist, n_threads = 4)]
    xtag=[]
    for i in range(len(xlist)):
        s=xlist[i]
        pairs,tags=return_range(xspacytags[i])
        xtag.append((s,substring(s,pairs,tags)))
    return xtag

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

def transform_input(s, ner=True):
    sclean=s.decode('unicode-escape').strip()
    scleannopunct=test_re(replace_string(sclean))
    if ner:
        stag = ner_tag([scleannopunct])
        stagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(s)] for k,s in stag]
    else:
        stagparse = [[(token.text, token.lemma_, token.pos_, token.tag_, token.is_stop, token.dep_) for token in nlp(k)]
                     for k in [scleannopunct]]
    stagparsenostop=remove_stop(stagparse)
    sin1=create_input(stagparsenostop)
    return remove_caps(sin1[0])

def transform_input_list(slist, ner=True):
    sclean=[s.decode('unicode-escape').strip() for s in slist]
    scleannopunct=[test_re(replace_string(s)) for s in sclean]
    if ner:
        stag = ner_tag(scleannopunct)
        staglist = [s for k,s in stag]
        stagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in document]
                   for document in nlp.pipe(staglist, n_threads = 4)]
    else:
        stagparse = [[(token.text, token.lemma_, token.pos_, token.tag_, token.is_stop, token.dep_) for token in document]
                     for document in nlp.pipe(scleannopunct, n_threads = 4)]
    stagparsenostop=remove_stop(stagparse)
    sin1=create_input(stagparsenostop)
    return [remove_caps(s) for s in sin1]


verbs=['MD', 'VB', 'VBD', 'VBN', 'VBP', 'VBG', 'VBZ', 'CAPS']
def normalize_string(s,o):
    olist=o.split(' ')
    l,words=[],[]
    for i in range(len(olist)-1):
        l.append(olist[i:i+2])
    l.append([olist[-1],''])
    for e in l:
        if e[0] in verbs:
            continue
        if e[1] in verbs:
            form=e[0]
            try:
                if e[1]=='VBD':
                    form=en.verb.past(form, person=3)
                elif e[1]=='VBG':
                    form=en.verb.present_participle(form)
                elif e[1]=='VBN':
                    form=en.verb.past_participle(form)
                elif e[1]=='VBP':
                    form=en.verb.present(form,person=2)
                elif e[1]=='VBZ':
                    form=en.verb.present(form,person=3)
                elif e[1]=='CAPS':
                    form=form[0].upper()+form[1:]
            except:
                swords=s.split(' ')
                if form not in swords:
                    x=s.split(form)
                    if len(x)>1:
                        suffix=x[1].split(' ')[0]
                        form = form+suffix
            words.append(form)
        else:
            words.append(e[0])
    return words, ' '.join(words)

def replace_entities(str, words):
    xlist=[test_re(replace_string(str.decode('unicode-escape').strip()))]
    xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in nlp(s).ents] for s in xlist]
    index=0
    newwords=[]
    for e in words:
        if e not in spacylist:
            newwords.append(e)
            continue
        while e != xspacytags[0][index][3] and index < len(xspacytags[0]):
            index+=1
        if e == xspacytags[0][index][3]:
            newwords.append(xspacytags[0][index][0])
            index+=1
    return newwords,' '.join(newwords)


def create_data(filename,threshold,outprefix):
    print 'Reading line by line....'
    f=open(filename,'r')
    x=f.readlines()
    xclean=[s.decode('unicode-escape').strip() for s in x]
    print 'Clean data generated....'
    print 'Removing punctuations....'
    xcleannopunct=[]
    xcleannopunct=[test_re(replace_string(s)) for s in xclean]
    print 'Perform NER tagging using spacy....'
    xtag=ner_tag(xcleannopunct)
    print 'Parsing using spacy....'
    xtagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(s)] for k,s in xtag]
    print 'Removing stopwords....'
    xtagparsenostop=remove_stop(xtagparse)
    print 'Creating input and output formats....'
    xin1=create_input(xtagparsenostop)
    xout1=create_output(xtagparse)
    print 'Inserting capitalization information....'
    xin1=[remove_caps(s) for s in xin1]
    xout1=[remove_caps(s) for s in xout1]
    print 'Filtering out tagged sentences (>%d words)...' % threshold
    xindices = [i for i in range(len(xtag)) if len(xtag[i][1].split()) <= threshold]
    print 'Dumping all processed data....'
    xdump=(xclean,xtag,xtagparse,xtagparsenostop,xin1,xout1,xindices)
    fout=open(outprefix+'_dump.pkl','wb')
    cp.dump(xdump,fout)
    fout.close()
    xin1=[xin1[i] for i in xindices]
    xout1=[xout1[i] for i in xindices]
    print 'Dumping seq2seq data...'
    f1=open(outprefix+'_simple.src','w')
    for e in xin1:
            f1.write(e.encode('unicode-escape')+'\n')
    f1.close()
    f2=open(outprefix+'_simple.tgt','w')
    for e in xout1:
            f2.write(e.encode('unicode-escape')+'\n')
    f2.close()

if __name__ == '__main__':
    #s='Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.\r\n'
    #print transform_input(s)
    create_data(sys.argv[1],int(sys.argv[2]),sys.argv[3])
