from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from tableparser import TableParser
from akf_corelib.database_handler import DatabaseHandler
import os



# fetch configurations
CODED_CONFIGURATION_PATH_VOTER = './configuration/voter/config_akftest_js.conf'  # configuration which is not given with cli args
CODED_CONFIGURATION_PATH_DB_READER = './configuration/to_db_reader/config_read_akftest.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_paths=[CODED_CONFIGURATION_PATH_VOTER, CODED_CONFIGURATION_PATH_DB_READER])


config = config_handler.get_config()
dbdir = 'sqlite:///'+str(Path(config.DB_DIR_VOTER).absolute())


dh = DatabaseHandler(dbdir=str(Path(config.DB_DIR_VOTER).absolute()))
#dh.set_dirpos(tablename_pos=config.TABLENAME_POS,ocr_profile_pos=config.OCR_PROFILE_POS,ocr_pos=config.OCR_POS,dbname_pos=config.DBPATH_POS)
#dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)

dh.fetch_gtfiles(config.GROUNDTRUTH_FILEGLOB, gtflag=True)
filestructs_gt = dh.get_groundtruths()
tableparser = TableParser(config)


#dbs_and_files = ftdh.fetch_dbs_and_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES, dbdir)
#groundtruths = ftdh.fetch_groundtruths("./Testfiles/groundtruth/long/**/*.", ["gt.txt"])

table_ctr = 0


# possibility to delete dir on restart

tableparser.delete_output_dir()
tableparser.create_output_dir()

count = 1
for db in dh.db:
    print("Parsing database:", db)
    files = dh.get_tablenames_from_db(db)

    temp = os.path.splitext(db)[0]
    db_keyname = os.path.basename(temp)  # this returns just the filename (wildlife)


    files_gt = filestructs_gt[db_keyname]
    for file in files:
        count += 1
        table = file
        dbpath = 'sqlite:////' + db
        print("Parsing table: ", table, "in database: ", dbpath)

        table_ctr += 1
        path_created_file, additional_created_files = tableparser.parse_a_table(dbpath, table)
        foundgt = None
        for gt_key in files_gt:
            gt_file = files_gt[gt_key]
            if table in gt_key:
                foundgt = gt_file.path
                print("found:", foundgt)
        if foundgt is not None:
            tableparser.validate_table_against_gt(path_created_file, foundgt)
            for additional_file in additional_created_files:
                # this validates the original outputs
                tableparser.validate_table_against_gt(additional_file,foundgt)




if config.SUMMARIZE_ISRI_REPORTS is True:
    tableparser.create_isri_reports(dh.db, filestructs_gt, "abbyy")
    tableparser.create_isri_reports(dh.db, filestructs_gt, "ocro")
    tableparser.create_isri_reports(dh.db, filestructs_gt, "tess")
    if config.DO_N_DIST_KEYING:
        tableparser.create_isri_reports(dh.db, filestructs_gt, "ndist_keying")
    if config.DO_MSA_BEST:
        tableparser.create_isri_reports(dh.db, filestructs_gt, "msa_best")
