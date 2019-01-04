from TextClassifier import TextClassifier

from ner import *
from postprocess import *
import cPickle

#from build_feature import *
#from ApproxNNClient import *
from S2SClient import *
#from S2SServer import *
from class_label_augmenter import *
from smt_generator import *
import json
from nltk import pos_tag
from utils import *
import spacy
from Compounding import *
import traceback
from wikirelations import *
from lm_scorer import *
import data_scripts.multi_morph.gen_data_multi_relation as simple
import data_scripts.multi_morph.gen_data_multi_relation_merge as merge
from anaphora_replacer.pronanaphora import *
from Compounding import extract_ent_rel_dict as triple


SPACY_TAGS = ['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','URL','UNK']
class Struct2Text():
    def __init__(self, config, via_rpc=True):
        self.nlp = spacy.load('en') # --- put it in class defination

        print('Initialize Struct2Text....')
        if via_rpc:
            self.s2smodel = S2SClient(config['s2s_port'])
            self.gendermodel = PronounReplacer(config['gen_port'])
        else:
            from S2SServer import *
            self.s2smodel = S2SFunctions(config)
            self.gendermodel = PronounReplacer(0000, via_rpc)
            
        #self.knnModel = ApproxNNClient(config['ann_port'])
        
        self.textClassifier = TextClassifier()
        self.wikirelation = WikiRelations(config)
        self.lmscorer = LMScorer(config)
        rel_path = config['rel_map']
        self.rel_mapper = cPickle.load(open(rel_path))
        log_file = config['log_file']
        self.logfile = open(log_file, 'a')
        print('Initialize done Struct2Text....')
        self.return_logs = ''
        self.debug = False
        
    def doc_sim(self, s1, s2):
        doc1 = self.nlp(s1.decode('unicode-escape'))
        doc2 = self.nlp(s2.decode('unicode-escape'))
        return doc1.similarity(doc2)
    
    def pos_tag_spacy(self, words):
        text = " ".join(words).decode('unicode-escape')
        doc = self.nlp(text)
        return [(tok.text, tok.pos_) for tok in doc]
    
    def log_something(self, sometext, somevalue):
        lstr = sometext + ': ' + str(somevalue)
        self.logfile.write('############## \n')
        self.logfile.write(lstr + '\n')
        self.return_logs = self.return_logs + '\n' + lstr
        #print(lstr + '\n')
    
    def pre_process_relations(self,relword):
        inf = relword.split()
        unchanged = True #Required for further processing in "map_relations" function
        if len(inf)==1:
            #just one relation word is present
            return (relword,unchanged)
        #add a dummy noun so that pos_tag should be accurate
        unchanged = False
        new_relword = "He "+relword
        pos = self.pos_tag_spacy(new_relword.split())
        verb_word = ""
        for p in pos:
            if p[1][0]=="V":
                #verb present
                verb_word = p[0]
                break
        if verb_word=="":
            rel_phrase = "has "+relword
            #rel_phrase = relword
        else:
            splitted = relword.split(verb_word)
            rel_phrase = verb_word+" "+splitted[1].strip()+" "+splitted[0].strip()
        return (rel_phrase.strip(),unchanged)
    
    def map_relations(self,tagged_triple):
        relation = tagged_triple[1]
        rel_phrase,unchanged = self.pre_process_relations(relation)
        if relation!=rel_phrase or not unchanged:
            #not a single word relation and pre-processing has changed it
            new_triple = [tagged_triple[0], rel_phrase, tagged_triple[2]]#tagged_triple.replace(relation,rel_phrase)
            return new_triple
        d = self.nlp(relation.lower().decode("unicode-escape"))
        new_relation = d[0].lemma_.encode("unicode-escape")
        modified_relation = self.rel_mapper.get(new_relation,"")
        if modified_relation=="":
            modified_relation = "has "+relation
            #modified_relation = relation
        #else:
        #    modified_relation = relation
        #new_triple = tagged_triple.replace(relation,modified_relation)
        new_triple = [tagged_triple[0], modified_relation, tagged_triple[2]]
        return new_triple
    
    def get_wiki_outputs(self, triple):
        '''
        triple is tagged triple
        '''
        s, r, o = triple[0], triple[1], triple[2]
        relation_phrases = self.wikirelation.get_wiki_relations(r)
        if len(relation_phrases) < 1:
            return []
        outputs = []
        for rp in relation_phrases:
            sen = s + ' ' + rp + ' '  + o
            outputs.append(sen)
            sen = o + ' ' + rp + ' '  + s
            outputs.append(sen)
        return outputs
    
    def generate_from_knn(self, tagged_triples, use_string_match=False):
        
        generated_outputs = []
        stuplelist = []
        for tt in tagged_triples:
            generated = self.knnModel.generate(tt, use_string_match)
            generated_outputs.append(generated)
            tts = ' '.join(tt)
            stuplelist.append((tts, generated))
        self.log_something('knn list ', stuplelist)
        return generated_outputs, stuplelist
        

    def generate_from_s2s_with_classifier(self, modified_tag_triple_string, class_label):
        augnemted_tagged_triple_string = augmenter(modified_tag_triple_string, class_label)
        generated = self.s2smodel.generate_with_classifier(augnemted_tagged_triple_string)
        return generated

    def generate_from_s2s_without_classifier(self, modified_tag_triple_string):
        generated = self.s2smodel.generate_without_classifier(modified_tag_triple_string)
        return generated
    
    def generate_with_multiword(self, modified_tag_triple_string):
        generated = self.s2smodel.generate_with_multiword(modified_tag_triple_string)
        return generated

    def generate_with_singleword(self, modified_tag_triple_string):
        generated = self.s2smodel.generate_with_singleword(modified_tag_triple_string)
        return generated

    def generate_from_smt(self, modified_tag_triple_string, class_label):
        augnemted_tagged_triple_string = augmenter(modified_tag_triple_string, class_label)
        generated = smt_gen(augnemted_tagged_triple_string)
        return generated
    
    def generate_from_smt_no_class(self, modified_tag_triple_string):
        generated = smt_gen_noclass(modified_tag_triple_string)
        return generated
    
    def generate_from_smt_multi(self, modified_tag_triple_string):
        generated = smt_gen_multi(modified_tag_triple_string)
        return generated

    def generate_multiword_morph_simple(self, s):
        generated = self.s2smodel.generate_multiword_morph_simple(s)
        return generated

    def generate_multiword_morph_merge(self, s):
        generated = self.s2smodel.generate_multiword_morph_merge(s)
        return generated

    '''
    def tag_triples(self, triples):
        tagged_triples = []
        modified_tag_triples = []
        class_labels  = []
        tag_maps = []

        for triple in triples:
            self.log_something('tagging triple', triple)
            tagged_triple, tag_map_list = tagTriple(triple)
            self.log_something('tagged_triple ', tagged_triple)
            self.log_something('tag_map_list ', tag_map_list)
            #tagged_triple_string = ' '.join(tagged_triple)
            modified_tagged_triple = self.map_relations(tagged_triple)
            self.log_something('modified_tagged_triple ', modified_tagged_triple)
            modified_tagged_triple_string = ' '.join(modified_tagged_triple)
            y_label = self.textClassifier.predict(modified_tagged_triple_string)
            self.log_something(' label ', y_label)

            class_labels.append(y_label)
            tagged_triples.append(tagged_triple)
            modified_tag_triples.append(modified_tagged_triple)
            class_labels.append(y_label)
            tag_maps.append(tag_map_list)
        return tagged_triples, modified_tag_triples, class_labels, tag_maps
    '''
    def tag_triples(self, triples, required_class_labels = True):
        tagged_triples = []
        modified_tag_triples = []
        class_labels  = []
        tag_maps = []

        for triple in triples:
            self.log_something('tagging triple', triple)
            tagged_triple, tag_map_list = tagTriple(triple)
            self.log_something('tagged_triple ', tagged_triple)
            self.log_something('tag_map_list ', tag_map_list)
            #tagged_triple_string = ' '.join(tagged_triple)
            modified_tagged_triple = self.map_relations(tagged_triple)
            self.log_something('modified_tagged_triple ', modified_tagged_triple)
            modified_tagged_triple_string = ' '.join(modified_tagged_triple)
            if required_class_labels:
                y_label = self.textClassifier.predict(modified_tagged_triple_string)
                self.log_something(' label ', y_label)
                class_labels.append(y_label)
            tagged_triples.append(tagged_triple)
            modified_tag_triples.append(modified_tagged_triple)
            #class_labels.append(y_label)
            tag_maps.append(tag_map_list)
        if required_class_labels:
            return tagged_triples, modified_tag_triples, class_labels, tag_maps
        else:
            return tagged_triples, modified_tag_triples, tag_maps
    
    def get_out_for_triples(self, triples, use_string_match=False):
        outputs = {}
        for triple in triples:
            output = {}
            tagged_outputs = []
            knn_outputs = []
            smt_outputs = []
            s2s_outputs = []
            classifier_outputs = []
            
            tagged_triple, tag_map_list = tagTriple(triple)
            tagged_triple_string = ' '.join(tagged_triple)
            modified_tagged_triple_string = self.map_relations(tagged_triple_string)
            tagged_triple = modified_tagged_triple_string.split()
            tagged_outputs.append(modified_tagged_triple_string)
            
            y_label = self.textClassifier.predict(modified_tagged_triple_string)
            classifier_outputs.append(y_label)
            
            #generated_knn = self.knnModel.generate(tagged_triple, use_string_match)
            generated_knn = []
            for g in generated_knn:
                gg = self.replaceTokens(g[0], tag_map_list)
                knn_outputs.append(gg)
    
            augnemted_tagged_triple_string = augmenter(modified_tagged_triple_string, y_label)
            #print('augnemted_tagged_triple_string ', augnemted_tagged_triple_string)
            generated_smt = smt_gen(augnemted_tagged_triple_string)
            
            generated_smt = self.replaceTokens(generated_smt, tag_map_list)
            smt_outputs.append(generated_smt)
            
            
            s2sgenerated = self.s2smodel.generate(augnemted_tagged_triple_string)
            s2sgenerated = self.replaceTokens(s2sgenerated, tag_map_list)
            s2s_outputs.append(s2sgenerated)
            output['tagged'] = tagged_outputs
            output['s2s'] = s2s_outputs
            output['smt'] = smt_outputs
            output['knn'] = knn_outputs
            output['classfier'] = classifier_outputs
            outputs[tagged_triple_string] = output
    
        return outputs
            

    def replaceTokens(self, generated, tag_map_list):
        return post_process(generated, tag_map_list)

    def add_apostrophe(self, t,gen):
        e1=t[0]
        rel=t[1]
        e2=t[2]
        g=gen
        try:
            parts=[x.strip() for x in g.split(e1)]
            g=' '.join(parts).strip()
            parts=[x.strip() for x in g.split(rel)]
            g=' '.join(parts).strip()
            parts=[x.strip() for x in g.split(e2)]
            g=' '.join(parts).strip().split(' ')
            if g[0]=='is' and len(g)==1:
                if gen.index('is')>gen.index(rel):
                    return e1.strip() + "\'s " + rel.strip() + " is " + e2.strip()
            if g[0] == 'was' and len(g) == 1:
                if gen.index('was')>gen.index(rel):
                    return e1.strip() + "\'s " + rel.strip() + " was " + e2.strip()
        except:
            return gen
        return gen

    def add_apostrophe_preranker(self, tm, gen):
        e1=tm[0].values()[0]
        e2=tm[1].values()[0]
        g=gen
        try:
            parts=[x.strip() for x in g.split(e1)]
            g=' '.join(parts).strip()
            parts=[x.strip() for x in g.split(e2)]
            rel=' '.join(parts).strip().rstrip('.').strip()
            postags = [(token.text,token.lemma_,token.pos_,token.tag_) for token in nlp(rel)]
            if postags[0][2] != u'VERB' and postags[0][0] != "\'s":
                parts=gen.split(rel)
                return parts[0].strip() + "\'s " + rel.strip() + " " + parts[1].strip()
        except:
            return gen
        return gen


    def extractTriple(self, headerline, valueline):
        headers = headerline.split('##')
        values = valueline.split('##')
        triple = [values[0], headers[1], values[1]]
        return triple
    
    def getTriple(self, lines):
        triples = []
        for line in lines:
            if line == '': continue
            #print(line)
            rows = line.split('####')
            #print(rows)
            headerline = rows[0].rstrip()
            valueline = rows[1].rstrip()
            triple = self.extractTriple(headerline, valueline)
            triples.append(triple)
            #print('Tagging::  ', line)
            #print('Triple ', triple)
        
        return triples

    
    def generate(self, text, use_string_match):
        try:
            triples = self.getTriple([text])
            out = self.get_out_for_triples(triples, use_string_match)
            out = json.dumps(out, indent=4, sort_keys=True)
            print(out)
            return out
        except Exception, error:
            print(str(error))
            return str(error)
    
    def generate_multiple(self, texts,  use_string_match, use_multi, debug, use_compounding, use_coref):
        self.debug = debug
        self.return_logs = ''
        texts = texts.split('\n')
        generated_tag_map = {}
        try:
            stuplelist  = []
            sdictlist = []
            triples = self.getTriple(texts)
            tagged_triples, modified_tag_triples, class_labels, tag_maps = self.tag_triples(triples)
            print('######################')
            self.log_something('tagged_triples ', tagged_triples)
            self.log_something('modified_tag_triples ', modified_tag_triples)
            self.log_something('class_labels ', class_labels)
            print('######################')
            count = 0
            
            for t, tt, mtt, cl, tm in zip(triples, tagged_triples, modified_tag_triples, class_labels, tag_maps):
                print(t, tt, mtt, cl, tm)
                mtts = ' '.join(mtt)
                tts = ' '.join(tt)
                output_dict = {}
                self.log_something(':######################', count)
                count += 1 
                self.log_something('Triple: ', t)
                self.log_something('Tagged Triple: ', tt)
                self.log_something('Modified Tagged triple ', mtts)
                
                #generated_knn = self.knnModel.generate(tt, False)
                generated_knn = []
                knn_outputs = []
            
                for g in generated_knn:
                    
                    gg = postprocess(g[0], self.nlp)
                    tagged_generated_version = gg
                    gg = self.replaceTokens(gg, tm)
                    generated_tag_map[gg] = tagged_generated_version
                    knn_outputs.append(gg)
                self.log_something('knn_outputs ', knn_outputs)
                output_dict['knn'] = knn_outputs
                
                wikirelations_generated_unm = self.get_wiki_outputs(tt)
                wikirelations_generated = self.get_wiki_outputs(mtt)
                wikirelations_generated_unm , _ = self.lmscorer.rank_kenlm(wikirelations_generated_unm, 5)
                wikirelations_generated , _ = self.lmscorer.rank_kenlm(wikirelations_generated, 5)
            
                wikioutputs = []
                for o in wikirelations_generated:
                   oo = self.replaceTokens(o, tm)
                   wikioutputs.append(oo)
                   generated_tag_map[oo] = o
                wikioutputs_um = []
                for o in wikirelations_generated_unm:
                    oo = self.replaceTokens(o, tm)
                    wikioutputs.append(oo)
                    generated_tag_map[oo] = o
            
                logfile.write('Generated from wikirelations  ' + str(wikioutputs_um) + '\n')
                logfile.write('Generated from wikirelations modified  ' + str(wikioutputs) + '\n')
                self.log_something(' Generated from wikirelations  ', wikioutputs_um)
                self.log_something(' Generated from wikirelations  modified ', wikioutputs)
                output_dict['wikioutputs'] = wikioutputs
                output_dict['knn'] = knn_outputs

                # tstring = ' '.join(t)
                tstring = ' '.join(tt)
                tinput = simple.transform_input(tstring, ner=False)
                self.log_something('input to s2s multi_morph_simple', tinput)
                g = self.generate_multiword_morph_simple(tinput)
                self.log_something('generate_from_s2s_multi_morph_simple', g)
                norm_g = simple.normalize_string(tstring,g)
                self.log_something('verbs generate_from_s2s_multi_morph_simple', norm_g[1])
                # g = simple.replace_entities(tstring, norm_g[0])[1]
                g = self.add_apostrophe(tt, norm_g[1])
                g = self.replaceTokens(g, tm)
                iscorrect = is_correct_pattern(g, tt)
                # g = self.add_apostrophe(t,g)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('ents generate_from_s2s_multi_morph_simple', g)
                output_dict['s2s_multi_morph_simple'] = [g]
                generated_tag_map[g] = norm_g[1]

                # inv_t = list(reversed(t))
                inv_t = list(reversed(tt))
                inv_tm = list(reversed(tm))
                tstring = ' '.join(inv_t)
                tinput = simple.transform_input(tstring, ner=False)
                self.log_something('input to s2s multi_morph_simple INV', tinput)
                g = self.generate_multiword_morph_simple(tinput)
                self.log_something('generate_from_s2s_multi_morph_simple INV', g)
                norm_g = simple.normalize_string(tstring,g)
                self.log_something('verbs generate_from_s2s_multi_morph_simple INV', norm_g[1])
                # g = simple.replace_entities(tstring, norm_g[0])[1]
                g = self.add_apostrophe(inv_t,norm_g[1])
                g = self.replaceTokens(g, inv_tm)
                iscorrect = is_correct_pattern(g, tt, inverse=True)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('ents generate_from_s2s_multi_morph_simple INV', g)
                output_dict['s2s_multi_morph_simple_inv'] = [g]
                generated_tag_map[g] = norm_g[1]

                # tstring = ' '.join(t)
                tstring = ' '.join(tt)
                tinput = merge.transform_input(tstring, ner=False)
                self.log_something('input to s2s morph_merge', tinput[0])
                g = self.generate_multiword_morph_merge(tinput[0])
                self.log_something('generate_from_s2s_morph_merge', g)
                norm_g = merge.normalize_string(tstring, g)
                self.log_something('verbs generate_from_s2s_morph_merge', norm_g[1])
                # g = merge.replace_entities(tstring, tinput[1], norm_g[0])[1]
                # g = self.add_apostrophe(t,g)
                g = self.add_apostrophe(tt, norm_g[1])
                g = self.replaceTokens(g, tm)
                iscorrect = is_correct_pattern(g, tt)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('ents generate_from_s2s_morph_merge', g)
                output_dict['s2s_morph_merge'] = [g]
                generated_tag_map[g] = norm_g[1]

                # inv_t = list(reversed(t))
                inv_t = list(reversed(tt))
                inv_tm = list(reversed(tm))
                tstring = ' '.join(inv_t)
                tinput = merge.transform_input(tstring, ner=False)
                self.log_something('input to s2s morph_merge INV', tinput[0])
                g = self.generate_multiword_morph_merge(tinput[0])
                self.log_something('generate_from_s2s_morph_merge INV', g)
                norm_g = merge.normalize_string(tstring, g)
                self.log_something('verbs generate_from_s2s_morph_merge INV', norm_g[1])
                # g = merge.replace_entities(tstring, tinput[1], norm_g[0])[1]
                g = self.add_apostrophe(inv_t,norm_g[1])
                g = self.replaceTokens(g, inv_tm)
                iscorrect = is_correct_pattern(g, tt, inverse=True)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('ents generate_from_s2s_morph_merge INV', g)
                output_dict['s2s_morph_merge_inv'] = [g]
                generated_tag_map[g] = norm_g[1]

                g = self.generate_from_s2s_with_classifier(mtts, cl)
                
                self.log_something('generate_from_s2s_with_classifier ', g)
                g = postprocess(g, self.nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_s2s_with_classifier ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('rt generate_from_s2s_with_classifier ', g)
                output_dict['s2s_classifier'] = [g]
                generated_tag_map[g] = tagged_generated_version

                g = self.generate_from_s2s_without_classifier(mtts)
                
                self.log_something('generate_from_s2s_without_classifier ', g)
                g = postprocess(g, self.nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_s2s_without_classifier ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('rt generate_from_s2s_without_classifier ', g)
                output_dict['s2s_no_classifier'] = [g]
                generated_tag_map[g] = tagged_generated_version

                g = self.generate_from_smt(mtts, cl)
                
                self.log_something('generate_from_smt ', g)
                g = postprocess(g, self.nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_smt ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('rt generate_from_smt ', g)
                output_dict['smt_classifier'] = [g]
                generated_tag_map[g] = tagged_generated_version

                g = self.generate_from_smt_no_class(mtts)
                
                self.log_something('generate_from_smt_no_class ', g)
                g = postprocess(g, self.nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_smt_no_class ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                g = self.add_apostrophe_preranker(tm, g)
                self.log_something('rt generate_from_smt_no_class ', g)
                output_dict['smt_no_classifier'] = [g]
                generated_tag_map[g] = tagged_generated_version

                r = mtt[1]
                print('******************', len(r.split()), use_multi)
                if len(r.split()) > 1 and use_multi:
                    self.log_something(' ', 'trying multi')
                    g = self.generate_with_multiword(' || '.join(mtt))
                    tagged_generated_version = g
                    self.log_something('generate_with_multiword ', g)
                    #g = postprocess(g, self.nlp)
                    #self.log_something('pp generate_with_multiword ', g)
                    g = self.replaceTokens(g, tm)
                    g = self.add_apostrophe(mtt, g)
                    g = self.add_apostrophe_preranker(tm, g)
                    self.log_something('rt generate_with_multiword ', g)
                    output_dict['s2s_mw'] = [g]
                    generated_tag_map[g] = tagged_generated_version

                    g = self.generate_from_smt_multi(mtts)
                    tagged_generated_version = g
                    self.log_something('generate_from_smt_multi ', g)
                    #g = postprocess(g, self.nlp)
                    #self.log_something('pp generate_from_smt_multi ', g)
                    g = self.replaceTokens(g, tm)
                    g = self.add_apostrophe(mtt,g)
                    g = self.add_apostrophe_preranker(tm, g)
                    self.log_something('rt generate_from_smt_multi ', g)
                    output_dict['smt_mw'] = [g]
                    generated_tag_map[g] = tagged_generated_version

                elif len(r.split()) == 1:
                    self.log_something(' ', 'trying single s2s')
                    g = self.generate_with_singleword(mtts)
                    tagged_generated_version = g
                    self.log_something('generate_with_singleword ', g)
                    g = self.replaceTokens(g, tm)
                    g = self.add_apostrophe(mtt, g)
                    g = self.add_apostrophe_preranker(tm, g)
                    self.log_something('rt generate_with_singleword ', g)
                    output_dict['s2s_sw'] = [g]
                    generated_tag_map[g] = tagged_generated_version
                
                inp_original = t[0] + '\t' + tt[1] + '\t' + t[2]
                inp_modified = t[0] + '\t' + mtt[1] + '\t' + t[2]
                inp = [inp_original, inp_modified]
                self.log_something('*** Input to ranker ', inp)
                self.log_something('output_dict ', output_dict)
                o= find_best(inp, output_dict, self.doc_sim, self.nlp, self.lmscorer)
                [best_sent,system_tag,max_score]  = o
                self.log_something('****************************** OUTPUT ***********', '')
                self.log_something('output list ', o)
                self.log_something('generated_tag_map', generated_tag_map)
                tagged_o = generated_tag_map[o[0]]
                stuplelist.append((tagged_o, o[0]))
                if "inv" in system_tag:
                    sdictlist.append((reversed(tm), o[0]))
                else:
                    sdictlist.append((tm, o[0]))
                        
            self.log_something('sdictlist ', sdictlist)
            #oo = stuplelist
            #oo = merge_sentences(stuplelist, punctProcess=True)
            return_output = ''
            if use_compounding:
                oo = merge_sentences(sdictlist, punctProcess=True)
                sentlist = [e[1] for e in oo]
                self.log_something('Merged ', sentlist)
                if debug:
                    return_output = str('\n'.join(sentlist)) + '\n\n\n' + self.return_logs
                else:
                    return_output = str('\n'.join(sentlist))
                """
                #out = json.dumps(out, indent=4, sort_keys=True)
                """
            if use_coref:
                coref_out = [' '.join(self.gendermodel.replace_pronoun(e[0], tag_maps)) for e in oo]
                self.log_something('Coreference resolution \n', coref_out)
                if debug:
                    return_output = str('\n'.join(coref_out)) + '\n\n\n' + self.return_logs
                else:
                    return_output = str('\n'.join(coref_out))
            return return_output
        except Exception, error:
            print(str(error))
            s = traceback.format_exc()
            print(s)
            o = self.return_logs + '\n\n' + str(s)
            return o



def replaceTokens(generated, tag_map_list):
    orders = {}
    for t in SPACY_TAGS:
        p = generated.find(t)
        if p != -1:
            orders[t] = p
    if len(orders) > 0:
        sorted_orders = sorted(orders.items(), key=operator.itemgetter(1))
        generated = generated.replace(sorted_orders[0][0], tag_map_list[0], 1)
        generated = generated.replace(sorted_orders[-1][0], tag_map_list[-1], 1)
    for t in SPACY_TAGS:
        generated = generated.replace(t, '')

    return generated

def is_correct_pattern(g, tt, inverse=False):
    t=tt
    if inverse:
        t=list(reversed(tt))
    try:
        parts = [s.strip() for s in g.split(t[0], 1)]
        g1 = ' '.join(parts).strip()
        parts = [s.strip() for s in g1.split(t[2], 1)]
        rel = ' '.join(parts).strip().rstrip('.').strip()
        postags = [(token.text, token.lemma_, token.pos_, token.tag_) for token in self.nlp(rel)]
        if postags[0][1] == 'be': #'is','was','were'
            if postags[1][2] == u'DET' or postags[1][2] == u'NOUN':
                # print '1'
                iscorrect=False
            elif postags[1][3] == u'VBG' and postags[2][2] == u'VERB':
                # print '2'
                iscorrect=False
            elif postags[1][2] == u'VERB' and postags[1][3] != u'VBG':
                # print '3'
                iscorrect=False
            else:
                # print '4'
                iscorrect=True
        else:
            # print '5'
            iscorrect=True
    except:
        # print '6'
        iscorrect=True
    # print 'Inverse:'+str(inverse)
    # print 'Iscorrect:'+str(iscorrect)
    if inverse:
        return not iscorrect
    return iscorrect

def main():
    texts = ['Name##Game####Michael##Football','Name##country played for####Michael##India','Name##Profit####IBM##23%',
    'Name##Loss####IBM##23%','Conference##Acceptances####COLING##23%','Conference##has acceptance rate####COLING##23%']
    orchestrator = Struct2Text()
    orchestrator.generate_multiple(texts)




if __name__ == '__main__':
    main()
