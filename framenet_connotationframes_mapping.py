from nltk.corpus import framenet as fn
import sys
import preprocessing.framenet_preprocessing as fn_pre
from preprocessing.serialization import load_obj

def common_verbs(filename: str) -> list:
    """tbd
    :param filename:
    :return:
    """
    common_verb_dict = {}
    connotation_frame_dict = load_obj(filename)
    for key, value in connotation_frame_dict.items():
        frame_count = fn_pre.frame_count(key)
        if frame_count > 0:
            common_verb_dict[key] = frame_count
    return common_verb_dict


def count_statistics(verb_dictionary: dict) -> dict:
    """tbd.

    :param verb_dictionary:
    :return:
    """
    statistics = {}
    for key, value in verb_dictionary.items():
        if value in statistics:
            statistics[value] += 1
        else:
            statistics[value] = 1
    return statistics


#common_verb_dict = common_verbs('extracted_cf_verbs')  # contains all common verbs/LUs and the amount of frames evoked.
#statistics = count_statistics(common_verb_dict)

hardcode_statistics = {10: 10, 6: 23, 11: 4, 12: 2, 16: 2, 5: 37, 4: 77, 3: 118, 33: 1, 9: 16, 2: 216, 8: 12, 7: 10,
                       1: 289, 14: 1, 46: 1, 15: 3, 20: 2, 13: 1, 29: 1}
list_to_sort = []

for key, value in hardcode_statistics.items():
    list_to_sort.append(key)
sorted_list = sorted(list_to_sort)

for key in sorted_list:
    print(str(hardcode_statistics[key]) + ' Lexical Units evoke {} frame(s).'.format(key))

