import preprocessing.framenet_preprocessing as fn_pre
from nltk.corpus import framenet as fn
from preprocessing.serialization import load_obj
from preprocessing.serialization import save_obj


def find_common_verbs(filename: str) -> list:
    """Creates a list with verbs that occur both in the Connotation Frame Lexicon and in FrameNet.

    For this project, input should be 'extracted_cf_verbs'.

    :param filename: String. The path to the preprocessed Connotation Frame Lexicon (Dictionary {verb:[CF]})
    :return: List. List containing common verbs.
    """
    common_verbs = []
    connotation_frame_dict = load_obj(filename)
    for key, value in connotation_frame_dict.items():
        frame_count = fn_pre.frame_count(key)
        if frame_count > 0:
            common_verbs.append(key)
    return common_verbs


def cf_verbs_frame_count(filename: str) -> dict:
    """Counts for each Connotation Frame verb the amount of FrameNet Frames evoked by this verb.

    Note: This method only counts verbs that occur both in the Connotation Frame Lexicon AND FrameNet.
    The dictionary looks like this: {'have': 10, 'say': 6, 'make': 11, ...}

    :param filename: String. The path to the preprocessed Connotation Frame Lexikon (Dictionary {verb:[CF]})
    :return: Dictionary. Keys are verbs, values are the number of evoked frames in FrameNet
    """
    verb_frame_amount_dict = {}
    connotation_frame_dict = load_obj(filename)
    for key, value in connotation_frame_dict.items():
        frame_count = fn_pre.frame_count(key)
        if frame_count > 0:
            verb_frame_amount_dict[key] = frame_count
    return verb_frame_amount_dict


def find_unambiguous_common_verbs(verb_frame_amount_dict: dict) -> list:
    """Extracts from the verb - frame amount dictionary those verbs which evoke only one frame.

    :param verb_frame_amount_dict: Dictionary. Keys are verbs, values are the amount of frames the verbs evoke.
    :return: List. Only those verbs which evoke only one frame.
    """
    unambiguous_verbs = []
    for key, value in verb_frame_amount_dict.items():
        if value == 1:
            unambiguous_verbs.append(key)
    return unambiguous_verbs


def map_cfs_lus(verbs: list, cfs: dict) -> dict:
    """Maps the Connotation Frames to the Lexical Units in FrameNet.

    Note: The distinction between ambiguous verbs and unambiguous verbs has to be made before. So the input list 'verbs'
    should already be filtered.

    The return dict looks like this:
    all verbs: { ( "verb", (Lexical Unit IDs) ) : {Connotation Frame} }
    unambiguous verbs: { ( "verb", Lexical Unit ID ) : {Connotation Frame} }

    :param verbs: List. Common words that occur both in the Connotation Frame Lexicon and in FrameNet
    :param cfs: Dictionary. Keys are verbs as strings, values are the Connotation Frames as nested dictionaries
    :return:
    """
    mapping = {}

    for verb in verbs:
        connotation_frame = cfs[verb]

        key_information = []
        key_information.append(verb)

        verb_regex = fn_pre.regex(verb)
        lus = fn.lus(verb_regex)

        if len(lus) == 1:
            lu = lus[0].ID
            key_information.append(lu)  # Distinction between single occurences and multiple occurences is crucial,
            # otherwise one will get an exception
        else:
            int_lus = []
            for lu in lus:
                int_lus.append(lu.ID)

            key_information.append(tuple(int_lus))

        information = tuple(key_information)

        mapping[information] = connotation_frame

    return mapping


if __name__ == '__main__':
    # cf_verb_frame_count_dict = cf_verbs_frame_count('extracted_cf_verbs')  # contains all common verbs/LUs and the
    # amount of frames evoked.

    verb_frame_count = load_obj('cf_verb_frame_count_dict')
    cf_verbs = load_obj('extracted_cf_verbs')

    # common_verbs = find_common_verbs('extracted_cf_verbs')
    unambiguous_verbs = find_unambiguous_common_verbs(verb_frame_count)
    map_cf_and_fn = map_cfs_lus(unambiguous_verbs, cf_verbs)

    # save_obj(cf_verb_frame_count_dict, 'cf_verb_frame_count_dict')
    # save_obj(map_cf_and_fn, 'mapping_verb_lu_cfs')
