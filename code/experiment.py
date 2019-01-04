from TextClassifier import TextClassifier
import time
from ner import *
from postprocess import *
import cPickle
#from ApproxNNClient import *
#from S2SClient import *
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
from orchestrator_multi import Struct2Text
from anaphora_replacer.pronanaphora import *
import shutil
import os
import ast
import argparse


            
class Dataset():
    def __init__(self, config):
        self.config = config
        self.orchestrator = Struct2Text(self.config, False)
        #self.gendermodel = PronounReplacer(0000, False)
    
    ###########################TAGGING PART########################
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
            tagged_triples, modified_tag_triples, tag_maps = self.orchestrator.tag_triples(triples, get_class_labels)
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
            tagged_information['triples'] = triples
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
            
    def tag_dataset_parallel(self, n = 1000):
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

    def extract_tagged_information(self, tagged_information_list):
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        all_triples = []
        for tagged_information in tagged_information_list:
            tagged_triples = tagged_information['tagged_triples']
            modified_tag_triples = tagged_information['modified_tag_triples']
            tag_maps = tagged_information['tag_maps']
            triples = tagged_information['triples']
            all_triples.extend(triples)
            all_tag_maps.extend(tag_maps)
            all_modified_tag_triples.extend(modified_tag_triples)
            all_tagged_triples.extend(tagged_triples)
        
        return all_triples, all_tag_maps, all_modified_tag_triples, all_tagged_triples 
    
    ###################################################
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
    
    def batch_generate_multiword_morph_simple(self, tagged_information_list, triple_counts, post_process_only=False, readload_transformed = False):
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
        
        if not post_process_only:
            tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_tstring.joblib'
            if readload_transformed:
                print('Loading tstring dump from', tstring_list_file)
                tinput_list = joblib.load(tstring_list_file)
            else:
                tinput_list = simple.transform_input_list(tstring_list, ner=False)
                joblib.dump(tinput_list, tstring_list_file)
            
            debug_file.write('Length ' + str(len(tinput_list)) + '\n')
            generated_list = orchestrator.generate_multiword_morph_simple('####'.join(tinput_list))
            generated_list = generated_list.split('####')
            raw_generate_filename = save_path + '/generate_multiword_morph_simple.raw'
            raw_generate_file = open(raw_generate_filename, 'w')
            for g in generated_list:
                raw_generate_file.write(g.rstrip() + '\n')
            raw_generate_file.close()
        else:
            raw_generate_filename = save_path + '/generate_multiword_morph_simple.raw'
            print('Loading raw generated file from ', raw_generate_filename)
            generated_list = open(raw_generate_filename, 'r').readlines()
            generated_list = [g.rstrip() for g in generated_list]
        

        print('Len generated_list' , len(generated_list))
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_generate_multiword_morph_simple.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            norm_g = simple.normalize_string(tstring, g)
            g = orchestrator.add_apostrophe(tt, norm_g[1])
            g = orchestrator.replaceTokens(g, tm)
            g = orchestrator.add_apostrophe_preranker(tm, g)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, False)
        return splitted_final_generated_outputs        

    def batch_generate_multiword_morph_simple_inv(self, tagged_information_list, triple_counts, post_process_only=False, readload_transformed = False):
        print('Running: batch_generate_multiword_morph_simple_inv' )
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        tstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        debug_file = open(save_path + '/debug_generate_multiword_morph_simple_inv.txt', 'w')
        for idx, tagged_information in enumerate(tagged_information_list):
            if idx % 5000 == 0:
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
          
        if not post_process_only:
            print('Running transform_input_list')
            tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_inv_tstring.joblib'
            if readload_transformed:
                print('Loading tstring dump from', tstring_list_file)
                tinput_list = joblib.load(tstring_list_file)
            else:
                tinput_list = simple.transform_input_list(tstring_list, ner=False)
                joblib.dump(tinput_list, tstring_list_file)
            
            print('Length ' + str(len(tinput_list)))
            debug_file.write('Length ' + str(len(tinput_list)) + '\n')
            generated_list = orchestrator.generate_multiword_morph_simple('####'.join(tinput_list))
            generated_list = generated_list.split('####')
            raw_generate_filename = save_path + '/generate_multiword_morph_simple_inv.raw'
            raw_generate_file = open(raw_generate_filename, 'w')
            for g in generated_list:
                raw_generate_file.write(g.rstrip() + '\n')
            raw_generate_file.close()
        else:
            raw_generate_filename = save_path + '/generate_multiword_morph_simple_inv.raw'
            print('Loading raw generated file from ', raw_generate_filename)
            generated_list = open(raw_generate_filename, 'r').readlines()
            generated_list = [g.rstrip() for g in generated_list]
        '''
        tinput_list = simple.transform_input_list(tstring_list, ner=False)
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_inv_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        '''
        print('Len generated_list' , len(generated_list))
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_batch_generate_multiword_morph_simple_inv.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            inv_tm = list(reversed(tm))
            inv_t = list(reversed(tt))
            norm_g = simple.normalize_string(tstring, g)
            g = orchestrator.add_apostrophe(inv_t, norm_g[1])
            g = orchestrator.replaceTokens(g, inv_tm)
            g = orchestrator.add_apostrophe_preranker(inv_tm, g)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, False)
        return splitted_final_generated_outputs   
    
    def batch_generate_multiword_morph_merge(self, tagged_information_list, triple_counts,post_process_only=False, readload_transformed = False):
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
            if idx % 5000 == 0:
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
        
        if not post_process_only:
            print('Running transform_input_list')
            tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_merge_tstring.joblib'
            if readload_transformed:
                print('Loading tstring dump from', tstring_list_file)
                tinput_list = joblib.load(tstring_list_file)
            else:
                tinput_list = merge.transform_input_list(tstring_list, ner=False)[0]
                joblib.dump(tinput_list, tstring_list_file)
            
            print('Length ' + str(len(tinput_list)))
            debug_file.write('Length ' + str(len(tinput_list)) + '\n')
            generated_list = orchestrator.generate_multiword_morph_merge('####'.join(tinput_list))
            generated_list = generated_list.split('####')
            raw_generate_filename = save_path + '/batch_generate_multiword_morph_merge.raw'
            raw_generate_file = open(raw_generate_filename, 'w')
            for g in generated_list:
                raw_generate_file.write(g.rstrip() + '\n')
            raw_generate_file.close()
        else:
            raw_generate_filename = save_path + '/batch_generate_multiword_morph_merge.raw'
            print('Loading raw generated file from ', raw_generate_filename)
            generated_list = open(raw_generate_filename, 'r').readlines()
            generated_list = [g.rstrip() for g in generated_list]
        
        '''
        print('Running transform_input_list')
        tinput_list = merge.transform_input_list(tstring_list, ner=False)[0]
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_merge_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        print('Length ' + str(len(tinput_list)))
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        generated_list = orchestrator.generate_multiword_morph_merge('####'.join(tinput_list))
        generated_list = generated_list.split('####')
        '''
        
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        print('Len generated_list' , len(generated_list))
        
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_generate_multiword_morph_merge.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            norm_g = merge.normalize_string(tstring, g)
            g = orchestrator.add_apostrophe(tt, norm_g[1])
            g = orchestrator.replaceTokens(g, tm)
            g = orchestrator.add_apostrophe_preranker(tm, g)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, False)
        return splitted_final_generated_outputs  
    
    def batch_generate_multiword_morph_merge_inv(self, tagged_information_list, triple_counts, post_process_only=False, readload_transformed = False):
        print('Running: batch_generate_multiword_morph_merge_inv' )
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        save_path_transformed = self.config['save_path_transformed']
        tinput_list = []
        tstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        all_tagged_triples = []
        debug_file = open(save_path + '/debug_generate_multiword_morph_merge_inv.txt', 'w')
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
        
        
        if not post_process_only:
            print('Running transform_input_list')
            tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_merge_inv_tstring.joblib'
            if readload_transformed:
                print('Loading tstring dump from', tstring_list_file)
                tinput_list = joblib.load(tstring_list_file)
            else:
                tinput_list = merge.transform_input_list(tstring_list, ner=False)[0]
                joblib.dump(tinput_list, tstring_list_file)
            
            print('Length ' + str(len(tinput_list)))
            debug_file.write('Length ' + str(len(tinput_list)) + '\n')
            generated_list = orchestrator.generate_multiword_morph_merge('####'.join(tinput_list))
            generated_list = generated_list.split('####')
            raw_generate_filename = save_path + '/batch_generate_multiword_morph_merge_inv.raw'
            raw_generate_file = open(raw_generate_filename, 'w')
            for g in generated_list:
                raw_generate_file.write(g.rstrip() + '\n')
            raw_generate_file.close()
        else:
            raw_generate_filename = save_path + '/batch_generate_multiword_morph_merge_inv.raw'
            print('Loading raw generated file from ', raw_generate_filename)
            generated_list = open(raw_generate_filename, 'r').readlines()
            generated_list = [g.rstrip() for g in generated_list]

        '''
        tinput_list = merge.transform_input_list(tstring_list, ner=False)[0]
        debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_merge_inv_tstring.joblib'
        joblib.dump(tinput_list, tstring_list_file)
        print('Running model')
        generated_list = orchestrator.generate_multiword_morph_merge('####'.join(tinput_list))
        generated_list = generated_list.split('####')
        '''
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        print('Len generated_list' , len(generated_list))
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_batch_generate_multiword_morph_merge_inv.txt', 'w')
        print(len(tstring_list), len(generated_list), len(all_tag_maps), len(all_tagged_triples))
        for tstring, g, tm, tt in zip(tstring_list, generated_list, all_tag_maps, all_tagged_triples):
            inv_tm = list(reversed(tm))
            inv_t = list(reversed(tt))
            norm_g = merge.normalize_string(tstring, g)
            g = orchestrator.add_apostrophe(inv_t, norm_g[1])
            g = orchestrator.replaceTokens(g, inv_tm)
            g = orchestrator.add_apostrophe_preranker(inv_tm, g)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, False)
        return splitted_final_generated_outputs 
    
    
    def batch_generate_with_multiword(self, tagged_information_list, triple_counts, post_process_only=False):
        print('Running batch_generate_with_multiword')
        orchestrator = self.orchestrator
        save_path = self.config['save_path_generate']
        mtstring_list = []
        all_tag_maps = []
        all_modified_tag_triples = []
        #all_tagged_triples = []
        debug_file = open(save_path + '/debug.txt', 'w')
        for idx, tagged_information in enumerate(tagged_information_list):
            if idx % 500 == 0:
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
                # tinput = simple.transform_input(mtstring, ner=False)
                # tinput_list.append(tinput)
                #debug_file.write(tinput.rstrip() + '\n')
        
        if not post_process_only:
            print('Running transform_input_list')
            generated_list = orchestrator.generate_with_multiword('####'.join(mtstring_list))
            generated_list = generated_list.split('####')
            raw_generate_filename = save_path + '/out_generate_with_multiword.raw'
            raw_generate_file = open(raw_generate_filename, 'w')
            for g in generated_list:
                raw_generate_file.write(g.rstrip() + '\n')
            raw_generate_file.close()
        else:
            raw_generate_filename = save_path + '/out_generate_with_multiword.raw'
            print('Loading raw generated file from ', raw_generate_filename)
            generated_list = open(raw_generate_filename, 'r').readlines()
            generated_list = [g.rstrip() for g in generated_list]
        
        # debug_file.write('Length ' + str(len(tinput_list)) + '\n')
        '''
        print('Running model')
        generated_list = orchestrator.generate_with_multiword('####'.join(mtstring_list))
        generated_list = generated_list.split('####')
        '''
        debug_file.write('generated_list length ' + str(len(generated_list)) + '\n')
        print('Len generated_list' , len(generated_list))
        final_generated_outputs = []
        
        ofile = open(save_path + '/out_generate_with_multiword.txt', 'w')
        print(len(mtstring_list), len(generated_list), len(all_tag_maps), len(all_modified_tag_triples))
        for mtstring, g, tm, mtt in zip(mtstring_list, generated_list, all_tag_maps, all_modified_tag_triples):
            # norm_g = simple.normalize_string(mtstring, g)
            g = orchestrator.add_apostrophe(mtt, g)
            g = orchestrator.replaceTokens(g, tm)
            g = orchestrator.add_apostrophe_preranker(tm, g)
            final_generated_outputs.append(g)
            ofile.write(g + '\n')
        
        ofile.close()
        print('len final_generated_outputs ', len(final_generated_outputs) )           
        splitted_final_generated_outputs = self.split_by_count(final_generated_outputs, triple_counts, False)
        return splitted_final_generated_outputs  
    
    
    def generate(self, tagged_information_list, triple_counts, post_process_only=False, readload_transformed = False):
        modules_to_run = 'all'
        config = self.config
        save_path_generate = config['save_path_generate']
        save_path_transformed= config['save_path_transformed']
        
        if path.exists(save_path_generate):
            print('Save directory %s already exist'% (save_path_generate))
            print('Y to continue, WARNING: IT MAY OVERWRITE FILES')
            y = raw_input()
            if y != 'Y':
                print('Exiting...')
                sys.exit(0)
        else:
            print('Creating directory: ', save_path_generate)
            os.mkdir(save_path_generate)
        
        
        if path.exists(save_path_transformed):
            print('Save directory %s already exist'% (save_path_transformed))
            print('Y to continue, WARNING: IT MAY OVERWRITE FILES')
            if not readload_transformed:
                print('Will not reload, readload_transformed  is ', readload_transformed)
            y = raw_input()
            if y != 'Y':
                print('Exiting...')
                sys.exit(0)
        else:
            print('Creating directory: ', save_path_transformed)
            os.mkdir(save_path_transformed)
        
        
        if modules_to_run == 'all':
            #batch_generate_multiword_morph_simple
            self.batch_generate_multiword_morph_simple(tagged_information_list, triple_counts,post_process_only, readload_transformed)
            #self.batch_generate_multiword_morph_simple_inv(tagged_information_list, triple_counts, post_process_only, readload_transformed)
            self.batch_generate_multiword_morph_merge(tagged_information_list, triple_counts, post_process_only, readload_transformed)
            #self.batch_generate_multiword_morph_merge_inv(tagged_information_list, triple_counts, post_process_only, readload_transformed)
            self.batch_generate_with_multiword(tagged_information_list, triple_counts, post_process_only)
        '''
        #function_list = [self.batch_generate_multiword_morph_simple_inv, self.batch_generate_multiword_morph_merge]
        function_list = [self.batch_generate_multiword_morph_simple,self.batch_generate_multiword_morph_simple_inv,self.batch_generate_multiword_morph_merge,self.batch_generate_multiword_morph_merge_inv,self.batch_generate_with_multiword]
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
        '''
        return None
        
    def ranker(self, tagged_information_list, triple_counts, to_rank_filename, default_key):
        '''filenames = ['out_generate_multiword_morph_simple.txt','out_batch_generate_multiword_morph_simple_inv.txt', \
        'out_generate_multiword_morph_merge.txt','out_batch_generate_multiword_morph_merge_inv.txt',\
        'out_generate_with_multiword.txt']
        '''
        #filenames = ['out_batch_generate_multiword_morph_merge_inv.txt', 'out_generate_multiword_morph_merge.txt', 'out_generate_with_multiword.txt']
        to_rank_files = open(to_rank_filename, 'r').readlines()
        to_rank_files = [f.rstrip() for f in to_rank_files]
        print('Will rank from sentences from files: ', to_rank_files)
        print('Number of files: ', len(to_rank_files))
        config = self.config
        orchestrator = self.orchestrator
        save_path_generate = config['save_path_generate']
        all_triples, all_tag_maps, all_modified_tag_triples, all_tagged_triples = self.extract_tagged_information(tagged_information_list)
        all_outputs_dict = {}
        no_split_output_dict = {}
        for filename in to_rank_files:
            lines = open(save_path_generate + '/' + filename, 'r').readlines()
            lines = [l.rstrip() for l in lines]
            splitted_final_generated_outputs = self.split_by_count(lines, triple_counts)
            all_outputs_dict[filename] = splitted_final_generated_outputs
            no_split_output_dict[filename] = lines 
        
        
        the_len = len(no_split_output_dict[next(iter(no_split_output_dict))])
        for key, _ in no_split_output_dict.items():
            if the_len != len(no_split_output_dict[key]):
                print('All files should have same length, something wrong at ', key)
                sys.exit(0)
        
        '''
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
        '''
        
        assert len(all_triples) == len(all_tag_maps) == len(all_modified_tag_triples), 'Lengths of triples should match %d %d %d %d %d %d' %(len(lines), len(tagged_information_list), len(triple_counts), len(all_triples), len(all_tag_maps), len(all_modified_tag_triples))
        
        ranked_out_file = open(save_path_generate + '/ranked.txt', 'w')
        ranked_sentences_file = open(save_path_generate + '/ranked_sentences.txt', 'w')
        for idx in range(the_len):
            output_dict_for_ranking = {}
            for key, value in no_split_output_dict.items():
                gline = no_split_output_dict[key][idx]
                output_dict_for_ranking[key] = [gline]
            t = all_triples[idx]
            tt = all_tagged_triples[idx]
            mtt = all_modified_tag_triples[idx]
            '''
            Copied from orchestrator
            inp_original = t[0] + '\t' + tt[1] + '\t' + t[2]
            inp_modified = t[0] + '\t' + mtt[1] + '\t' + t[2]
            '''
            inp_original = t[0] + '\t' + tt[1] + '\t' + t[2]
            inp_modified = t[0] + '\t' + mtt[1] + '\t' + t[2]
            inp = [inp_original, inp_modified]
            print(inp, output_dict_for_ranking)
            ro = find_best(inp, output_dict_for_ranking, orchestrator.doc_sim, orchestrator.nlp, orchestrator.lmscorer, default_key)
            print(ro)
            rsent = ro[0]
            ranked_sentences_file.write(rsent.rstrip() + '\n')
            ranked_out_file.write(str(ro).rstrip() + '\n')
        ranked_out_file.close() 
        ranked_sentences_file.close()
        #split and merge now
        return None
    
    
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
  
    def merge_sentences(self, input_file, is_ranked_file, inv_key_phrase , to_be_reversed, tagged_information_list, triple_counts, take_it_or_not_list, save_path_merged):
        if is_ranked_file and to_be_reversed:
            print('Both options should be used for different type of files, both true is not handled properly.')
            print('is_ranked_file will reverse for outputs with system containing phrase %s.',  inv_key_phrase)
            print("Ranked file line format: ['sentence', 'system', 'score']")
            print('to_be_reversed will reverse for whole file in input.')
            sys.exit(0)
       
        print('Merging sentences from ', input_file)
        config = self.config
        orchestrator = self.orchestrator
        #save_path_merged = config['save_path_merged']
        if path.exists(save_path_merged):
            print('Save directory %s already exist'% (save_path_merged))
            print('Y to continue, WARNING: IT WILL OVERWRITE FILES')
            y = raw_input()
            if y != 'Y':
                print('Exiting...')
                sys.exit(0)
            '''
            files = os.listdir(save_path_merged)
            dest1 = os.path.join(save_path_merged, 'tmp')
            os.mkdir(dest1)
            for f in files:
                print('Moving ', f)
                shutil.move(save_path_merged+ '/' +f, dest1)
            '''
        else:
            print('Creating directory: ', save_path_merged)
            os.mkdir(save_path_merged)
        

        outfile_basename = path.splitext(path.basename(input_file))[0]
        lines = open(input_file, 'r').readlines()
        lines = [l.rstrip() for l in lines]
        print('Number of lines' , lines)
        
        splitted_generated_outputs = self.split_by_count(lines, triple_counts)
        if take_it_or_not_list == None:
          take_it_or_not_list = [1] * len(lines)
        splitted_take_it_or_not_list = self.split_by_count(take_it_or_not_list, triple_counts)
        assert len(splitted_generated_outputs) == len(tagged_information_list), 'Lengths does not match'
        print('Number of tables: ', len(splitted_generated_outputs))
        merged = []
        output_files = {}
        filenameinp = save_path_merged + '/' + 'inputs.txt'
        ifile =open(filenameinp, 'w')
        for idx, tagged_information in enumerate(tagged_information_list):
            print('************:: ', idx)
            generated_list = splitted_generated_outputs[idx]
            take_it_or_not_list = splitted_take_it_or_not_list[idx]
            tag_maps = tagged_information['tag_maps']
            stuplelist = []
            assert len(generated_list) == len(tag_maps) == len(take_it_or_not_list), 'generated_list and tag_maps length does not match'
            for g, tm, flag in zip(generated_list, tag_maps, take_it_or_not_list):
                if flag == 0:
                    continue
                if is_ranked_file:
                    gl =  ast.literal_eval(g)
                    #looks like: ['philippe adnot term started to 24 september 1989 july 1990 1982', 'out_generate_multiword_morph_merge.txt', -1000]
                    assert len(gl) == 3, 'Tried to parse %s \n But length did not matched.' % (g)
                    g = gl[0]
                    systemname = gl[1]
                    if inv_key_phrase in systemname:
                        print('Reversed')
                        tm = list(reversed(tm))
                elif to_be_reversed:
                    tm = list(reversed(tm))
                stuple = (tm , g)
                #print(stuple)
                stuplelist.append(stuple)
            print('stuplelist', stuplelist)
            if len(stuplelist) < 1:
                #This needs to be fixed, should not happen
                g = generated_list[0]
                tm = tag_maps[0]
                stuple = (tm , g)
                stuplelist.append(stuple)
            oo = merge_sentences(stuplelist, punctProcess=True)
            coref_out = [' '.join(orchestrator.gendermodel.replace_pronoun(e[0], tag_maps)) for e in oo]
            #ifilenameinp = save_path_merged + '/' + 'inputs.txt'
            #ifile =open(filenameinp, 'a')
            print(oo)
            ifile.write(str(stuplelist).rstrip() + '\n')
            for mid, s in enumerate(coref_out):
                filename = save_path_merged + '/' + outfile_basename + '_' + str(mid) + '.txt'
                if filename in output_files:
                    outfile = output_files[filename]
                else:
                    outfile = open(filename, 'a')
                    output_files[filename] = outfile
                outfile.write(s.rstrip() + '\n')
                print(s)

        for key, value in output_files.iteritems():
            print('Closing file: ', key)
            value.close()
        
  
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


def get_args():
  args = argparse.ArgumentParser()
  args.add_argument(
    "--config_file",  
  )
  args.add_argument(
    "--module",  
  )
  args.add_argument(
    "--post_process_only"
  )
  args.add_argument(
    "--readload_transformed" 
  )
  args.add_argument(
    "--to_rank_filename", 
  )
  args.add_argument(
    "--default_key", 
  )
  args.add_argument(
    "--merge_input_file", 
  )
  args.add_argument(
    "--take_it_or_not_list_file", default=None
  )
  args.add_argument(
    "--save_path_merged", 
  )
  args.add_argument(
    "--is_ranked_file"
  )
  args.add_argument(
    "--to_be_reversed"
  )
  args = args.parse_args()
  return args



def main():
    args = get_args()
    config_file = args.config_file#sys.argv[1]
    module = args.module#sys.argv[2]
    config = json.load(open(config_file))
    datasetProcessor = Dataset(config)
    #tagged_information_list, triple_counts = 
    #datasetProcessor.tag_dataset_parallel()
    #datasetProcessor.merge_tagged()
    #tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
    #outputs = datasetProcessor.batch_generate_multiword_morph_simple(tagged_information_list, triple_counts)
    
    save_path = config['save_path']
    if not path.exists(save_path):
      print('Creating directory: ', save_path)
      os.mkdir(save_path)
    if module == 'tag':
        datasetProcessor.tag_dataset_parallel(50)
    elif module == 'generate':
        tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
        post_process_only = args.post_process_only  == 'true'#sys.argv[3].lower() == 'true'
        readload_transformed = args.readload_transformed  == 'true'#sys.argv[4].lower() == 'true'
        datasetProcessor.generate(tagged_information_list, triple_counts, post_process_only, readload_transformed)
    elif module == 'post_process':
        tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
        datasetProcessor.generate(tagged_information_list, triple_counts, True)
    elif module == 'ranker':
        to_rank_filename = args.to_rank_filename#sys.argv[3]
        default_key = args.default_key#sys.argv[4]
        tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
        datasetProcessor.ranker(tagged_information_list, triple_counts, to_rank_filename, default_key)
    elif module == 'merge':
        input_file = args.merge_input_file#sys.argv[3]
        take_it_or_not_list_file = args.take_it_or_not_list_file#sys.argv[4]
        save_path_merged = args.save_path_merged#sys.argv[5]
        is_ranked_file = args.is_ranked_file  == 'true' #sys.argv[6].lower() == 'true'
        to_be_reversed = args.to_be_reversed  == 'true' #sys.argv[7].lower() == 'true'
        inv_key_phrase = 'inv'
        if take_it_or_not_list_file is None:
          take_it_or_not_list = None
        else:
          take_it_or_not_list = open(take_it_or_not_list_file, 'r').readlines()
          take_it_or_not_list = [int(i) for i in take_it_or_not_list]
        tagged_information_list, triple_counts = datasetProcessor.load_tagged_data()
        #input_file = '../biography_outputs_parallel/generated_filtered/out_generate_with_multiword.txt'
        datasetProcessor.merge_sentences(input_file, is_ranked_file, inv_key_phrase , to_be_reversed, tagged_information_list, triple_counts, take_it_or_not_list, save_path_merged)
    else:
        print('You need to pass a module to run...')
        sys.exit(0)
     
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
