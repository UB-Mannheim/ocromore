from random import randint
from pickle import load
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from machine_learning_components.special_char_predictor_create_sequences import config, main_create_aufsichtsrat_sequences, generate_tokens


# load doc into memory
def load_doc(filename):
	# open the file as read only
	file = open(filename, 'r')
	# read all text
	text = file.read()
	# close the file
	file.close()
	return text

# generate a sequence from a language model
def generate_seq(model, tokenizer, seq_length, seed_text, n_words):
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



aufsichtsrat_sequences,sequences_as_array, af_seq_length= main_create_aufsichtsrat_sequences(config.FILEGLOB_LEARNDICTS, config.FILEPATH_SEQUENCES)
aufsichtsrat_sequences_eval,sequences_as_array_eval, af_seq_length_eval = main_create_aufsichtsrat_sequences(config.FILEGLOB_EVALUATIONDICTS, config.FILEPATH_EVAL_SEQUENCES, sequence_length=af_seq_length)


# load cleaned text sequences
# in_filename = config.FILEPATH_SEQUENCES
# doc = load_doc(in_filename)
# lines = doc.split('\n')
# seq_length = len(lines[0].split()) - 1


lines = aufsichtsrat_sequences
lines_eval = aufsichtsrat_sequences_eval
seq_length = af_seq_length -1




# load the model
model = load_model(config.PREDICTOR_AUFSICHTSRAT_MODEL)

# load the tokenizer
tokenizer = load(open(config.PREDICTOR_AUFSICHTSRAT_TOKENIZER, 'rb'))

# select a seed text
line_index = randint(0,len(lines))
seed_text = lines[line_index]
print(seed_text + '\n')

# check some line indices wich predict

# generate new text
# generated = generate_seq(model, tokenizer, seq_length, seed_text, 15)

evaluate_direct = False
if evaluate_direct:
	# evaluation with learn data
	generated_1 = generate_seq(model, tokenizer, seq_length, lines[89], 3)
	generated_2 = generate_seq(model, tokenizer, seq_length, lines[85], 3)
	generated_3 = generate_seq(model, tokenizer, seq_length, lines[55], 3)
	generated_4 = generate_seq(model, tokenizer, seq_length, lines[249], 3)


	# evaluation with evaluation data
	generated_e1 = generate_seq(model, tokenizer, seq_length, aufsichtsrat_sequences_eval[18], 3)
	generated_e2 = generate_seq(model, tokenizer, seq_length, aufsichtsrat_sequences_eval[45], 3)
	generated_e3 = generate_seq(model, tokenizer, seq_length, aufsichtsrat_sequences_eval[108], 3)
	generated_e4 = generate_seq(model, tokenizer, seq_length, aufsichtsrat_sequences_eval[166], 3)

	print("done")



def is_special_character(text):
	if len(text) > 1:
		return False

	is_alphanumberical = text.isalnum()

	if is_alphanumberical:
		return False
	else:
		return True

numchecks = 0
numfaults = 0
numrights = 0
numadds = 0
for seq_eval_index, seq_eval in enumerate(aufsichtsrat_sequences_eval):
	if seq_eval_index >= len(aufsichtsrat_sequences_eval)-4:
		break




	# obtain first token which is the proclaimed result
	res_next_tokens = sequences_as_array_eval[seq_eval_index+3][seq_length-2:seq_length+1]

	res_next = sequences_as_array_eval[seq_eval_index+1][seq_length]

	# generate result for input sequence
	res_gen  = generate_seq(model, tokenizer, seq_length, seq_eval, 3)
	res_gen_tokens = generate_tokens(res_gen)
	res_gen_next = res_gen_tokens[0]

	res_next_is_specialchar = is_special_character(res_next)
	res_gen_next_is_specialchar = is_special_character(res_gen_next)


	print("Sequence:", seq_eval)
	print("ResultT_act:", res_next_tokens,"is_special_char:", res_next_is_specialchar)
	print("ResultT_gen:", res_gen_tokens,"is_special_char:", res_gen_next_is_specialchar)


	if not res_next_is_specialchar and res_gen_next_is_specialchar:
		print("add special char")
		#reduce errors by looking atfurther generated next tokens

		numfaults += 1
		numadds += 1
	if res_next_is_specialchar and res_gen_next_is_specialchar:
		if res_next != res_gen_next:
			# similarity or also look at next generated tokens
			print("swapping special char")
			numfaults += 1
		else:
			numrights += 1

	numchecks +=1


print("Number of runs:", numchecks)
print("Number of faults:", numfaults)
print("Number of rights:", numrights)
print("Number of adds:", numadds)
print("Number of faults without adds:", numfaults-numadds)

