#concat merge
import spacy
import sys
from os import path
import argparse

nlp = spacy.load('en_core_web_sm')

def tokenize(line):
    line = line.decode('unicode-escape')
    line.replace(u'\xe2\x80\x99',u'\'')
    doc = nlp(line)
    words = [token.text for token in doc]
    oline = ' '.join(words)
    oline = oline.rstrip().lower().encode('unicode-escape')
    return oline

def split_by_count(input_list, counts, debug=False):
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

def merge_sentences(input_file, outfile_name, triple_counts):
    if path.exists(outfile_name):
        print('Output file ' + str(outfile_name) + ' already exist')
        sys.exit(0)
    lines = open(input_file, 'r').readlines()
    lines = [l.rstrip() for l in lines]
    print('Number of lines' , len(lines))
    splitted_generated_outputs = split_by_count(lines, triple_counts)
    
    outfile = open(outfile_name, 'w')
    outfile_tokenized = open(outfile_name + '.tokenized', 'w')
    for idx, splitted in enumerate(splitted_generated_outputs):
        sentence = ' '.join(splitted)
        sentence_tokenized = tokenize(sentence)
        outfile.write(sentence.rstrip() + '\n')
        outfile_tokenized.write(sentence_tokenized.rstrip() + '\n')
    outfile.close()
    outfile_tokenized.close()

def get_args():
  args = argparse.ArgumentParser()
  args.add_argument(
    "--input_file",  
  )
  args.add_argument(
    "--triple_counts_file",  
  )
  args.add_argument(
    "--outfile_name"
  )
  args = args.parse_args()
  return args    

args = get_args()    

def main():
    input_file = args.input_file#sys.argv[1]
    triple_counts_file = args.triple_counts_file#sys.argv[2]
    outfile_name = args.outfile_name#sys.argv[3]
    triple_counts_file = open(triple_counts_file, 'r')
    triple_counts = triple_counts_file.readlines()
    triple_counts = [int(tc.rstrip()) for tc in triple_counts]
    merge_sentences(input_file, outfile_name, triple_counts)
        
    
if __name__ == '__main__':
    main()
        
        
    
     
    
