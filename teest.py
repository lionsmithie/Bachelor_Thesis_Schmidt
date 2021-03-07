#tbd
from nltk.corpus import framenet as fn
import preprocessing.framenet_preprocessing as fn_pre
from preprocessing.serialization import load_obj
import en_core_web_sm
import spacy
from spacy.pipeline import DependencyParser
import re
import pickle
import os
import pprint

# nlp = en_core_web_sm.load()
# parser = DependencyParser(nlp.vocab)
#
# doc = nlp("We sign in , have our boat inspected by that nice man from Eclipse and are duly body tagged with a nylon cord bracelet and a number .")
#
# for token in doc:
#     print(token.text, token.head, token.pos_, token.dep_)

# #print(doc)
#

# subtree = [t.idx for t in doc[4].subtree]
# children = doc[2].children
#
# for token in subtree:
#     print(token)
#
# for token in children:
#     print(token.text)
#
# print(subtree[0])
#
# example = ['provide', 11673, ('Agent', 'Supplier'), ('Patient', 'Theme'), 'They quickly provide the necessary '
#                                                                           'interface to network PCs , workstations , '
#                                                                           'and other Ethernet equipment .']
# test = load_obj('extracted_cf_verbs')
# print(test)
#
# hate = fn.lus(r'hate\.v')
# print(hate[0].ID)

role_mapping = load_obj('role_mapping_nonamb_lus_long_phrases_all_sents')

# for key, value in role_mapping.items():
#     print(value[0:3])
#     print(value[-1])

# mapping_lenght = len(role_mapping)
# no_map_count = 0
# no_agent_count = 0
# no_theme_count = 0
#
#
# for key, value in role_mapping.items():
#     print(value)
#     if len(value) < 4:
#         no_map_count +=1
#     else:
#         if len(value[2]) < 2:
#             no_agent_count +=1
#         elif len(value[3]) < 2:
#             no_theme_count +=1
#
#
# print('Anzahl des nicht-ambigen mapping dicts: ' + str(mapping_lenght))
#
# # print('Anzahl fehlender Mappings: ' + str(no_map_count))
#
# print('Anzahl fehlender Themes: ' + str(no_theme_count))
# print('Anzahl fehlender Agents: ' + str(no_agent_count))
#
# print('Anzahl vollständige Mappings: ' + str(mapping_lenght-no_map_count-no_agent_count-no_theme_count))


#with open(os.path.join('obj', 'role_mapping_nonamb_lus_long_phrases_all_sents' + '.pkl'), 'rb') as f:
#    test_load = pickle.load(f)

with open(os.path.join('eval', 'sina_map_short_eval.pkl'), 'rb') as f:
    sina_short_eval = pickle.load(f)

with open(os.path.join('eval', 'sina_map_long_eval.pkl'), 'rb') as f:
    sina_long_eval = pickle.load(f)

with open(os.path.join('eval', 'sina_map_naive_eval.pkl'), 'rb') as f:
    sina_naive_eval = pickle.load(f)

with open(os.path.join('eval', 'lschmidt_map_short_eval.pkl'), 'rb') as f:
    lschmidt_short_eval = pickle.load(f)

with open(os.path.join('eval', 'lschmidt_map_long_eval.pkl'), 'rb') as f:
    lschmidt_long_eval = pickle.load(f)

with open(os.path.join('eval', 'lschmidt_map_naive_eval.pkl'), 'rb') as f:
    lschmidt_naive_eval = pickle.load(f)

role_mapping_long = load_obj("role_mapping_nonamb_lus_long_phrases_all_sents")
# print(lschmidt_short_eval[1])
# pprint.pprint(lschmidt_long_eval)
# print(lschmidt_naive_eval[0])

liste = [0,1,2,3,4,5]

print(liste[2:6])