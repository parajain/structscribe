#import spacy
import numpy as np
import gensim
from gensim.models import KeyedVectors

#nlp = spacy.load('en')
#nlp = spacy.load('en_core_web_lg')

# Load Google's pre-trained Word2Vec model.
word_vectors = KeyedVectors.load_word2vec_format('/data1/data1/parag/word2vec/GoogleNews-vectors-negative300.bin', binary=True)
#word_vectors = KeyedVectors.load_word2vec_format('../word2vec/GoogleNews-vectors-negative300.bin', binary=True)

UNK = 'UNK'
def build_features(lines):
    pass

def get_wv_spacy(w):
    """
    https://spacy.io/usage/vectors-similarity
    """
    w = w.decode("unicode-escape")
    tokens = nlp(w)
    #print(tokens.vector)
    token = tokens[0]
    #print(token.text, token.has_vector, token.vector_norm, token.is_oov)
    return token.vector, token.is_oov

def get_wv(w):
    is_oov = False
    if w in word_vectors:
        wv = word_vectors[w]
    else:
        wv = np.zeros(300)
        is_oov = True
    return wv, is_oov

            


def get_relation_features(relations):
    features = []
    for r in relations:
        v, is_oov = get_wv(r)
        #print(v.shape, is_oov) ## why oov always?
        features.append(v)

def get_input_feature(o1, r, o2, output_class_map, ner_class_map):
    n_ner_classes = len(ner_class_map)
    ner_one_hots = np.eye(n_ner_classes)
    if o1 in ner_class_map:
        nco1 = ner_class_map[o1.strip()]
    else:
        nco1 = ner_class_map[UNK]
    if o2 in ner_class_map:
        nco2 = ner_class_map[o2.strip()]
    else:
        nco2 = ner_class_map[UNK]
    fo1 = ner_one_hots[nco1]
    fo2 = ner_one_hots[nco2]
    v, is_oov = get_wv(r)
    f = np.concatenate((fo1, fo2, v), axis=0)
       
    return f

def get_io_features(lines, output_class_map, ner_class_map):
    n_samples = len(lines)
    print('Number of samples ', n_samples)
    input_X = np.zeros((n_samples, 340), dtype=np.float32)
    output_Y = np.zeros((n_samples), dtype=np.int)
    n_ner_classes = len(ner_class_map)
    ner_one_hots = np.eye(n_ner_classes)
    for idx, line in enumerate(lines):
        print(idx)
        inp, out = line.rstrip().split('\t')
        o1, r, o2 = inp.split(' ')
        nco1 = ner_class_map[o1.strip()]
        nco2 = ner_class_map[o2.strip()]
        """
        print(nco1, nco2, r)
        print(o1, o2)
        print(ner_one_hots[nco1])
        """
        fo1 = ner_one_hots[nco1]
        fo2 = ner_one_hots[nco2]
        v, is_oov = get_wv(r)
        f = np.concatenate((fo1, fo2, v), axis=0)
        #print(f.shape) # (422L,) = 300 + 19 + 19
        input_X[idx, :] = f
        oc = output_class_map[out]
        output_Y[idx]= oc
    
    return input_X, output_Y

def get_test_feature(tagged_triple):
    # For TEST
    #data_file = '../data/data_classifier.tsv'

    o1, r, o2 = tagged_triple[0], tagged_triple[1], tagged_triple[2]
    ner_class_file = 'ner_classes.txt'
    output_class_file = 'output_classes.txt'

    ner_classes = open(ner_class_file, 'r').readlines()

    ner_class_map = {}
    for idx, nc in enumerate(ner_classes):
        #print(nc, idx)
        nc = nc.rstrip()
        ner_class_map[nc] = idx

    output_classes = open(output_class_file, 'r').readlines()
    output_class_map = {}
    for idx, o in enumerate(output_classes):
        o = o.rstrip()
        output_class_map[o] = idx

    
    f = get_input_feature(o1, r, o2, output_class_map, ner_class_map)
    return f

def get_features(data_file):
    #data_file = '../data/data_classifier.tsv'
    ner_class_file = '../data/ner_classes.txt'
    output_class_file = '../data/output_classes.txt'

    ner_classes = open(ner_class_file, 'r').readlines()

    ner_class_map = {}
    for idx, nc in enumerate(ner_classes):
        print(nc, idx)
        nc = nc.rstrip()
        ner_class_map[nc] = idx

    output_classes = open(output_class_file, 'r').readlines()
    output_class_map = {}
    for idx, o in enumerate(output_classes):
        o = o.rstrip()
        output_class_map[o] = idx

    lines = open(data_file, 'r').readlines()[1:]
    
    X, Y = get_io_features(lines, output_class_map, ner_class_map)
    return X, Y

def main():
    get_features()

if __name__ == '__main__':
    main()
