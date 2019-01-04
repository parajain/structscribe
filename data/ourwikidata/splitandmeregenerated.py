#our wiki table dataset has rows which is generated separately, splitandmeregenerated just concats all the rows to create a paragraph
#this split is not triple level, each row is already splitted into triples by main experiment code

import sys
import os.path as path

def merge(lines):
    merged = ' '.join(lines)
    return merged

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

input_file = sys.argv[1]
input_count_file = sys.argv[2]
output_file = sys.argv[3]
if path.exists(output_file):
    print('Output file ' + str(output_file) + ' already exist')
    sys.exit(0)

input_lines = open(input_file, 'r').readlines()
input_counts = open(input_count_file, 'r').readlines()

output_file = open(output_file, 'w')
input_lines = [l.rstrip() for l in input_lines]
input_counts  = [int(tc.rstrip()) for tc in input_counts]

splitted_final_generated_outputs = split_by_count(input_lines, input_counts)

for lines in splitted_final_generated_outputs:
    outline = merge(lines)
    output_file.write(outline + '\n')

output_file.close()

