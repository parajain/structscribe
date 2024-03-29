## Major dependencies
* Python
* Pytorch
* Spacy

## Dataset

* Link to download dataset: [link](https://zenodo.org/record/8079837)
* Above link contains: Dataset 1, 2 and 3 as describes in the paper

## Setup DBpedia Lookup

* You can use online API (http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString=Albert%20Einstein), *but it will be faster (and recommended) to host the API locally.*
* Follow instruction: https://github.com/dbpedia/lookup
* Change api link. code/lookupner/dbpedia_ner.py


_For experimentation purpose models are directly loaded in the memory. But there is an option to create an rpc server to create an API (this is slower, but to try our different inputs it is useful)._ *Not needed to run experiment.py*
## Generation server
* To run: python S2SServer.py configurations/s2s.config.json

## Gender predictor module server
* Gender server code is present in code\anaphora_replacer
* To run: python GenderServer.py
