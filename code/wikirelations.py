import json
import joblib
import json, math

from nltk.stem import WordNetLemmatizer


class WikiRelations:
    def __init__(self, config):
        self.lemmatizer = WordNetLemmatizer()
        #config = json.load(open('config.json'))
        filename = config['lemma_dictionary']
        #filename = '../../wikidata/lemma_dictionary.joblib2'
        print('Loading wiki relation dictionary: ', filename)
        self.j = joblib.load(filename)


    def get_wiki_relations(self, r):
        #use lemma?
        relations = []
        if r in self.j:
            relations = self.j[r]
        return relations

if __name__ == '__main__':
    r = 'molest'
    relations = get_wiki_relations(r)
    print(relations)