import preprocessing.framenet_preprocessing as fn_pre
from nltk.corpus import framenet as fn
from preprocessing.serialization import load_obj
from preprocessing.serialization import save_obj
import framenet_connotationframes_mapping as map
import en_core_web_sm
import random
import os
import pickle


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


def show_mapping_for_one_verb_naive(nlp: object, lu_id: str, lu_text: str) -> list:
    """ Prints each example sentence and the calculated mapping (naive substring approach) for a verb/LU.

    :param lu_text: String. Lexical Unit in String Format.
    :param lu_id: String. Lexical Unit ID in String Format.
    :param nlp: Object. Preloaded Language Model.
    :return: None.
    """
    lu_object = fn.lu(lu_id)
    examples = lu_object.exemplars

    if len(examples) > 0:

        for example in examples:
            agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            theme_mapping = ['CF_Theme']
            sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
            fes = example.frameAnnotation.FE[0]

            logical_subject = map.detect_subject(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
            logical_object = map.detect_object(nlp, sentence, lu_text)  # same as above.

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

            print(sentence)
            print(agent_mapping)
            print(theme_mapping)
            print("Passivsatz?: "+str(subject_passive_bool)+"\n")
    else:
        print("No examples found; no mapping possible.\n")


def show_mapping_for_one_verb_short(nlp: object, lu_id: str, lu_text: str) -> list:
    """ Prints each example sentence and the calculated mapping (short phrase approach) for a verb/LU.

    :param lu_text: String. Lexical Unit in String Format.
    :param lu_id: String. Lexical Unit ID in String Format.
    :param nlp: Object. Preloaded Language Model.
    :return: None.
    """
    lu_object = fn.lu(lu_id)
    examples = lu_object.exemplars

    if len(examples) > 0:

        for example in examples:
            agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            theme_mapping = ['CF_Theme']
            sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
            fes = example.frameAnnotation.FE[0]

            logical_subject = map.detect_subject_short_phrase(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
            logical_object = map.detect_object_short_phrase(nlp, sentence, lu_text)  # same as above.

            subject_passive_bool = logical_subject[3] if len(logical_subject) > 0 else 0

            if len(
                    logical_subject) > 0:  # and (len(agent_mapping) == 1 or subject_passive_bool is True):  # if a subject was detected.
                subject_text = logical_subject[0]
                subject_start = logical_subject[1][0]
                subject_end = logical_subject[1][1]

                for fe in fes:
                    fe_start = fe[0]
                    fe_end = fe[1]
                    frame_element_text = sentence[fe_start:fe_end]

                    if subject_start == fe_start and subject_end == fe_end:
                        agent_mapping.append(fe[2]) if subject_passive_bool == 0 else theme_mapping.append(fe[2])
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

            print(sentence)
            print(agent_mapping)
            print(theme_mapping)
            print("Passivsatz?: " + str(subject_passive_bool) + "\n")
    else:
        print("No examples found; no mapping possible.\n")


def show_mapping_for_one_verb_long(nlp: object, lu_id: str, lu_text: str) -> None:
    """ Prints each example sentence and the calculated mapping (long phrase approach) for a verb/LU.

    :param lu_text: String. Lexical Unit in String Format.
    :param lu_id: String. Lexical Unit ID in String Format.
    :param nlp: Object. Preloaded Language Model.
    :return: None.
    """
    lu_object = fn.lu(lu_id)
    examples = lu_object.exemplars

    if len(examples) > 0:

        for example in examples:
            agent_mapping = ['CF_Agent']  # For the direct mapping of the cf 'agent' to the fn 'frame element'
            theme_mapping = ['CF_Theme']
            sentence = example.text  # In case there are only subjects/objects mapable I take the first sentence.
            fes = example.frameAnnotation.FE[0]

            logical_subject = map.detect_subject_long_phrase(nlp, sentence, lu_text)  # looks like this:
            # ["subject", (position start, position end), "head", 0] (0 means False for passive boolean; so 0 is active)
            logical_object = map.detect_object_long_phrase(nlp, sentence, lu_text)  # same as above.

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
                        agent_mapping.append(fe[2]) if subject_passive_bool == 0 else theme_mapping.append(fe[2])
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

            print(sentence)
            print(agent_mapping)
            print(theme_mapping)
            print("Passivsatz?: " + str(subject_passive_bool) + "\n")
    else:
        print("No examples found; no mapping possible.\n")


def map_evaluation(nlp: object, role_mapping: dict, eval_list: list) -> None:
    """

    :param eval_list: List. A list of LU IDs that are going to be evaluated.
    :param nlp:
    :param role_mapping:
    :return: None.
    """
    name = (input("What's your name? ")).lower()

    if os.path.exists('eval/{}_eval.pkl'.format(name)):
        with open(os.path.join('eval', name + '_eval.pkl'), 'rb') as f:
            updated_eval = pickle.load(f)
            last_stopped = updated_eval[0]['last_stopped']
    else:
        last_stopped = 0
        new_eval = [{'last_stopped': 0, 'sentence_count': 0, 'agent_positive_count': 0, 'agent_negative_count': 0,
                     'agent_not_existing_count': 0, 'theme_positive_count': 0, 'theme_negative_count': 0,
                     'theme_not_existing_count': 0}, {}]
        with open(os.path.join('eval', name + '_eval.pkl'), 'wb') as f:
            pickle.dump(new_eval, f, pickle.HIGHEST_PROTOCOL)

        with open(os.path.join('eval', name + '_eval.pkl'), 'rb') as f:
            updated_eval = pickle.load(f)

    for lexical_unit in eval_list[last_stopped:]:

        to_be_evaluated = role_mapping[lexical_unit]

        if len(to_be_evaluated) < 4:  # If no proper mapping was found
            continue

        agent_mapping = to_be_evaluated[2]
        # print(agent_mapping)
        # agent_mapping.remove('CF_Agent')

        theme_mapping = to_be_evaluated[3]
        # theme_mapping.remove('CF_Theme')

        lu_text = to_be_evaluated[0]
        lu_id = to_be_evaluated[1]
        lu_object = fn.lu(lu_id)

        examples = lu_object.exemplars

        print("Verb/Lexical Unit: '{}'\n".format(lu_text))

        this_verb_eval = []

        for example in examples:

            this_sentence_eval = []

            if len(agent_mapping) <= 1 or type(agent_mapping) != set:
                continue

            if len(theme_mapping) <= 1 or type(theme_mapping) != set:
                continue

            sentence = example.text
            fes = (example.frameAnnotation.FE)[0]
            # one entry looks like this: (start pos, end pos, 'Frame Element name')

            agent_frame_elements_in_sentence = []
            theme_frame_elements_in_sentence = []
            agent_mapping_in_this_sentence = []
            theme_mapping_in_this_sentence = []

            # checking if an Agent was found in this sentence
            for fe in fes:
                frame_element_name = fe[2]
                if frame_element_name in agent_mapping:
                    agent_mapping_in_this_sentence.append(frame_element_name)
                    fe_content_text = sentence[fe[0]:fe[1]]
                    agent_frame_elements_in_sentence.append("{} -> '{}'".format(frame_element_name, fe_content_text))

            if len(agent_frame_elements_in_sentence) == 0:
                continue  # Going to the next sentence as an evaluation wouldn't make sense.

            # Checking if a Theme was found in this sentence
            for fe in fes:
                frame_element_name = fe[2]
                if frame_element_name in theme_mapping:
                    theme_mapping_in_this_sentence.append(frame_element_name)
                    fe_content_text = sentence[fe[0]:fe[1]]
                    theme_frame_elements_in_sentence.append("{} -> '{}'".format(frame_element_name, fe_content_text))

            if len(theme_frame_elements_in_sentence) == 0:
                continue  # Going to the next sentence as an evaluation wouldn't make sense.



            # Agent Evaluation
            print("\n-------------------------AGENT------------------------\n")

            print("The sentence to be evaluated (VERB: {}): \n{}\n".format(lu_text.upper(), sentence))

            print("For the role of the Agent, the following Frame Element(s) have been found:")
            for frame_element in agent_frame_elements_in_sentence:
                print(frame_element)
                this_sentence_eval.append('Agent Mapping: ' + str(frame_element))

            print("\nDoes at least one of the found Frame Elements match the Role of the Agent?")
            agent_answer = input("y/n/-/?: ")

            while agent_answer not in ['y', 'n', '-']:
                print("Please answer the question by typing 'y' for yes, 'n' for no or '-' if there is actually "
                      "no Agent in the sentence")
                agent_answer = input("y/n/-: ")

            # Theme Evaluation

            print("\n\n-------------------------THEME------------------------\n")

            print("The sentence to be evaluated (VERB: {}): \n{}\n".format(lu_text.upper(), sentence))

            print("For the role of the Theme, the following Frame Element(s) have been found:")
            for frame_element in theme_frame_elements_in_sentence:
                print(frame_element)
                this_sentence_eval.append('Theme Mapping :' + str(frame_element))

            print("\nDoes at least one of the found Frame Elements match the Role of the Theme?")
            theme_answer = input("y/n/-/?: ")

            while theme_answer not in ['y', 'n', '-']:
                print("Please answer the question by typing 'y' for yes, 'n' for no or '-' if there is actually "
                      "no Theme in the sentence")
                theme_answer = input("y/n/-: ")

            updated_eval[0]['sentence_count'] += 1

            if agent_answer == 'y':
                updated_eval[0]['agent_positive_count'] += 1
            elif agent_answer == 'n':
                updated_eval[0]['agent_negative_count'] += 1
            else:
                updated_eval[0]['agent_not_existing_count'] += 1

            if theme_answer == 'y':
                updated_eval[0]['theme_positive_count'] += 1
            elif theme_answer == 'n':
                updated_eval[0]['theme_negative_count'] += 1
            else:
                updated_eval[0]['theme_not_existing_count'] += 1

            this_sentence_eval.append(sentence)
            this_sentence_eval.append('Agent Answer: ' + agent_answer)
            this_sentence_eval.append('Theme Answer: ' + theme_answer)

            this_verb_eval.append(this_sentence_eval)

        updated_eval[1][lu_id] = this_verb_eval
        updated_eval[0]['last_stopped'] += 1

        with open(os.path.join('eval', name + '_eval.pkl'), 'wb') as f:
            pickle.dump(updated_eval, f, pickle.HIGHEST_PROTOCOL)



if __name__ == '__main__':
    nlp = en_core_web_sm.load()
    role_mapping_short = load_obj("role_mapping_nonamb_lus_short_phrases_all_sents")
    #
    # all_lus = [k for k in role_mapping_short.keys()]
    # picked_lus = []
    #
    # i = 50
    #
    # while i > 0:
    #     random_index = random.randint(0, len(all_lus)-1)
    #     picked_lus.append(all_lus[random_index])
    #     all_lus.remove(all_lus[random_index])
    #     i -= 1
    #
    #
    # with open(os.path.join('eval', 'random_lus.pkl'), 'wb') as f:
    #     pickle.dump(picked_lus, f, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join('eval', 'random_lus.pkl'), 'rb') as f:
        picked_lus = pickle.load(f)

    # show_mapping_for_one_verb_short(nlp, 157, "imagine")

    map_evaluation(nlp, role_mapping_short, picked_lus[0:3])