from configuration.configuration_handler import ConfigurationHandler
from utils.conditional_print import ConditionalPrint


from random import randint
from pickle import load
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences



class SpecialCharPredictor():

    def __init__(self):

        config_handler = ConfigurationHandler(first_init=False)
        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_SPECIALCHAR_PREDICTOR, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)



    def load_prediction_model(self):
        # load model and tokenizer for aufsichtsrat prediction
        self.model_aufsichtsrat = load_model(self.config.PREDICTOR_AUFSICHTSRAT_MODEL)
        self.tokenizer_aufsichtsrat = load(open(self.config.PREDICTOR_AUFSICHTSRAT_TOKENIZER, 'rb'))
        self.generate_prediction_seq(self.model_aufsichtsrat, self.tokenizer_aufsichtsrat, 19, 'jens ƿ sturm ƿ ( arbeitnehmervertreter ) aufsichtsrat : bernhard ƿ garbe ƿ ( vors . ) , ƿ hamburg',1)
        self.generate_prediction_seq(self.model_aufsichtsrat, self.tokenizer_aufsichtsrat, 19, 'jens ƿ sturm ƿ ( arbeitnehmervertreter ) aufsichtsrat :',1)


    def generate_prediction_seq(self, model, tokenizer, seq_length, seed_text, n_words):
        result = list()
        in_text = seed_text
        # generate a fixed number of words
        for _ in range(n_words):
            # encode the text as integer
            encoded = tokenizer.texts_to_sequences([in_text])[0]
            # truncate sequences to a fixed length
            encoded = pad_sequences([encoded], maxlen=seq_length, truncating='pre')
            # predict probabilities for each word
            yhat = model.predict_classes(encoded, verbose=0)
            # map predicted word index to word
            out_word = ''
            for word, index in tokenizer.word_index.items():
                if index == yhat:
                    out_word = word
                    break
            # append to input
            in_text += ' ' + out_word
            result.append(out_word)
        return ' '.join(result)

    def predict_next_aufsichtsrat_chars(self,input_sequence_length, input_text):
        predicted_seq = self.generate_prediction_seq(self.model_aufsichtsrat,
                                  self.tokenizer_aufsichtsrat,
                                  input_sequence_length, input_text, 1)
        pchar = predicted_seq[0]
        return pchar

