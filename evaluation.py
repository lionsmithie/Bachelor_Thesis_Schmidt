import preprocessing.framenet_preprocessing as fn_pre
from nltk.corpus import framenet as fn
from preprocessing.serialization import load_obj
from preprocessing.serialization import save_obj
import framenet_connotationframes_mapping as map


def frame_and_sentence(mapping: dict) -> dict:
    """Creates a dictionary with verbs, Lexical Units, an example sentence and the mapped Connotation Frame.

    In case of multiple Lexical Units, an example sentence for each Lexical Unit will be stored.

    The returned dictionary looks like this:
    { ( "verb", LU ID, "Example Sentence" ) :  {Connotation Frame} }

    :param mapping: Dictionary. Keys are information about the verb and its LUs, values are the mapped CFs
    :return: Dictionary. Keys are information about the verb/LU with an example sentence, values are the mapped CFs
    """
    sentence_mapping = {}

    for key, value in mapping.items():
        verb = key[0]
        lus = key[1]

        if type(lus) == int:  # this means that there was only one single entry
            key_information = []
            key_information.append(verb)

            key_information.append(lus)  # lu is an Integer in this case

            lu_object = fn.lu(lus)

            example = fn_pre.get_random_example_and_fes(lu_object)[0]  #[0] because function gets also the FEs in [1]
            key_information.append(example)

            information = tuple(key_information)
            sentence_mapping[information] = value  # value is the Connotation Frame

        else:
            for lu in lus:
                key_information = []
                key_information.append(verb)

                key_information.append(lu)

                lu_object = fn.lu(lus)

                example = fn_pre.get_random_example_and_fes(lu_object)[0]
                key_information.append(example)

                information = tuple(key_information)
                sentence_mapping[information] = value
    return sentence_mapping

mapping = load_obj('mapping_verb_lu_cfs')
#print(mapping)
sentences = frame_and_sentence(mapping)
print(sentences)