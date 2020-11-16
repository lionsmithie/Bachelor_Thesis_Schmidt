#tbd
from nltk.corpus import framenet as fn

lu_cook = fn.lus(r'.*cook\.v')
lu_love = fn.frames_by_lemma(r'love\.v')

#print(lu_cook)  #returns a list of all lexical units which evoke a frame. (Can be more than one)
#print(lu_cook[2])  #refers to one lexical unit and its respective frame.
#print(lu_love)

frame_love_sense1 = lu_love[0]

print(frame_love_sense1.keys())
print(frame_love_sense1.definition)
print(frame_love_sense1.definitionMarkup)

cook_sense3 = lu_cook[2]

#print(cook_sense3.keys())  # to see what attributes / keys are saved for this object.
#print(cook_sense3.frame)   # getting the info about the frame.
#print(cook_sense3.frame.name)   # refers to the frame object, same procedure as for a lexical unit.


lu_threaten = fn.lus(r'.*threaten\.v')
threaten_sense1 = lu_threaten[0]
threaten_sense2 = lu_threaten[1]

#print(threaten_sense1.frame)
#print(threaten_sense2.frame)