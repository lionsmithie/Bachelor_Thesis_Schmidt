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
* nltk.download('framenet_v17')

The preprocessing of FrameNet and Connotation Frame data for the purpose of this work is implemented in the folder `/preprocessing/`
It consists of the following files: 
* `/connotation_frames_preprocessing.py`: Preprocessing all connotation frames to a format designed for further processes
* `/framenet_preprocessing.py`: Preprocessing FrameNet data and a few methods for an easier access to FrameNet data
* `/serialization.py`: Methods for loading and saving pickle objects

The processed Connotation Frame Verbs can be found as a dictionary in `/preprocessing/obj/extracted_cf_verbs.pkl`.

### Main Algorithms
The main algorithms can be found in `/framenet_connotationframes_mapping.py`. 
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
* map_cf_roles_and_fes_long_phrase_approach(nlp, mapping_verb_lu_cfs): Mapping of semantic roles with the so calles long phrase approach. For each verb, all sentences in FrameNet are being parsed. If the logical subject/object matches the position of a frame element, this frame element will be added to the set of subject- or object corresponding roles (see Thesis for more detail)
* 
### Sentiment Classification & Evaluation
* When you have done the above, go to ``src/data/Classifier_Evaluation`` and download the data how it's described in the readme there.
* Now run ``src/Classifier_Evaluation.py``.
* This python file creates numeric features out of the recently created features. This results in an numpy array that contains one row for each tweet and each row consists of multiple numeric features (number of anger words, number of sad words...)
* Then the given sentiment scores are loaded into the program. For now we use them as "gold truth" until we have annotated our own data. 
* Then we test multiple classifiers applying k-fold-cross-validation on the given feature matrix and the given "gold truth".
* The classification task is assigning each tweet either a positive, a negative or a neutral sentiment. 
* Afterwards we choose the best of the recently tested classifiers to for further work. We apply it to all of the tweets in order to get an idea how the final distribution looks like. 
* In addition several visualizations are computed and saved locally in the `src/data/Classifier_Evaluation/` folder as svg.
* May take 15-35 minutes.

### Relation to real world Covid development
* In the file ``src/data/timeline_corona_events_csv.csv`` the main covid-related events in the US, India and the UK are listed by date of the event.
Events of special importance are marked with 'x' and it will be checked if they show effects in twitter data, be it the number of tweets or a specific sentiment.  
  We have collected and put together the data by ourselfs, using these sources: https://www.ajmc.com/view/a-timeline-of-covid19-developments-in-2020,,https://en.wikipedia.org/wiki/Timeline_of_the_COVID-19_pandemic_in_India_(January%E2%80%93May_2020),,https://en.wikipedia.org/wiki/Timeline_of_the_COVID-19_pandemic_in_England_(2020),
https://timesofindia.indiatimes.com/india/coronavirus-india-timeline/articleshow/80030867.cms
-------------
