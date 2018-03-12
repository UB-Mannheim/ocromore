"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from file_to_database_handler import FileToDatabaseHandler as ftdh
from utils.database_handler import DatabaseHandler

CODED_CONFIGURATION_PATH = "./configuration/to_db_reader/config_read_akftest.conf"

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, coded_configuration_paths=[CODED_CONFIGURATION_PATH])
config = config_handler.get_config()

# Read hocr and create sql-db
dbdir = 'sqlite:////'+str(Path(config.DBDIR).absolute())

# 0 = set to 'default'
TABLENAME_POS   = 1 #necessary
OCR_PROFILE_POS = 2
OCR_POS         = 3
DBPATH_POS      = 4 #necessary


dh = DatabaseHandler(dbdir=dbdir)
dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)
dh.fetch_gtfiles("./Testfiles/groundtruth/**/*.")
test = dh.gtfiles['1957'][list(dh.gtfiles['1957'].keys())[0]]
#dbs_and_files = ftdh.fetch_dbs_and_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES, dbdir)

if config.HOCR2SQL is True:
    report_conv = dh.parse_to_db()


if config.PREPROCESSING:
    report_prep = dh.preprocess_dbdata()


if config.WORKWITHOBJ:
    ftdh.work_with_object(dbs_and_files)

# Plot DF (not working atm)
if config.PLOT:
    ftdh.plot_charinfo()
