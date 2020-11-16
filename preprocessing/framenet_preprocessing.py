from nltk.corpus import framenet as fn


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
    frames = fn.frames_by_lemma(verb_regex)  # Returns a list with all frames evoked by the verb.
    return len(frames)

#print(frame_count("love"))
