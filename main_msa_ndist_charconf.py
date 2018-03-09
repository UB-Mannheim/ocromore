from utils.df_objectifier import DFObjectifier
from pathlib import Path
from n_dist_keying.database_handler import DatabaseHandler
from utils.pycharm_handler import PycharmHandler
from ocr_validation.isri_handler import IsriHandler
import importlib
from configuration.configuration_handler import ConfigurationHandler
from file_to_database_handler import FileToDatabaseHandler as ftdh
from tableparser import TableParser

# fetch configurations
CODED_CONFIGURATION_PATH_VOTER = './configuration/voter/config_akftest_js.conf'  # configuration which is not given with cli args
CODED_CONFIGURATION_PATH_DB_READER = './configuration/to_db_reader/config_read_akftest.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_paths=[CODED_CONFIGURATION_PATH_VOTER, CODED_CONFIGURATION_PATH_DB_READER])


config = config_handler.get_config()
dbdir = 'sqlite:///'+str(Path(config.DBDIR).absolute())

dbs_and_files = ftdh.fetch_dbs_and_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES, dbdir)

table_ctr = 0

tableparser = TableParser(config, delete_and_create_output_dir=True)
for db in dbs_and_files:
    print("Parsing database:", db)
    files = dbs_and_files[db]
    for file, mode in files:
        table = ftdh.get_table_name_from_filename(file)
        print("Parsing table: ", table, "in database: ", db)
        table_ctr += 1
        res = tableparser.parse_a_table(db, table)
        if table_ctr == 2: #j4t parse 4 tables then done
            break



print("asd")



