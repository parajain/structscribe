import sys, spacy

#takes file for type <Input>, <Tuple>, <Sentence>

fin = sys.argv[1]
outdir = sys.argv[2]

nlp = spacy.load("en_core_web_lg")


s2s_input = open(outdir+"/seq2seq.src","w")
s2s_output = open(outdir+"/seq2seq.tgt","w")

classifier = open(outdir+"/small_classifier.tsv","w")
classifier.write("Input\tLabel\n")


classes = {}
with open (fin) as f:
	for line in f:
		line = line.strip()
		inf = line.split("\t")
		
		if len(inf)!=3:
			print "Not in format: "+ line
			continue
		
		inp = inf[0].strip()
		tup = inf[1].strip()
		sent = inf[2].strip()
		
		i2inf = tup.split("||")
		
		if len(i2inf)!=3:
			print "Not in format: "+ line
			continue
		
		rel = i2inf[1].strip()
		
		rel = rel.decode('unicode-escape')
		doc = nlp("He "+rel)
		
		verbs = 0
		prep = 0
		
		for tok in doc:
			if str(tok.pos_)=="VERB":
				verbs+=1
			if str(tok.pos_)=="ADP":
				prep+=1
		
		if verbs==0:
			print " No verb for "+rel+" "+str(map(lambda x:x.pos_,doc))
			continue
		
		cls = "VERB"
		s2s_in = inp
		s2s_out = sent
		
		if verbs>1:
			if "is " in rel[:4]:
				cls += "_IS"
				s2s_in+=" IS"
			elif "has " in rel[:5]:
				cls += "_HAS"
				s2s_in+=" HAS"
		elif verbs==1:	
			if "is " in rel[:4]:
				tmp = inp.split()
				cls = "NULL_IS"
				s2s_in = tmp[0]+" NULL "+tmp[2]+" IS"
			elif "has " in rel[:5]:
				tmp = inp.split()
				cls = "NULL_HAS" 
				s2s_in = tmp[0]+" NULL "+tmp[2]+" HAS"
				
		if prep>0:
			cls+="_PREP"
			s2s_in+=" PREP"
		
		
		classes[cls] = 1
		
		classifier.write(inp+"\t"+cls+"\n")
		s2s_input.write(s2s_in+"\n")
		s2s_output.write(s2s_out+"\n")

print "classes = "+str(classes.keys())+" count = "+str(len(classes.keys()))

s2s_input.close()
s2s_output.close()
classifier.close()
