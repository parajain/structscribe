import sys
import re
import spacy
import cPickle as cp
import en
from collections import Counter
nlp = spacy.load('en_core_web_sm')
spacylist=['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','UNK', 'FAC']

#puncts='!"#$%&\()*+,-./:;<=>?@[\\]^`{|}~'
puncts='"&\*+-/:<=>?@\\^`|~'
def test_re(s):
    regex = re.compile('[%s]' % re.escape(puncts))
    return regex.sub('', s)
def replace_string(s):
    return s.replace('-',' ').replace('\'',' \'')

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
def ner_tag(xlist):
        xspacytags=[[(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in document.ents] for document in nlp.pipe(xlist, n_threads = 4)]
        xtag=[]
        for i in range(len(xlist)):
            s=xlist[i]
            pairs,tags=return_range(xspacytags[i])
            xtag.append((s,substring(s,pairs,tags)))
        return xtag

def add_unk(xtagpos):
    xtagposunk=[]
    for tlist in xtagpos:
        l=[]
        for a,b,c,d,e,f in tlist:
            if d==u'NNP' or d==u'NNPS' or c==u'PROPN':
                if a not in spacylist:
                    a=u'UNK'
            l.append((a,b,c,d,e,f))
        xtagposunk.append(l)
    return xtagposunk

def find_entity_loc(xtagparseunk):
    xspacytagloc=[]
    for tlist in xtagparseunk:
        l=[]
        for i in range(len(tlist)):
            if tlist[i][0] in spacylist:
                l.append(i)
        xspacytagloc.append(l)
    return xspacytagloc

def gen_3_tuple(xspacytagloc):
    x3tuplist=[]
    for j in range(len(xspacytagloc)):
        tlist=xspacytagloc[j]
        l=[]
        if len(tlist) < 3:
            l=[(j,tlist)]
        else:
            for i in range(len(tlist)-2):
                l.append((j,tlist[i:i+3]))
        x3tuplist.append(l)
    return x3tuplist

def is_valid_tuple(xtagparseunk,index,ilist):
    if len(ilist) < 2:
        return False
    tlist=xtagparseunk[index]
    tags=[tlist[k][0] for k in ilist]
    #has only one type of spacy tag - rest unk or all unk
    validtagcombo=(len(ilist)-Counter(tags)[u'UNK']) <= 1
    st,ed=ilist[0]+1,ilist[-1]-1
    if st > ed:
        return validtagcombo
    # no punct in between
    #only stopwords in between
    # no ROOT dep word in between
    isroot=False
    ispunct=False
    onlystop=True
    for e in tlist[st:ed+1]:
        if e[0] in spacylist:
            continue
        if e[2]==u'PUNCT':
            ispunct=True
        if not e[4]:
            onlystop=False
        if e[5]==u'ROOT':
            isroot=True
    return validtagcombo and not ispunct and not isroot and onlystop

def gen_2_tuple(xspacytagloc):
    x2tuplist=[]
    for j in range(len(xspacytagloc)):
        tlist=xspacytagloc[j]
        l=[]
        if len(tlist) < 2:
            l=[(j,tlist)]
        else:
            for i in range(len(tlist)-1):
                l.append((j,tlist[i:i+2]))
        x2tuplist.append(l)
    return x2tuplist

'''
def gen_all23_tuple(xtagparseunk,xspacytagloc):
    xtuplist=[]
    for j in range(len(xspacytagloc)):
        tlist=xspacytagloc[j]
        if len(tlist) < 1:
            continue
        l=[]
        if len(tlist) < 3 and is_valid_tuple(xtagparseunk,j,tlist):
            l=[(j,tlist)]
        else:
            for i in range(len(tlist)-2):
                if is_valid_tuple(xtagparseunk,j,tlist[i:i+3]):
                    l.append(tlist[i:i+3])
                else:
                    if is_valid_tuple(xtagparseunk,j,tlist[i:i+2]):
                        l.append(tlist[i:i+2])
                    elif is_valid_tuple(xtagparseunk,j,tlist[i+1:i+3]):
                        l.append(tlist[i+1:i+3])
        if len(l) > 0:
            xtuplist.append((j,l))
    return xtuplist

xtuplist = gen_all23_tuple(xtagparseunk,xspacytagloc)
'''

def gen_all23_tuple(xtagparseunk,xspacytagloc):
    xtuplist={}
    for j in range(len(xspacytagloc)):
        tlist=xspacytagloc[j]
        if len(tlist) < 1:
            continue
        l=[]
        if len(tlist) < 3 and is_valid_tuple(xtagparseunk,j,tlist):
            l=[tlist]
        else:
            for i in range(len(tlist)-2):
                if is_valid_tuple(xtagparseunk,j,tlist[i:i+3]):
                    l.append(tlist[i:i+3])
                else:
                    if is_valid_tuple(xtagparseunk,j,tlist[i:i+2]):
                        l.append(tlist[i:i+2])
                    elif is_valid_tuple(xtagparseunk,j,tlist[i+1:i+3]):
                        l.append(tlist[i+1:i+3])
        if len(l) < 1:
            continue

        #detect overlap and remove redundancy
        def remove_redundant(l):
            final_l=[]
            contnext =False
            if len(l) < 2:
                return l
            for num in range(len(l)-1):
                l1=l[num]
                l2=l[num+1]
                if contnext :
                    contnext =False
                    if num==len(l)-2:
                        final_l.append(l2)
                    continue
                s1,e1=l1[0],l1[-1]
                s2,e2=l2[0],l2[-1]
                #l1 contained in l2
                if s2<=s1 and e2>=e1:
                    final_l.append(l2)
                    contnext =True
                #l2 contained in l1
                elif s1<=s2 and e1>=e2:
                    final_l.append(l1)
                    contnext =True
                #just overlap no containment
                elif e1>=s2:
                    final_l.append(l1)
                    contnext =True
                else:
                    final_l.append(l1)
                    if num==len(l)-2:
                        final_l.append(l2)
            return final_l

        l=remove_redundant(l)
        final_l=remove_redundant(l)
        xtuplist[j]=final_l
    return xtuplist

def merge_entity_tokens(xtagparseunk,xtuplist):
    xout = []
    for i in range(len(xtagparseunk)):
        if i not in xtuplist:
            xout.append(xtagparseunk[i])
            continue
        l=xtuplist[i]
        outl=[]
        prevst,preved=-1,-1
        for window in l:
            tag=u'UNK'
            postag=u'NOUN'
            penntag=u'NNP'
            dep=u'nsubj'
            for j in window:
                if xtagparseunk[i][j][0]!=u'UNK':
                    tag=xtagparseunk[i][j][0]
                    postag=xtagparseunk[i][j][2]
                    penntag=xtagparseunk[i][j][3]
                    dep=xtagparseunk[i][j][5]
            st,ed = window[0],window[-1]
            string=[]
            for k in range(st,ed+1):
                string.append(xtagparseunk[i][k][1])
            outl.extend(xtagparseunk[i][preved+1:st])
            outl.append((tag,'_'.join(string),postag,penntag,False,dep))
            prevst,preved=st,ed
        if preved<len(xtagparseunk[i])-1:
            outl.extend(xtagparseunk[i][preved+1:])
        xout.append(outl)
    return xout

def remove_cap_determiners(xmerged):
    xout=[]
    for tlist in xmerged:
        l=[]
        for i in range(len(tlist)-1):
            t=tlist[i]
            if t[2]==u'DET' and not t[0].islower() and (not t[0].isupper() or len(t[0])<2) and tlist[i+1][0] in spacylist:
                continue
            l.append(t)
        l.append(tlist[-1])
        xout.append(l)
    return xout

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

def remove_punct(xtagparse):
    xout=[]
    for t in xtagparse:
        l=[]
        for tup in t:
            if tup[2]==u'PUNCT':
                continue
            l.append(tup)
        xout.append(l)
    return xout


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

'''
def get_output1(s):
    sinput=transform_input(s)
    mout=model1.generate(sinput[0])
    norm_g=normalize_string(s,mout)
    return replace_entities(s,sinput[1],norm_g[0])[1]
'''

def create_entity_map(s, stagged):
    d=[]
    s=' '+s+' '
    for i in range(len(stagged[0])):
        e = stagged[0][i]
        if e[0] in spacylist:
            continue
        parts = s.split(' '+e[0]+' ', 1)
        if parts[0].strip()!='':
            d.append({stagged[0][i-1][0]:parts[0].strip().rstrip('.')})
        s=' '+' '.join(parts[1:])
    if len(s.strip())>0 and stagged[0][-1][0].strip()!='.':
        d.append({stagged[0][-1][0]: s.strip().rstrip('.')})
    return d

def replace_entities(string, sprefinal, words):
    entmap=create_entity_map(string, sprefinal)
    index=0
    newwords=[]
    for e in words:
        if e not in spacylist:
            newwords.append(e)
            continue
        if index<len(entmap) and e in entmap[index]:
            newwords.append(entmap[index][e])
            index+=1
    return newwords,' '.join(newwords)

def transform_input(s, ner=True):
    sclean=s.decode('unicode-escape').strip()
    scleannopunct=test_re(replace_string(sclean))
    sprefinal = []
    if ner:
        stag = ner_tag([scleannopunct])
        stagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(s)] for k,s in stag]
        stagparseunk = add_unk(stagparse)
        sspacytagloc = find_entity_loc(stagparseunk)
        stuplist = gen_all23_tuple(stagparseunk, sspacytagloc)
        smerged = merge_entity_tokens(stagparseunk, stuplist)
        sprefinal = remove_cap_determiners(smerged)
        sfinal = remove_punct(sprefinal)
    else:
        sfinal=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(k)] for k in [scleannopunct]]
    sfinalnostop = remove_stop(sfinal)
    sin1 = create_input(sfinalnostop)
    return remove_caps(sin1[0]), sprefinal

def transform_input_list(slist, ner=True):
    sclean=[s.decode('unicode-escape').strip() for s in slist]
    scleannopunct=[test_re(replace_string(s)) for s in sclean]
    sprefinal = []
    if ner:
        stag = ner_tag(scleannopunct)
        staglist = [s for k,s in stag]
        stagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in document]
                   for document in nlp.pipe(staglist, n_threads = 4)]
        stagparseunk = add_unk(stagparse)
        sspacytagloc = find_entity_loc(stagparseunk)
        stuplist = gen_all23_tuple(stagparseunk, sspacytagloc)
        smerged = merge_entity_tokens(stagparseunk, stuplist)
        sprefinal = remove_cap_determiners(smerged)
        sfinal = remove_punct(sprefinal)
    else:
        sfinal=[[(token.text, token.lemma_, token.pos_, token.tag_, token.is_stop, token.dep_) for token in document]
                     for document in nlp.pipe(scleannopunct, n_threads = 4)]
    sfinalnostop = remove_stop(sfinal)
    sin1 = create_input(sfinalnostop)
    return [remove_caps(s) for s in sin1], sprefinal


def create_data(filename,threshold,outprefix):
    print 'Reading line by line....'
    f=open(filename,'r')
    x=f.readlines()
    xclean=[s.decode('unicode-escape').strip() for s in x]
    print 'Clean data generated....'
    print 'Removing some punctuations....'
    xcleannopunct=[test_re(replace_string(s)) for s in xclean]
    print 'Perform NER tagging using spacy....'
    xtag=ner_tag(xcleannopunct)
    print 'Parsing using spacy....'
    xtagparse=[[(token.text,token.lemma_,token.pos_,token.tag_,token.is_stop,token.dep_) for token in nlp(s)] for k,s in xtag]
    print 'Replacing untagged Proper nouns with UNK....'
    xtagparseunk = add_unk(xtagparse)
    print 'Finding entity locations to be merged....'
    xspacytagloc = find_entity_loc(xtagparseunk)
    xtuplist = gen_all23_tuple(xtagparseunk, xspacytagloc)
    print 'Merge untagged entity words....'
    xmerged = merge_entity_tokens(xtagparseunk, xtuplist)
    print 'Removing preceding capital determiners....'
    xfinal = remove_cap_determiners(xmerged)
    print 'Removing all punctuations....'
    xfinal = remove_punct(xfinal)
    print 'Removing stopwords....'
    xfinalnostop=remove_stop(xfinal)
    print 'Creating input and output formats....'
    xin1=create_input(xfinalnostop)
    xout1=create_output(xfinal)
    print 'Inserting capitalization information....'
    xin1=[remove_caps(s) for s in xin1]
    xout1=[remove_caps(s) for s in xout1]
    print 'Filtering out tagged sentences (>%d words)...' % threshold
    xindices = [i for i in range(len(xtag)) if len(xtag[i][1].split()) <= threshold]
    print 'Dumping all processed data....'
    xdump=(xclean,xtag,xtagparse,xtuplist,xfinal,xfinalnostop,xin1,xout1,xindices)
    fout=open(outprefix+'_merge_dump.pkl','wb')
    cp.dump(xdump,fout)
    fout.close()
    xin1=[xin1[i] for i in xindices]
    xout1=[xout1[i] for i in xindices]
    print 'Dumping seq2seq data...'
    f1=open(outprefix+'_merge.src','w')
    for e in xin1:
            f1.write(e.encode('unicode-escape')+'\n')
    f1.close()
    f2=open(outprefix+'_merge.tgt','w')
    for e in xout1:
            f2.write(e.encode('unicode-escape')+'\n')
    f2.close()

if __name__ == '__main__':
    #s='Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.\r\n'
    #print transform_input(s)
    create_data(sys.argv[1],int(sys.argv[2]),sys.argv[3])
