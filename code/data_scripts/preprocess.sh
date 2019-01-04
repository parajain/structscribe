echo 'Found directory...'
echo 'Extracting three column data..'
python extract_three_column_data.py $1/$2
echo 'Merging data...' 
cat $1/${2}_classifier_data.tsv $1/Taxonomy_classifier_data.tsv $1/OpenIE_classifier_data.tsv $1/verbnet_classifier_data.tsv | grep -v 'Input' > $1/Facts_Tax_OpenIE_verbnet_data.tsv
echo 'Filtering data...'
python filter_data_v2.py $1/Facts_Tax_OpenIE_verbnet_data.tsv 30 50 $1/Facts_Tax_OpenIE_verbnet_data_filterrels.tsv $1/Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv $1/Facts_Tax_OpenIE_verbnet_data_filterrels_invalidents.tsv
echo 'Creating data subset for ApproxNN...'
python data_subset_knn.py $1/Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv $1/Facts_Tax_OpenIE_verbnet_data_filterrels_validents_subset.tsv
echo 'Creating classifier and seq2seq data..'
python method2_classifier_seq2seq_generator.py $1/Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv $1
echo 'Partitioning seq2seq data..'
python partition_data.py $1 0.8 0.1 0.1
echo '*********DONE*********'
#cut -f1 'Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv' | sort | uniq | wc -l
#cut -f2 'Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv' | sort | uniq | wc -l
#cut -f3 -d'|' 'Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv' | sort | uniq | wc -l
~
