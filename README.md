## Dataset

* Link to download dataset: https://ibm.box.com/s/tmutm503e8z8ud09moq3xj6wkdb52dti
* Above link contains: Dataset 1, 2 and 3 as describes in the paper

## Setup DBpedia Lookup

* You can use online API (http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString=Albert%20Einstein), *but it will be faster (and recommended) to host the API locally.*
* Follow instruction: https://github.com/dbpedia/lookup
* Change api link. code/lookupner/dbpedia_ner.py


_For experimentation purpose models are directly loaded in the memory. But there is an option to create an rpc server to create an API (this is slower, but to try our different inputs it is useful)._
## Generation server
* To run: python S2SServer.py configurations/s2s.config.json

## Gender predictor module server
* Gender server code is present in code\anaphora_replacer
* To run: python GenderServer.py
