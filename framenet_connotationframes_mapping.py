import preprocessing.framenet_preprocessing as fn_pre
from nltk.corpus import framenet as fn
from preprocessing.serialization import load_obj
from preprocessing.serialization import save_obj
import en_core_web_sm
import re
import pprint


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
    The returned dictionary looks like this: {'have': 10, 'say': 6, 'make': 11, ...}

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


def detect_subject(nlp: object, sentence: str, lu: str) -> list:
    """Detects the syntactic subject of a given head and returns it's string, position, head and passive boolean.

    The returned list looks like this:
    ["subject", (position start, position end), "head", 0] (0 means False for passive; so 0 is active)

    :param nlp: Object. Preloaded Language Model.
    :param lu: String. The Lexical Unit that we want to retrieve the information for.
    :param sentence: String. Sentence to be parsed.
    :return: List. Containing information about the syntactic subject, position in the sentence and head
    """
    # nlp = en_core_web_sm.load()
    doc = nlp(sentence)
    regex = re.compile('.*subj.*')  # To check later whether the token is parsed as a subject
    head = lu

    token_and_head = []

    for token in doc:  # For each word in the given sentence

        if re.match(regex, token.dep_) and head == token.head.lemma_:  # To make sure the subject is headed by our
            start_pos = token.idx                                      # Lexical Unit. Lemmatizing is important here.
            end_pos = start_pos + len(token.text)                      # (Therefore head.lemma_)
            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)

            passive_regex = re.compile('.*subjpass.*')  # To check whether it's an active or passive case.
            if re.match(passive_regex, token.dep_):
                token_and_head.append(1)
            else:
                token_and_head.append(0)

    return token_and_head


def detect_subject_short_phrase(nlp: object, sentence: str, lu: str) -> list:
    """Detects the syntactic subject phrase of a given head and returns it's string, position, head and passive boolean.

    The 'short' phrase is considered as the syntactic subject and (only) it's direct descendants (children).
    Only subjects which depend directly on the given lexical unit are being retrieved. E.g. if the verb for which we
    want to detect the subject is 'hate', only a syntactic subject in the sentence which is headed by 'hate' will be
    considered - and it's phrase will be retrieved.

    The returned list looks like this:
    ["subject head", (position start, position end), "head", 0] (0 means False for passive; so 0 is active)

    :param nlp: Object. Preloaded Language Model.
    :param lu: String. The Lexical Unit that we want to retrieve the information for.
    :param sentence: String. Sentence to be parsed.
    :return: List. Containing information about the syntactic 'short' subject phrase, position in the sentence and head
    """
    # nlp = en_core_web_sm.load()
    doc = nlp(sentence)
    regex = re.compile('.*subj.*')  # To check later whether the token is parsed as a subject
    head = lu

    token_and_head = []

    for token in doc:  # For each word in the given sentence

        if re.match(regex, token.dep_) and head == token.head.lemma_:  # To make sure the subject is headed by our
            children_indicies = [t.idx for t in token.children]        # Lexical Unit. Lemmatizing is important here!
            children_indicies.append(token.idx)  # Adding the 'head' token as it has to be a part of the phrase
            children_indicies.sort()

            token_index = children_indicies.index(token.idx)  # Saving the index of the head token in the sentence

            children_texts = [t.text for t in token.children]
            children_texts.insert(token_index, token.text)  # Inserting the 'head' token text at the right position

            start_pos = children_indicies[0]  # Because we want to retrieve the left most index of the phrase
            end_pos = children_indicies[-1] + len(children_texts[-1])  # Retrieving the right most index of the phrase

            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)

            passive_regex = re.compile('.*subjpass.*')  # To check whether it's an active or passive case.
            if re.match(passive_regex, token.dep_):
                token_and_head.append(1)
            else:
                token_and_head.append(0)

    return token_and_head


def detect_subject_long_phrase(nlp: object, sentence: str, lu: str) -> list:
    """Detects the syntactic subject phrase of a given head and returns it's string, position, head and passive boolean.

    The 'long' phrase is considered as the syntactic subject and ALL it's descendants (subtree).
    Only subjects which depend directly on the given lexical unit are being retrieved. E.g. if the verb for which we
    want to detect the subject is 'hate', only a syntactic subject in the sentence which is headed by 'hate' will be
    considered - and it's phrase will be retrieved.

    The returned list looks like this:
    ["subject head", (position start, position end), "head", 0] (0 means False for passive; so 0 is active)

    :param lu: String. The Lexical Unit that we want to retrieve the information for.
    :param sentence: String. Sentence to be parsed.
    :return: List. Containing information about logical subject, position in the sentence and head
    """
    # nlp = en_core_web_sm.load()
    doc = nlp(sentence)
    regex = re.compile('.*subj.*')  # To check later whether the token is parsed as a subject
    head = lu

    token_and_head = []

    for token in doc:  # For each word in the given sentence

        if re.match(regex, token.dep_) and head == token.head.lemma_:  # To make sure the subject is headed by our
            subtree_indicies = [t.idx for t in token.subtree]          # Lexical Unit. Lemmatizing is important here!
            subtree_indicies.append(token.idx)   # Adding the 'head' token as it has to be part of the phrase.

            token_index = subtree_indicies.index(token.idx)  # Saving the index of the head token in the sentence

            subtree_texts = [t.text for t in token.subtree]
            subtree_texts.insert(token_index, token.text)  # Inserting the 'head' token text at the right position

            start_pos = subtree_indicies[0]  # Because we want to retrieve the left most index of the phrase
            end_pos = subtree_indicies[-1] + len(subtree_texts[-1])  # Retrieving the right most index of the phrase

            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)

            passive_regex = re.compile('.*subjpass.*')  # To check whether it's an active or passive case.
            if re.match(passive_regex, token.dep_):
                token_and_head.append(1)
            else:
                token_and_head.append(0)

    return token_and_head


def detect_object(nlp: object, sentence: str, lu: str) -> list:
    """Detects the syntactic object of a given head and returns it's string, position, head and passive boolean.

    The returned list looks like this:
    ["object", (position start, position end), "head", 0] (0 means False for passive; so 0 is active)

    :param nlp: Object. Preloaded Language Model.
    :param lu: String. The Lexical Unit that we want to retrieve the information for.
    :param sentence: String. Sentence to be parsed.
    :return: List. Containing information about the syntactic object, position in the sentence and head.
    """
    # nlp = en_core_web_sm.load()
    doc = nlp(sentence)
    regex = re.compile('.*obj.*')  # To check later whether a token is a parsed object.
    head = lu

    token_and_head = []

    for token in doc:  # For each word in the given sentence

        if re.match(regex, token.dep_) and head == token.head.lemma_:  # To make sure the object is headed by our
            start_pos = token.idx                                      # Lexical Unit. Lemmatizing is important here!
            end_pos = start_pos + len(token.text)
            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)
            token_and_head.append(0)  # Passive indicator which is not used but added in order to keep the list length

        elif re.match(regex, token.dep_) and head == token.head.head.lemma_:  # the object can also be 'grand-child' of
            start_pos = token.idx                                             # the Lexical Unit
            end_pos = start_pos + len(token.text)
            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)
            token_and_head.append(0)


    return token_and_head


def detect_object_short_phrase(nlp: object, sentence: str, lu: str) -> list:
    """Detects the syntactic object phrase of a given head and returns it's string, position, head and passive boolean.

    The 'short' phrase is considered as the syntactic object and (only) it's direct descendants (children).
    Only objects which depend directly OR secondly on the given lexical unit are being retrieved. E.g. if the verb for
    which we want to detect the object is 'hate', only a syntactic object in the sentence whose 'parent' or 'grand
    parent' is 'hate' will be considered - and it's phrase will be retrieved.

    The returned list looks like this:
    ["object head", (position start, position end), "head", 0] (0 means False for passive; so 0 is active)

    :param lu: String. The Lexical Unit that we want to retrieve the information for.
    :param sentence: String. Sentence to be parsed.
    :return: List. Containing information about the syntactic object, position in the sentence and head.
    """
    # nlp = en_core_web_sm.load()
    doc = nlp(sentence)
    regex = re.compile('.*obj.*')  # To check later whether the token is parsed as a subject
    head = lu

    token_and_head = []

    for token in doc:  # For each word in the given sentence

        if re.match(regex, token.dep_) and head == token.head.lemma_:  # To make sure the object is headed by our
            children_indicies = [t.idx for t in token.children]        # Lexical Unit.
            children_indicies.append(token.idx)  # Adding the 'head' token as well as it has to be part of the phrase.
            children_indicies.sort()

            token_index = children_indicies.index(token.idx)  # Saving the index of the head token in the sentence

            children_texts = [t.text for t in token.children]
            children_texts.insert(token_index, token.text)  # Inserting the 'head' token text at the right position

            start_pos = children_indicies[0]  # Because we want to retrieve the left most index of the phrase
            end_pos = children_indicies[-1] + len(children_texts[-1])  # Retrieving the right most index of the phrase

            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)
            token_and_head.append(0)  # Passive indicator which is not used but added in order to keep the list length

        elif re.match(regex, token.dep_) and head == token.head.head.lemma_:  # the object can also be 'grand-child' of
            children_indicies = [t.idx for t in token.children]               # the Lexical Unit.
            children_indicies.append(token.idx)  # Adding the 'head' token as it has to be part of the phrase.
            children_indicies.sort()

            token_index = children_indicies.index(token.idx)  # Saving the index of the head token in the sentence

            children_texts = [t.text for t in token.children]
            children_texts.insert(token_index, token.text)  # Inserting the 'head' token text at the right position

            start_pos = children_indicies[0]  # Because we want to retrieve the left most index of the phrase
            end_pos = children_indicies[-1] + len(children_texts[-1])  # Retrieving the right most index of the phrase

            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)
            token_and_head.append(0)

    return token_and_head


def detect_object_long_phrase(nlp: object, sentence: str, lu: str) -> list:
    """Detects the syntactic object phrase of a given head and returns it's string, position, head and passive boolean.

    The 'long' phrase is considered as the syntactic object and ALL it's descendants (subtree).
    Only objects which depend directly OR secondly on the given lexical unit are being retrieved. E.g. if the verb for
    which we want to detect the object is 'hate', only a syntactic object in the sentence whose 'parent' or 'grand
    parent' is 'hate' will be considered - and it's phrase will be retrieved.

    The returned list looks like this:
    ["object head", (position start, position end), "head", 0] (0 means False for passive; so 0 is active)

    :param lu: String. The Lexical Unit that we want to retrieve the information for.
    :param sentence: String. Sentence to be parsed.
    :return: List. Containing information about the syntactic object, position in the sentence and head.
    """
    # nlp = en_core_web_sm.load()
    doc = nlp(sentence)
    regex = re.compile('.*obj.*')  # To check later whether the token is parsed as a subject
    head = lu

    token_and_head = []

    for token in doc:  # For each word in the given sentence

        if re.match(regex, token.dep_) and head == token.head.lemma_:  # To make sure the object is headed by our
            subtree_indicies = [t.idx for t in token.subtree]          # Lexical Unit
            subtree_indicies.append(token.idx)  # Adding the 'head' token as it has to be part of the phrase.
            subtree_indicies.sort()

            token_index = subtree_indicies.index(token.idx)  # Saving the index of the head token in the sentence

            subtree_texts = [t.text for t in token.subtree]
            subtree_texts.insert(token_index, token.text)  # Inserting the 'head' token text at the right position

            start_pos = subtree_indicies[0]  # Because we want to retrieve the left most index of the phrase
            end_pos = subtree_indicies[-1] + len(subtree_texts[-1])  # Retrieving the right most index of the phrase

            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)
            token_and_head.append(0)  # Passive indicator which is not used but added in order to keep the list length

        elif re.match(regex, token.dep_) and head == token.head.head.lemma_:  # the object can also be 'grand-child' of
            subtree_indicies = [t.idx for t in token.subtree]                 # the Lexical Unit.
            subtree_indicies.append(token.idx)  # Adding the 'head' token as it has to be part of the phrase.
            subtree_indicies.sort()

            token_index = subtree_indicies.index(token.idx)  # Saving the index of the head token in the sentence

            subtree_texts = [token.text for t in token.subtree]
            subtree_texts.insert(token_index, token.text)  # Inserting the 'head' token text at the right position

            start_pos = subtree_indicies[0]  # Because we want to retrieve the left most index of the phrase
            end_pos = subtree_indicies[-1] + len(subtree_texts[-1])  # Retrieving the right most index of the phrase

            token_and_head.append(token.text)
            token_and_head.append((start_pos, end_pos))
            token_and_head.append(token.head.text)
            token_and_head.append(0)  # Passive indicator which is not used but added in order to keep the list length

    return token_and_head


def map_cf_roles_and_fes_long_phrase_approach(nlp: object, mapping_verb_lu_cfs: dict) -> list:
    """Mapping of all Connotation Frame Roles and Frame Elements in FrameNet through Subjects/Objects in a sentence.

    The mapping is taking a dictionary as an input which contains the FrameNet Lexical Units as keys and the (already)
    mapped Connotation Frames as values. One key - value pair looks like this:
    {('verb', lu id): {'Perspective(writer->object)':'0,3', ...}}

    For each verb (-> for each Lexical Unit) a full mapping of both Connotation Frame Roles (Agent & Theme) is being
    performed. It is considered that the 'Agent' role aligns with the logical subject of a sentence and the 'Theme'
    role aligns with the logical object of a sentence.

    The mapping is carried out as following:
    - For each LU, one example sentence is being generated which is meant to contain both a subject and an object.
    - Both the long subject phrase and the long object phrase for the LU are being detected in this sentence.
    - For each Frame Element in the sentence is being checked whether the boundaries of the subject/object phrase match
      with the boundary of the Frame Element.
    - If the boundary of a subject phrase matches the boundary of a Frame Element, the mapping will be carried out, the
      'Agent' role will be mapped to this Frame Element.
    - If the boundary of an object phrase matches the boundary of a Frame Element, the mapping will be carried out, the
      'Theme' role will be mapped to this Frame Element.
    - If the subject is marked as passive, the 'Theme' role will be mapped to this Frame Element and the 'Agent' role
      will be mapped to the object of the LU. This ensures that the mapping is carried out using the *logical*
      subject and the *logical* object

    One example of the returned list looks like this:
    ['verb', lu id, ('Agent', 'mapped FE'), ('Patient', 'mapped FE'), 'Example sentence.']

    :param nlp: Object. Preloaded Language Model.
    :param mapping_verb_lu_cfs: Dictionary. Keys are a tuple containing verb and lu id, values are the respective CF.
    :return: Dictionary. Keys are LU IDs, values are the verbs, role mappings, CFs and example sentences in a list.
    """
    mapping = []

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        examples = fn_pre.get_examples_containing_subj_and_obj(nlp, lu_object, lu_text)

        if len(examples) > 0:

            sentence = examples[0].text  # I just chose the first sentence as it is a black box anyway
            fes = (examples[0].frameAnnotation.FE)[0]

            logical_subject = detect_subject_long_phrase(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
            logical_object = detect_object_long_phrase(nlp, sentence, lu_text)  # same as above.

            if len(logical_subject) > 0:  # if a subject was detected.
                agent_role = ['Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
                for fe in fes:
                    if logical_subject[1][0] == fe[0] and logical_subject[1][1] == fe[1]:  # Refers to the start and end positions.
                        agent_role.append(fe[2])  # fe looks like this: (start pos, end pos, 'Frame Element name')
                tupled_agent_role = tuple(agent_role)
                information.append(tupled_agent_role)
            else:
                information.append('No agent role mapping possible.')

            if len(logical_object) > 0:
                patient_role = ['Patient']
                for fe in fes:
                    if logical_object[1][0] == fe[0] and logical_object[1][1] == fe[1]:
                        patient_role.append(fe[2])
                tupled_patient_role = tuple(patient_role)
                information.append(tupled_patient_role)
            else:
                information.append('No patient role mapping possible.')

            information.append(sentence)

        else:
            information.append('No mapping possible at all')

        print(information)

        mapping.append(information)

    return mapping


def map_cf_roles_and_fes_short_phrase_approach(nlp: object, mapping_verb_lu_cfs: dict) -> list:
    """Mapping of all Connotation Frame Roles and Frame Elements in FrameNet through Subjects/Objects in a sentence.

    The mapping is taking a dictionary as an input which contains the FrameNet Lexical Units as keys and the (already)
    mapped Connotation Frames as values. One key - value pair looks like this:
    {('verb', lu id): {'Perspective(writer->object)':'0,3', ...}}

    For each verb (-> for each Lexical Unit) a full mapping of both Connotation Frame Roles (Agent & Theme) is being
    performed. It is considered that the 'Agent' role aligns with the logical subject of a sentence and the 'Theme'
    role aligns with the logical object of a sentence.

    The mapping is carried out as following:
    - For each LU, one example sentence is being generated which is meant to contain both a subject and an object.
    - Both the short subject phrase and the short object phrase for the LU are being detected in this sentence.
    - For each Frame Element in the sentence is being checked whether the boundaries of the subject/object phrase match
      with the boundary of the Frame Element.
    - If the boundary of a subject phrase matches the boundary of a Frame Element, the mapping will be carried out, the
      'Agent' role will be mapped to this Frame Element.
    - If the boundary of an object phrase matches the boundary of a Frame Element, the mapping will be carried out, the
      'Theme' role will be mapped to this Frame Element.
    - If the subject is marked as passive, the 'Theme' role will be mapped to this Frame Element and the 'Agent' role
      will be mapped to the object of the LU. This ensures that the mapping is carried out using the *logical*
      subject and the *logical* object

    One example of the returned list looks like this:
    ['verb', lu id, ('Agent', 'mapped FE'), ('Patient', 'mapped FE'), 'Example sentence.']

    :param nlp: Object. Preloaded Language Model.
    :param mapping_verb_lu_cfs: Dictionary. Keys are a tuple containing verb and lu id, values are the respective CF.
    :return: Dictionary. Keys are LU IDs, values are the verbs, role mappings, CFs and example sentences in a list.
    mapping = []
    """
    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        examples = fn_pre.get_examples_containing_subj_and_obj(nlp, lu_object, lu_text)

        if len(examples) > 0:

            sentence = examples[0].text  # I just chose the first sentence as it is a black box anyway
            fes = (examples[0].frameAnnotation.FE)[0]

            logical_subject = detect_subject_short_phrase(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
            logical_object = detect_object_short_phrase(nlp, sentence, lu_text)  # same as above.

            if len(logical_subject) > 0:  # if a subject was detected.
                agent_role = ['Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
                for fe in fes:
                    if logical_subject[1][0] == fe[0] and logical_subject[1][1] == fe[1]:  # Refers to the start and end positions.
                        agent_role.append(fe[2])  # fe looks like this: (start pos, end pos, 'Frame Element name')
                tupled_agent_role = tuple(agent_role)
                information.append(tupled_agent_role)
            else:
                information.append('No agent role mapping possible.')

            if len(logical_object) > 0:
                patient_role = ['Patient']
                for fe in fes:
                    if logical_object[1][0] == fe[0] and logical_object[1][1] == fe[1]:
                        patient_role.append(fe[2])
                tupled_patient_role = tuple(patient_role)
                information.append(tupled_patient_role)
            else:
                information.append('No patient role mapping possible.')

            information.append(sentence)

        else:
            information.append('No mapping possible at all')

        print(information)

        mapping.append(information)

    return mapping


def map_cf_roles_and_fes_alternative2(nlp: object, mapping_verb_lu_cfs: dict) -> dict:
    """Mapping of all Connotation Frame Roles and Frame Elements in FrameNet through Subjects/Objects in a sentence.

    The mapping is taking a dictionary as an input which contains the FrameNet Lexical Units as keys and the (already)
    mapped Connotation Frames as values. One key - value pair looks like this:
    {('verb', lu id): {'Perspective(writer->object)':'0,3', ...}}

    For each verb (-> for each Lexical Unit) a full mapping of both Connotation Frame Roles (Agent & Patient) is being
    performed. It is considered that the 'Agent' role aligns with the logical subject of a sentence and the 'Patient'
    role aligns with the logical object of a sentence.

    The mapping is carried out as following:
    - For each LU, one example sentence is being generated which is meant to contain both a subject and an object.
    - Both subject and object are being detected in this sentence.
    - For each Frame Element in the sentence is being checked whether the subject or object is a substring of this FE.
    - If a subject is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Agent' role will be mapped to this Frame Element.
    - If an object is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Patient' role will be mapped to this Frame Element.
    - If the subject is marked as passive, the 'Patient' role will be mapped to this Frame Element and the 'Agent' role
      will be mapped to the object of the sentence.

    One example of the returned list looks like this:
    ['verb', lu id, ('Agent', 'mapped FE'), ('Patient', 'mapped FE'), 'Example sentence.']

    :param mapping_verb_lu_cfs: Dictionary. Keys are a tuple containing verb and lu id, values are the respective CF.
    :return: Dictionary. Keys are LU IDs, values are the verbs, role mappings, CFs and example sentences in a list.
    """
    mapping = {}

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        examples = fn_pre.get_examples_containing_subj_and_obj(nlp, lu_object, lu_text)

        if len(examples) > 0:

            sentence = examples[0].text  # In case there are only subjects/objects mapable I take the first sentence.
            fes = examples[0].frameAnnotation.FE[0]

            logical_subject = detect_subject(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)

            logical_object = detect_object(nlp, sentence, lu_text)  # same as above.

            agent_mapping = ['Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            patient_mapping = ['Theme']

            if len(logical_subject) > 0:  # if a subject was detected.
                subject_text = logical_subject[0]
                subject_passive_bool = logical_subject[3]

                for fe in fes:
                    fe_start = fe[0]
                    fe_end = fe[1]
                    frame_element_text = sentence[fe_start:fe_end]
                    if subject_text in frame_element_text and subject_passive_bool == 0:
                        agent_mapping.append(fe[2])  # fe looks like this: (start pos, end pos, 'Frame Element name')
                    elif subject_text in frame_element_text and subject_passive_bool == 1:
                        patient_mapping.append(fe[2])
            else:
                information.append('No agent role mapping possible.')

            if len(logical_object) > 0:
                object_text = logical_object[0]
                subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0

                for fe in fes:
                    fe_start = fe[0]
                    fe_end = fe[1]
                    frame_element_text = sentence[fe_start:fe_end]
                    if object_text in frame_element_text and subject_passive_bool == 0:  # subject passive bool is taken
                        patient_mapping.append(fe[2])  # on purpose because objects
                    elif object_text in frame_element_text and subject_passive_bool == 1:  # are not marked as passive,
                        agent_mapping.append(fe[2])  # but when subject is passive
            else:  # the object has to take the
                information.append('No patient role mapping possible.')  # agent role anyway.

            tupled_agent_mapping = tuple(agent_mapping)
            information.append(tupled_agent_mapping) if len(tupled_agent_mapping) > 0 else None

            tupled_patient_mapping = tuple(patient_mapping)
            information.append(tupled_patient_mapping) if len(tupled_patient_mapping) > 0 else None

            information.append(value)
            information.append(sentence)

        else:
            information.append('No sentences with subjects or objects found; no mapping possible.')

        print(information)

        mapping[lu_id] = information

    return mapping


def map_cf_roles_and_fes_naive_all_sents(nlp: object, mapping_verb_lu_cfs: dict) -> dict:
    """Mapping of all Connotation Frame Roles and Frame Elements in FrameNet through Subjects/Objects in a sentence.

    The mapping is taking a dictionary as an input which contains the FrameNet Lexical Units as keys and the (already)
    mapped Connotation Frames as values. One key - value pair looks like this:
    {('verb', lu id): {'Perspective(writer->object)':'0,3', ...}}

    For each verb (-> for each Lexical Unit) a full mapping of both Connotation Frame Roles (Agent & Patient) is being
    performed. It is considered that the 'Agent' role aligns with the logical subject of a sentence and the 'Patient'
    role aligns with the logical object of a sentence.

    The mapping is carried out as following:
    - For each LU, one example sentence is being generated which is meant to contain both a subject and an object.
    - Both subject and object are being detected in this sentence.
    - For each Frame Element in the sentence is being checked whether the subject or object is a substring of this FE.
    - If a subject is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Agent' role will be mapped to this Frame Element.
    - If an object is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Patient' role will be mapped to this Frame Element.
    - If the subject is marked as passive, the 'Patient' role will be mapped to this Frame Element and the 'Agent' role
      will be mapped to the object of the sentence.

    One example of the returned list looks like this:
    {123: ['verb', lu id, ('Agent', 'mapped FE'), ('Patient', 'mapped FE'), frame name, passive bool, CF]}

    :param mapping_verb_lu_cfs: Dictionary. Keys are a tuple containing verb and lu id, values are the respective CF.
    :return: Dictionary. Keys are LU IDs, values are the verbs, role mappings, CFs and example sentences in a list.
    """
    mapping = {}

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        frame_text = lu_object.frame.name

        examples = lu_object.exemplars

        passive_count = 0

        if len(examples) > 0:
            agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            theme_mapping = ['CF_Theme']

            for example in examples:
                sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
                fes = example.frameAnnotation.FE[0]

                logical_subject = detect_subject(nlp, sentence, lu_text)  # looks like this:
                # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
                logical_object = detect_object(nlp, sentence, lu_text)  # same as above.

                # subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0

                if len(logical_subject) > 0:  # and (len(agent_mapping) == 1 or subject_passive_bool is True):  # if a subject was detected.
                    subject_text = logical_subject[0]
                    subject_passive_bool = logical_subject[3]
                    subject_start = logical_subject[1][0]
                    subject_end = logical_subject[1][1]

                    for fe in fes:
                        fe_start = fe[0]
                        fe_end = fe[1]
                        frame_element_text = sentence[fe_start:fe_end]

                        if subject_start >= fe_start and subject_end <= fe_end and subject_passive_bool == 0:
                            agent_mapping.append(fe[2])  # fe looks like this: (start pos, end pos, 'Frame Element name')

                        elif subject_start >= fe_start and subject_end <= fe_end and subject_passive_bool == 1:
                            theme_mapping.append(fe[2])
                            passive_count += 1

                if len(logical_object) > 0:  # and (len(theme_mapping) == 1 or subject_passive_bool is True):
                    object_text = logical_object[0]
                    subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0
                    object_start = logical_object[1][0]
                    object_end = logical_object[1][1]

                    for fe in fes:
                        fe_start = fe[0]
                        fe_end = fe[1]
                        frame_element_text = sentence[fe_start:fe_end]

                        if object_start >= fe_start and object_end <= fe_end and subject_passive_bool == 0:  # subject passive bool is taken
                            theme_mapping.append(fe[2])  # on purpose because objects

                        elif object_start >= fe_start and object_end <= fe_end and subject_passive_bool == 1:  # are not marked as passive,
                            agent_mapping.append(fe[2])  # but when subject is passive the object has to take the agent role

                # if len(agent_mapping) > 1 and len(theme_mapping) > 1:
                #     break

            # tupled_agent_mapping = tuple(agent_mapping)
            # information.append(tupled_agent_mapping)
            set_agent_mapping = set(agent_mapping)
            information.append(set_agent_mapping)

            # tupled_patient_mapping = tuple(theme_mapping)
            # information.append(tupled_patient_mapping)
            set_theme_mapping = set(theme_mapping)
            information.append(set_theme_mapping)

            information.append(frame_text)

            information.append(passive_count)

            information.append(value)
            # information.append(sentence)

        else:
            information.append('No examples found. No Mapping possible')

        print(information)

        mapping[lu_id] = information

    return mapping


def map_cf_roles_and_fes_short_phrase_all_sents(nlp: object, mapping_verb_lu_cfs: dict) -> dict:
    """Mapping of all Connotation Frame Roles and Frame Elements in FrameNet through Subjects/Objects in a sentence.

    The mapping is taking a dictionary as an input which contains the FrameNet Lexical Units as keys and the (already)
    mapped Connotation Frames as values. One key - value pair looks like this:
    {('verb', lu id): {'Perspective(writer->object)':'0,3', ...}}

    For each verb (-> for each Lexical Unit) a full mapping of both Connotation Frame Roles (Agent & Patient) is being
    performed. It is considered that the 'Agent' role aligns with the logical subject of a sentence and the 'Patient'
    role aligns with the logical object of a sentence.

    The mapping is carried out as following:
    - For each LU, one example sentence is being generated which is meant to contain both a subject and an object.
    - Both subject and object are being detected in this sentence.
    - For each Frame Element in the sentence is being checked whether the subject or object is a substring of this FE.
    - If a subject is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Agent' role will be mapped to this Frame Element.
    - If an object is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Patient' role will be mapped to this Frame Element.
    - If the subject is marked as passive, the 'Patient' role will be mapped to this Frame Element and the 'Agent' role
      will be mapped to the object of the sentence.

    One example of the returned list looks like this:
    {123: ['verb', lu id, ('Agent', 'mapped FE'), ('Patient', 'mapped FE'), frame name, passive bool, CF]}

    :param mapping_verb_lu_cfs: Dictionary. Keys are a tuple containing verb and lu id, values are the respective CF.
    :return: Dictionary. Keys are LU IDs, values are the verbs, role mappings, CFs and example sentences in a list.
    """
    mapping = {}

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        frame_text = lu_object.frame.name

        examples = lu_object.exemplars

        passive_count = 0

        if len(examples) > 0:
            agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            theme_mapping = ['CF_Theme']

            for example in examples:
                sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
                fes = example.frameAnnotation.FE[0]

                logical_subject = detect_subject_short_phrase(nlp, sentence, lu_text)  # looks like this:
                # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
                logical_object = detect_object_short_phrase(nlp, sentence, lu_text)  # same as above.

                subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0

                if len(logical_subject) > 0:  # and (len(agent_mapping) == 1 or subject_passive_bool is True):  # if a subject was detected.
                    subject_text = logical_subject[0]
                    subject_start = logical_subject[1][0]
                    subject_end = logical_subject[1][1]

                    for fe in fes:
                        fe_start = fe[0]
                        fe_end = fe[1]
                        frame_element_text = sentence[fe_start:fe_end]

                        if subject_start == fe_start and subject_end == fe_end:
                            if subject_passive_bool == 0:
                                agent_mapping.append(fe[2])
                            else:
                                theme_mapping.append(fe[2])
                                passive_count += 1
                            # fe looks like this: (start pos, end pos, 'Frame Element name')

                if len(logical_object) > 0:  # and (len(theme_mapping) == 1 or subject_passive_bool is True):
                    object_text = logical_object[0]
                    object_start = logical_object[1][0]
                    object_end = logical_object[1][1]

                    for fe in fes:
                        fe_start = fe[0]
                        fe_end = fe[1]
                        frame_element_text = sentence[fe_start:fe_end]

                        if object_start == fe_start and object_end == fe_end:
                            theme_mapping.append(fe[2]) if subject_passive_bool == 0 else agent_mapping.append(fe[2])
                            # subject passive bool is taken on purpose because objects are not marked as passive, but
                            # when subject is passive the object has to take the agent role

                # if len(agent_mapping) > 1 and len(theme_mapping) > 1:
                #     break

            # tupled_agent_mapping = tuple(agent_mapping)
            # information.append(tupled_agent_mapping)
            set_agent_mapping = set(agent_mapping)
            information.append(set_agent_mapping)

            # tupled_patient_mapping = tuple(theme_mapping)
            # information.append(tupled_patient_mapping)
            set_theme_mapping = set(theme_mapping)
            information.append(set_theme_mapping)

            information.append(frame_text)
            information.append(passive_count)

            information.append(value)
            # information.append(sentence)

        else:
            information.append('No examples found. No Mapping possible')

        print(information)

        mapping[lu_id] = information

    return mapping


def map_cf_roles_and_fes_long_phrase_all_sents(nlp: object, mapping_verb_lu_cfs: dict) -> dict:
    """Mapping of all Connotation Frame Roles and Frame Elements in FrameNet through Subjects/Objects in a sentence.

    The mapping is taking a dictionary as an input which contains the FrameNet Lexical Units as keys and the (already)
    mapped Connotation Frames as values. One key - value pair looks like this:
    {('verb', lu id): {'Perspective(writer->object)':'0,3', ...}}

    For each verb (-> for each Lexical Unit) a full mapping of both Connotation Frame Roles (Agent & Patient) is being
    performed. It is considered that the 'Agent' role aligns with the logical subject of a sentence and the 'Patient'
    role aligns with the logical object of a sentence.

    The mapping is carried out as following:
    - For each LU, one example sentence is being generated which is meant to contain both a subject and an object.
    - Both subject and object are being detected in this sentence.
    - For each Frame Element in the sentence is being checked whether the subject or object is a substring of this FE.
    - If a subject is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Agent' role will be mapped to this Frame Element.
    - If an object is a substring, it is considered as matching with the respective Frame Element and therefore the
      'Patient' role will be mapped to this Frame Element.
    - If the subject is marked as passive, the 'Patient' role will be mapped to this Frame Element and the 'Agent' role
      will be mapped to the object of the sentence.

    One example of the returned dictionary looks like this:
    {123: ['verb', lu id, ('Agent', 'mapped FE'), ('Patient', 'mapped FE'), frame name, passive bool, CF]}

    :param mapping_verb_lu_cfs: Dictionary. Keys are a tuple containing verb and lu id, values are the respective CF.
    :return: Dictionary. Keys are LU IDs, values are the verbs, role mappings, CFs and example sentences in a list.
    """
    mapping = {}

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)

        frame_text = lu_object.frame.name

        examples = lu_object.exemplars

        passive_count = 0

        if len(examples) > 0:
            agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            theme_mapping = ['CF_Theme']

            for example in examples:
                sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
                fes = example.frameAnnotation.FE[0]

                logical_subject = detect_subject_long_phrase(nlp, sentence, lu_text)  # looks like this:
                # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
                logical_object = detect_object_long_phrase(nlp, sentence, lu_text)  # same as above.

                subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0

                if len(logical_subject) > 0:  # and (len(agent_mapping) == 1 or subject_passive_bool is True):  # if a subject was detected.
                    subject_text = logical_subject[0]
                    subject_start = logical_subject[1][0]
                    subject_end = logical_subject[1][1]

                    for fe in fes:  # fe looks like this: (start pos, end pos, 'Frame Element name')
                        fe_start = fe[0]
                        fe_end = fe[1]
                        frame_element_text = sentence[fe_start:fe_end]

                        if subject_passive_bool == 0:
                            agent_mapping.append(fe[2])
                        else:
                            theme_mapping.append(fe[2])
                            passive_count += 1


                if len(logical_object) > 0:  # and (len(theme_mapping) == 1 or subject_passive_bool is True):
                    object_text = logical_object[0]
                    object_start = logical_object[1][0]
                    object_end = logical_object[1][1]

                    for fe in fes:
                        fe_start = fe[0]
                        fe_end = fe[1]
                        frame_element_text = sentence[fe_start:fe_end]

                        if object_start == fe_start and object_end == fe_end:
                            theme_mapping.append(fe[2]) if subject_passive_bool == 0 else agent_mapping.append(fe[2])
                            # subject passive bool is taken on purpose because objects are not marked as passive, but
                            # when subject is passive the object has to take the agent role

                # if len(agent_mapping) > 1 and len(theme_mapping) > 1:
                #     break

            # tupled_agent_mapping = tuple(agent_mapping)
            # information.append(tupled_agent_mapping)
            set_agent_mapping = set(agent_mapping)
            information.append(set_agent_mapping)

            # tupled_patient_mapping = tuple(theme_mapping)
            # information.append(tupled_patient_mapping)
            set_theme_mapping = set(theme_mapping)
            information.append(set_theme_mapping)

            information.append(frame_text)
            information.append(passive_count)

            information.append(value)
            # information.append(sentence)

        else:
            information.append('No examples found. No Mapping possible')

        print(information)

        mapping[lu_id] = information

    return mapping


def mapping_naive_all_sents(nlp: object, lu_text: str, lu_id: str, lu_object: object) -> dict:
    """Noch schauen, ob dieser Workaround gebraucht wird.
    """
    mapping = {}
    examples = lu_object.exemplars

    if len(examples) > 0:
        agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
        theme_mapping = ['CF_Theme']

        for example in examples:
            sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
            fes = example.frameAnnotation.FE[0]

            logical_subject = detect_subject(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
            logical_object = detect_object(nlp, sentence, lu_text)  # same as above.

            # subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0

            if len(logical_subject) > 0:  # and (len(agent_mapping) == 1 or subject_passive_bool is True):  # if a subject was detected.
                subject_text = logical_subject[0]
                subject_passive_bool = logical_subject[3]

                for fe in fes:
                    fe_start = fe[0]
                    fe_end = fe[1]
                    frame_element_text = sentence[fe_start:fe_end]

                    if subject_text in frame_element_text and subject_passive_bool == 0:
                        agent_mapping.append(fe[2])  # fe looks like this: (start pos, end pos, 'Frame Element name')

                    elif subject_text in frame_element_text and subject_passive_bool == 1:
                        theme_mapping.append(fe[2])

            if len(logical_object) > 0:  # and (len(theme_mapping) == 1 or subject_passive_bool is True):
                object_text = logical_object[0]
                subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0
                for fe in fes:
                    fe_start = fe[0]
                    fe_end = fe[1]
                    frame_element_text = sentence[fe_start:fe_end]

                    if object_text in frame_element_text and subject_passive_bool == 0:  # subject passive bool is taken
                        theme_mapping.append(fe[2])  # on purpose because objects

                    elif object_text in frame_element_text and subject_passive_bool == 1:  # are not marked as passive,
                        agent_mapping.append(fe[2])  # but when subject is passive the object has to take the agent role

        set_agent_mapping = set(agent_mapping)
        set_theme_mapping = set(theme_mapping)

    return [set_agent_mapping, set_theme_mapping]


def map_cf_roles_and_fes(nlp: object, mapping_verb_lu_cfs: dict) -> dict:
    """ Noch schauen, ob dieser Workaround gebraucht wird.
    """
    mapping = {}

    for key, value in mapping_verb_lu_cfs.items():
        information = []

        lu_text = key[0]
        lu_id = key[1]
        lu_object = fn.lu(lu_id)
        information.append(lu_text)
        information.append(lu_id)


        mapping_naive_all_sents = mapping_naive_all_sents(nlp, lu_text, lu_id, lu_object)
        # agent_mapping = mapping_all_sents[0]
        # theme_mapping = mapping_all_sents[1]

        information.append(mapping_naive_all_sents)
        information.append(value)

        print(information)

        mapping[lu_id] = information

    return mapping


if __name__ == '__main__':
    nlp = en_core_web_sm.load()

    print('no error please')
    # cf_verb_frame_count_dict = cf_verbs_frame_count('extracted_cf_verbs')  # contains all common verbs/LUs and the
    # amount of frames evoked.
    # save_obj(cf_verb_frame_count_dict, 'cf_verb_frame_count_dict')

    # verb_frame_count = load_obj('cf_verb_frame_count_dict')
    # cf_verbs = load_obj('extracted_cf_verbs')
    # print(cf_verbs)

    # common_verbs = find_common_verbs('extracted_cf_verbs')
    # unambiguous_verbs = find_unambiguous_common_verbs(verb_frame_count)
    # map_cf_and_fn = map_cfs_lus(unambiguous_verbs, cf_verbs)

    # save_obj(map_cf_and_fn, 'mapping_verb_lu_cfs')

    mapping = load_obj('mapping_verb_lu_cfs')
    # print(mapping)
    # lus_sentences = frame_and_sentence(mapping)
    # role_mapping_own_approach = map_cf_roles_and_fes_alternative2(mapping)
    # save_obj(role_mapping_own_approach, 'role_mapping_nonambiguous_lus')



    # role_mapping_short_phrases = map_cf_roles_and_fes_short_phrase_approach(nlp, mapping)
    # save_obj(role_mapping_short_phrases, 'role_mapping_nonamb_lus_short_phrases')
    #
    # role_mapping_long_phrases = map_cf_roles_and_fes_long_phrase_approach(nlp, mapping)
    # save_obj(role_mapping_long_phrases, 'role_mapping_nonamb_lus_long_phrases')

    # role_mapping_all_sents = map_cf_roles_and_fes_naive_all_sents(nlp, mapping)
    # save_obj(role_mapping_all_sents, 'role_mapping_nonamb_naive_all_sents_UPDATED')
    #
    # role_mapping_first_approach = map_cf_roles_and_fes_alternative2(nlp, mapping)
    # save_obj(role_mapping_first_approach, 'role_mapping_first_approach')

    role_mapping_short_phrases_all_sents = map_cf_roles_and_fes_short_phrase_all_sents(nlp, mapping)
    save_obj(role_mapping_short_phrases_all_sents, 'role_mapping_nonamb_lus_short_phrases_all_sents')

    role_mapping_long_phrases_all_sents = map_cf_roles_and_fes_long_phrase_all_sents(nlp, mapping)
    save_obj(role_mapping_long_phrases_all_sents, 'role_mapping_nonamb_lus_long_phrases_all_sents')
