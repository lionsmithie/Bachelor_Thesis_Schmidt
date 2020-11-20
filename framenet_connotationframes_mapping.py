import preprocessing.framenet_preprocessing as fn_pre
from preprocessing.serialization import load_obj
from preprocessing.serialization import save_obj

def cf_verbs_frame_count(filename: str) -> list:
    """Counts for each Connotation Frame verb the amount of FrameNet Frames evoked by this verb.

    Note: This method only counts verbs that occur both in the Connotation Frame Lexicon AND FrameNet.

    :param filename: String. The path to the preprocessed Connotation Frame Lexikon (Dictionary {verb:[CF]})
    :return: Dictionary. Keys are verbs, values are the number of evoked frames in FrameNet
    """
    common_verb_dict = {}
    connotation_frame_dict = load_obj(filename)
    for key, value in connotation_frame_dict.items():
        frame_count = fn_pre.frame_count(key)
        if frame_count > 0:
            common_verb_dict[key] = frame_count
    return common_verb_dict


if __name__ == '__main__':
    cf_verb_frame_count_dict = cf_verbs_frame_count('extracted_cf_verbs')  # contains all common verbs/LUs and the amount of
    # frames evoked.
    #save_obj(cf_verb_frame_count_dict, 'cf_verb_frame_count_dict')