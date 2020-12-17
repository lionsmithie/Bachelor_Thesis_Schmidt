# -*- coding: utf-8 -*-
from serialization import save_obj
from serialization import load_obj
import os


def extract_verbs_and_cfs(filename: str) -> dict:
    """Creates a dictionary of all English verbs and their respective Connotation Frames.

    Using the Connotation Frame Dataset from Rashkin et al. 2016, extract the verbs and their frames to be accessible
    for further work. The returned dictionary contains the verbs as keys and their frames as values.

    The Connotation Frames are saved within a nested dictionary with the following format:

    {'Perspective(writer->theme)': int, 'Perspective(writer->agent)': int, 'Perspective(agent->theme)': int,
    'Effect(theme)': int, 'Effect(agent)': int, 'Value(theme)' int, 'Value(agent)': int, 'State(theme)': int,
    'State(agent)': int, 'Perspective(reader->theme)': int, 'Perspective(reader->agent)': int,
    'Perspective(theme->agent)': int}.

    :param filename: Path to connotation frames file
    :return: Dictionary containing English verbs as keys and nested dictionaries of Connotation Frames
    """

    connotation_frames = ['Perspective(writer->theme)', 'Perspective(writer->agent)', 'Perspective(agent->theme)',
                          'Effect(theme)', 'Effect(agent)', 'Value(theme)', 'Value(agent)', 'State(theme)',
                          'State(agent)', 'Perspective(reader->theme)', 'Perspective(reader->agent)',
                          'Perspective(theme->agent)']
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
    save_obj(extracted_cf_verbs, 'extracted_cf_verbs', up=True)