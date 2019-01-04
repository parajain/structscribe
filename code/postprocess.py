import operator

SPACY_TAGS = ['PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL','URL','UNK']

def post_process(generated, tag_map_list):
    generated_tagged = generated
    orders = {}
    allp = []
    for t in SPACY_TAGS:
        p = generated.find(t)
        if p != -1:
            orders[t] = p
            allp.append(p)
    if len(orders) > 0:
        sorted_orders = sorted(orders.items(), key=operator.itemgetter(1))
        #generated = generated.replace(sorted_orders[0][0], tag_map_list[tag_map_list.keys()[0]],  1)
        #generated = generated.replace(sorted_orders[-1][0], tag_map_list[tag_map_list.keys()[-1]], 1)
        generated = generated.replace(sorted_orders[0][0], tag_map_list[0].values()[0], 1)
        generated = generated.replace(sorted_orders[-1][0], tag_map_list[-1].values()[0], 1)
    for t in SPACY_TAGS:
        generated = generated.replace(t, '')

    return generated



def main():
    generated = 'EVENT GPE chooses GPE before LANGUAGE ORG'
    tag_map_list = []
    tag_map_list1 = {}
    tag_map_list2 = {}
    tag_map_list1['R'] = 'Algiers, Algeria'
    tag_map_list2['RR'] = '23 March'
    tag_map_list.append(tag_map_list1)
    tag_map_list.append(tag_map_list2)
    print(tag_map_list)
    print(post_process(generated, list(tag_map_list)))



if __name__ == '__main__':
    main()