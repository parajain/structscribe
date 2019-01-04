
import sys
from itertools import izip
import spacy,cPickle,codecs
from nltk.stem import WordNetLemmatizer


NER = False
lemmatizer = WordNetLemmatizer()

nlp = spacy.load("en_core_web_lg")

typ = sys.argv[1]

data = {}
morph = {}
print "Loading morphosemantic respurces..."
data = {}
with open("catvars.dat") as f:
	data = cPickle.load(f)
	
with open("morpho_symantic.txt") as f3:
	for line in f3:
		line = line.strip()
		l = line.split(":")
		d = morph.get(l[0],[])
		d.append(l[0]) 
		d.append(l[1])
		morph[l[0]] = d
	


all_words = []
with open("all.txt","r") as f1:
	for line in f1:
		line = line.strip()
		all_words.append(line.lower())
print "Loaded morphosemantic respurces..."		


def get_root_with_vars(rel):
	rel = rel.replace("has ","") .replace("is ","").strip()
	
	doc = nlp(rel)
	var = []
	
	if len(rel.split())==1:
		vrb = rel
		vrb = lemmatizer.lemmatize(vrb,"v")
		morph_semantics = data.get(vrb,[vrb])
		morph_semantics1 = morph.get(vrb,[vrb])
		var = list(set(morph_semantics+morph_semantics1))
		return var
		
	for tok in doc:
		if "ROOT" in tok.dep_:
			vrb = tok.text
			vrb = lemmatizer.lemmatize(vrb,"v")
			morph_semantics = data.get(vrb,[vrb])
			morph_semantics1 = morph.get(vrb,[vrb])
			var = list(set(morph_semantics+morph_semantics1))
	return var

output = codecs.open(typ+"_classifier_data.tsv","w","utf-8")
output.write("Input\tTuple(Class)\tSentence\n")
with open(typ+".input") as textfile1, open(typ+".output") as textfile2: 
	for x, y in izip(textfile1, textfile2):
		x = x.strip()
		y = y.strip()
		x = x.decode('unicode-escape')
		y = y.decode('unicode-escape')
		inf = x.split("||")
		
		if NER:
			inf1 = nlp(inf[0].strip())
			inf2 = nlp(inf[2].strip())
			
			tup = ""
			
			ent1 = ""
			ent2 = ""
			
			if inf1.ents:
				ent1 = str(inf1.ents[0].label_)
				#print ent1
			else:
				for tok in inf1:
					if "ROOT" in tok.dep_:
						ent1 = tok.text
						if ent1.lower() not in all_words:
							ent1 = "UNK"
			if inf2.ents:
				ent2 = str(inf2.ents[0].label_)
				
			else:
				for tok in inf2:
					if "ROOT" in tok.dep_:
						ent2 = tok.text
						if ent2.lower() not in all_words:
							ent2 = "UNK"
		else:
			
			ent1 = inf[0].strip()
			ent2 = inf[2].strip()
			
			
		if ent1!="" and ent2!="":
			x_new = x.replace(inf[0].strip(),ent1).replace(inf[2].strip(),ent2)
			y_new = y.replace(inf[0].strip(),ent1).replace(inf[2].strip(),ent2)
			
			#print inf[1].strip()
			var = get_root_with_vars(inf[1].strip())
			#print var
			if var !=[]:
				for vv in var:
					tup = ent1+" "+vv+" "+ent2
					towrite = tup+"\t"+x_new+"\t"+y_new+"\n"
					#print towrite
					output.write(towrite)
			
output.close()




