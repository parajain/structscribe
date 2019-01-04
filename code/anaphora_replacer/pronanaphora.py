# Program for pronominal anaphora resolution 

import xmlrpclib
import sys, os
'''
class FakeServer():
    def __init__(self):
        print(sys.path)
        sys.path.append(".")
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(here)
        from cnngender.gender_predict import predict_gender
    def determine_gender(self, name):
        print('*******************Path', sys.path)
        return predict_gender(name)
'''
class PronounReplacer:
    def __init__(self, port_n, via_rpc = True):
        #self.via
        if via_rpc:
            addr = 'http://localhost:' + str(port_n)
            self.server = xmlrpclib.Server(addr)
        else:
            from GenderServer import Gender
            self.server = Gender()
            
        self.unchange_list = ["DATE","TIME","PERCENT","MONEY","QUANTITY","ORDINAL","CARDINAL"]
        
    def predict_gender(self, name):
        return self.server.determine_gender(name)

    def pronoun_map(self, word, enttyp, role, possesive=False):
        pron = "it"
        pron_type = ""
        if enttyp in self.unchange_list:
            return [word,-1]
        if enttyp == "PERSON":
            gender = self.predict_gender(word)
            if str(gender) == "0":
                # FEMALE
                pron_type = 0
                if role == "e1":
                    if possesive:
                        pron = "her"
                    else:
                        pron = "she"
                else:
                    if possesive:
                        pron = "her"
                    else:
                        pron = "her"
            else:
                # MALE
                pron_type = 1
                if role == "e1":
                    if possesive:
                        pron = "his"
                    else:
                        pron = "he"
                else:
                    if possesive:
                        pron = "his"
                    else:
                        pron = "him"                
        else:
            pron_type = 2
            if possesive:
                pron = "its"
            else:
                pron = "it"
        return [pron,pron_type]

    def replace_pronoun(self, sentences, dicttags):
        # prepare modified sents
        new_sents = []
        new_dtags = {}

        # Fuse dictionalry
        for d in dicttags:
            for small_dict in d:
                for k in small_dict.keys():
                    v = small_dict[k]  # value which is the actual word
                    new_dtags[v] = k
        #print new_dtags

        # Prepare sentences by replacing entities with enriched intities
        for i in range(len(sentences)):
            new_sent = ""
            e = "e1"
            sent = sentences[i].strip().rstrip(".")+" "

            for key in new_dtags.keys():

                key_with_poss = key + "'s"
                new_key = "@@".join(key.split())  # for multiword keys
                new_key_with_poss = new_key + "@@'s"
                
                sent = sent.replace(key_with_poss+" ", new_key_with_poss + "@@" + new_dtags[key]+" ")
                sent = sent.replace(key+" ", new_key + "@@" + new_dtags[key]+" ")
                    
            for word in sent.split():
                if "@@" in word:
                    new_word = word + "@@" + e
                    if e == "e1":
                        e = "e2"
                    else:
                        e = "e1"
                else:
                    new_word = word
                new_sent += new_word + " "
            new_sent = new_sent.strip()
            new_sents.append(new_sent)
        

        # Again revisit sentences but this time replace with pronouns
        final_para = []
        previous_sentence = ""
        for s in new_sents:
            # Flag to be used to ensure, pronoun is replaced once in the sentence
            final_sent = ""
            replaced_pronoun = []
            processed_entities = []
            wwid = 0
            for word in s.split():
                rest_sent = " ".join(s.split()[wwid+1:])
                if "@@" in word:
                    inf = word.split("@@")

                    sentword = "@@".join(inf[:-2])
                    root = sentword

                    possesive = False
                    enttyp = inf[-2]
                    role = inf[-1]
                    if "'s" in sentword:
                        root = sentword.rstrip("'s").strip("@@")
                        possesive = True
                    
                    if root in previous_sentence or root in final_sent: #word is in previous sentence the sentence so far
                        pron,pron_type = self.pronoun_map(root, enttyp, role, possesive)
                        
                        if pron_type not in replaced_pronoun or root not in processed_entities:
                            if root not in rest_sent:
                                #only replace the last entity if entity occurs more than once in a sentence. 
                                final_sent += pron + " "
                                replaced_pronoun.append(pron_type)
                                processed_entities.append(root)
                            else:
                                final_sent += sentword + " "
                                processed_entities.append(root)
                            
                        else:
                            final_sent += sentword + " "
                            processed_entities.append(root)
                        
                    else:
                        final_sent += sentword + " "
                else:
                    final_sent += word + " "
                wwid+=1
            print processed_entities
            previous_sentence = s
            final_sent = final_sent.strip().replace("@@"," ").replace("in it","there")
            final_sent = final_sent[0].upper() + final_sent[1:]  # Capitalize the first letter
            final_para.append(final_sent+".")
        return final_para


if __name__ == "__main__":
    dicttags = [[{u'ORG': u'IBM'}, {u'PERSON': u'Charles Ranlett Flint'}], [{u'ORG': u'IBM'}, {u'GPE': u'New York'}],
                [{u'ORG': u'IBM'}, {u'PERSON': u'Ginni Rometty'}], [{u'ORG': u'IBM'}, {u'MONEY': u'$79.139 billion'}],
                [{u'ORG': u'IBM'}, {u'MONEY': u'$5.753 billion'}]]
    sentences = [u'IBM appointed Ginni Rometty and profit $79.139 billion.',
                 u"IBM's net income $5.753 billion and IBM has founder Charles Ranlett Flint.",
                 u'Charles Ranlett Flint was a scientist.', u'IBM is headquarter New York.']

    port_n = 18902
    pr = PronounReplacer(port_n)

    print pr.replace_pronoun(sentences, dicttags)
