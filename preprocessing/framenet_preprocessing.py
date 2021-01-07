from nltk.corpus import framenet as fn
import random
import framenet_connotationframes_mapping as map


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


def get_examples_containing_subj_and_obj(nlp, lu: object, lu_text: str) -> list:
    """ Retrieves and example sentence for a lexical unit which is meant to contain both a subject and an object.

    As soon as one sentence is found which contains a subject and an object, this sentence will be returned.
    If no sentence contains both subject and object the first sentence containing a subject will be returned.
    If no sentence contains a subject the first sentence containing an object will be returned.
    If still no sentence could be found, no sentence will be returned.

    :param lu_text: String. The Lexical Unit as a string.
    :param lu: Object. The Lexical Unit as a FrameNet Object.
    :return: List. Contains one or more sentences in string format.
    """
    all_examples = get_lu_examples(lu)

    sent_containing_subject = []
    sent_containing_object = []
    sent_containing_subject_object = []

    for example in all_examples:
        counter = 0
        sentence_text = example.text

        logical_subject = map.detect_subject(nlp, sentence_text, lu_text)
        if len(logical_subject) > 0:
            sent_containing_subject.append(example)
            counter += 1
        # print('Das logische Subjekt dieses Beispielsatzes ist: ' + str(logical_subject))

        logical_object = map.detect_object(nlp, sentence_text, lu_text)
        if len(logical_object) > 0:
            sent_containing_object.append(example)
            counter +=1
        # print('Das logische Objekt dieses Beispielsatzes ist: ' + str(logical_object))

        if counter == 2:
            sent_containing_subject_object.append(example)

    if len(sent_containing_subject_object) > 0:
        return sent_containing_subject_object

    else:
        return sent_containing_subject if len(sent_containing_subject) != 0 else sent_containing_object


def get_random_example_and_fes(lu: object) -> list:
    """ Retrieves random example sentence with the respective Frame Elements and their positions in the sentence.

    :param lu: Object. FrameNet Lexical Unit Object which can be processed within the FrameNet API
    :return: List. Contains two elements: 1: example sentence, 2: FEs with position in sentence
    """
    example_and_fes = []
    examples = lu.exemplars
    amount_examples = len(examples)
    if amount_examples > 0:
        random_position = random.randint(0, amount_examples-1)
        random_sentence = examples[random_position]
        random_sentence_fes = (random_sentence.frameAnnotation.FE)[0]

        example_and_fes.append(random_sentence.text)  # Only the text of the sentence will be added, not the 'object'
        example_and_fes.append(random_sentence_fes)
    else:
        example_and_fes.append("No sentence")
        example_and_fes.append("No FEs")

    return example_and_fes


if __name__ == '__main__':
    love = get_lu_instance('love', rand=False)
    love_example = get_random_example_and_fes(love)
    print(love_example)
    print(love.keys())