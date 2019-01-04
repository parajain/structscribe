import spacy
from nltk.translate import chrf_score

prepositions = ["with","at","from","into","during","including","until","against","among","throughout","despite","towards","upon","concerning","of","to","in","for","on","about","through","over","before","between","after","since","without","under","within","along","following","across","behind","beyond","plus","except","up","out","around","down","off","above","near"]
def is_passive(root):
    for ch in root.children:
        if "pass" in ch.dep_:
            return True
    return False
def has_agent_passive(root):
    if is_passive(root):
        for ch in root.children:
            if "agent" in ch.dep_:
                return True
    return False
def ends_with_preposition(relation):
    rel = relation.strip().split()
    if rel[-1].lower() in prepositions:
        return True
    return False
    
def semantic_wrongness(sent,tagged_input,nlp):
    if sent.strip()=="":
        return -1000
    e1,r,e2 = tagged_input[0],tagged_input[1],tagged_input[2]
    doc = nlp(sent.decode("unicode-escape"))
    root = None
    total_id = 0
    if "not" in sent and "not" not in r:
        #unnecessary negation insertion 
        return -1000
    for tok in doc:

        if tok.dep_ =="ROOT" and tok.pos_=="VERB":
            root = tok
        if tok.dep_ =="ROOT" and tok.pos_!="VERB":
            #print "verb missing"
            return -1000
        total_id+=1

    if root.i==0:
        #print "start index"
        return -1000
    if root.i==total_id-1:
        #print "end index"
        return -1000
    id1 = sent.find(e1)
    id2 = sent.find(e2)
    if id1 ==-1 or id2 ==-1:
        #print "Missing entity"
        return -1000

    if root.lemma_ =="be":
        try:
            next_tok = doc[root.i+1]
        except:
            next_tok = root
        if next_tok.pos_=="ADP":
            if id1<id2:
                #print "not flipped"
                return 1000
            else:
                return -1000
        elif "'s" in sent:
            if id1<id2:
                return 1000
            else:
                #print "flipped"
                return -1000
        elif ends_with_preposition(r) and r in sent:
            if id1<id2:
                return 1000
            else:
                return -1000
        else:
            if id1<id2:
                return -1000
            else:
                #print "flipped"
                return 1000

    elif root.lemma_ =="has":
        if id1<id2:
            return 1000
        else:
            #print "flipped"
            return -1000
    else:
        if has_agent_passive(root):
            if id1<id2:
                return -1000
            else:
                #print "Active flipped"
                return 1000
        else:
            if id1<id2:
                return 1000
            else:
                return -1000
    return -1000

def char_rank_scorer(sent,input_tuple):
    sent = sent.encode("unicode-escape")
    input_tuple = input_tuple.encode("unicode-escape")
    try:
        score = chrf_score.sentence_chrf(input_tuple.split(),sent.split())
    except Exception, error:
        print(str(error))
        return 0

    return score

def bleu_rank_scorer(sent,original):
    #For computing bleu based overlap scores
    sent = sent.encode("unicode-escape")
    original = original.encode("unicode-escape")
    ble = bleu([original],sent)
    return ble

def postprocess(sent, nlp):
    #This funciton tries to remove spurious nouns that appear in the middle of relations 
    #IMPORTANT: Only call this for single relation input
    #INPUT <str>: Tagged SMT / KNN / Seq2Seq output
    # Output: Polished tagged sentence <str>
    if "is " in sent or "has " in sent:
        return sent
    rel = " ".join(sent.split()[1:-1])
    mod_rel = "He "+rel
    mod_rel = mod_rel.decode("unicode-escape")
    doc = nlp(mod_rel)
    
    new_rel = ""
    first_tok = 1
    for tok in doc:
        if first_tok ==1:
            #remove that spurious "He" we deliberately inserted
            first_tok = 0
            continue
        if "NOUN" in tok.pos_ or "ADJ" in tok.pos_ or "ADV" in tok.pos_:
            continue
        new_rel+=str(tok.text)+" "
    new_rel = new_rel.strip()
    new_sent = sent.replace(str(rel), str(new_rel))
    
    return new_sent




def find_best(inp, output_dict, score_func_spacy,nlp, lm_scorer, default_key= 's2s_morph_merge'):
    #This function finds the best output and the corresponding system used (for interpretation) 
    #The best system is found based on char-ngram based ranking
    #INPUT <str,dict>: The input triple (before tagged) and dict containing list of outputs for each system (system type (KNN, SMT) is taken as Key.
    #Output <str, str, float>: The best output string  and the system type (from which it came) and the score it got. 
    best_sent = ""
    max_score = -1000
    system_tag = ""
    
    inp_original = inp[0].replace("\t"," ")
    inp_modified = inp[1].replace("\t"," ")
    tagged_tuple_list = inp[0].split("\t")

    fout=open('debug.csv','a')
    for k in output_dict.keys(): 
        '''
        if k not in ['s2s_morph_merge','s2s_morph_merge_inv','s2s_mw','s2s_sw','s2s_multi_morph_simple','s2s_multi_morph_simple_inv']:
            continue
        '''
        opsents = output_dict[k]
        for opsent in opsents:
            if semantic_wrongness(opsent,tagged_tuple_list,nlp)==-1000:
                print "Hello:: "+ opsent+" : "+str(tagged_tuple_list)
                continue
            #opsent= opsent.strip().rstrip(".").rstrip()
            score_original = char_rank_scorer(opsent, inp_original)
            score_modified = char_rank_scorer(opsent, inp_modified)
            #score = max([score_original,score_modified])
            score_lm = lm_scorer.kenlm_score_ranker(opsent.lower())
            score_sim1 = score_func_spacy(opsent.lower(), inp_original.lower())
            score_sim2 = score_func_spacy(opsent.lower(), inp_modified.lower())
            score_fuzzy_overlap1 = find_overlap_fuzzy(opsent.lower(), inp_original.lower())
            score_fuzzy_overlap2 = find_overlap_fuzzy(opsent.lower(), inp_modified.lower())
            score_fuzzy_overlap = max([score_fuzzy_overlap1, score_fuzzy_overlap2])
            debug=[k, opsent,score_original,score_modified,score_sim1,score_sim2,score_lm,score_fuzzy_overlap1,score_fuzzy_overlap2,len(inp_original.split())-len(opsent.split())]
            dstring=','.join([str(e) for e in debug])
            fout.write(dstring + '\n')
            fout.write('--------------------------' + '\n')
            score_sim = max([score_sim1, score_sim2])
            # score = score_original+score_modified+score_lm+score_sim1+score_sim2
            score = score_fuzzy_overlap + score_lm
            #score = score_original + score_modified + score_lm + score_sim1 + score_sim2 + score_fuzzy_overlap
            #score = score * score_sim
            #print opsent, score
            if score>max_score:
                max_score = score
                best_sent = opsent
                system_tag = k
    if best_sent=="":
        best_sent = output_dict[default_key][0]
        system_tag = default_key#"s2s_morph_merge"
    return [best_sent,system_tag,max_score]


def find_overlap_fuzzy(sent, original):
    score = 0
    for word in original.split():
        c1 = original.count(word)
        c2 = sent.count(word)
        if c1 == c2:
            score += 1
    score /= float(len(original.split()))
    if sent == original:
        score = score * 0.8
    return score

if __name__ == "__main__":
    
    x1 = "PERSON has won prize GPE"
    x2 = "PERSON has won a tremendous greatly amount of prize GPE"
    
    print "Loading NLP modules..."
    nlp = spacy.load('en')
    print "NLP modules loaded..."
    
    print postprocess(x1,nlp)
    print postprocess(x2,nlp)
    
    
    OUTPUT = {"knn": ["IBM is to invoke 23%", "IBM loses game as 23%", "IBM refuses to implement 23%", "IBM opens road to 23%"], \
    "s2s": ["IBM loses consciousness on 23%"], \
    "smt": ["IBM loses 23% ."]}
    
    inp = "IBM loss 23%"
    
    print find_best(inp, OUTPUT)
    
    
    
    
