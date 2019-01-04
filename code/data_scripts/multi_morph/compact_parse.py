import sys


clauses = ["acl","relcl","advcl","csubj","csubjpass","xcomp","rcmod","ccomp"]
	
dat = {"ROOT":[]}

def split_list(l):
	l = sorted(l)
	dl = []
	templ = []
	prev_l = -1
	for ll in l:
		if prev_l == -1:
			prev_l=ll
			templ.append(ll)
			continue
		if ll-prev_l>1:
			dl.append(templ)
			templ = []
			templ.append(ll)
		else:
			templ.append(ll)
		prev_l = ll
	dl.append(templ)
	return dl


def find_indices(node,flag,parent):
	global dat
	if flag ==0:
		dat = {"ROOT":[]}
		flag = 1
	indxs = dat.get(parent,[])
	indxs.append(int(node.i))
	dat[parent] = indxs 
	if node.children:
		for child in node.children:
			if child.dep_ in clauses:
				find_indices(child,1,"ROOT")
			elif "subj" in child.dep_ and parent=="ROOT":
				find_indices(child,1,child.dep_)
			elif "obj" in child.dep_ and parent=="ROOT":
				find_indices(child,1,child.dep_)
			elif "attr" in child.dep_ and parent=="ROOT":
				find_indices(child,1,child.dep_)
			elif "oprd" in child.dep_ and parent=="ROOT":
				find_indices(child,1,child.dep_)
			#elif "prep" in child.dep_ and parent=="ROOT":
				#find_indices(child,1,child.dep_)
			elif "punct" in child.dep_ and parent=="ROOT":
				find_indices(child,1,child.dep_) 
			else:
				find_indices(child,1,parent)
	
	return

def spans_to_be_merged():
	global dat
	new_dat = {}
	indices = []
	for ks in dat.keys():
		l = dat[ks]
		dl = split_list(l)
		new_dat[ks] = dl
	for ks in new_dat.keys():
		if ks == "ROOT":
			continue
		dl = new_dat[ks]
		for ddl in dl:
			indices.append(ddl)
	return indices	


def compact_tree(document, dat):
	new_dat = {}
	spans = []
	for ks in dat.keys():
		l = dat[ks]
		dl = split_list(l)
		new_dat[ks] = dl
	#print new_dat
	for ks in new_dat.keys():
		if ks == "ROOT":
			continue
		dl = new_dat[ks]
		for ddl in dl:
			span = document[ddl[0]:ddl[-1]+1]
			spans.append(span)#tag=ks,lemma=span.text,ent_type=u"MERGED")
	for s in spans:
		s.merge()
		
	return document


def compact_parser_document(document):
	all_indices = []
	for sent in document.sents:
		root  = sent.root
		find_indices(root,0,"ROOT")
		indices = spans_to_be_merged()
		all_indices+=indices
	
	spans = []
	for ddl in all_indices:
		span = document[ddl[0]:ddl[-1]+1]
		spans.append(span)
	for s in spans:
		s.merge()
	return document

if __name__=="__main__":
	import spacy
	nlp = spacy.load('en')
	print "Enter sentences"
	s = raw_input()
	s = s.decode('unicode-escape')
	doc = nlp(s)
	returned_doc = compact_parser_document(doc)
	print [(x.dep_,x.pos_) for x in returned_doc]
	print [x.text for x in returned_doc]
