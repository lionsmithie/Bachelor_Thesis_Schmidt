from nltk.corpus import framenet as fn
import random

def regex(verb: str) -> str:
    """ Converts a verb into a regular expression so it can be processed for a FrameNet lookup.

    :param verb: String. The verb to be converted
    :return: String. The regular expression for further processing
    """
    regex = r'{}\.v'.format(verb)
    return regex


def frame_count(verb: str) -> int:
    """ Counts the amount of evoked frames in FrameNet per verb.

    :param verb: String. Input verb for which the amount of evoked frames will be counted
    :return: Integer. Amount of evoked frames
    """
    verb_regex = regex(verb)
    frames = fn.lus(verb_regex)  # Returns a list with all frames evoked by the verb.
    return len(frames)


def get_lu_instance(verb: str, rand=False) -> object:
    """ Retrieves a Lexical Unit Object from FrameNet given a verb.

    Note: If several Lexical Units for the given verb exist, and rand is set to True (default), a random Lexical Unit
    will be retrieved. If rand is set to False, the first entry of Lexical Units will be retrieved.

    :param verb: String. A verb for which the Lexical Unit shall be retrieved
    :param rand: Boolean. If True, returned object will be chosen pseudo randomly. Else, first element will be returned
    :return: Object: Lexical Unit Object which can be processed within the FrameNet API
    """
    lu = regex(verb)
    lus_list = fn.lus(lu)
    if rand is False:
        return lus_list[0]
    amount_lus = len(lus_list)
    random_index = random.randint(0, amount_lus-1)
    return lus_list[random_index]


def get_lu_examples(lu: object) -> list:
    """ Retrieves a list of example sentences for a Lexical Unit in FrameNet.

    :param lu: FrameNet Object. Lexical Unit Instance which can be processed within the FrameNet API
    :return: List. List of example sentences
    """
    instance = lu
    examples = instance.exemplars
    return examples


def get_random_example_and_fes(lu: object) -> list:
    """ Retrieves random example sentence with the respective Frame Elements and their positions in the sentence.

    :param lu: Object. FrameNet Lexical Unit Object which can be processed within the FrameNet API
    :return: List. Contains two elements: 1: example sentence, 2: FEs with position in sentence
    """
    example_and_fes = []
    examples = lu.exemplars
    amount_examples = len(examples)
    random_position = random.randint(0, amount_examples-1)
    random_sentence = examples[random_position]
    random_sentence_fes = random_sentence.frameAnnotation.FE

    example_and_fes.append(random_sentence.text)  # Only the text of the sentence will be added, not the 'object'
    example_and_fes.append(random_sentence_fes)

    return example_and_fes


if __name__ == '__main__':
    love = get_lu_instance('love', rand=False)
    love_example = get_random_example_and_fes(love)
    print(love_example)