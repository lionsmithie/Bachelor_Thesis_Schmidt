import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from preprocessing.serialization import load_obj
import os
import spacy
from spacy import displacy
from preprocessing.serialization import save_obj
import pickle


def frames_per_verb(verb_dictionary: dict) -> dict:
    """Counts the amount of Lexical Units which evoke a specific number of frames.

    Looks like this: {1: 289, 2: 216, ...,  46: 1}
    This means that 289 Lexical Units evoke exactly 1 frame, 216 Lexical Units evoke exactly 2 frames, 1 Lexical Unit
    evokes exactly 46 frames.

    :param verb_dictionary: Dictionary. Keys are verbs, values are the number of evoked frames in FrameNet
    :return: Dictionary. Keys are the exact Number of frames evoked, values are the amount of LUs that evoke this amount
    of frames.
    """
    statistics = {}
    for key, value in verb_dictionary.items():
        if value in statistics:
            statistics[value] += 1
        else:
            statistics[value] = 1
    return statistics


def plot_verb_frame_amount(verb_frame_amount_dict: dict) -> None:
    """Plots the statistics for evoked frames per Verb/Lexical Unit and saves the plot as a .png file.

    :param verb_frame_amount_dict:
    :return:
    """
    labels = []
    means = []
    for frames, lus in verb_frame_amount_dict.items():
        labels.append(frames)
    labels.sort()

    for label in labels:
        mean_for_label = verb_frame_amount_dict[label]
        means.append(mean_for_label)


    x = np.arange(len(labels))  # the label locations
    width = 0.6  # the width of the bars

    fig, ax = plt.subplots()
    rects = ax.bar(x, means, width, color='grey')

    ax.set_ylabel('Verbs')
    ax.set_xlabel('Frames')
    ax.set_title('Amount of Verbs evoking a certain number of frames')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects)

    fig.tight_layout()

    plt.savefig(os.path.join('plots', 'lus_frames_amount_updated'))
    plt.show()
    plt.close()


def show_dependency_parse(sentence: str) -> None:
    """

    :param sentence:
    :return:
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentence)
    # sentence_spans = list(doc.sents)
    rendered = displacy.render(doc, style='dep', jupyter=True)
    # print(rendered)
    displacy.serve(doc, style="dep")
    return rendered


def cohens_kappa(eval_r1: list, eval_r2: list, role: str) -> int:
    """ Cohens Kappa calculation for the role mapping evaluation.

    :param role: String. The role for which the Cohens Kappa shall be calculated. "Theme" or "Agent".
    :param eval_r1: List. The finished evaluation with all values of annotator 1.
    :param eval_r2: List. The finished evaluation with all values of annotator 2.
    :return: Integer. The calculated Cohens Kappa
    """
    sentence_eval_r1 = eval_r1[1]  #dict, looks like this: {655: ['lu_text', lu id, 'frame', ['Agent Mapping', 'Theme
    # Mapping', 'sentence', 'Agent Answer: y', 'Theme Answer: y'], [same for sentence 2]], 6454: [...] }
    sentence_eval_r2 = eval_r2[1]

    i = 0

    if role.lower() == 'agent':
        i = -2
    elif role.lower() == 'theme':
        i = -1

    # matrix for cohens kappa:  -> left is r1, right is r2, so 'yn' means r1 said 'y', r2 said 'n'
    yy = 0
    yn = 0
    y_ = 0  # '_' means '-'

    ny = 0
    nn = 0
    n_ = 0

    _y = 0
    _n = 0
    __ = 0

    # to have a better overview over the process, firstly I save all results in a simple list:
    r1_results = []
    r2_results = []

    for key, value in sentence_eval_r1.items():
        id = key

        answer1 = value[3][i][-1]  # refers to sentence 1
        answer2 = value[4][i][-1]  # refers to sentence 2

        r1_results.append(id)
        r1_results.append(answer1)
        r1_results.append(answer2)

    for key, value in sentence_eval_r2.items():
        id = key

        answer1 = value[3][i][-1]  # refers to sentence 1
        answer2 = value[4][i][-1]  # refers to sentence 2

        r2_results.append(id)
        r2_results.append(answer1)
        r2_results.append(answer2)

    # print(r1_results)
    # print(r2_results)
    # print('\n')

    index = 0

    for r1, r2 in zip(r1_results, r2_results):

        if r1 == '?' or r2 == '?':
            del r1_results[index]
            del r2_results[index]
            continue

        if r1 == 'y' and r2 == 'y':
            yy += 1

        elif r1 == 'y' and r2 == 'n':
            yn += 1

        elif r1 == 'y' and r2 == '-':
            y_ += 1

        elif r1 == 'n' and r2 == 'y':
            ny += 1

        elif r1 == 'n' and r2 == 'n':
            nn += 1

        elif r1 == 'n' and r2 == '-':
            n_ += 1

        elif r1 == '-' and r2 == 'y':
            _y += 1

        elif r1 == '-' and r2 == 'n':
            _n += 1

        elif r1 == '-' and r2 == '-':
            __ += 1

        index += 1

    # print(r1_results)
    # print(r2_results)

    # row totals:
    r1_y = yy + yn + y_
    r1_n = ny + nn + n_
    r1__ = _y + _n + __

    # column totals:
    r2_y = yy + ny + _y
    r2_n = yn + nn + _n
    r2__ = y_ + n_ + __

    # print('Total yes R1: ' + str(r1_y))
    # print('Total yes R2: ' + str(r2_y))
    #
    # print('Total No R1: ' + str(r1_n))
    # print('Total No R1: ' + str(r2_n))
    #
    # print('Total - R1: ' + str(r1__))
    # print('Total - R2: ' + str(r2__))

    total = r1_y + r1_n + r1__
    total_r2 = r2_y + r2_n + r2__

    print('TOTAL 1 = ' + str(total))

    if total != total_r2:
        print("TOTALS SIND NICHT GLEICH!!!")

    total_agreements = yy + nn + __

    print('TOTAL AGREEMENTS: ' + str(total_agreements))

    y_product = (r1_y * r2_y)
    n_product = (r1_n * r2_n)
    __product = (r1__ * r2__)

    sum_of_products = y_product + n_product + __product

    real_expt_by_chance = sum_of_products * (1/(52*52*52))

    kappa = ((total_agreements/52) - real_expt_by_chance) / (1 - real_expt_by_chance)

    return kappa


def read_cf_eval(eval_r1: dict, eval_r2: dict) -> list:
    """ Reads and calculates statistics of both CF evaluations.

    :param eval_r2: Dictionary. Evaluation of the Connotation Frames of annotator 2.
    :param eval_r1: Dictionary. Evaluation of the Connotation Frames of annotator 1.
    :return: List. Contains statistical values for getting the result of the evaluation.
    """
    cf_eval = []

    eval_dict_r1 = eval_r1[1]
    eval_dict_r2 = eval_r2[1]

    equal_connotations = 0
    unequal_connotations = 0

    verb_count_no_connotation = 0
    feature_count_no_connotation = 0
    feature_count = 0

    connotation_ratings_r1 = []
    connotation_ratings_r2 = []

    for key, value in eval_dict_r1.items():
        no_connotation_intermediate = feature_count_no_connotation
        for rating in value[3][0:5]:
            for e in rating[1:]:
                connotation_ratings_r1.append(float(e) if e != '?' else 0)
                if e == '?':
                    feature_count_no_connotation += 1
                feature_count += 1
        if no_connotation_intermediate != feature_count_no_connotation:
            verb_count_no_connotation += 1

    for key, value in eval_dict_r2.items():
        no_connotation_intermediate = feature_count_no_connotation
        for rating in value[3][0:5]:
            for e in rating[1:]:
                connotation_ratings_r2.append(float(e) if e != '?' else 0)
                if e == '?':
                    feature_count_no_connotation += 1
                feature_count += 1
        if no_connotation_intermediate != feature_count_no_connotation:
            verb_count_no_connotation += 1

    mean_ratings = []

    for r1, r2 in zip(connotation_ratings_r1, connotation_ratings_r2):
        mean = (r1 + r2) / 2
        mean_ratings.append(mean)

    gold = 0
    no_context = 1
    sent1 = 2
    sent2 = 3

    feature_iterator = 0

    while feature_iterator < 130:
        gold_standard = mean_ratings[gold]
        rating_no_context = mean_ratings[no_context]
        rating_sent1 = mean_ratings[sent1]
        rating_sent2 = mean_ratings[sent2]

        mean_no_gold = (rating_no_context + rating_sent1 + rating_sent2) / 3
        fitted_mean = mean_no_gold / 2

        if gold_standard - 0.2 <= fitted_mean <= gold_standard + 0.2:
            equal_connotations += 1
        else:
            unequal_connotations += 1

        feature_iterator += 1
        gold += 4
        no_context += 4
        sent1 += 4
        sent2 += 4

    verb_count_no_connotation = verb_count_no_connotation / 2
    feature_count_no_connotation = feature_count_no_connotation / 2
    feature_count = feature_count / 2 - 130

    cf_eval.append('Equal Connotations: ' + str(equal_connotations))
    cf_eval.append('Unequal Connotations: ' + str(unequal_connotations))
    cf_eval.append('Verbs where at least one feature has no Connotation: ' + str(verb_count_no_connotation))
    cf_eval.append('Feature count with no Connotation: ' + str(feature_count_no_connotation))
    cf_eval.append('Feature count total: ' + str(feature_count))

    return cf_eval


def cf_kappa(eval_r1: dict, eval_r2: dict) -> int:
    """ Calculates the Cohens Kappa for the CF evaluation.

    :param eval_r2: Dictionary. Evaluation of the Connotation Frames of annotator 2.
    :param eval_r1: Dictionary. Evaluation of the Connotation Frames of annotator 1.
    :return: Integer. Cohens Kappa value.
    """
    eval_dict_r1 = eval_r1[1]
    eval_dict_r2 = eval_r2[1]

    connotation_ratings_r1 = []
    connotation_ratings_r2 = []

    for key, value in eval_dict_r1.items():
        for rating in value[3][0:5]:
            for e in rating[2:]:
                connotation_ratings_r1.append(e)

    for key, value in eval_dict_r2.items():
        for rating in value[3][0:5]:
            for e in rating[2:]:
                connotation_ratings_r2.append(e)

    result_dict = {'-2-2': 0, '-2-1': 0, '-20': 0, '-21': 0, '-22': 0, '-2?': 0,
                   '-1-2': 0, '-1-1': 0, '-10': 0, '-11': 0, '-12': 0, '-1?': 0,
                   '0-2': 0, '0-1': 0, '00': 0, '01': 0, '02': 0, '0?': 0,
                   '1-2': 0, '1-1': 0, '10': 0, '11': 0, '12': 0, '1?': 0,
                   '2-2': 0, '2-1': 0, '20': 0, '21': 0, '22': 0, '2?': 0,
                   '?-2': 0, '?-1': 0, '?0': 0, '?1': 0, '?2': 0, '??': 0,
                   }

    total_amount_ratings = len(connotation_ratings_r1)
    print('Anzahl der Ratings: ' + str(total_amount_ratings))

    for r1, r2 in zip(connotation_ratings_r1, connotation_ratings_r2):
        result_dict['{}{}'.format(r1, r2)] += 1

    # row totals:
    r1_minus_2 = result_dict['-2-2'] + result_dict['-2-1'] + result_dict['-20'] + result_dict['-21'] + result_dict['-22'] + result_dict['-2?']
    r1_minus_1 = result_dict['-1-2'] + result_dict['-1-1'] + result_dict['-10'] + result_dict['-11'] + result_dict['-12'] + result_dict['-1?']
    r1_0 = result_dict['0-2'] + result_dict['0-1'] + result_dict['00'] + result_dict['01'] + result_dict['02'] + result_dict['0?']
    r1_1 = result_dict['1-2'] + result_dict['1-1'] + result_dict['10'] + result_dict['11'] + result_dict['12'] + result_dict['1?']
    r1_2 = result_dict['2-2'] + result_dict['2-1'] + result_dict['20'] + result_dict['21'] + result_dict['22'] + result_dict['2?']
    r1_question = result_dict['?-2'] + result_dict['?-1'] + result_dict['?0'] + result_dict['?1'] + result_dict['?2'] + result_dict['??']

    # column totals:
    r2_minus_2 = result_dict['-2-2'] + result_dict['-1-2'] + result_dict['0-2'] + result_dict['1-2'] + result_dict['2-2'] + result_dict['?-2']
    r2_minus_1 = result_dict['-2-1'] + result_dict['-1-1'] + result_dict['0-1'] + result_dict['1-1'] + result_dict['2-1'] + result_dict['?-1']
    r2_0 = result_dict['-20'] + result_dict['-10'] + result_dict['00'] + result_dict['10'] + result_dict['20'] + result_dict['?0']
    r2_1 = result_dict['-21'] + result_dict['-11'] + result_dict['01'] + result_dict['11'] + result_dict['21'] + result_dict['?1']
    r2_2 = result_dict['-22'] + result_dict['-12'] + result_dict['02'] + result_dict['12'] + result_dict['22'] + result_dict['?2']
    r2_question = result_dict['-2?'] + result_dict['-1?'] + result_dict['0?'] + result_dict['1?'] + result_dict['2?'] + result_dict['??']

    total_agreements = result_dict['-2-2'] + result_dict['-1-1'] + result_dict['00'] + result_dict['11'] + result_dict['22'] + result_dict['??']

    print('TOTAL AGREEMENTS: ' + str(total_agreements))

    minus2_product = (r1_minus_2 * r2_minus_2)
    minus1_product = (r1_minus_1 * r2_minus_1)
    zero_product = (r1_0 * r2_0)
    one_product = (r1_1 * r2_1)
    two_product = (r1_2 * r2_2)
    question_product =(r1_question * r2_question)

    sum_of_products = minus1_product + minus2_product + zero_product + one_product + two_product + question_product

    real_expt_by_chance = sum_of_products * (1 / (78 * 78 * 78 * 78 * 78 * 78))

    kappa = ((total_agreements / total_amount_ratings) - real_expt_by_chance) / (1 - real_expt_by_chance)

    return kappa


def cf_kappa_with_original(eval_r1: dict, eval_r2: dict, type: str) -> int:
    """Calculates the Cohens Kappa between the original CF values and the evaluated CF values of this work.

    All CF values (integer of each CF feature) of this work are calculated as one value (mean) which is being computed
    as a value between -1 and 1 as in the original paper. Therefore the Cohens Kappa can be calculated.
    Depending on the input parameter 'type', different values of this work's evaluation will be compared to the original
    values. As the Connotation Frames for each LU were evaluated without context and in two different sentences (-> two
    different contexts), different values were retrieved and safed and should be compared to the original values.

    :param type: String. The type of CF values that shall be compared to original values. E.G. 'context_free'.
    :param eval_r2: Dictionary. Evaluation of the Connotation Frames of annotator 2.
    :param eval_r1: Dictionary. Evaluation of the Connotation Frames of annotator 1.
    :return:
    """

    if type == 'context_free':
        start = 2
        end = 3
        amount = 1

    elif type == 'context':
        start = 3
        end = 5
        amount = 2

    elif type == 'all':
        start = 2
        end = 5
        amount = 3

    eval_dict_r1 = eval_r1[1]
    eval_dict_r2 = eval_r2[1]

    connotation_ratings_r1 = []
    connotation_ratings_r2 = []

    connotation_ratings_r1_mean = []
    connotation_ratings_r2_mean = []

    for key, value in eval_dict_r1.items():
        for rating in value[3][0:5]:
            sum = 0
            for e in rating[start:end]:
                connotation_ratings_r1.append(e)
                sum += float(e) if e != '?' else 0
            mean = sum/amount
            connotation_ratings_r1_mean.append(mean)

    for key, value in eval_dict_r2.items():
        for rating in value[3][0:5]:
            sum = 0
            for e in rating[start:end]:
                connotation_ratings_r2.append(e)
                sum += float(e) if e != '?' else 0
            mean = sum/amount
            connotation_ratings_r2_mean.append(mean)

    connotation_ratings_original = []

    # To get also the original values:
    for key, value in eval_dict_r1.items():
        for rating in value[3][0:5]:
            original_rating = float(rating[1])
            if -1 <= original_rating <= -0.35:
                modified_rating = -1
            elif -0.35 < original_rating <= 0.35:
                modified_rating = 0
            elif 0.35 < original_rating <= 1:
                modified_rating = 1

            connotation_ratings_original.append(modified_rating)

    connotation_ratings_thesis_mean = []

    for value1, value2 in zip(connotation_ratings_r1_mean, connotation_ratings_r2_mean):
        mean_value = (float(value1) + float(value2)) / 2
        if -2 <= mean_value <= -0.65:
            modified_rating = -1
        elif -0.65 < mean_value <= 0.65:
            modified_rating = 0
        elif 0.65 < mean_value <= 2:
            modified_rating = 1
        connotation_ratings_thesis_mean.append(modified_rating)

    result_dict = {'-1-1': 0, '-10': 0, '-11': 0, '0-1': 0, '00': 0, '01': 0, '1-1': 0, '10': 0, '11': 0}

    total_amount_ratings = len(connotation_ratings_thesis_mean)
    print('Anzahl der Ratings: ' + str(total_amount_ratings))

    for r1, r2 in zip(connotation_ratings_thesis_mean, connotation_ratings_original):
        result_dict['{}{}'.format(r1, r2)] += 1

    # row totals:
    r1_negative = result_dict['-1-1'] + result_dict['-10'] + result_dict['-11']
    r1_neutral = result_dict['0-1'] + result_dict['00'] + result_dict['01']
    r1_positive = result_dict['1-1'] + result_dict['10'] + result_dict['11']

    # column totals:
    r2_negative = result_dict['-1-1'] + result_dict['0-1'] + result_dict['1-1']
    r2_neutral = result_dict['-10'] + result_dict['00'] + result_dict['10']
    r2_positive = result_dict['-11'] + result_dict['01'] + result_dict['11']

    total_agreements = result_dict['-1-1'] + result_dict['00'] + result_dict['11']

    print('TOTAL AGREEMENTS: ' + str(total_agreements))

    negative_product = (r1_negative * r2_negative)
    neutral_product = (r1_neutral * r2_neutral)
    positive_product = (r1_positive * r2_positive)

    sum_of_products = negative_product + neutral_product + positive_product

    real_expt_by_chance = sum_of_products * (1 / (26*26*26))  # 26 is the amount of annotations. It is 26^3 because
    # there were 3 possible answers (modified: -1, 0, 1)

    kappa = ((total_agreements / total_amount_ratings) - real_expt_by_chance) / (1 - real_expt_by_chance)

    return kappa


if __name__ == '__main__':
    cf_verb_frame_count_dict = load_obj('cf_verb_frame_count_dict')
    frame_amount_per_lexical_unit = frames_per_verb(cf_verb_frame_count_dict)
    plot_verb_frame_amount(frame_amount_per_lexical_unit)

    with open(os.path.join('eval', 'sina_map_short_eval.pkl'), 'rb') as f:
        sina_short_eval = pickle.load(f)

    with open(os.path.join('eval', 'sina_map_long_eval.pkl'), 'rb') as f:
        sina_long_eval = pickle.load(f)

    with open(os.path.join('eval', 'sina_map_naive_eval.pkl'), 'rb') as f:
        sina_naive_eval = pickle.load(f)


    with open(os.path.join('eval', 'lschmidt_map_short_eval.pkl'), 'rb') as f:
        lschmidt_short_eval = pickle.load(f)

    with open(os.path.join('eval', 'lschmidt_map_long_eval.pkl'), 'rb') as f:
        lschmidt_long_eval = pickle.load(f)

    with open(os.path.join('eval', 'lschmidt_map_naive_eval.pkl'), 'rb') as f:
        lschmidt_naive_eval = pickle.load(f)

    # # __________________________________________________________________________________
    # Kappa:

    kappa_short_agent = cohens_kappa(sina_short_eval, lschmidt_short_eval, 'agent')
    kappa_short_theme = cohens_kappa(sina_short_eval, lschmidt_short_eval, 'theme')

    kappa_long_agent = cohens_kappa(sina_long_eval, lschmidt_long_eval, 'agent')
    kappa_long_theme = cohens_kappa(sina_long_eval, lschmidt_long_eval, 'theme')

    kappa_naive_agent = cohens_kappa(sina_naive_eval, lschmidt_naive_eval, 'agent')
    kappa_naive_theme = cohens_kappa(sina_naive_eval, lschmidt_naive_eval, 'theme')

    print('\nKAPPA Short Approach for Agent = ' + str(kappa_short_agent))
    print('KAPPA Short Approach for Theme = ' + str(kappa_short_theme))

    print('\nKAPPA Long Approach for Agent = ' + str(kappa_long_agent))
    print('KAPPA Long Approach for Theme = ' + str(kappa_long_theme))

    print('\nKAPPA Naive Approach for Agent = ' + str(kappa_naive_agent))
    print('KAPPA Naive Approach for Theme = ' + str(kappa_naive_theme))

    #__________________________________________________________________________________________
    # Connotation Frames:

    with open(os.path.join('eval', 'lschmidt_cf_eval.pkl'), 'rb') as f:
        lschmidt_cf_eval = pickle.load(f)

    with open(os.path.join('eval', 'sina_cf_eval.pkl'), 'rb') as f:
        sina_cf_eval = pickle.load(f)

    evaluated_cf_eval = read_cf_eval(lschmidt_cf_eval, sina_cf_eval)

    print(evaluated_cf_eval)

    cf_kappa = cf_kappa(lschmidt_cf_eval, sina_cf_eval)
    cf_kappa_original_all = cf_kappa_with_original(lschmidt_cf_eval, sina_cf_eval, "all")
    cf_kappa_original_context = cf_kappa_with_original(lschmidt_cf_eval, sina_cf_eval, "context")
    cf_kappa_original_context_free = cf_kappa_with_original(lschmidt_cf_eval, sina_cf_eval, "context_free")

    print("Kappa Autoren + Thesis Gesamt: " + str(cf_kappa_original_all))
    print("Kappa Autoren + Thesis Kontext: " + str(cf_kappa_original_context))
    print("Kappa Autoren + Thesis Kontextfrei: " + str(cf_kappa_original_context_free))


