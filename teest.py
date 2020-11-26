#tbd
from nltk.corpus import framenet as fn
import preprocessing.framenet_preprocessing as fn_pre
from preprocessing.serialization import load_obj

list1 = [1,("hi")]
list2 = [1,9]

liste = tuple(list1)

test_dict = {(1,2,3): 5}

test_dict[liste] = 4

lu_object = fn_pre.get_lu_instance('seem')
random_sentence = fn_pre.get_random_example_and_fes(lu_object)[0]


print(random_sentence)
