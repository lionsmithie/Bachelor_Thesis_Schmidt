# -*- coding: utf-8 -*-
import pickle
import os


def save_obj(obj, name: str) -> None:
    """Saves an object as name.pkl file in the obj/ directory.
    This function requires obj/ to exist prior to its use.
    :param obj: Object to be serialized
    :param name: Filename for the object
    :return: None
    """
    with open(os.path.join('obj', name + '.pkl'), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name: str) -> object:
    """Loads an object from the obj/ directory.
    Loads and returns the object named name.pkl from the obj/ directory.
    :param name: Name of the object
    :return: Loaded object
    """
    with open(os.path.join('obj', name + '.pkl'), 'rb') as f:
        return pickle.load(f)
