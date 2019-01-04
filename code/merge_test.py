from TextClassifier import TextClassifier
import time
from ner import *
from postprocess import *
import cPickle
from ApproxNNClient import *
from S2SClient import *
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
import os.path
from os import path
from multiprocessing import Process
from S2SServer import *
import joblib

SPACY_TAGS = ['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','URL','UNK']
class Struct2Text():
    def __init__(self, config):
        print('Initialize Struct2Text....')
        self.nlp = spacy.load('en') # --- put it in class defination
        self.s2smodel = S2SFunctions(config)#S2SClient(config['s2s_port'])
        self.knnModel = ApproxNNClient(config['ann_port'])
        self.gendermodel = PronounReplacer(config['gen_port'])
        #self.textClassifier = TextClassifier()
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
        '''
        lstr = sometext + ': ' + str(somevalue)
        self.logfile.write('############## \n')
        self.logfile.write(lstr + '\n')
        self.return_logs = self.return_logs + '\n' + lstr
        print(lstr + '\n')
        '''
        return None
    
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
        
        modified_relation = self.rel_mapper.get(relation.lower(),"")
        if modified_relation=="":
            modified_relation = "has "+relation
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
                return e1.strip() + "\'s " + rel.strip() + " is " + e2.strip()
            if g[0]=='was' and len(g)==1:
                return e1.strip() + "\'s " + rel.strip() + " was " + e2.strip()
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
   
    
    def generate_multiple(self, save_path, texts,  use_string_match, use_multi, debug, use_compounding, use_coref):
        self.debug = debug
        self.return_logs = ''
        #Now text is already a list, this split is required for UI
        #texts = texts.split('\n')
        generated_tag_map = {}
        try:
            stuplelist  = []
            sdictlist = []
            triples = self.getTriple(texts)
            tagged_triples, modified_tag_triples, class_labels, tag_maps = self.tag_triples(triples)
            '''
            print('######################')
            self.log_something('tagged_triples ', tagged_triples)
            self.log_something('modified_tag_triples ', modified_tag_triples)
            self.log_something('class_labels ', class_labels)
            print('######################')
            '''
            count = 0
            all_outputs = {}
            all_outputs['s2s_multi_morph_simple'] = []
            all_outputs['s2s_multi_morph_simple_inv'] = []
            all_outputs['s2s_morph_merge'] = []
            all_outputs['s2s_morph_merge_inv'] = []
            all_outputs['s2s_no_classifier'] = []
            all_outputs['s2s_classifier'] = []
            all_outputs['smt_classifier'] = []
            all_outputs['smt_no_classifier'] = []
            all_outputs['s2s_mw'] = []
            all_outputs['smt_mw'] = []
            all_inputs = []
            all_tag_maps = []
            
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
                
                tick33 = time.time()
                # tstring = ' '.join(t)
                tstring = ' '.join(tt)
                tinput = simple.transform_input(tstring, ner=False)
                self.log_something('input to s2s multi_morph_simple', tinput)
                t1 = time.time()
                print(t1-tick33)
                g = self.generate_multiword_morph_simple(tinput)
                t2 = time.time()
                print(t2-t1)
                self.log_something('generate_from_s2s_multi_morph_simple', g)
                norm_g = simple.normalize_string(tstring,g)
                t3 = time.time()
                print(t3-t2)
                self.log_something('verbs generate_from_s2s_multi_morph_simple', norm_g[1])
                # g = simple.replace_entities(tstring, norm_g[0])[1]
                g = self.add_apostrophe(tt, norm_g[1])
                t4=time.time()
                print(t4-t3)
                g = self.replaceTokens(g, tm)
                t5=time.time()
                print(t5-t4)
                # g = self.add_apostrophe(t,g)
                self.log_something('ents generate_from_s2s_multi_morph_simple', g)
                output_dict['s2s_multi_morph_simple'] = [g]
                all_outputs['s2s_multi_morph_simple'].append(g)
                generated_tag_map[g] = norm_g[1]
                tick34 = time.time()
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                print(tick34 - t5)
                return 0

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
                self.log_something('ents generate_from_s2s_multi_morph_simple INV', g)
                output_dict['s2s_multi_morph_simple_inv'] = [g]
                all_outputs['s2s_multi_morph_simple_inv'].append(g)
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
                self.log_something('ents generate_from_s2s_morph_merge', g)
                output_dict['s2s_morph_merge'] = [g]
                all_outputs['s2s_morph_merge'].append(g)
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
                self.log_something('ents generate_from_s2s_morph_merge INV', g)
                output_dict['s2s_morph_merge_inv'] = [g]
                all_outputs['s2s_morph_merge_inv'].append(g)
                generated_tag_map[g] = norm_g[1]

                g = self.generate_from_s2s_with_classifier(mtts, cl)
                
                self.log_something('generate_from_s2s_with_classifier ', g)
                g = postprocess(g, nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_s2s_with_classifier ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                self.log_something('rt generate_from_s2s_with_classifier ', g)
                output_dict['s2s_classifier'] = [g]
                all_outputs['s2s_classifier'].append(g)
                generated_tag_map[g] = tagged_generated_version

                g = self.generate_from_s2s_without_classifier(mtts)
                
                self.log_something('generate_from_s2s_without_classifier ', g)
                g = postprocess(g, nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_s2s_without_classifier ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                self.log_something('rt generate_from_s2s_without_classifier ', g)
                output_dict['s2s_no_classifier'] = [g]
                all_outputs['s2s_no_classifier'].append(g)
                generated_tag_map[g] = tagged_generated_version

                g = self.generate_from_smt(mtts, cl)
                
                self.log_something('generate_from_smt ', g)
                g = postprocess(g, nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_smt ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                self.log_something('rt generate_from_smt ', g)
                output_dict['smt_classifier'] = [g]
                all_outputs['smt_classifier'].append(g)
                generated_tag_map[g] = tagged_generated_version

                g = self.generate_from_smt_no_class(mtts)
                
                self.log_something('generate_from_smt_no_class ', g)
                g = postprocess(g, nlp)
                tagged_generated_version = g
                self.log_something('pp generate_from_smt_no_class ', g)
                g = self.replaceTokens(g, tm)
                g = self.add_apostrophe(mtt,g)
                self.log_something('rt generate_from_smt_no_class ', g)
                output_dict['smt_no_classifier'] = [g]
                all_outputs['smt_no_classifier'].append(g)
                generated_tag_map[g] = tagged_generated_version

                r = mtt[1]
                print('******************', len(r.split()), use_multi)
                if True: #len(r.split()) > 1 and use_multi:
                    self.log_something(' ', 'trying multi')
                    g = self.generate_with_multiword(' || '.join(mtt))
                    tagged_generated_version = g
                    self.log_something('generate_with_multiword ', g)
                    #g = postprocess(g, nlp)
                    #self.log_something('pp generate_with_multiword ', g)
                    g = self.replaceTokens(g, tm)
                    g = self.add_apostrophe(mtt,g)
                    self.log_something('rt generate_with_multiword ', g)
                    output_dict['s2s_mw'] = [g]
                    all_outputs['s2s_mw'].append(g)

                    generated_tag_map[g] = tagged_generated_version

                    g = self.generate_from_smt_multi(mtts)
                    tagged_generated_version = g
                    self.log_something('generate_from_smt_multi ', g)
                    #g = postprocess(g, nlp)
                    #self.log_something('pp generate_from_smt_multi ', g)
                    g = self.replaceTokens(g, tm)
                    g = self.add_apostrophe(mtt,g)
                    self.log_something('rt generate_from_smt_multi ', g)
                    output_dict['smt_mw'] = [g]
                    all_outputs['smt_mw'].append(g)
                    generated_tag_map[g] = tagged_generated_version

                
                inp_original = t[0] + ' ' + tt[1] + ' ' + t[2]
                inp_modified = t[0] + ' ' + mtt[1] + ' ' + t[2]
                inp = [inp_original, inp_modified]
                all_inputs.append([inp_original, inp_modified])
                self.log_something('*** Input to ranker ', inp)
                self.log_something('output_dict ', output_dict)
                o= find_best(inp, output_dict, self.doc_sim, self.lmscorer)
                [best_sent,system_tag,max_score]  = o
                self.log_something('****************************** OUTPUT ***********', '')
                self.log_something('output list ', o)
                self.log_something('generated_tag_map', generated_tag_map)
                tagged_o = generated_tag_map[o[0]]
                stuplelist.append((tagged_o, o[0]))
                sdictlist.append((tm, o[0]))
                all_tag_maps.append(tm)
                        
            self.log_something('sdictlist ', sdictlist)
            #oo = stuplelist
            #oo = merge_sentences(stuplelist, punctProcess=True)
            
            return_output = ''
            output_files = {}
            if use_compounding:
                oo = merge_sentences(sdictlist, punctProcess=True)
                sentlist = [e[1] for e in oo]
                for idxs, s in enumerate(sentlist):
                   filename = save_path + '/compounding' + '_' + str(idxs) + '.txt'
                   if filename in output_files:
                        outfile = output_files[filename]
                   else:
                        outfile = open(filename, 'a')
                        output_files[filename] = outfile
                    
                   outfile.write(s.rstrip() + '\n')

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
                for idxs, s in enumerate(coref_out):
                   filename = save_path + '/coref' + '_' + str(idxs) + '.txt'
                   if filename in output_files:
                        outfile = output_files[filename]
                   else:
                        outfile = open(filename, 'a')
                        output_files[filename] = outfile
                   outfile.write(s.rstrip() + '\n')
                self.log_something('Coreference resolution \n', coref_out)
                if debug:
                    return_output = str('\n'.join(coref_out)) + '\n\n\n' + self.return_logs
                else:
                    return_output = str('\n'.join(coref_out))
            
            
            keys = all_outputs.keys()
            
            print('Keys', keys)
            for kidx, k in enumerate(keys):
                generated_sententes = all_outputs[k]
                print('************************************************System name: ', k)
                temp_sdictlist = []
                for idx, s in enumerate(generated_sententes):
                    print(idx)
                    tm = all_tag_maps[idx]
                    temp_sdictlist.append((tm, s))
                oo = merge_sentences(temp_sdictlist)
                self.log_something(k + '\n******************************************Merged\n ', oo)
                for idxs, s in enumerate([e[1] for e in oo]):
                    filename = save_path + '/' + k + '_' + str(idxs) + '.txt'
                    if filename in output_files:
                        outfile = output_files[filename]
                    else:
                        outfile = open(filename, 'a')
                        output_files[filename] = outfile
                    outfile.write(s.rstrip() + '\n')
                    self.log_something('out :: ', s)
            
            for key, value in output_files.iteritems():
                print('Closing file: ', key)
                value.close()
            
            return return_output
        except Exception, error:
            print(str(error))
            s = traceback.format_exc()
            print(s)
            o = self.return_logs + '\n\n' + str(s)
            return o


            

class Dataset():
    def __init__(self, config):
        self.config = config
        self.orchestrator = Struct2Text(self.config)
    
    def tag_dataset(self):
        config = self.config
        orchestrator = self.orchestrator
        dataset_file = config['dataset_file']
        save_path_tagging = config['save_path_tagging']
        
        if path.exists(save_path_tagging):
            print('Save directory %s already exist'% (save_path_tagging))
            sys.exit(0)
        else:
            print('Creating directory: ', save_path_tagging)
            os.mkdir(save_path_tagging)
        
        tagged_information_filename = save_path_tagging + '/tagged_data.jl'
        triple_counts_filename = save_path_tagging + '/triple_counts.txt'
        triple_counts = []
        tagged_information_file = open(tagged_information_filename, 'w')
        triple_counts_file = open(triple_counts_filename, 'w')
        tagged_information_list = []
        lines = open(dataset_file, 'r').readlines()
        for idx, line in enumerate(lines):
            print('Running line number: ', idx)
            text_triples = line.split('||')
            num_text_triples = len(text_triples)
            triple_counts.append(num_text_triples)
            triples = orchestrator.getTriple(text_triples)
            get_class_labels = False
            tagged_triples, modified_tag_triples, tag_maps = orchestrator.tag_triples(triples, get_class_labels)
            tagged_information = {}
            tagged_information['tagged_triples'] = tagged_triples
            tagged_information['modified_tag_triples'] = modified_tag_triples
            tagged_information['tag_maps'] = tag_maps
            tagged_information_list.append(tagged_information)
            ostr = json.dumps(tagged_information)
            tagged_information_file.write(ostr.rstrip() + '\n')
            triple_counts_file.write(str(num_text_triples) + '\n')
        
        triple_counts_file.close()
        tagged_information_file.close()
        return tagged_information_list, triple_counts
    
    
    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(l), n):
            yield l[i:i + n]    
        
    def tag_lines(self, lines, file_id):
        config = self.config
        orchestrator = self.orchestrator
        dataset_file = config['dataset_file']
        save_path_tagging = config['save_path_tagging']
        
        tagged_information_filename = save_path_tagging + '/' + str(file_id) + '_tagged_data.jl'
        triple_counts_filename = save_path_tagging + '/' + str(file_id) + '_triple_counts.txt'
        triple_counts = []
        tagged_information_file = open(tagged_information_filename, 'w')
        triple_counts_file = open(triple_counts_filename, 'w')
        tagged_information_list = []
        
        for idx, line in enumerate(lines):
            print('Running line number: ', idx)
            text_triples = line.split('||')
            num_text_triples = len(text_triples)
            triple_counts.append(num_text_triples)
            triples = orchestrator.getTriple(text_triples)
            get_class_labels = False
            try:
                tagged_triples, modified_tag_triples, tag_maps = orchestrator.tag_triples(triples, get_class_labels)
            except Exception, error:
                tagged_triples = modified_tag_triples = tag_maps = 'ERROR PROCESSING TAG TRIPLES'
                print('File id', file_id)
                print(str(error))
            tagged_information = {}
            tagged_information['tagged_triples'] = tagged_triples
            tagged_information['modified_tag_triples'] = modified_tag_triples
            tagged_information['tag_maps'] = tag_maps
            tagged_information_list.append(tagged_information)
            ostr = json.dumps(tagged_information)
            tagged_information_file.write(ostr.rstrip() + '\n')
            triple_counts_file.write(str(num_text_triples) + '\n')
        
        triple_counts_file.close()
        tagged_information_file.close()
        #return tagged_information_list, triple_counts
        return None
        
    
    def merge_tagged(self):
        #Not used, will delete
        orchestrator = self.orchestrator
        config = self.config
        dataset_file = config['dataset_file']
        save_path_tagging = config['save_path_tagging']
        
        tagged_information_filename = save_path_tagging + '/' + '_tagged_data.jl'
        triple_counts_filename = save_path_tagging + '/' + '_triple_counts.txt'
        tagged_information_file = open(tagged_information_filename, 'w')
        triple_counts_file = open(triple_counts_filename, 'w')
        
        
        lines = open(dataset_file, 'r').readlines()
        n = 5000
        list_of_lines = self.chunks(lines, n)
        proc = []
        total = 0
        for idx, split_lines in enumerate(list_of_lines):
            file_id = idx
            tif = save_path_tagging + '/' + str(file_id) + '_tagged_data.jl'
            ti_lines = open(tif, 'r').readlines()
            tcf = save_path_tagging + '/' + str(file_id) + '_triple_counts.txt'
            tc_lines = open(tcf, 'r').readlines()
            print(len(ti_lines), len(tc_lines))
            total += len(ti_lines)
            print(idx, total)
        print(total)
            
    def tag_dataset_parallel(self):
        config = self.config
        dataset_file = config['dataset_file']
        save_path_tagging = config['save_path_tagging']
        
        
        if path.exists(save_path_tagging):
            print('Save directory %s already exist'% (save_path_tagging))
            sys.exit(0)
        else:
            print('Creating directory: ', save_path_tagging)
            os.mkdir(save_path_tagging)
        #not_skiplist = [7, 14]
        
        lines = open(dataset_file, 'r').readlines()
        n = 5000
        list_of_lines = self.chunks(lines, n)
        proc = []
        file_ids = []
        '''
        for idx, split_lines in enumerate(list_of_lines):
            print('Running in parallel: ')
            file_ids.append(idx)
        '''
        for idx, split_lines in enumerate(list_of_lines):
            print('Running in parallel: ')
            file_ids.append(idx)
            p = Process(target=self.tag_lines, args=(split_lines, idx))
            p.start()
            proc.append(p)
        for p in proc:
            p.join()
        
        
        ## Merge files 
        tagged_information_filename = save_path_tagging + '/' + 'combined_tagged_data.jl'
        triple_counts_filename = save_path_tagging + '/' + 'combined_triple_counts.txt'
        tagged_information_file = open(tagged_information_filename, 'w')
        triple_counts_file = open(triple_counts_filename, 'w')
        total = 0
        for file_id in file_ids:
            tif = save_path_tagging + '/' + str(file_id) + '_tagged_data.jl'
            ti_lines = open(tif, 'r').readlines()
            tcf = save_path_tagging + '/' + str(file_id) + '_triple_counts.txt'
            tc_lines = open(tcf, 'r').readlines()
            print(len(ti_lines), len(tc_lines))
            assert len(ti_lines) == len(tc_lines), "Number of lines does not match %d " % file_id
            total += len(ti_lines)
            print(file_id, total)
            for c, l in zip(tc_lines, ti_lines):
                c = str(c).rstrip()
                l = l.rstrip()
                triple_counts_file.write(str(c) + '\n')
                tagged_information_file.write(l + '\n')
        print(total)
        tagged_information_file.close()
        triple_counts_file.close()
        
    
    def split_by_count(self, input_list, counts, debug=False):
        """
        input_list: is a list to be splitted
        counts is a list of count
        """
        assert sum(counts) == len(input_list)
        splitted_final_generated_outputs = []
        start = 0
        for c in counts:
            end = start + c
            slist = input_list[start:end]
            splitted_final_generated_outputs.append(slist)
            start = end
        
        if debug:
            print('Overall length')
            print(len(counts), len(splitted_final_generated_outputs))
            assert len(counts) == len(splitted_final_generated_outputs)
            for idx, c in enumerate(counts):
                c2 = len(splitted_final_generated_outputs[idx])
                print(c, c2)
        
        return splitted_final_generated_outputs
    
    def batch_generate_multiword_morph_simple(self, tagged_information_list, triple_counts):
        print('Running batch_generate_multiword_morph_simple')
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        tstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        debug_file = open(save_path + '/debug_generate_multiword_morph_simple.txt', 'w')
        for tagged_information in tagged_information_list:
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            all_tagged_triples.extend(tagged_triples)
            for tt in tagged_triples:
                tstring = ' '.join(tt)
                tstring_list.append(tstring)
                #tinput = simple.transform_input(tstring, ner=False)
                #tinput_list.append(tinput)
                #debug_file.write(tinput.rstrip() + '\n')
        
        
        
        
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        tinput_list = simple.transform_input_list(tstring_list, ner=False)
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        generated_list = orchestrator.generate_multiword_morph_simple('####'.join(tinput_list))
        
        generated_list = generated_list.split('####')
        print('Len generated_list' , len(generated_list))
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_generate_multiword_morph_simple.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            norm_g = simple.normalize_string(tstring, g)
            appos_g = orchestrator.add_apostrophe(tt, norm_g[1])
            g = orchestrator.replaceTokens(g, tm)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, True)
        return splitted_final_generated_outputs        

    def batch_generate_multiword_morph_simple_inv(self, tagged_information_list, triple_counts):
        print('Running: batch_generate_multiword_morph_simple_inv' )
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        tstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        debug_file = open(save_path + '/debug_generate_multiword_morph_simple.txt', 'w')
        for idx, tagged_information in enumerate(tagged_information_list):
            if idx % 1000 == 0:
                print(idx)
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            all_tagged_triples.extend(tagged_triples)
            for tt in tagged_triples:
                inv_t = list(reversed(tt))
                tstring = ' '.join(inv_t)
                tstring_list.append(tstring)
                #tinput = simple.transform_input(tstring, ner=False)
                #tinput_list.append(tinput)
                #debug_file.write(tinput.rstrip() + '\n')
        
        
        print('Running transform_input_list')
        tinput_list = simple.transform_input_list(tstring_list, ner=False)
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_inv_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        
        print('Length ' + str(len(tinput_list)))
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        generated_list = orchestrator.generate_multiword_morph_simple('####'.join(tinput_list))
        generated_list = generated_list.split('####')
        print('Len generated_list' , len(generated_list))
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')

        final_generated_outputs = []
        
        ofile = open(save_path + '/out_batch_generate_multiword_morph_simple_inv.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            inv_tm = list(reversed(tm))
            inv_t = list(reversed(tt))
            norm_g = simple.normalize_string(tstring, g)
            appos_g = orchestrator.add_apostrophe(inv_t, norm_g[1])
            g = orchestrator.replaceTokens(g, inv_tm)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, True)
        return splitted_final_generated_outputs   
    
    def batch_generate_multiword_morph_merge(self, tagged_information_list, triple_counts):
        print('Running batch_generate_multiword_morph_merge')
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        tstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        debug_file = open(save_path + '/debug_out_generate_multiword_morph_merge.txt', 'w')
        for idx, tagged_information in enumerate(tagged_information_list):
            if idx % 1000 == 0:
                print(idx)
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            all_tagged_triples.extend(tagged_triples)
            for tt in tagged_triples:
                tstring = ' '.join(tt)
                tstring_list.append(tstring)
                #tinput = simple.transform_input(tstring, ner=False)
                #tinput_list.append(tinput)
                #debug_file.write(tinput.rstrip() + '\n')
        
        print('Running transform_input_list')
        tinput_list = simple.transform_input_list(tstring_list, ner=False)
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_merge_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        print('Length ' + str(len(tinput_list)))
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        generated_list = orchestrator.generate_multiword_morph_merge('####'.join(tinput_list))
        generated_list = generated_list.split('####')
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        print('Len generated_list' , len(generated_list))
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_generate_multiword_morph_merge.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            norm_g = simple.normalize_string(tstring, g)
            appos_g = orchestrator.add_apostrophe(tt, norm_g[1])
            g = orchestrator.replaceTokens(g, tm)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, True)
        return splitted_final_generated_outputs  
    
    def batch_generate_multiword_morph_merge_inv(self, tagged_information_list, triple_counts):
        print('Running: batch_generate_multiword_morph_merge_inv' )
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        tstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        debug_file = open(save_path + '/debug_generate_multiword_morph_merge.txt', 'w')
        for tagged_information in tagged_information_list:
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            all_tagged_triples.extend(tagged_triples)
            for tt in tagged_triples:
                inv_t = list(reversed(tt))
                tstring = ' '.join(inv_t)
                tstring_list.append(tstring)
                #tinput = simple.transform_input(tstring, ner=False)
                #tinput_list.append(tinput)
                #debug_file.write(tinput.rstrip() + '\n')
        
        
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        tinput_list = simple.transform_input_list(tstring_list, ner=False)
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_merge_inv_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        print('Running model')
        generated_list = orchestrator.generate_multiword_morph_merge('####'.join(tinput_list))
        generated_list = generated_list.split('####')
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        print('Len generated_list' , len(generated_list))
        final_generated_outputs = []
        
        ofile = open(save_path + '/batch_generate_multiword_morph_merge_inv.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            inv_tm = list(reversed(tm))
            inv_t = list(reversed(tt))
            norm_g = simple.normalize_string(tstring, g)
            appos_g = orchestrator.add_apostrophe(inv_t, norm_g[1])
            g = orchestrator.replaceTokens(g, inv_tm)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, True)
        return splitted_final_generated_outputs 
    
    
    def batch_generate_with_multiword(self, tagged_information_list, triple_counts):
        print('Running batch_generate_with_multiword')
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        mtstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        #all_tagged_triples = []
        debug_file = open(save_path + '/debug.txt', 'w')
        for idx, tagged_information in enumerate(tagged_information_list):
            if idx % 1000 == 0:
                print(idx)
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            #all_tagged_triples.extend(tagged_triples)
            for idx2, mtt in enumerate(modified_tag_triples):
                #print(idx2)
                mtstring = ' || '.join(mtt)
                mtstring_list.append(mtstring)
                tinput = simple.transform_input(mtstring, ner=False)
                tinput_list.append(tinput)
                #debug_file.write(tinput.rstrip() + '\n')
        
        
        
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        print('Running model')
        generated_list = orchestrator.generate_with_multiword('####'.join(tinput_list))
        generated_list = generated_list.split('####')
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        print('Len generated_list' , len(generated_list))
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_generate_with_multiword.txt', 'w')
        print(len(mtstring_list), len(generated_list), len(all_tag_maps), len(all_modified_tag_triples))
        for mtstring, g, tm, mtt in zip(mtstring_list, generated_list, all_tag_maps, all_modified_tag_triples):
            norm_g = simple.normalize_string(mtstring, g)
            appos_g = orchestrator.add_apostrophe(mtt, norm_g[1])
            g = orchestrator.replaceTokens(g, tm)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, True)
        return splitted_final_generated_outputs  
    
    
    def generate(self, tagged_information_list, triple_counts, modules_to_run='all'):
        config = self.config
        orchestrator = self.orchestrator
        dataset_file = config['dataset_file']
        save_path_generate = config['save_path_generate']
        
        if path.exists(save_path_generate):
            print('Save directory %s already exist'% (save_path_generate))
            sys.exit(0)
        else:
            print('Creating directory: ', save_path_generate)
            os.mkdir(save_path_generate)
        '''
        if modules_to_run == 'all':
            self.batch_generate_multiword_morph_simple(tagged_information_list, triple_counts)
            self.batch_generate_multiword_morph_simple_inv(tagged_information_list, triple_counts)
            self.batch_generate_multiword_morph_merge(tagged_information_list, triple_counts)
            self.batch_generate_multiword_morph_merge_inv(tagged_information_list, triple_counts)
            self.batch_generate_with_multiword(tagged_information_list, triple_counts)
        '''
        function_list = [self.batch_generate_multiword_morph_simple_inv, self.batch_generate_multiword_morph_merge]
        #function_list = [self.batch_generate_multiword_morph_simple,self.batch_generate_multiword_morph_simple_inv,self.batch_generate_multiword_morph_merge,self.batch_generate_multiword_morph_merge_inv,self.batch_generate_with_multiword]
        def runInParallel(fns):
            proc = []
            for fn in fns:
                print('Running in parallel: ', fn.__name__)
                p = Process(target=fn, args=(tagged_information_list, triple_counts))
                p.start()
                proc.append(p)
            for p in proc:
                p.join()
        
        runInParallel(function_list)
        
    def compounding(self, tagged_information_list, triple_counts):
        filenames = ['out_generate_multiword_morph_simple.txt','out_batch_generate_multiword_morph_simple_inv.txt','out_generate_multiword_morph_merge.txt','batch_generate_multiword_morph_merge_inv.txt','out_generate_with_multiword.txt']
        config = self.config
        orchestrator = self.orchestrator
        save_path_generate = config['save_path_generate']
        all_tag_maps, all_modified_tag_triples, all_tagged_triples = self.extract_tagged_information(tagged_information_list)
        all_outputs_dict = {}
        no_split_output_dict = {}
        for filename in filenames:
            lines = open(save_path_generate + '/' + filename, 'r').readlines()
            lines = [l.rstrip() for l in lines]
            splitted_final_generated_outputs = self.split_by_count(lines, triple_counts)
            all_outputs_dict[filename] = splitted_final_generated_outputs
            no_split_output_dict[filename] = lines 
        
        
        the_len = len(no_split_output_dict[next(iter(no_split_output_dict))])
        for key, value in no_split_output_dict.items():
            if the_len != len(no_split_output_dict[key]):
                print('All files should have same length, something wrong at ', key)
        
        dataset_file = config['dataset_file']
        lines = open(dataset_file, 'r').readlines()
        all_triples = []
        line_num = 0
        #Dump does not have raw triples as of now, so extracting it again
        for line, tagged_information, triple_count in zip(lines, tagged_information_list, triple_counts):
            line_num += 1
            text_triples = line.split('||')
            triples = orchestrator.getTriple(text_triples)
            all_triples.extend(triples)
        
        #assert len(lines) == len(tagged_information_list) == len(triple_counts) == len(all_triples) == len(all_tag_maps) == len(all_modified_tag_triples), 'Lengths of triples should match %d %d %d %d %d %d' %(len(lines), len(tagged_information_list), len(triple_counts), len(all_triples), len(all_tag_maps), len(all_modified_tag_triples))
        
        output_dict_for_ranking = {}
        ranked_outputs = []
        ranked_out_file = open(save_path_generate + '/ranked.txt', 'w')
        for idx in range(the_len):
            for key, value in no_split_output_dict.items():
                gline = no_split_output_dict[key][idx]
                output_dict_for_ranking[key] = [gline]
            t = all_triples[idx]
            tt = all_tagged_triples[idx]
            mtt = all_modified_tag_triples[idx]
            inp_original = t[0] + ' ' + tt[1] + ' ' + t[2]
            inp_modified = t[0] + ' ' + mtt[1] + ' ' + t[2]
            inp = [inp_original, inp_modified]
            print(inp, output_dict_for_ranking)
            ro = find_best(inp, output_dict_for_ranking, orchestrator.doc_sim, orchestrator.lmscorer)
            print(ro)
            ranked_out_file.write(str(ro).rstrip() + '\n')
        ranked_out_file.close() 
        #split and merge now
        return None
    
    
    def merge_sentences(self, input_file, outfile_basename, tagged_information_list, triple_counts):
        config = self.config
        orchestrator = self.orchestrator
        save_path_generate = config['save_path_generate']
        lines = open(input_file, 'r').readlines()
        lines = [l.rstrip() for l in lines]
        splitted_generated_outputs = self.split_by_count(lines, triple_counts)
        assert len(splitted_generated_outputs) == len(tagged_information_list), 'Lengths does not match'
        merged = []
        output_files = {}
        for idx, tagged_information in enumerate(tagged_information_list):
            print('************:: ', idx)
            generated_list = splitted_generated_outputs[idx]
            tag_maps = tagged_information['tag_maps']
            stuplelist = []
            assert len(generated_list) == len(tag_maps), 'generated_list and tag_maps length does not match'
            for g, tm in zip(generated_list, tag_maps):
                stuple = (tm , g)
                print(stuple)
                stuplelist.append(stuple)
            print('stuplelist', stuplelist)
            oo = merge_sentences(stuplelist)
            for mid, s in enumerate([e[1] for e in oo]):
                filename = outfile_basename + '_' + str(mid) + '.txt'
                if filename in output_files:
                    outfile = output_files[filename]
                else:
                    outfile = open(filename, 'a')
                    output_files[filename] = outfile
                outfile.write(s.rstrip() + '\n')

        for key, value in output_files.iteritems():
            print('Closing file: ', key)
            value.close()
    
    
    def extract_tagged_information(self, tagged_information_list):
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        for tagged_information in tagged_information_list:
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            all_tagged_triples.extend(tagged_triples)
        
        return all_tag_maps, all_modified_tag_triples, all_tagged_triples
    
    def check_data(self, tagged_information_list, triple_counts):
        config = self.config
        print('Cross checking loaded data count with dataset file...')
        dataset_file = config['dataset_file']
        lines = open(dataset_file, 'r').readlines()
        line_num = 0
        for line, tagged_information, triple_count in zip(lines, tagged_information_list, triple_counts):
            line_num += 1
            text_triples = line.split('||')
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            for idxtm, tm in enumerate(tag_maps):
                assert len(tm) == 2, 'Tag map %d Does not match line %d ' % (idxtm, line_num)
            num_text_triples = len(text_triples)
            num_tag_maps = len(tag_maps)
            num_mtt = len(modified_tag_triples)
            assert num_mtt == num_tag_maps == num_text_triples, 'Does not match line %d ' % (line_num)
    
    def load_tagged_data(self):
        config = self.config
        orchestrator = self.orchestrator
        dataset_file = config['dataset_file']
        save_path_tagging = config['save_path_tagging']
        tagged_information_filename = save_path_tagging + '/combined_tagged_data.jl'
        triple_counts_filename = save_path_tagging + '/combined_triple_counts.txt'
        
        tagged_information_file = open(tagged_information_filename, 'r')
        triple_counts_file = open(triple_counts_filename, 'r')
        print('Loading tagged data ...', tagged_information_filename, triple_counts_filename)
        triple_counts = []
        tagged_information_list = []
        tagged_information_list = tagged_information_file.readlines()
        triple_counts = triple_counts_file.readlines()
        tagged_information_list = [json.loads(t.rstrip()) for t in tagged_information_list]
        triple_counts = [int(tc.rstrip()) for tc in triple_counts]
        self.check_data(tagged_information_list, triple_counts)
        return tagged_information_list, triple_counts
 
    def maybe_create_directories(self):
        config = self.config
        orchestrator = self.orchestrator
        dataset_file = config['dataset_file']
        save_path_tagging = config['save_path_tagging']
        save_path_generate = config['save_path_generate']
     
         
      
            
def main():
    config_file = sys.argv[1]
    config = json.load(open(config_file))
    datasetProcessor = Dataset(config)
    #tagged_information_list, triple_counts = 
    #datasetProcessor.tag_dataset_parallel()
    tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
    input_file = '../biography_outputs_parallel/generated/out_generate_multiword_morph_simple.txt'
    outfile_basename = '../biography_outputs_parallel/out_generate_multiword_morph_simple_merged'
    datasetProcessor.merge_sentences(input_file,outfile_basename, tagged_information_list, triple_counts)
    #datasetProcessor.merge_tagged()
    #tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
    #outputs = datasetProcessor.batch_generate_multiword_morph_simple(tagged_information_list, triple_counts)
    #datasetProcessor.generate(tagged_information_list, triple_counts)
    #datasetProcessor.compounding(tagged_information_list, triple_counts)
     
    '''
    orchestrator = Struct2Text(config)
    dataset_file = config['dataset_file']
    lines = open(dataset_file, 'r').readlines()
    save_path = config['save_path']
    if path.exists(save_path):
        print('Save directory %s already exist'% (save_path))
        sys.exit(0)
    else:
        print('Creating directory: ', save_path)
        os.mkdir(save_path)
    print('Number of lines in datafile: ', len(lines))
    for idx, line in enumerate(lines):
        print('Running line number: ', idx)
        text_triples = line.split('||')
        ticks1 = time.time()
        orchestrator.generate_multiple(save_path, text_triples,  True, True, True, True, True)
        print "Number of ticks since 12:00am, January 1, 1970:", ticks1
        ticks = time.time()
        print "Number of ticks since 12:00am, January 1, 1970:", ticks
        break
    '''
    print('Done')

    

if __name__ == '__main__':
    main()
