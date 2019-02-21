"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
   (former plt_charinfo.py)
"""

from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from akf_corelib.database_handler import DatabaseHandler

CODED_CONFIGURATION_PATH = "./configuration/to_db_reader/config_read_bus3b.conf"

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, coded_configuration_paths=[CODED_CONFIGURATION_PATH])
config = config_handler.get_config()

# Read hocr and create sql-db
dbdir = str(Path(config.DBDIR_READER).absolute())
dh = DatabaseHandler(dbdir=dbdir)
dh.set_dirpos(tablename_pos=config.TABLENAME_POS, ocr_profile_pos=config.OCR_PROFILE_POS,\
              ocr_pos=config.OCR_POS, dbname_pos=config.DBPATH_POS)

dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)
test = dh.get_files()  # just a simple check if files were read


if config.HOCR2SQL:
    # Write the hocr files from output of the first step to sql-database
    report_conv = dh.parse_to_db(delete_and_create_dir=config.DELETE_AND_CREATE_DBDIR)

dh.update_db()

if config.PREPROCESSING:
    # do pre-alignment of data (lines in the files engine-wise, word-wise, ... )
    report_prep = dh.preprocess_dbdata(force=True, PRINT_SUSPICIOUSLINES=config.PRINT_SUSPICIOUSLINES,
                                       CLEAN_ABBYY=config.CLEAN_ABBYY, VERBOSE=config.VERBOSE,
                                       VERBOSEPATH=config.VERBOSEPATH)

if config.WORKWITHOBJ:
    # test the data-integrity (did alignment steps work ...)
    dh._work_with_object(dh.dburlscheme+dh.db[0], dh.tablefilter)

# Plot DF (not working atm)
if config.PLOT:
    # deprecated function to plot results
    dh._plot_charinfo()
