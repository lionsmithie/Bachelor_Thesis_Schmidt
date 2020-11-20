#tbd
from nltk.corpus import framenet as fn

lu_love_frames = fn.frames_by_lemma(r'love\.v')
lu_love_lus = fn.lus(r'love\.v')

frame_love_sense1 = lu_love_frames[0]

#print(frame_love_sense1.keys())
print(lu_love_lus)

love_sense1 = lu_love_lus[0]
love_id1 = fn.lu(880)
#print(love_id1)

#print(love_sense1)
#print(love_id17947.keys())
# -> dict_keys(['_type', 'status', 'POS', 'name', 'ID', 'lemmaID', 'cBy', 'cDate', 'definition', 'definitionMarkup',
# 'sentenceCount', 'lexemes', 'semTypes', 'frame', 'URL', 'subCorpus', 'exemplars'])
#print(love_id1.exemplars)
#print(love_id1.definition)
#print(love_id1.subCorpus)
#print(fn.annotations('love.v'))
#print(frame_love_sense1.definition)
#print(frame_love_sense1.definitionMarkup)

#print(love_id1.exemplars[0].annotationSet[1])
#print(love_id1.exemplars[0].annotationSet[1].PT)
#print(love_id1.exemplars[0].annotationSet[1].FE)

