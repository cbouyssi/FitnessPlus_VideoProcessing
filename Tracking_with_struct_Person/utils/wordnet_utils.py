"""
Deep learning for efficient video surveillance segmentation, indexing and retrieval.

@author: Tom
"""

from nltk.corpus import wordnet as wn

def preds_to_hypernyms(preds):
    """Translate YOLO predictions to the corresponding wordnet hypernyms"""
    res = []
    for pred in preds:
        res.append(cat_to_hypernyms(pred))
    return res

def cat_to_hypernyms(cat):
    """Translate categories to the corresponding wordnet hypernyms"""
    res = []
    wo_syn = wn.synsets(cat)
    for elem in wo_syn:
        elem = elem.hypernyms()
        if elem:
            elem = elem[0].name().split(".")[0].replace('_', ' ')
            if elem not in res:
                res.append(elem)
    return res

def find_synset(noun):
    """Find synset of a word"""
    res = []
    wo_syn = wn.synsets(noun)
    for i in wo_syn:
        j = i.name().split(".")[0]
        type_i = i.name().split(".")[1]
        if type_i == 'n':
            res.append(j)
    return res

def similarities(cat1, cat2):
    """Return similarity between two words based on the wordnet graph"""
    node1 = wn.synset(str(cat1) + str('.n.01'))
    node2 = wn.synset(str(cat2) + str('.n.01'))
    return node1.path_similarity(node2)
