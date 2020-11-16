# -*- coding: utf-8 -*-
from serialization import save_obj
import os


def extract_verbs_and_cfs(filename: str) -> dict:
    """Creates a dictionary of all English verbs and their respective Connotation Frames.

    Using the Connotation Frame Dataset from Rashkin et al. 2016, extract the verbs and their frames to be accessible
    for further work. The returned dictionary contains the verbs as keys and their frames as values.

    The Connotation Frames are saved within a nested dictionary with the following format:

    {'Perspective(writer->object)': int, 'Perspective(writer->subject)': int, 'Perspective(subject->object)': int,
    'Effect(object)': int, 'Effect(subject)': int, 'Value(object)' int, 'Value(subject)': int, 'State(object)': int,
    'State(subject)': int, 'Perspective(reader->object)': int, 'Perspective(reader->subject)': int,
    'Perspective(object-subject)': int}.

    :param filename: Path to connotation frames file
    :return: Dictionary containing English verbs as keys and nested dictionaries of Connotation Frames
    """

    connotation_frames = ['Perspective(writer->object)', 'Perspective(writer->subject)', 'Perspective(subject->object)',
                          'Effect(object)', 'Effect(subject)', 'Value(object)', 'Value(subject)', 'State(object)',
                          'State(subject)', 'Perspective(reader->object)', 'Perspective(reader->subject)',
                          'Perspective(object-subject)']
    verbs_and_frames = {}

    with open(filename, "r", encoding="UTF-8") as file:
        header_line = next(file)
        for line in file:
            columns = line.strip().split()
            verb = columns[0]
            connotation_frame = {}
            for connotation, value in zip(connotation_frames, columns[1:]):
                connotation_frame[connotation] = value
            verbs_and_frames[verb] = connotation_frame
    return verbs_and_frames


if __name__ == '__main__':
    extracted_cf_verbs = extract_verbs_and_cfs('/mntpnts/theses_diddley/ws20/lschmidt/data/full_frame_info.txt')
    save_obj(extracted_cf_verbs, 'extracted_cf_verbs')
