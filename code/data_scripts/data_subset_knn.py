# coding: utf-8
import sys
f=open(sys.argv[1],'r')
x=f.readlines()
col1=[t.split('\t')[0] for t in x]
col2=[t.split('\t')[1] for t in x]
col2rels=[t.split(' || ')[1] for t in col2]
from collections import Counter
col2relsmap=Counter(col2rels)
col1fullmap={}
for i in range(len(col1)):
    if col1[i] not in col1fullmap:
        col1fullmap[col1[i]]=[]
    col1fullmap[col1[i]].append(col2rels[i])
col1countmap={}
for k,v in col1fullmap.items():
    col1countmap[k]=Counter(v)
for k,v in col1countmap.items():
    for t in v.keys():
        v[t]=col2relsmap[t]
    col1countmap[k]=v
    
col2relssubset=[]
for k,v in col1countmap.items():
    col2relssubset.extend(v.most_common(10))
    
relssub=Counter(dict(col2relssubset).keys())
xsub=[x[i] for i in range(len(x)) if col2rels[i] in relssub]
fout=open(sys.argv[2],'w')
fout.writelines(xsub)
fout.close()
