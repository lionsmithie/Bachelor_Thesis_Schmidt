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
    sentence_count = 0

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
            sentence_count += 1
    else:
        print("No examples found; no mapping possible.\n")
    print('Anzahl der Sätz: ' + str(sentence_count))


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


def map_evaluation(role_mapping: dict, approach: str, eval_list: list) -> None:
    """The interactive evaluation programm for evaluating the role mapping from a technical view.

    :param approach: String. The name of the approach to be evaluated (to save the approach name in file name)
    :param eval_list: List. A list of LU IDs that are going to be evaluated.
    :param role_mapping: Dictionary. The finished dictionary with all LUs, role mappings, connotationn frames etc.
    :return: None.
    """
    name = (input("What's your name? ")).lower()

    if os.path.exists('eval/{}_map_{}_eval.pkl'.format(name, approach)):
        with open(os.path.join('eval', (name + '_map_{}_eval.pkl').format(approach)), 'rb') as f:
            updated_eval = pickle.load(f)
            last_stopped = updated_eval[0]['last_stopped']

            if last_stopped == (len(eval_list) - 1):  # The evaluation process won't run if it's already completed.
                return

    else:
        last_stopped = 0
        new_eval = [{'last_stopped': 0, 'sentence_count': 0, 'agent_positive_count': 0, 'agent_negative_count': 0,
                     'agent_not_existing_count': 0, 'theme_positive_count': 0, 'theme_negative_count': 0,
                     'theme_not_existing_count': 0, 'agent_not_sure_count': 0, 'theme_not_sure_count': 0}, {}]
        with open(os.path.join('eval', (name + '_map_{}_eval.pkl').format(approach)), 'wb') as f:
            pickle.dump(new_eval, f, pickle.HIGHEST_PROTOCOL)

        with open(os.path.join('eval', (name + '_map_{}_eval.pkl').format(approach)), 'rb') as f:
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

        this_verb_eval.append(lu_text)
        this_verb_eval.append(lu_id)
        this_verb_eval.append(lu_object.frame.name)

        sentence_count = 0

        for example in examples:

            if sentence_count == 2:
                sentence_count = 0
                break

            this_sentence_eval = []
            #
            # if len(agent_mapping) <= 1 or type(agent_mapping) != set:  # this means that no agent FE was being mapped
            #     continue
            #
            # if len(theme_mapping) <= 1 or type(theme_mapping) != set:  # this means that no theme FE was being mapped
            #     continue

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

            while agent_answer not in ['y', 'n', '-', '?']:
                print("Please answer the question by typing\n'y' for yes\n'n' for no\n'-' if there is actually "
                      "no Agent in the sentence\n'?' if you're not sure")
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

            while theme_answer not in ['y', 'n', '-', '?']:
                print("Please answer the question by typing:\n'y' for yes\n'n' for no\n'-' if there is actually "
                      "no Theme in the sentence\n'?' if you're not sure")
                theme_answer = input("y/n/-: ")

            updated_eval[0]['sentence_count'] += 1

            if agent_answer == 'y':
                updated_eval[0]['agent_positive_count'] += 1
            elif agent_answer == 'n':
                updated_eval[0]['agent_negative_count'] += 1
            elif agent_answer == '?':
                updated_eval[0]['agent_not_sure_count'] += 1
            else:
                updated_eval[0]['agent_not_existing_count'] += 1

            if theme_answer == 'y':
                updated_eval[0]['theme_positive_count'] += 1
            elif theme_answer == 'n':
                updated_eval[0]['theme_negative_count'] += 1
            elif theme_answer == '?':
                updated_eval[0]['theme_not_sure_count'] += 1
            else:
                updated_eval[0]['theme_not_existing_count'] += 1

            this_sentence_eval.append(sentence)
            this_sentence_eval.append('Agent Answer: ' + agent_answer)
            this_sentence_eval.append('Theme Answer: ' + theme_answer)

            this_verb_eval.append(this_sentence_eval)

            sentence_count += 1

        updated_eval[1][lu_id] = this_verb_eval
        updated_eval[0]['last_stopped'] += 1

        with open(os.path.join('eval', (name + '_map_{}_eval.pkl').format(approach)), 'wb') as f:
            pickle.dump(updated_eval, f, pickle.HIGHEST_PROTOCOL)

    print("Evaluation completed! Thank you")


def cf_evaluation(role_mapping: dict, eval_list: list) -> None:
    """Interactive programm for evaluating the connotation frames in the FrameNet context.

    The returned list looks like this:
    [{statistics dict}, {LU ID: [lu_text, lu_id, frame, [sentence1_eval, sentence2_eval]]}]
    :param eval_list: List. A list of LU IDs that are going to be evaluated.
    :param role_mapping: Dictionary. The finished dictionary with all LUs, role mappings, connotation frames etc.
    :return: None.
    """
    name = (input("What's your name? ")).lower()

    if os.path.exists('eval/{}_cf_eval.pkl'.format(name)):
        with open(os.path.join('eval', name + '_cf_eval.pkl'), 'rb') as f:
            updated_eval = pickle.load(f)
            last_stopped = updated_eval[0]['last_stopped']

            if last_stopped == (len(eval_list) - 1):  # The evaluation process won't run if it's already completed.
                return

    else:
        last_stopped = 0
        new_eval = [{'last_stopped': 0, 'sentence_count': 0}, {}]
        with open(os.path.join('eval', name + '_cf_eval.pkl'), 'wb') as f:
            pickle.dump(new_eval, f, pickle.HIGHEST_PROTOCOL)

        with open(os.path.join('eval', name + '_cf_eval.pkl'), 'rb') as f:
            updated_eval = pickle.load(f)

    for lexical_unit in eval_list[last_stopped:]:

        to_be_evaluated = role_mapping[lexical_unit]

        if len(to_be_evaluated) < 4:  # If no proper mapping was found
            continue

        agent_mapping = to_be_evaluated[2]  # To check later if agent and theme are in the sentence in order to be able
        theme_mapping = to_be_evaluated[3]  # to evaluate the Connotation Frame

        connotation_frame = to_be_evaluated[6]

        lu_text = to_be_evaluated[0]
        lu_id = to_be_evaluated[1]
        lu_object = fn.lu(lu_id)

        examples = lu_object.exemplars

        this_verb_eval = []

        this_verb_eval.append(lu_text)
        this_verb_eval.append(lu_id)
        this_verb_eval.append(lu_object.frame.name)

        sentence_count = 0

        print("Verb: '{}'\n".format(lu_text))
        print("Please answer the following Connotation Frame Questions. How would you rate the following features?:\n")

        persp_writer_agent_verb_eval = input("Perspective(writer->agent) [please type in value between -2 and 2 or '?']:\n")
        while persp_writer_agent_verb_eval not in ['-2', '-1', '0', '1', '2', '?']:
            persp_writer_agent_verb_eval = input("Perspective(writer->agent) [please type in value between -2 and 2 or '?']:\n")

        persp_writer_theme_verb_eval = input("Perspective(writer->theme) [please type in value between -2 and 2 or '?']:\n")
        while persp_writer_theme_verb_eval not in ['-2', '-1', '0', '1', '2', '?']:
            persp_writer_theme_verb_eval = input("Perspective(writer->theme) [please type in value between -2 and 2 or '?']:\n")

        persp_agent_theme_verb_eval = input("Perspective(agent->theme) [please type in value between -2 and 2 or '?']:\n")
        while persp_agent_theme_verb_eval not in ['-2', '-1', '0', '1', '2', '?']:
            persp_agent_theme_verb_eval = input("Perspective(agent->theme) [please type in value between -2 and 2 or '?']:\n")

        persp_theme_agent_verb_eval = input("Perspective(theme->agent) [please type in value between -2 and 2 or '?']:\n")
        while persp_theme_agent_verb_eval not in ['-2', '-1', '0', '1', '2', '?']:
            persp_theme_agent_verb_eval = input("Perspective(theme->agent) [please type in value between -2 and 2 or '?']:\n")

        value_theme_verb_eval = input("Value(theme) [please type in value between -2 and 2 or '?']:\n")
        while value_theme_verb_eval not in ['-2', '-1', '0', '1', '2', '?']:
            value_theme_verb_eval = input("Value(theme) [please type in value between -2 and 2 or '?']:\n")

        verb_cf_eval = []

        persp_writer_agent_list = ['Perspective(writer->agent)', connotation_frame['Perspective(writer->agent)'],
                                   persp_writer_agent_verb_eval]
        persp_writer_theme_list = ['Perspective(writer->theme)', connotation_frame['Perspective(writer->theme)'],
                                   persp_writer_theme_verb_eval]
        persp_agent_theme_list = ['Perspective(agent->theme)', connotation_frame['Perspective(agent->theme)'],
                                  persp_agent_theme_verb_eval]
        persp_theme_agent_list = ['Perspective(theme->agent)', connotation_frame['Perspective(theme->agent)'],
                                  persp_theme_agent_verb_eval]
        value_theme_list = ['Value(theme)', connotation_frame['Value(theme)'], value_theme_verb_eval]

        for example in examples:

            if sentence_count == 2:
                sentence_count = 0
                break

            sentence = example.text
            fes = (example.frameAnnotation.FE)[0]
            # one entry looks like this: (start pos, end pos, 'Frame Element name')

            agent_frame_elements_in_sentence = []
            theme_frame_elements_in_sentence = []
            agent_mapping_in_this_sentence = []
            theme_mapping_in_this_sentence = []

            # checking if an Agent was found in this sentence - This is also important for the CF evaluation!!
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

            # CF in Sentence Evaluation
            print("Verb: '{}'\n".format(lu_text))

            print("The sentence to be evaluated (VERB: {}): \n{}\n".format(lu_text.upper(), sentence))

            persp_writer_agent_sent_eval = input(
                "Perspective(writer->agent) [please type in value between -2 and 2 or '?']:\n")
            while persp_writer_agent_sent_eval not in ['-2', '-1', '0', '1', '2', '?']:
                persp_writer_agent_sent_eval = input(
                    "Perspective(writer->agent) [please type in value between -2 and 2 or '?']:\n")

            persp_writer_theme_sent_eval = input(
                "Perspective(writer->theme) [please type in value between -2 and 2 or '?']:\n")
            while persp_writer_theme_sent_eval not in ['-2', '-1', '0', '1', '2', '?']:
                persp_writer_theme_sent_eval = input(
                    "Perspective(writer->theme) [please type in value between -2 and 2 or '?']:\n")

            persp_agent_theme_sent_eval = input(
                "Perspective(agent->theme) [please type in value between -2 and 2 or '?']:\n")
            while persp_agent_theme_sent_eval not in ['-2', '-1', '0', '1', '2', '?']:
                persp_agent_theme_sent_eval = input(
                    "Perspective(agent->theme) [please type in value between -2 and 2 or '?']:\n")

            persp_theme_agent_sent_eval = input(
                "Perspective(theme->agent) [please type in value between -2 and 2 or '?']:\n")
            while persp_theme_agent_sent_eval not in ['-2', '-1', '0', '1', '2', '?']:
                persp_theme_agent_sent_eval = input(
                    "Perspective(theme->agent) [please type in value between -2 and 2 or '?']:\n")

            value_theme_sent_eval = input("Value(theme) [please type in value between -2 and 2 or '?']:\n")
            while value_theme_sent_eval not in ['-2', '-1', '0', '1', '2', '?']:
                value_theme_sent_eval = input("Value(theme) [please type in value between -2 and 2 or '?']:\n")

            updated_eval[0]['sentence_count'] += 1

            persp_writer_agent_list.append(persp_writer_agent_sent_eval)
            persp_writer_theme_list.append(persp_writer_theme_sent_eval)
            persp_agent_theme_list.append(persp_agent_theme_sent_eval)
            persp_theme_agent_list.append(persp_theme_agent_sent_eval)
            value_theme_list.append(value_theme_sent_eval)

            this_verb_eval.append(sentence)

            sentence_count += 1

        verb_cf_eval.append(tuple(persp_writer_agent_list))
        verb_cf_eval.append(tuple(persp_writer_theme_list))
        verb_cf_eval.append(tuple(persp_agent_theme_list))
        verb_cf_eval.append(tuple(persp_theme_agent_list))
        verb_cf_eval.append(tuple(value_theme_list))

        this_verb_eval.insert(3, verb_cf_eval)

        updated_eval[1][lu_id] = this_verb_eval
        updated_eval[0]['last_stopped'] += 1

        with open(os.path.join('eval', name + '_cf_eval.pkl'), 'wb') as f:
            pickle.dump(updated_eval, f, pickle.HIGHEST_PROTOCOL)

    print("Evaluation completed! Thank you")


def pick_lus_for_evaluation(nlp: object, role_mapping: dict) -> list:
    """Picks pseudo randomly LUs for the evaluation.

    One entry of the Role Mapping Dictionaty looks like this:
    {LU ID: ['verb', LU ID, {'CF_Agent', 'Frame Element'}, {'CF_Theme', 'Frame Element'}, 'Frame', Passive Cases, {CF}]}
    :param role_mapping: Dictionary. The finished dictionary with all LUs, role mappings, connotation frames etc.
    :return: List. First element are statistics about picked LUs, second element is the list with all picked LUs (IDs).
    """
    lus_and_counts = []

    candidate_lus = [k for k in role_mapping.keys()]

    picked_lus = []

    sentence_count = 0
    passive_count = 0
    # same_frame_count = 0  # später manuell evaluieren, wie sich das Mapping bei Verben desselben Frames verhält. Sind
                            # wahrscheinlich nicht so viele.

    for lu_id, information in role_mapping.items():
        if len(information) < 6:
            candidate_lus.remove(lu_id)
        elif len(information[2]) < 2 or len(information[3]) < 2:
            candidate_lus.remove(lu_id)

    while len(picked_lus) <= 25:
        random_index = random.randint(0, len(candidate_lus)-1)

        chosen_lu = candidate_lus[random_index]

        lu_text = role_mapping[chosen_lu][0]
        lu_object = fn.lu(chosen_lu)
        examples = lu_object.exemplars

        agent_mapping = role_mapping[chosen_lu][2]
        theme_mapping = role_mapping[chosen_lu][3]

        usable_sentence_count = 0
        passive_cases_this_sent = 0

        for example in examples:
            sentence = example.text
            fes = (example.frameAnnotation.FE)[0]
            # one entry looks like this: (start pos, end pos, 'Frame Element name')

            agent_frame_elements_in_sentence = []
            theme_frame_elements_in_sentence = []
            agent_mapping_in_this_sentence = []
            theme_mapping_in_this_sentence = []

            # checking if an Agent and Theme was found in this sentence
            for fe in fes:
                frame_element_name = fe[2]

                if frame_element_name in agent_mapping:
                    agent_mapping_in_this_sentence.append(frame_element_name)

                if frame_element_name in theme_mapping:
                    theme_mapping_in_this_sentence.append(frame_element_name)

            if len(agent_mapping_in_this_sentence) != 0 and len(theme_mapping_in_this_sentence) != 0:
                usable_sentence_count += 1

            # passive case checking:
            subject = map.detect_subject(nlp, sentence, lu_text)
            passive = subject[3] if len(subject) == 4 else 0
            passive_cases_this_sent += passive  # 'passive' is an integer 0 or 1

        if usable_sentence_count != 0:
            sentence_count += usable_sentence_count
            passive_count += passive_cases_this_sent
            picked_lus.append(chosen_lu)
            candidate_lus.remove(chosen_lu)

    lus_and_counts.append(sentence_count)
    lus_and_counts.append(passive_count)
    lus_and_counts.append(picked_lus)

    return lus_and_counts


if __name__ == '__main__':
    nlp = en_core_web_sm.load()
    role_mapping_short = load_obj("role_mapping_nonamb_lus_short_phrases_all_sents")
    role_mapping_long = load_obj("role_mapping_nonamb_lus_long_phrases_all_sents")
    role_mapping_naive = load_obj("role_mapping_nonamb_naive_all_sents")

    picked_lus = pick_lus_for_evaluation(nlp, role_mapping_short)
    # print(picked_lus)
    with open(os.path.join('eval', 'picked_lus.pkl'), 'wb') as f:
        pickle.dump(picked_lus, f, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join('eval', 'picked_lus.pkl'), 'rb') as f:
        picked_lus = pickle.load(f)

    map_evaluation(role_mapping_short, "short", picked_lus[2])
    map_evaluation(role_mapping_long, "long", picked_lus[2])
    map_evaluation(role_mapping_naive, "naive", picked_lus[2])
    cf_evaluation(role_mapping_short, picked_lus[2])
