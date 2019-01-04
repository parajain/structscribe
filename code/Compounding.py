import itertools
import random

spacylist = ['PERSON', 'NORP', 'FACILITY', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW',
             'LANGUAGE', 'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL', 'UNK']
spacymap = {}
for i in range(len(spacylist)):
    spacymap[spacylist[i]]=i

def gen_pairs(num):
    return list(itertools.combinations(range(num), 2))

def gen_random_pairs(slist):
    def pop_random(lst):
        idx = random.randrange(0, len(lst))
        return lst.pop(idx)
    lst = list(slist)
    pairs = []
    while lst:
        rand1 = pop_random(lst)
        rand2 = None
        if len(lst) > 0:
            rand2 = pop_random(lst)
        pair = rand1, rand2
        pairs.append(pair)
    return pairs

def gen_definite_pairs(slist):
    lst = list(slist)
    pairs = []
    while lst:
        rand1 = lst.pop(0)
        rand2 = None
        if len(lst) > 0:
            rand2 = lst.pop(0)
        pair = rand1, rand2
        pairs.append(pair)
    return pairs

def get_clause(ent_spacy_type):
    if spacylist[ent_spacy_type] == 'PERSON':
        return ' who '
    return ' which '

'''
def extract_ent_rel_dict(x):
    # input ([{'Bangalore': 'GPE'}, {'India': 'GPE'}], 'Bangalore is located in India')
    # default = [(4, 'Bangalore'), (4, 'India')], 'is located in'
    s = x[1]
    xent = []
    for d in x[0]:
        # assuming dict has only one key
        k = d.keys()[0]
        parts = s.strip().split(k)
        if len(parts) > 1:
            xent.append((spacymap[d[k]], k))
        s = ' '.join([e.strip() for e in parts]).strip()
    flag = True
    if len(xent) != 2:
        flag = False
    return xent, s, flag
'''

def extract_ent_rel_dict(x):
    # input ([{u'ORG': u'IBM'}, {u'PERSON': u'Charles Ranlett Flint'}], 'IBM founder is Charles Ranlett Flint')
    s = x[1]
    xent = []
    for d in x[0]:
        # assuming dict has only one key
        k = d.keys()[0]
        v = d[k]
        parts = s.strip().split(v)
        if len(parts) > 1:
            xent.append((spacymap[k], v))
        s = ' '.join([e.strip() for e in parts]).rstrip('.').strip()
    flag = True
    if len(xent) != 2:
        flag = False
    return xent, s, flag


def extract_ent_rel(x):
    # default = [(4, 'Bangalore'), (4, 'India')], 'is located in'
    if type(x[0])==list:
        return extract_ent_rel_dict(x)
    tagged_tokens = x[0].split(' ')
    tokens = x[1].split(' ')
    spacy_indices = [i for i in range(len(tagged_tokens)) if tagged_tokens[i] in spacylist]
    xrel = ' '.join([tagged_tokens[i] for i in range(len(tagged_tokens)) if i not in spacy_indices]).rstrip('.').strip()
    # assert len(tagged_tokens) == len(tokens)
    # print spacy_indices
    # print xrel
    if xrel not in x[1]:
        return [], '', False
    entities = [e.strip() for e in x[1].split(xrel)]
    # print entities
    xent = []
    for i in range(len(spacy_indices)):
        j = spacy_indices[i]
        xent.append((spacymap[tagged_tokens[j]], entities[i]))
    flag = True
    if entities[0] == '' or entities[1] == '':
        flag = False
    return xent, xrel, flag

'''
def extract_ent_rel(x):
    # default = [(4, 'Bangalore'), (4, 'India')], 'is located in'
    tagged_tokens = x[0].split(' ')
    tokens = x[1].split(' ')
    spacy_indices = [i for i in range(len(tagged_tokens)) if tagged_tokens[i] in spacylist]
    assert len(tagged_tokens) == len(tokens)
    xent = []
    for i in spacy_indices:
        xent.append((spacymap[tagged_tokens[i]], tokens[i]))
    xrel = ' '.join([tokens[i] for i in range(len(tokens)) if i not in spacy_indices])
    return xent, xrel
'''

def merge_pair(x,y):
    if y is None:
        return x[1]
    if len(x[1].split('\'s')) > 1 or len(y[1].split('\'s')) > 1:
        return x[1] + ' and ' + y[1]
    try:
        # x and y are tuples like ('GPE is located in GPE','Bangalore is located in India')
        xent, xrel, xflag = extract_ent_rel(x)
        # xent looks like [(4,'Bangalore'),(4,'India')] and xrel is 'is located in'
        yent, yrel, yflag = extract_ent_rel(y)
        if not xflag or not yflag:
            return x[1] + ' and ' + y[1]
        if len(xent)==2 and len(yent)==2:
            if xent[1][1] == yent[0][1]:
                return xent[0][1] + ' ' + xrel + ' ' + xent[1][1] + get_clause(xent[1][0]) + yrel + ' ' + yent[1][1]
            elif xent[0][1] == yent[1][1]:
                return yent[0][1] + ' ' + yrel + ' ' + yent[1][1] + get_clause(yent[1][0]) + xrel + ' ' + xent[1][1]
            elif xent[0][1] == yent[0][1]:
                if xrel == yrel:
                    return xent[0][1] + ' ' + xrel + ' ' + xent[1][1] + ' and ' + yent[1][1]
                else:
                    return xent[0][1] + ' ' + xrel + ' ' + xent[1][1] + ' and ' + yrel + ' ' + yent[1][1]

            elif xent[1][1]==yent[1][1]:
                    return xent[0][1] + ' and ' + yent[0][1] + ' ' + xrel + ' ' + yent[1][1]
            else:
                    return x[1] + ' and ' + y[1]

        else:
            return x[1]+' and '+y[1]
    except:
        return x[1] + ' and ' + y[1]


def remove_periods(stuplelist):
    if type(stuplelist[0][0]) == list:
        return [(k, v.strip().rstrip(".").rstrip()) for k, v in stuplelist]
    else:
        return [(k.strip().rstrip(".").rstrip(), v.strip().rstrip(".").rstrip()) for k, v in stuplelist]

def merge_sentences_all(stuplelist):
    pairs = gen_pairs(len(stuplelist))
    return [merge_pair(stuplelist[i], stuplelist[j]) for i, j in pairs]

def merge_sentences(stuplelist, k=5, punctProcess=False):
    if punctProcess:
        stuplelist=remove_periods(stuplelist)
    paralist = []
    for index in range(k):
        if index == 0:
            pairs = gen_definite_pairs(stuplelist)
        else:
            pairs = gen_random_pairs(stuplelist)
        # print pairs
        compounded = [merge_pair(x, y)+'.' for x, y in pairs]
        paralist.append((compounded,' '.join(compounded)))
    return paralist

''',
if __name__ == '__main__':
    stuplelist = [
        ('GPE is located in GPE','Bangalore is located in India'),
        ('ORG is located in GPE','IBM is located in Bangalore'),
        ('PERSON plays for ORG','John plays for IBM'),
        ('PERSON has won prize ORG','John has won prize Turing'),
        ('PERSON has gender PERSON','John has gender male'),
        ('PERSON is married to PERSON','Claire is married to John'),
        ('ORG has website UNK','IBM has website ibm.com'),
        ('PERSON has won prize ORG', 'John has won prize Nobel'),
        ('PERSON has gender PERSON', 'Claire has gender female')
    ]
    # print merge_sentences_all(stuplelist)
    print merge_sentences(stuplelist, punctProcess=True)
'''

if __name__ == '__main__':
    # sdictlist = [
    #     ([{'Bangalore': 'GPE'}, {'India': 'GPE'}], 'Bangalore is located in India'),
    #     ([{'IBM': 'ORG'}, {'Bangalore': 'GPE'}], 'IBM is located in Bangalore'),
    #     ([{'John': 'PERSON'}, {'IBM': 'ORG'}], 'John plays for IBM'),
    #     ([{'John': 'PERSON'}, {'Turing': 'ORG'}], 'John has won prize Turing'),
    #     ([{'John': 'PERSON'}, {'male': 'PERSON'}], 'John has gender male'),
    #     ([{'Claire': 'PERSON'}, {'John': 'PERSON'}], 'Claire is married to John'),
    #     ([{'IBM': 'ORG'}, {'ibm.com': 'UNK'}], 'IBM has website ibm.com'),
    #     ([{'John': 'PERSON'}, {'Nobel': 'ORG'}], 'John has won prize Nobel'),
    #     ([{'Claire': 'PERSON'}, {'female': 'PERSON'}], 'Claire has gender female')
    # ]
    # sdictlist = [
    #     ([{u'ORG': u'IBM'}, {u'PERSON': u'Charles Ranlett Flint'}], 'IBM founder is Charles Ranlett Flint'),
    #     ([{u'ORG': u'IBM'}, {u'GPE': u'New York'}], 'IBM is headquarter New York'),
    #     ([{u'ORG': u'IBM'}, {u'PERSON': u'Ginni Rometty'}], 'IBM appointed Ginni Rometty'),
    #     ([{u'ORG': u'IBM'}, {u'MONEY': u'$79.139 billion'}], 'IBM profit $79.139 billion'),
    #     ([{u'ORG': u'IBM'}, {u'MONEY': u'$5.753 billion'}], 'IBM has net income $5.753 billion')
    # ]
    sdictlist= [([{u'PERSON': u'Sachin Tendulkar'}, {u'DATE': u'1973'}], u'Sachin Tendulkar has birth year 1973 .'), (
    [{u'PERSON': u'Sachin Tendulkar'}, {u'DATE': u'24 April'}], u'Sachin Tendulkar has birth day 24 April .'),
                ([{u'PERSON': u'Sachin Tendulkar'}, {u'GPE': u'India'}], u'Sachin Tendulkar played for country India'),
                ([{u'PERSON': u'Sachin Tendulkar'}, {u'PERSON': u'Bharat Ratna'}],
                 u'Sachin Tendulkar is an award in Bharat Ratna'), (
                [{u'PERSON': u'Sachin Tendulkar'}, {u'DATE': u'24 April 1973'}],
                u"Sachin Tendulkar's date of birth is 24 April 1973")]
    print '\n'.join([str(e) for e in merge_sentences(sdictlist, punctProcess=True)])

