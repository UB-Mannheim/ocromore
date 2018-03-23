"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from utils.database_handler import DatabaseHandler
from utils.df_objectifier import DFObjectifier

CODED_CONFIGURATION_PATH = "./configuration/to_db_reader/config_read_akftest.conf"

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, coded_configuration_paths=[CODED_CONFIGURATION_PATH])
config = config_handler.get_config()

# Read hocr and create sql-db

dbdir = str(Path(config.DBDIR).absolute())


TABLENAME_POS   = 1 #necessary
OCR_PROFILE_POS = 4
OCR_POS         = 2
DBPATH_POS      = 3 #necessary

dh = DatabaseHandler(dbdir=dbdir)
dh.tablefilter = "0650_1957_hoppa-405844417-0050_0805"
dh.dbfilter = "1957"
dh.set_dirpos(tablename_pos=config.TABLENAME_POS,ocr_profile_pos=config.OCR_PROFILE_POS,\
              ocr_pos=config.OCR_POS,dbname_pos=config.DBPATH_POS)

dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)

#dh.update_db()
#dh.work_with_object(dh.dburlscheme+dh.db[0],dh.tablefilter)

if config.HOCR2SQL is True:
    report_conv = dh.parse_to_db(delete_and_create_dir=config.DELETE_AND_CREATE_DBDIR)



dh.update_db()


if config.PREPROCESSING:
    report_prep = dh.preprocess_dbdata()


#dh.print_object(dh.dburlscheme+dh.db[0],dh.tablefilter)


if config.WORKWITHOBJ:
    dh.work_with_object(dh.dburlscheme+dh.db[0],dh.tablefilter)

# Plot DF (not working atm)
if config.PLOT:
    dh.plot_charinfo()
