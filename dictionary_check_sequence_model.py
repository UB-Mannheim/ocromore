from dictionary_check_create_sequences import load_doc, config,main_create_aufsichtsrat_sequences

from numpy import array
from pickle import dump
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Embedding
import re

doc = load_doc(config.FILEPATH_SEQUENCES)
lines = doc.split('\n')
text_tokens = re.split(r"([^\w])", doc)
aufsichtsrat_sequences, sequences_as_array, af_seq_length =\
    main_create_aufsichtsrat_sequences(config.FILEGLOB_LEARNDICTS,config.FILEPATH_SEQUENCES)


# integer encode sequences of words
# tokenizer = Tokenizer() #example usage
tokenizer = Tokenizer(filters="")
tokenizer.fit_on_texts(text_tokens)
#tokenizer.fit_on_texts(lines)
sequences = tokenizer.texts_to_sequences(sequences_as_array)

# vocabulary size
vocab_size = len(tokenizer.word_index) + 1

# separate into input and output
sequences = array(sequences)
X, y = sequences[:, :-1], sequences[:, -1]
y = to_categorical(y, num_classes=vocab_size)
seq_length = X.shape[1]

 # define model
model = Sequential()
# second param dimensions to represent each word in vector space
model.add(Embedding(vocab_size, seq_length, input_length=seq_length))

# mind 2*seq_length was 100 before
model.add(LSTM(2*seq_length, return_sequences=True))
model.add(LSTM(2*seq_length))
model.add(Dense(2*seq_length, activation='relu'))
model.add(Dense(vocab_size, activation='softmax'))
print(model.summary())
# compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# fit model
model.fit(X, y, batch_size=128, epochs=100)

# save the model to file
model.save('model_aufsichtsrat_cds.h5')
# save the tokenizer
dump(tokenizer, open('tokenizer_aufsichtsrat_cds.pkl', 'wb'))







print("done")
