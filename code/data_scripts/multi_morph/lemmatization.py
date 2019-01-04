# coding: utf-8
import spacy
nlp = spacy.load('en_core_web_sm')
f=open('output_train.txt')
x=f.readlines()
x
xclean=[e.strip() for e in x]
xclean
import spacy
nlp = spacy.load('en_core_web_sm')
xcleanlemmas = [[(token.text,token.lemma_,token.pos_) for token in nlp(s)] for s in xclean]
doc=nlp[xclean[0]]
doc=nlp(xclean[0])
xclean[0]
doc=nlp('Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.')
doc=nlp(unicode(xclean[0],'utf-8'))
doc
for token in doc:
    print token.text,token.lemma_,token.pos_
    
xcleanlemmas = [[(token.text,token.lemma_,token.pos_) for token in nlp(unicode(s,'utf-8'))] for s in xclean]
xcleanlemmas = [[(token.text,token.lemma_,token.pos_) for token in nlp(unicode(s,'utf-8'))] for s in xclean]
