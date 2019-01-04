#generation script
from orchestrator_multi import *
import json
import joblib
import os


from experiment import *
import json
import joblib
import os

def extract_tagged_information(tagged_information_list):
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

def load_tagged_data(config):
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
    return tagged_information_list, triple_counts

def generate_multiword_morph_simple(orchestrator, config, outdir):
    save_path_transformed = config['save_path_transformed']
    tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_tstring.joblib'
    print('Loading tstring dump from', tstring_list_file)
    tinput_list = joblib.load(tstring_list_file)
    print('Length ' + str(len(tinput_list)) + '\n')
    generated_list = orchestrator.generate_multiword_morph_simple('####'.join(tinput_list))
    if path.exists(outdir):
        print('Save directory %s already exist'% (outdir))
    else:
        print('Creating directory: ', outdir)
        os.mkdir(outdir)
    generated_list = generated_list.split('####')
    print('Len generated_list' , len(generated_list))
    ofilename_up = outdir + '/raw_generated_multiword_morph_simple.joblib'
    #if path.exists(outdir):
    #    print('File exist ', ofilename_up)
    joblib.dump(generated_list, ofilename_up)
    print('Dumped before postprocess')

def generate_multiword_morph_simple_inv(orchestrator, config, outdir):
    save_path_transformed = config['save_path_transformed']
    tstring_list_file = save_path_transformed + '/batch_generate_multiword_morph_simple_inv_tstring.joblib'
    print('Loading tstring dump from', tstring_list_file)
    tinput_list = joblib.load(tstring_list_file)
    print('Length ' + str(len(tinput_list)) + '\n')
    generated_list = orchestrator.generate_multiword_morph_simple('####'.join(tinput_list))
    if path.exists(outdir):
        print('Save directory %s already exist'% (outdir))
    else:
        print('Creating directory: ', outdir)
        os.mkdir(outdir)
    generated_list = generated_list.split('####')
    print('Len generated_list' , len(generated_list))
    ofilename_up = outdir + '/raw_generated_multiword_morph_simple_inv.joblib'
    #if path.exists(outdir):
    #    print('File exist ', ofilename_up)
    joblib.dump(generated_list, ofilename_up)
    print('Dumped before postprocess')


def main():
    config_file = sys.argv[1]
    outdir = sys.argv[2]
    module = sys.argv[3]
    config = json.load(open(config_file))
    #tagged_information_list, triple_counts = load_tagged_data(config)
    orchestrator = Struct2Text(config)
    if module == 'multiword_morph_simple':
        generate_multiword_morph_simple(orchestrator, config, outdir)
    elif module == 'multiword_morph_simple_inv':
        generate_multiword_morph_simple_inv(orchestrator, config, outdir)
    else:
        print('Module not matched!')


if __name__ == '__main__':
    main()