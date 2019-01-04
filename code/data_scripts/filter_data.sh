cat ../../Abhijit/Graph2Text/massive_classifier_method1/version2/Facts_tagged_classifier_data.tsv ../../Abhijit/Graph2Text/massive_classifier_method1/version2/Taxonomy_classifier_data.tsv ../../Abhijit/Graph2Text/massive_classifier_method1/version2/OpenIE_classifier_data.tsv ../../Abhijit/Graph2Text/massive_classifier_method1/version2/verbnet_classifier_data.tsv | grep -v 'Input' > Facts_Tax_OpenIE_verbnet_data.tsv.v2
python filter_data_v2.py Facts_Tax_OpenIE_verbnet_data.tsv.v2 30 50 Facts_Tax_OpenIE_verbnet_data_filterrels.tsv Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv Facts_Tax_OpenIE_verbnet_data_filterrels_invalidents.tsv
cut -f1 'Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv' | sort | uniq | wc -l
cut -f2 'Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv' | sort | uniq | wc -l
cut -f3 -d'|' 'Facts_Tax_OpenIE_verbnet_data_filterrels_validents.tsv' | sort | uniq | wc -l
