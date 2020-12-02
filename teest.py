#tbd
from nltk.corpus import framenet as fn
import preprocessing.framenet_preprocessing as fn_pre
from preprocessing.serialization import load_obj
import en_core_web_sm
import spacy
from spacy.pipeline import DependencyParser
import re

nlp = en_core_web_sm.load()
parser = DependencyParser(nlp.vocab)

doc = nlp("How could she compare with you ? ")

#print(doc)

#for token in doc:
#    print(token.text, token.tag_, token.dep_, token.head.lemma_, token.head.head.lemma_)


test_set = set()
test_set.add("Hi")
test_set.add("baaam")
test_set.add("Hi")

print(test_set)


def map_cf_roles_and_fes(mapping_verb_lu_cfs: dict) -> list:
    """(  [(90, 91, 'Experiencer'), (97, 127, 'Content')]  )

    :return:
    """
    mapping = []

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        sentence_and_fes = fn_pre.get_random_example_and_fes(lu_object)
        sentence = sentence_and_fes[0]
        fes = sentence_and_fes[1]

        logical_subject = detect_subject(sentence, lu_text)  # looks like this:
        # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 means active)
        logical_object = detect_object(sentence, lu_text)  # same as above.

        if len(logical_subject) > 0:  # if a subject was detected.
            agent_role = ['Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            for fe in fes:
                if logical_subject[1][0] in fe or logical_subject[1][1] in fe:  # Refers to the start or end positions.
                    agent_role.append(fe[2])  # fe looks like this: (start pos, end pos, 'Frame Element name')
            tupled_agent_role = tuple(agent_role)
            information.append(tupled_agent_role)
        else:
            information.append('No agent role mapping possible.')

        if len(logical_object) > 0:
            patient_role = ['Patient']
            for fe in fes:
                if logical_object[1][0] in fe or logical_object[1][1] in fe:
                    patient_role.append(fe[2])
            tupled_patient_role = tuple(patient_role)
            information.append(tupled_patient_role)
        else:
            information.append('No patient role mapping possible.')

        information.append(sentence)
        mapping.append(information)

test_list = []
satz = "I love you."
fe = (0,1)
print(satz[0:1])