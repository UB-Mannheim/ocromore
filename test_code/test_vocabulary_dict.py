import keras.preprocessing
import json
import nltk

DICTIONARY_FILE = "/media/sf_Transfer/dictionary_created.txt"
REMOVE_BORDER_SPECIAL_CHARS = True

# load doc into memory
def load_doc(filename):
	# open the file as read only
	file = open(filename, 'r')
	# read all text
	texts = file.readlines()
	# close the file
	file.close()
	return texts




doc = load_doc(DICTIONARY_FILE)

lines_doc = []
for line in doc:
    if "--------------" in line:
        continue

    line = line.replace('\n', "")

    if REMOVE_BORDER_SPECIAL_CHARS:
        #print("lbef",line)
        if len(line)>2:
            line = line.strip(",)(;.:")
        #print("laft",line)

    lines_doc.append(line)


try:
    from pysymspell.symspell import SymSpell

    initial_capacity = len(lines_doc)
    max_edit_dist = 2
    sym_spell = SymSpell(max_edit_dist)

    sym_spell.create_dictionary_by_list(lines_doc)

    input_term = "Frankftr"
    max_edit_distance_lookup = 2
    suggenstion_verbosity = SymSpell.Verbosity.ALL
    suggestions1 = sym_spell.lookup("Frankftr", suggenstion_verbosity, max_edit_distance_lookup)
    suggestions2 = sym_spell.lookup("Hulahu", suggenstion_verbosity, max_edit_distance_lookup)
    suggestions3 = sym_spell.lookup("Ausrichtsrat", suggenstion_verbosity, max_edit_distance_lookup)
    suggestions4 = sym_spell.lookup("BASV", suggenstion_verbosity, max_edit_distance_lookup)

    USE_TOKENIZE = False
    if USE_TOKENIZE:
        freq = nltk.FreqDist(lines_doc)  # alt way to get word frequencies

        tokenizer = keras.preprocessing.text.Tokenizer(num_words=None, filters='',
                                                       lower=False, split=' ', char_level=False, oov_token=None)

        tokenizer.fit_on_texts(lines_doc)
        print("Overall length:", len(tokenizer.word_counts))

        # print lines in ordered way
        for item in tokenizer.word_index:
            # index = tokenizer.word_index[item]
            count = tokenizer.word_counts[item]
            print(item, ":", count)

        # for x in range(0, len(tokenizer.word_counts)):
        #    last = tokenizer.word_counts.popitem()
        #    print(last)
        print(json.dumps(tokenizer.word_counts, indent=4))
except Exception as e:
    print(
        "To use the vocabulary checker you must pull PySymSpell from GitHub in the directory (AWARE: MIT License)"
        "by activate and initalize the submodule (delete the comment symbol: #):\n"
        ".gitmodule at line: 1-3")


# http://norvig.com/spell-correct.html
import re
from collections import Counter

def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(lines_doc)

def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N

def correction(word):
    "Most probable spelling correction for word."
    correction_candidates = candidates(word)
    best_candidate = max(correction_candidates, key=P)
    #probability = P(best_candidate)
    return best_candidate#, probability

def candidates(word):
    "Generate possible spelling corrections for word."
    kw = known([word])
    kwe1 = known(edits1(word))
    kwe2 = known(edits2(word))


    return (kw or kwe1 or kwe2 or [word])

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))




corr_res = correction("Aufsschtsrut")
corr_res2 = correction("Bruhuas")
corr_res3 = correction("hyperbola")
corr_res4 = correction("kl0newars")
# 4 words take around 1 minute! ! ! too slow system!

print("tokenizzer")