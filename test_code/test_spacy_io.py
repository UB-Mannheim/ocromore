"""
Ideas:
- Improve spacy speed by using the api / server functionality
- Use spacy for classifying stuff within af2 (table information)
- Use spacy for calculating word similaritys for distance keying
- Use spacy to recognize word validity and build a junk filter
"""


# Install: pip install spacy && python -m spacy download en
import spacy
from spacy import displacy

#spacy_client = Client(model="de") # default args host/port
# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('de')

# Process whole documents
text = open('Testfiles/oneprof.gt.txt').read()
text = "Sämtliche Stammaktien sind lieferbar."
doc = nlp(text)

#doc = spacy_client.single("How are you")

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop)

# Find named entities, phrases and concepts
for entity in doc.ents:
    print(entity.text, entity.label_)
displacy.serve(doc, style='dep')
# Determine semantic similarities
#doc1 = nlp(u'the fries were gross')
#doc2 = nlp(u'worst fries ever')
#doc1.similarity(doc2)

# Hook in your own deep learning models
#nlp.add_pipe(load_my_model(), before='parser')