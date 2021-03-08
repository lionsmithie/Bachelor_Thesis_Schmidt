# Bachelor Thesis - "Konnotierte" Connotation Frames im Satzkontext
* Maintainer
* Topic
* Runthrough

-------------
-------------
## Maintainer
* [Leon Schmidt](lschmidt@cl.uni-heidelberg.de), Computational Linguistics B.A.

-------------
## General requirements
* re
* os
* nltk
* random
* framenet

-------------

## Topic
This repository corresponds to my Bachelor Thesis in which I perform a merge between [FrameNet](https://framenet.icsi.berkeley.edu/fndrupal/) information and Connotation Frames [(Rashkin et. al, 2016)](https://homes.cs.washington.edu/~hrashkin/connframe.html). The semantic roles of each ressource are being connected for every verb that is represented in FrameNet exactly once. The evaluation consists also of an interactive program which can be found in this repository.

## Runthrough
To get everything going follow the instructions here. First some requirements need to be met: 
 
### Data Preprocessing
* The Connotation Frame Lexicon can be found in `/data/full_frame_info.txt`
* In order to run most of the code you need to download FrameNet from the nltk library. You can easily install FrameNet by importing nltk and running the command:
`>>>nltk.download('framenet_v17')`

The preprocessing of FrameNet and Connotation Frame data for the purpose of this work is implemented in the folder `/preprocessing/`.
It consists of the following files: 
* `/connotation_frames_preprocessing.py`: Preprocessing all connotation frames to a format designed for further processes
* `/framenet_preprocessing.py`: Preprocessing FrameNet data and a few methods for an easier access to FrameNet data
* `/serialization.py`: Methods for loading and saving pickle objects

The processed Connotation Frame Verbs can be found as a dictionary in `/preprocessing/obj/extracted_cf_verbs.pkl`.

### Main Algorithm
The main algorithm can be found in `/framenet_connotationframes_mapping.py`. 
The implemented methods are:
* `find_common_verbs(filename)`: Finding all verbs that are in the Connotation Frame lexicon and FrameNet; returns a list of all verbs
* `cf_verbs_frame_count(filename)`: Computes for each Connotation Frame verb the amount of Lexical Units in FrameNet; returns a dictionary with verbs as key and the amount of LUs as value
* `find_unambiguous_common_verbs(verb_frame_amount_dict)`: Retrieves verbs that occur only once in FrameNet; returns a list
* `map_cfs_lus(verbs, cfs)`: Merges the FrameNet information (lemma & Lexical Unit ID) with the respective Connotation Frame for each verb
* `detect_subject(nlp, sentence, lu)`: Detects the syntactic subject of a given head (verb) and returns it's string, position, head and a boolean whether it's a passive case or not
* `detect_subject_short_phrase(nlp, sentence, lu)`: Same as above, but the returned subject can be a phrase. All syntactic children of the subject are being added to the phrase
* `detect_subject_long_phrase(nlp, sentence, lu`): Same as above, but the returned subject can be a phrase. All syntactic descendants (not only children) of the subject are being added to the phrase
* `detect_object(nlp, sentence, lu)`: Detects the syntactic object of a given head (verb) and returns it's string, position, head and a boolean whether it's a passive case or not
* `detect_object_short_phrase(nlp, sentence, lu)`: Same as above, but the returned object can be a phrase. All syntactic children of the object are being added to the phrase
* `detect_object_long_phrase(nlp, sentence, lu`): Same as above, but the returned object can be a phrase. All syntactic descendants (not only children) of the object are being added to the phrase

# Role Mapping:
* `map_cf_roles_and_fes_long_phrase_all_sents(nlp, mapping_verb_lu_cfs)`: Mapping of semantic roles with the so called long phrase approach. For each verb, all sentences in FrameNet are being parsed. If the logical subject/object matches the position of a frame element, this frame element will be added to the set of subject- or object corresponding roles (see Thesis for more detail)
* `map_cf_roles_and_fes_short_phrase_all_sents(nlp, mapping_verb_lu_cfs)`: Mapping of semantic roles with the so called short phrase approach
* `map_cf_roles_and_fes_naive_all_sents(nlp, mapping_verb_lu_cfs)`: Mapping of semantic roles with the so called naive approach

All of the methods return a dictionary which contains the Lexical Unit IDs as keys and further information, e.g. thr mapped roles, as values.

### Evaluation

-------------
