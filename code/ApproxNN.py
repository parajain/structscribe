# coding: utf-8

from annoy import AnnoyIndex
print('annoy')
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
print('fw')
import numpy as np
import io

import argparse
import codecs


spacylist = ['PERSON', 'NORP', 'FACILITY', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW',
             'LANGUAGE', 'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL', 'UNK']


class S2SModel(): #nn.Module
    def __init__(self):
        print('Init sequence 2 sequence here')
    
    def generate(self, triple):
        return ' '.join(triple)

def onehotnp(l):
    a=np.arange(len(l))
    b=np.zeros((len(l),len(l)))
    b[a,a]=1
    mapl={}
    for i in range(len(l)):
        mapl[l[i]]=list(b[i])
    return mapl

mapl = onehotnp(spacylist)


def encodecol1(tlist, glovemap):
    en1 = np.zeros((19))
    if tlist[0] in mapl:
        en1 = np.array(mapl[tlist[0]])
    rel = np.zeros((300))
    if tlist[1] in glovemap:
        rel = np.array(glovemap[tlist[1]])
    en3 = np.zeros((19))
    if tlist[2] in mapl:
        en3 = np.array(mapl[tlist[2]])
    return list(np.concatenate((en1, rel, en3), axis=0))

def encodecol2(tlist, glovemap):
    en1=np.zeros((19))
    a=tlist[0].split()
    for t in a:
        if t in mapl:
            en1=en1+np.array(mapl[t])
    ena=en1/len(a)
    rel=np.zeros((300))
    b=tlist[1].split()
    for t in b:
        if t in glovemap:
            rel=rel+np.array(glovemap[t])
    rel=rel/len(b)
    en3=np.zeros((19))
    c=tlist[2].split()
    for t in c:
        if t in mapl:
            en3=en3+np.array(mapl[t])
    enc=en3/len(c)
    return list(np.concatenate((ena, rel, enc), axis=0))

def encode_triple(tlist, glovemap):
    en1=np.zeros((19))
    t=tlist[0]
    if t in mapl:
        en1=en1+np.array(mapl[t])
    rel=np.zeros((300))
    b=tlist[1].split()
    for t in b:
        if t in glovemap:
            rel=rel+np.array(glovemap[t])
    rel=rel/len(b)
    en3=np.zeros((19))
    t=tlist[2]
    if t in mapl:
        en3=en3+np.array(mapl[t])
    return list(np.concatenate((en1, rel, en3), axis=0))


def initializeAnnoy(glovefile, datafile, dim=338):
    glv = open(glovefile, 'r').readlines()
    glove = glv[1:]
    glovemap = {}
    print('Building glovemap...')
    for i in xrange(len(glove)):
        l = glove[i].strip().split()
        k = l[0]
        v = [float(e) for e in l[1:]]
        if k in glovemap:
            continue
        glovemap[k] = v

    print('Reading data file...')
    xuni=io.open(datafile,'r',encoding="utf-8").readlines()

    print('Column 1...')
    col1=set([t.split('\t')[0] for t in xuni])
    col1list=list(col1)

    print('Encoding column 1...')
    col1map={}
    for t in col1:
        col1map[t]=encodecol1(t.split(), glovemap)
    col1reversemap={}
    for i in range(len(col1list)):
        col1reversemap[col1list[i]]=i

    print('Column 2...')
    col2=set([t.split('\t')[1] for t in xuni])
    col2list=list(col2)

    print('Encoding column 2...')
    col2map={}
    for t in col2:
        col2map[t]=encodecol2(t.split(' || '), glovemap)
    col2reversemap={}
    for i in range(len(col2list)):
        col2reversemap[col2list[i]]=i

    print('Column 3 - Sentences...')
    sent=set(xuni)
    sentmap={}
    for t in sent:
        tuplist=t.split('\t')
        a, b, c = tuplist[0], tuplist[1], tuplist[2].strip()
        if a not in sentmap:
            sentmap[a] = c
        if b not in sentmap:
            sentmap[b] = c

    bAngular=AnnoyIndex(dim)
    print('Building column 1 angular annoy index..')
    for i in range(len(col1list)):
        bAngular.add_item(i, col1map[col1list[i]])
    print('Building column 2 angular annoy index..')
    for i in range(len(col2list)):
        bAngular.add_item(len(col1list)+i, col2map[col2list[i]])
        bAngular.build(10)

    bHamming=AnnoyIndex(dim, metric='hamming')
    print('Building column 1 hamming annoy index..')
    for i in range(len(col1list)):
        bHamming.add_item(i, col1map[col1list[i]])
    print('Building column 2 hamming annoy index..')
    for i in range(len(col2list)):
        bHamming.add_item(len(col1list)+i, col2map[col2list[i]])
        bHamming.build(10)

    bEuclidean=AnnoyIndex(dim, metric='euclidean')
    print('Building column 1 euclidean annoy index..')
    for i in range(len(col1list)):
        bEuclidean.add_item(i, col1map[col1list[i]])
    print('Building column 2 euclidean annoy index..')
    for i in range(len(col2list)):
        bEuclidean.add_item(len(col1list)+i, col2map[col2list[i]])
        bEuclidean.build(10)

    bManhattan = AnnoyIndex(dim, metric='manhattan')
    print('Building column 1 manhattan annoy index..')
    for i in range(len(col1list)):
        bManhattan.add_item(i, col1map[col1list[i]])
    print('Building column 2 manhattans annoy index..')
    for i in range(len(col2list)):
        bManhattan.add_item(len(col1list) + i, col2map[col2list[i]])
        bManhattan.build(10)

    print('Approximate Nearest Neighbor ready to try!!!!!!!!!')
    return bAngular, bHamming, bEuclidean, bManhattan, \
           col1list, col1map, col2list, col2map, sentmap, glovemap


class ApproxNN(S2SModel):
    def __init__(self, config, filename='/data1/Facts_Tax_OpenIE_verbnet_data_filterrels_validents_subset.tsv'):
        print('Initializing ApproxNN with config', config)
        embeddings_file = config['embeddings_file']
        print('Will load embeddings from: ', embeddings_file) 

        bAngular, bHamming, bEuclidean, bManhattan, \
        col1list, col1map, col2list, col2map, sentmap, glovemap = \
            initializeAnnoy(embeddings_file, filename)
        self.annoyIndexAngular = bAngular
        self.annoyIndexHamming = bHamming
        self.annoyIndexEuclidean = bEuclidean
        self.annoyIndexManhattan = bManhattan
        self.annoyIndexB = self.annoyIndexAngular
        self.metric = 'angular'
        self.col1list = col1list
        self.col2list = col2list
        self.col1map = col1map
        self.col2map = col2map
        self.sentmap = sentmap
        self.embedding = glovemap

    def generate(self, triple, use_string_match=False):
        outputs =  [self.generate_metric(triple, metric='angular'),
               self.generate_metric(triple, metric='hamming'),
               self.generate_metric(triple, metric='euclidean'),
               self.generate_metric(triple, metric='manhattan')]
        if use_string_match:
            outputs.append(self.generate_string_match(triple, typecol='c1'))
            outputs.append(self.generate_string_match(triple, typecol='c2'))
        return outputs

    def generate_string_match(self, triple, typecol='c1'):
        if typecol == 'c1':
            val=process.extractOne(' '.join(triple), self.col1list)
            return (self.sentmap[val[0]], val[1])
        elif typecol == 'c2':
            val=process.extractOne(' || '.join(triple), self.col2list)
            return (self.sentmap[val[0]], val[1])

    def generate_metric(self, triple, metric='angular'):
        self.metric = metric
        self.annoyIndexB = self.annoyIndexAngular
        if metric == 'hamming':
            self.annoyIndexB = self.annoyIndexHamming
        elif metric == 'euclidean':
            self.annoyIndexB = self.annoyIndexEuclidean
        elif metric == 'manhattan':
            self.annoyIndexB = self.annoyIndexManhattan
        if len(triple[1].split()) > 1:
            val=self.approxNN(' || '.join(triple), typecol='c2', k=1)[0]
            return (self.sentmap[val[0]], val[1])
        else:
            val=self.approxNN(' '.join(triple), k=1)[0]
            return (self.sentmap[val[0]], val[1])

    def approxNN(self, s, typecol='c1', k=20):
        len1 = len(self.col1list)
        if typecol == 'c1':
            if s not in self.col1map:
                self.col1map[s] = encode_triple(s.split(), self.embedding)
            result = self.annoyIndexB.get_nns_by_vector(self.col1map[s], k, include_distances=True)
            return [(self.col1list[result[0][i]], result[1][i]) if result[0][i] / len1 == 0 else (
                self.col2list[result[0][i] % len1], result[1][i]) for i in range(len(result[0]))]
        elif typecol == 'c2':
            if s not in self.col2map:
                self.col2map[s] = encode_triple(s.split(' || '), self.embedding)
            result = self.annoyIndexB.get_nns_by_vector(self.col2map[s], k, include_distances=True)
            return [(self.col1list[result[0][i]], result[1][i]) if result[0][i] / len1 == 0 else (
                self.col2list[result[0][i] % len1], result[1][i]) for i in range(len(result[0]))]

class Seq2Seq(S2SModel):
    def __init__(self, modelfile='/data1/data1/Anirban/structure2text/model_softmax_acc_78.18_ppl_9.60_e4.pt'):
    #def __init__(self, modelfile='/data1/data1/Anirban/structure2text/model_softmax_1_acc_84.10_ppl_2.13_e1.pt'):
        parser = argparse.ArgumentParser(
            description='seq2seq_predict',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        opts.add_md_help_argument(parser)
        opts.translate_opts(parser)
        opt = parser.parse_args()
        dummy_parser = argparse.ArgumentParser(description='train.py')
        opts.model_opts(dummy_parser)
        dummy_opt = dummy_parser.parse_known_args([])[0]

        opt.cuda = opt.gpu > -1
        if opt.cuda:
            torch.cuda.set_device(opt.gpu)

        opt.src = 'temp_seq2seq_pred.txt'
        opt.model = modelfile

        print('Loading seq2seq model...')
        # Load the model.
        fields, model, model_opt = \
            onmt.ModelConstructor.load_test_model(opt, dummy_opt.__dict__)

        self.opt = opt
        self.fields = fields
        self.model = model
        self.model_opt = model_opt

    def generate(self, input):
        ftemp = codecs.open(self.opt.src, 'w', "utf-8")
        ftemp.write(input.strip() + '\n')
        ftemp.close()

        # File to write sentences to.
        out_file = codecs.open('out_seq2seq_pred.txt', 'w', 'utf-8')
        output_sentence = ''

        # Test data
        data = onmt.io.build_dataset(self.fields, self.opt.data_type,
                                     self.opt.src, self.opt.tgt,
                                     src_dir=self.opt.src_dir,
                                     sample_rate=self.opt.sample_rate,
                                     window_size=self.opt.window_size,
                                     window_stride=self.opt.window_stride,
                                     window=self.opt.window,
                                     use_filter_pred=False)

        # Sort batch by decreasing lengths of sentence required by pytorch.
        # sort=False means "Use dataset's sortkey instead of iterator's".
        data_iter = onmt.io.OrderedIterator(
            dataset=data, device=self.opt.gpu,
            batch_size=self.opt.batch_size, train=False, sort=False,
            sort_within_batch=True, shuffle=False)

        # Translator
        scorer = onmt.translate.GNMTGlobalScorer(self.opt.alpha,
                                                 self.opt.beta,
                                                 self.opt.coverage_penalty,
                                                 self.opt.length_penalty)

        translator = onmt.translate.Translator(
            self.model, self.fields,
            beam_size=self.opt.beam_size,
            n_best=self.opt.n_best,
            global_scorer=scorer,
            max_length=self.opt.max_length,
            copy_attn=self.model_opt.copy_attn,
            cuda=self.opt.cuda,
            beam_trace=self.opt.dump_beam != "",
            min_length=self.opt.min_length,
            stepwise_penalty=self.opt.stepwise_penalty,
            block_ngram_repeat=self.opt.block_ngram_repeat,
            ignore_when_blocking=self.opt.ignore_when_blocking)
        builder = onmt.translate.TranslationBuilder(
            data, translator.fields,
            self.opt.n_best, self.opt.replace_unk, self.opt.tgt)

        for batch in data_iter:
            batch_data = translator.translate_batch(batch, data)
            translations = builder.from_batch(batch_data)

            for trans in translations:

                n_best_preds = [" ".join(pred)
                                for pred in trans.pred_sents[:self.opt.n_best]]
                out_file.write('\n'.join(n_best_preds))
                out_file.write('\n')
                out_file.flush()
                output_sentence = '\n'.join(n_best_preds)

                break
            break

        return output_sentence

if __name__ == '__main__':
    # model = ApproxNN()
    # print(model.generate(['ORG', 'locate', 'GPE']))
    model = Seq2Seq()
    print(model.generate('GPE locator GPE IS PREP'))

