# coding: utf-8
import sys
dirname=sys.argv[1]
trainpc=float(sys.argv[2])
validpc=float(sys.argv[3])
testpc=float(sys.argv[4])
assert trainpc+validpc+testpc == 1
src=dirname+'/seq2seq.src'
tgt=dirname+'/seq2seq.tgt'
f1=open(src,'r')
f2=open(tgt,'r')
x1=f1.readlines()
x2=f2.readlines()
import numpy as np
values=np.random.uniform(low=0,high=1,size=len(x1))
tr=[i for i in range(len(x1)) if values[i]<trainpc]
va=[i for i in range(len(x1)) if values[i]>=trainpc and values[i]<trainpc+validpc]
te=[i for i in range(len(x1)) if values[i]>=trainpc+validpc and values[i]<=1]
x1tr=[x1[i] for i in tr]
x2tr=[x2[i] for i in tr]
f1o=open(src+'.train','w')
f2o=open(tgt+'.train','w')
f1o.writelines(x1tr)
f2o.writelines(x2tr)
x1va=[x1[i] for i in va]
x2va=[x2[i] for i in va]
f1o.close()
f2o.close()
f1o=open(src+'.valid','w')
f2o=open(tgt+'.valid','w')
f1o.writelines(x1va)
f2o.writelines(x2va)
f1o.close()
f2o.close()
x1te=[x1[i] for i in te]
x2te=[x2[i] for i in te]
f1o=open(src+'.test','w')
f2o=open(tgt+'.test','w')
f1o.writelines(x1te)
f2o.writelines(x2te)
f1o.close()
f2o.close()
