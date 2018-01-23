"""
Testing the Textblob library for later purposes, notes:
- translation is done via webapi and therefore needs web-connection
- find foreign words (for example in dictionary comparison) with the pos tagging mechanism, maybe can act as junk filter
- in german version spellcheck and correct are not implemented yet, project is not developed further atm
- german version: https://github.com/markuskiller/textblob-de
- => Conclusion, for english texts this could be good, but for german, it's too primitive yet and would need much dev-effort to work
"""


from textblob import TextBlob
from textblob import Word
from textblob.wordnet import Synset
from textblob.wordnet import VERB, NOUN

from textblob_de import TextBlobDE
from textblob_de import Word as WordDE



def download_nltk_stuff():
    """
    Downloads the missing nltk packages
    :return:
    """
    import nltk


    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('brown')
    nltk.download('wordnet')


# download_nltk_stuff()


def test_word_lists():
    animals = TextBlob("cat dog octopus ocropus")
    pluralized_words = animals.words.pluralize()
    corrected_words = animals.correct()
    word_ocropus = Word('ocropus')
    word_ocr_spellechecked = word_ocropus.spellcheck()
    word_mice = Word('mice')
    word_mice_lemmatized = word_mice.lemmatize()
    word_highest = Word('highest')
    word_highest_lemmatized = word_highest.lemmatize()

    # test word net simmilarities
    king_synsets = Word("king").get_synsets(pos=NOUN)
    king = Synset('king.n.01')
    queen = Synset('queen.n.02')
    man = Synset('man.n.01')
    wife = Synset('wife.n.01')
    woman = Synset('woman.n.01')
    octopus = Synset('octopus.n.01')
    kq_similarity = king.path_similarity(queen)
    km_similarity = king.path_similarity(man)
    ko_similarity = king.path_similarity(octopus)
    qw_similarity = queen.path_similarity(woman)

    print("done")


def test_word_lists_de():
    animals = TextBlobDE("katze hund octopus ocropus aktienführer stammaktien syndikus anwälte ")
    pluralized_words = animals.words.pluralize()
    lemmatized_words = animals.words.lemmatize()


    blob = TextBlobDE("das ist ein deutscher Text mit asbjaskfbjjn als fremdwort salut! space")
    # this doesn't detect foreign words as such
    # link to see meaning of tags: http://blog.thedigitalgroup.com/sagarg/wp-content/uploads/sites/12/2015/06/POS-Tags.png
    tags = blob.tags
    for word in blob.words:
        print(word, "language is: ", word.detect_language()) # this takes google translator api requests


    print("done")

#test_word_lists()
test_word_lists_de()
text = '''
The titular threat of The Blob has always struck me as the ultimate movie
monster: an insatiably hungry, amoeba-like mass able to penetrate
virtually any safeguard, capable of--as a doomed doctor chillingly
describes it--"assimilating flesh on contact.
Snide comparisons to gelatin be damned, it's a concept with the most
devastating of potential consequences, not unlike the grey goo scenario
proposed by technological theorists fearful of
artificial intelligence run rampant.
'''

blob = TextBlob(text)

# link to see meaning of tags: http://blog.thedigitalgroup.com/sagarg/wp-content/uploads/sites/12/2015/06/POS-Tags.png
tags = blob.tags           # [('The', 'DT'), ('titular', 'JJ'),
                    #  ('threat', 'NN'), ('of', 'IN'), ...]

nounphrases = blob.noun_phrases   # WordList(['titular threat', 'blob',
                    #            'ultimate movie monster',
                    #            'amoeba-like mass', ...])

for sentence in blob.sentences:
    print(sentence.sentiment.polarity)
# 0.060
# -0.341

result_es = blob.translate(to="es")  # 'La amenaza titular de The Blob...'
result_de = blob.translate(to="de")
print("test")