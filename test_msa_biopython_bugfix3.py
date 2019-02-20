from multi_sequence_alignment.msa_handler import MsaHandler
from configuration.configuration_handler import ConfigurationHandler



CODED_CONFIGURATION_PATH_VOTER = './configuration/voter/config_akftest_js.conf'  # configuration which is not given with cli args
CODED_CONFIGURATION_PATH_DB_READER = './configuration/to_db_reader/config_read_akftest.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_paths=[CODED_CONFIGURATION_PATH_VOTER, CODED_CONFIGURATION_PATH_DB_READER])


config = config_handler.get_config()


msa_handler = MsaHandler()


word_1 = "s?=HS=S“=" #doesn't work
#word_1 = "etwas Produktions ist der anders"
word_1 = "s?=HS=S=" # doesn't work
word_2 = "das Produktionsprogramm der Gesell-"
word_3 = "das Produktionsprogramm der Gesell-"
word1_al, word2_al, word3_al = msa_handler.align_three_texts(word_1, word_2, word_3)

print("asd")