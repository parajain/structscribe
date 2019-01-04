#!/bin/sh
echo "Running tagger.."
python experiment.py --config_file configurations/ourwikidata.json --module tag
echo "Running genetation..."
python experiment.py --config_file configurations/ourwikidata.json --module generate --post_process_only false --readload_transformed false
echo "Running Ranker..."
python experiment.py --config_file configurations/ourwikidata.json --module ranker --to_rank_filename configurations/to_rank_ourwikidata.files --default_key out_generate_multiword_morph_merge.txt
echo "Running merge..."
python experiment.py --config_file configurations/ourwikidata.json  --module merge --merge_input_file ../data/ourwikidata_output/generated/ranked.txt --save_path_merged ../data/ourwikidata_output/merged_ranked --is_ranked_file true --to_be_reversed false
echo "Combining row by row outputs to create table output..."
python splitandmeregenerated.py --input_file ../data/ourwikidata_output/merged_ranked/ranked_0.txt --input_count_file ../data/ourwikidata/outwikitable.ourformat.row.count --output_file ../data/ourwikidata_output/merged_ranked/table_level_merge.txt
echo 'Tokenizing for BLEU...'
python postprocess_for_bleu.py ../data/ourwikidata_output/merged_ranked/table_level_merge.txt ../data/ourwikidata_output/merged_ranked/table_level_merge.txt.tokenized
echo 'Calculating results...'
nlg-eval --hypothesis=../data/ourwikidata_output/merged_ranked/table_level_merge.txt.tokenized --references=../data/ourwikidata/ref1.txt.tokenized --references=../data/ourwikidata/ref2.txt.tokenized --references=../data/ourwikidata/ref3.txt.tokenized --references=../data/ourwikidata/ref4.txt.tokenized
echo 'Running string concat merge..'
echo 'Creating dir.. at ../data/ourwikidata_output/simple_merged'
mkdir ../data/ourwikidata_output/simple_merged
python concat_merge.py --input_file ../data/ourwikidata_output/generated/ranked_sentences.txt --triple_counts_file ../data/ourwikidata_output/tagged/combined_triple_counts.txt --outfile_name ../data/ourwikidata_output/simple_merged/simple_concat_merge.txt
echo "Combining row by row outputs to create table output for simple merge..."
python splitandmeregenerated.py --input_file ../data/ourwikidata_output/simple_merged/simple_concat_merge.txt --input_count_file ../data/ourwikidata/outwikitable.ourformat.row.count --output_file ../data/ourwikidata_output/simple_merged/table_level_merge.txt
echo 'Tokenizing for BLEU...'
python postprocess_for_bleu.py ../data/ourwikidata_output/simple_merged/table_level_merge.txt ../data/ourwikidata_output/simple_merged/table_level_merge.txt.tokenized
echo 'Calculating results...'
nlg-eval --hypothesis=../data/ourwikidata_output/simple_merged/table_level_merge.txt.tokenized  --references=../data/ourwikidata/ref1.txt.tokenized --references=../data/ourwikidata/ref2.txt.tokenized --references=../data/ourwikidata/ref3.txt.tokenized --references=../data/ourwikidata/ref4.txt.tokenized