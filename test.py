import pprint   # For proper print of sequences.
import treetaggerwrapper
#1) build a TreeTagger wrapper:
tagger = treetaggerwrapper.TreeTagger(TAGLANG='it')
#2) tag your text.
tags = tagger.tag_text("Questa è una prova abbastanza veloce per vedere se funziona.")
#3) use the tags list... (list of string output from TreeTagger).
tags2 = treetaggerwrapper.make_tags(tags)
for t in tags2:
    print(t.lemma)