import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from preprocessing.serialization import load_obj
import os
import spacy
from spacy import displacy
from preprocessing.serialization import save_obj


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
        means.append(lus)
    labels.sort()
    means.sort(reverse=True)

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

    plt.savefig(os.path.join('plots', 'lus_frames_amount'))
#    plt.show()
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

if __name__ == '__main__':
    cf_verb_frame_count_dict = load_obj('cf_verb_frame_count_dict')
    frame_amount_per_lexical_unit = frames_per_verb(cf_verb_frame_count_dict)
    plot_verb_frame_amount(frame_amount_per_lexical_unit)

    # show_dependency_parse("He hates days when he ca n't get straight into his workshop .")

