# coding: utf-8
import io
import unicodedata
import sys
f=io.open(sys.argv[1],'r',encoding="utf-8")
x=f.readlines()
len(x)
print 'Removing unicode...'
x=[unicodedata.normalize('NFKD', t).encode('ascii','ignore') for t in x]
len(x)
print 'Removing longer relations...'
rels=[e.split(' || ')[1] for e in x]
xlen=[x[i] for i in range(len(x)) if len(rels[i])<=int(sys.argv[2])]
len(xlen)
from collections import Counter

print 'Counting relations...'
cx=Counter([t.split(' || ')[1] for t in x])
cxlen=Counter([t.split(' || ')[1] for t in xlen])
set(cx.viewvalues())
set(cxlen.viewvalues())
cxlen['is located in']
xlenrels=[t.split(' || ')[1] for t in xlen]
len(xlenrels)
print 'Removing relations with less frequency...'
xlenfreq=[xlen[i] for i in range(len(xlen)) if cx[xlenrels[i]]>int(sys.argv[3])]
len(xlenfreq)
cxlenfreq=Counter([t.split(' || ')[1] for t in xlenfreq])
set(cxlenfreq.viewvalues())
spacylist=['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','UNK']

print 'Removing relations without valid DBPedia/spacy NER...'
col1=[t.split('\t')[0] for t in xlenfreq]
fout=open(sys.argv[4],'w')
fout.writelines(xlenfreq)
fout.close()
xlenfreqvalid=[xlenfreq[i] for i in range(len(xlenfreq)) if len(col1[i].split())==3 and col1[i].split()[0] in spacylist and col1[i].split()[2] in spacylist]
len(xlenfreqvalid)
fout=open(sys.argv[5],'w')
fout.writelines(xlenfreqvalid)
fout.close()
xlenfreqinvalid=[xlenfreq[i] for i in range(len(xlenfreq)) if len(col1[i].split())!=3 or col1[i].split()[0] not in spacylist or col1[i].split()[2] not in spacylist]
len(xlenfreqinvalid)
fout=open(sys.argv[6],'w')
fout.writelines(xlenfreqinvalid)
fout.close()
