import math, re
import kenlm
from collections import Counter
import json, math

#config2 = json.load(open("config.json"))


class LMScorer():
    def __init__(self, config):
        kenlm_path = config["kenlm_path_bigram"]
        print('Loading KENLM from ', kenlm_path)
        self.model = kenlm.Model(kenlm_path)
        kenlm_path_ranker = config['kenlm_path_ranker']
        self.model_ranker = kenlm.Model(kenlm_path_ranker)

        

    def kenlm_score(self, sent):
        if sent.strip()=="":
		        return 0.00000001
        exp_s = self.model.score(sent, bos = True, eos = True)
        return exp_s


    def rank_kenlm(self, sentences, topk = 5):
        sen_score_pairs = []
        for s in sentences:
            score = self.kenlm_score(s)
            score = math.pow(10,score)
            sen_score_pairs.append((s, score))
        sen_score_pairs = sorted(sen_score_pairs, key=lambda x: x[1], reverse=True)
        topsentences = []
        for ss in sen_score_pairs[:topk]:
            topsentences.append(ss[0])
        return topsentences, sen_score_pairs
    
    
    def kenlm_score_ranker(self, sent):
        exp_s = self.model_ranker.score(sent, bos = False, eos = False)
        #exp_s = math.pow(10,exp_s)
        exp_s = exp_s/float(len(sent))
        return exp_s  


if __name__ == '__main__':
    sentences = ['ORG has  benefited with PRODUCT', 'ORG has  benefited with PRODUCT', 'ORG have  benefited through PRODUCT', 'ORG have  benefited through PRODUCT', 'ORG benefited PRODUCT', 'ORG benefited PRODUCT', 'ORG have  benefitted by PRODUCT', 'ORG have  benefitted by PRODUCT', 'ORG have been  benefiting from PRODUCT', 'ORG have been  benefiting from PRODUCT', 'ORG has  benefited by PRODUCT', 'ORG has  benefited by PRODUCT', 'ORG benefited to PRODUCT', 'ORG benefited to PRODUCT', 'ORG have  benefited in PRODUCT', 'ORG have  benefited in PRODUCT', 'ORG Having  benefits from PRODUCT', 'ORG Having  benefits from PRODUCT', 'ORG would  benefit from PRODUCT', 'ORG would  benefit from PRODUCT', 'ORG has has  benefited from PRODUCT', 'ORG has has  benefited from PRODUCT', 'ORG have  benefited on PRODUCT', 'ORG have  benefited on PRODUCT', 'ORG have  benefited from PRODUCT', 'ORG have  benefited from PRODUCT', 'ORG benefits by PRODUCT', 'ORG benefits by PRODUCT', 'ORG had  benefited from PRODUCT', 'ORG had  benefited from PRODUCT', 'ORG have been  benefited from PRODUCT', 'ORG have been  benefited from PRODUCT', 'ORG benefitted from PRODUCT', 'ORG benefitted from PRODUCT', 'ORG benefits because PRODUCT', 'ORG benefits because PRODUCT', 'ORG did  benefit from PRODUCT', 'ORG did  benefit from PRODUCT', 'ORG benefited along PRODUCT', 'ORG benefited along PRODUCT', 'ORG do  benefit in PRODUCT', 'ORG do  benefit in PRODUCT', 'ORG has  benefited PRODUCT', 'ORG has  benefited PRODUCT', 'ORG benefits through PRODUCT', 'ORG benefits through PRODUCT', 'ORG benefitted with PRODUCT', 'ORG benefitted with PRODUCT', 'ORG will  benefit from PRODUCT', 'ORG will  benefit from PRODUCT', 'ORG benefited for PRODUCT', 'ORG benefited for PRODUCT', 'ORG can  benefit from PRODUCT', 'ORG can  benefit from PRODUCT', 'ORG benefited over PRODUCT', 'ORG benefited over PRODUCT', 'ORG benefits from PRODUCT', 'ORG benefits from PRODUCT', 'ORG benefited at PRODUCT', 'ORG benefited at PRODUCT', 'ORG would  benefit than PRODUCT', 'ORG would  benefit than PRODUCT', 'ORG are  benefiting from PRODUCT', 'ORG are  benefiting from PRODUCT', 'ORG had  benefited for PRODUCT', 'ORG had  benefited for PRODUCT', 'ORG benefit as PRODUCT', 'ORG benefit as PRODUCT', 'ORG benefited as PRODUCT', 'ORG benefited as PRODUCT', 'ORG have  benefitted from PRODUCT', 'ORG have  benefitted from PRODUCT', 'ORG benefited from PRODUCT', 'ORG benefited from PRODUCT', 'ORG benefitted to PRODUCT', 'ORG benefitted to PRODUCT', 'ORG can  benefit PRODUCT', 'ORG can  benefit PRODUCT', 'ORG has  benefited on PRODUCT', 'ORG has  benefited on PRODUCT', 'ORG have  benefited due PRODUCT', 'ORG have  benefited due PRODUCT', 'ORG benefited Without PRODUCT', 'ORG benefited Without PRODUCT', 'ORG benefited with PRODUCT', 'ORG benefited with PRODUCT', 'ORG has  benefited in PRODUCT', 'ORG has  benefited in PRODUCT', 'ORG benefited after PRODUCT', 'ORG benefited after PRODUCT', 'ORG benefited following PRODUCT', 'ORG benefited following PRODUCT', 'ORG benefited during PRODUCT', 'ORG benefited during PRODUCT', 'ORG benefitted PRODUCT', 'ORG benefitted PRODUCT', 'ORG will  benefit PRODUCT', 'ORG will  benefit PRODUCT', 'ORG can  benefit by PRODUCT', 'ORG can  benefit by PRODUCT', 'ORG has  benefited from PRODUCT', 'ORG has  benefited from PRODUCT', 'ORG may  benefit PRODUCT', 'ORG may  benefit PRODUCT', 'ORG would  benefit PRODUCT', 'ORG would  benefit PRODUCT', 'ORG Had would have  benefited in PRODUCT', 'ORG Had would have  benefited in PRODUCT', 'ORG benefit on PRODUCT', 'ORG benefit on PRODUCT', 'ORG has  benefited since PRODUCT', 'ORG has  benefited since PRODUCT', 'ORG will  benefit at PRODUCT', 'ORG will  benefit at PRODUCT', 'ORG benefited of PRODUCT', 'ORG benefited of PRODUCT', 'ORG benefit without PRODUCT', 'ORG benefit without PRODUCT', 'ORG may  benefit from PRODUCT', 'ORG may  benefit from PRODUCT', 'ORG benefit in PRODUCT', 'ORG benefit in PRODUCT', 'ORG benefited in PRODUCT', 'ORG benefited in PRODUCT', 'ORG have been  benefiting to PRODUCT', 'ORG have been  benefiting to PRODUCT', 'ORG benefits as PRODUCT', 'ORG benefits as PRODUCT', 'ORG will  benefit by PRODUCT', 'ORG will  benefit by PRODUCT', 'ORG could  benefit PRODUCT', 'ORG could  benefit PRODUCT', 'ORG benefits PRODUCT', 'ORG benefits PRODUCT', 'ORG Had would have  benefited PRODUCT', 'ORG Had would have  benefited PRODUCT', 'ORG benefit through PRODUCT', 'ORG benefit through PRODUCT', 'ORG benefits in PRODUCT', 'ORG benefits in PRODUCT', 'ORG do  benefit PRODUCT', 'ORG do  benefit PRODUCT', 'ORG may  benefit in PRODUCT', 'ORG may  benefit in PRODUCT', 'ORG benefit by PRODUCT', 'ORG benefit by PRODUCT', 'ORG can  benefit in PRODUCT', 'ORG can  benefit in PRODUCT', 'ORG has has  benefited to PRODUCT', 'ORG has has  benefited to PRODUCT', 'ORG benefits with PRODUCT', 'ORG benefits with PRODUCT', 'ORG benefit PRODUCT', 'ORG benefit PRODUCT', 'ORG benefit from PRODUCT', 'ORG benefit from PRODUCT', 'ORG did  benefit PRODUCT', 'ORG did  benefit PRODUCT', 'ORG benefited until PRODUCT', 'ORG benefited until PRODUCT', 'ORG benefited like PRODUCT', 'ORG benefited like PRODUCT', 'ORG benefitted as PRODUCT', 'ORG benefitted as PRODUCT', 'ORG could  benefit from PRODUCT', 'ORG could  benefit from PRODUCT']
    topsentences, sen_score_pairs = rank_kenlm(sentences)
    for ss in sen_score_pairs:
        print(ss)
    print(topsentences)
    
