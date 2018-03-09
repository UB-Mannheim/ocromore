"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from file_to_database_handler import FileToDatabaseHandler as ftdh


CODED_CONFIGURATION_PATH = "./configuration/to_db_reader/config_read_akftest.conf"

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, coded_configuration_path=CODED_CONFIGURATION_PATH)
config = config_handler.get_config()

# Read hocr and create sql-db
dbdir = 'sqlite:///'+str(Path(config.DBDIR).absolute())

dbs_and_files = ftdh.fetch_dbs_and_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES, dbdir)

if config.HOCR2SQL is True:
    report_conv = ftdh.convert_files_to_dbs(dbs_and_files,delete_and_create_dir=True, dbdir=config.DBDIR)

if config.PREPROCESSING:
    report_prep = ftdh.do_preprocessing(dbs_and_files)


if config.WORKWITHOBJ:
    ftdh.work_with_object(dbs_and_files)

# Plot DF (not working atm)
if config.PLOT:
    ftdh.plot_charinfo()
