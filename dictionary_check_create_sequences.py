import string
import glob
import re




class config():
	FILEPATH_LEARNDICT = "./Testfiles/republic.txt"
	FILEPATH_SEQUENCES = "./Testfiles/sequences_aufsichtsrat_cds.txt"
	FILEPATH_EVAL_SEQUENCES = "./Testfiles/sequences_aufsichtsrat_eval.txt"
	SEQUENCE_LENGTH =  50 + 1
	FILEGLOB_LEARNDICTS = "/media/sf_Transfer/groundtruth/**/*."
	FILEGLOB_EVALUATIONDICTS = "./Testfiles/evaluation/**/"
	PADDING_CHAR = "¦"  ## Alternative ſ  ƿ
	SPACE_SUBST = "ƿ"

def filter_aufsichtsrat(text, special_file = False):
	end_lines = []
	end_text = ""

	lines = text.split('\n')
	do_read = False

	for line_index, line in enumerate(lines):
		line_trimmed = line.strip()
		if "Aufsichtsrat:" == line_trimmed:
			do_read = True

		if "Gründung:" in line_trimmed or "Arbeitnehmervertreter:" in line_trimmed:
			do_read = False

		if do_read:
			end_lines.append(line)
			end_text += line + "\n"

		if line_index >= 300 and special_file == False:
			break

	return end_lines, end_text

def load_fileglob(fileglob_path):
	files = glob.glob(fileglob_path + "*.txt", recursive=True)
	final_lines = []
	final_texts = []

	for file in files:
		special_file = False
		if "akf_cds_aufsichtsrat_learndata" in file:
			special_file = True
		text = load_doc(file)
		lines_only_aufsichtsrat, text_only_aufsichtsrat = filter_aufsichtsrat(text, special_file=special_file)
		final_lines.append(lines_only_aufsichtsrat)
		final_texts.append(text_only_aufsichtsrat)
		print("Adding:", file)

	return final_lines, final_texts


# load doc into memory
def load_doc(filename):
	# open the file as read only
	file = open(filename, 'r')
	# read all text
	text = file.read()
	# close the file
	file.close()
	return text

def generate_tokens(text):
	# tokens can be all special characters, words and whitespaces
	text_tokens = re.split(r"([^\w])", text)

	# testwise remove \n
	filtered_tokens = []
	for token in text_tokens:
		if token != "\n":
			if token == " ":
				filtered_tokens.append(config.SPACE_SUBST)
			elif token == "":
				continue
			else:
				filtered_tokens.append(token)

	text_tokens = filtered_tokens
	# make lower case
	text_tokens = [word.lower() for word in text_tokens]
	return text_tokens

def prepare_aufsichtsrat_tokens(aufsichtsrat_texts, aufsichtsrat_lines, sequence_length=-1):

	all_tokens = []
	number_of_tokens = 0
	number_of_lines = 0

	# get the number of lines
	for doc in aufsichtsrat_lines:
		for line in doc:
			number_of_lines += 1

	# get tokens for each aufsichtsrat file
	for text in aufsichtsrat_texts:

		text_tokens = generate_tokens(text)
		number_of_tokens += len(text_tokens)
		all_tokens.append(text_tokens)


	average_number_tokens_each_line = number_of_tokens / number_of_lines

	if sequence_length==-1:
		# determine sequence length dynamically if there is no predefinition
		sequence_length = int(round(2 * average_number_tokens_each_line))

	# do padding
	padding_sequence = []
	for i in range(0, sequence_length-1):
		padding_sequence.append(config.PADDING_CHAR)

	all_tokens_padded = []
	for tokens in all_tokens:
		new_tokens = padding_sequence[:]
		new_tokens.extend(tokens)
		all_tokens_padded.append(new_tokens)

	print("average number of tokens per line:", average_number_tokens_each_line)
	print("Sequence length:", sequence_length)
	return all_tokens_padded, sequence_length


def create_aufsichtsrat_sequences(aufsichtsrat_tokens, af_seq_length):
	sequences = []
	sequences_as_array = []

	for file_tokens in aufsichtsrat_tokens:
		for i in range(af_seq_length, len(file_tokens)):
			# select sequence of tokens
			seq = file_tokens[i - af_seq_length:i]

			# convert into a line
			line = ' '.join(seq)
			sequences_as_array.append(seq)
			# stores
			sequences.append(line)

	return sequences, sequences_as_array

# turn a doc into clean tokens
def clean_doc(doc):
	# replace '--' with a space ' '
	doc = doc.replace('--', ' ')
	# split into tokens by white space
	tokens = doc.split()
	# remove punctuation from each token
	table = str.maketrans('', '', string.punctuation)
	tokens = [w.translate(table) for w in tokens]
	# remove remaining tokens that are not alphabetic
	tokens = [word for word in tokens if word.isalpha()]
	# make lower case
	tokens = [word.lower() for word in tokens]
	return tokens


# save tokens to file, one dialog per line
def save_doc(lines, filename):
	data = '\n'.join(lines)
	file = open(filename, 'w')
	file.write(data)
	file.close()

def main_create_aufsichtsrat_sequences(fileglob_path, save_path, sequence_length=-1):
	aufsichtsrat_lines, aufsichtsrat_texts = load_fileglob(fileglob_path)
	aufsichtsrat_tokens,af_seq_length = prepare_aufsichtsrat_tokens(aufsichtsrat_texts, aufsichtsrat_lines,
																	sequence_length=sequence_length)
	aufsichtsrat_sequences,sequences_as_array = create_aufsichtsrat_sequences(aufsichtsrat_tokens, af_seq_length)
	save_doc(aufsichtsrat_sequences, save_path)
	return aufsichtsrat_sequences,sequences_as_array, af_seq_length


def main_creates_example_sequences():
	# this is the example code
	text = load_doc(config.FILEPATH_LEARNDICT)
	print("text is ", text[:30],"...")

	tokens = clean_doc(text)
	print('Total Tokens: %d' % len(tokens))
	print('Unique Tokens: %d' % len(set(tokens)))

	# organize into sequences of tokens
	sequences = list()
	for i in range(config.SEQUENCE_LENGTH, len(tokens)):
		# select sequence of tokens
		seq = tokens[i-config.SEQUENCE_LENGTH:i]
		# convert into a line
		line = ' '.join(seq)
		# stores
		sequences.append(line)

	print('Total Sequences: %d' % len(sequences))
	save_doc(sequences, config.FILEPATH_SEQUENCES)


	print("done")

main_create_aufsichtsrat_sequences(config.FILEGLOB_LEARNDICTS,config.FILEPATH_SEQUENCES)