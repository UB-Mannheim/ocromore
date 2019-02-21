"""
This is the starting file for the vote/best of functionalities
it loads the the specified database in config as input,
then combines the files with n_dist_keying or multi sequence alignment
does post correction and saves the results as an output.

This usually comes after steps in main_prepare_dataset.py
"""


from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from tableparser import TableParser
from akf_corelib.database_handler import DatabaseHandler
import os

# fetch configurations  (here it's the bus3b unlv-test configuration, these files come with the repository)
CODED_CONFIGURATION_PATH_VOTER = './configuration/voter/config_vote_bus3b.conf'             # configuration which is not given with cli args
CODED_CONFIGURATION_PATH_DB_READER = './configuration/to_db_reader/config_read_bus3b.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_paths=[CODED_CONFIGURATION_PATH_VOTER, CODED_CONFIGURATION_PATH_DB_READER])

config = config_handler.get_config()
dbdir = 'sqlite:///'+str(Path(config.DB_DIR_VOTER).absolute())
dh = DatabaseHandler(dbdir=str(Path(config.DB_DIR_VOTER).absolute()))
dh.fetch_gtfiles(config.GROUNDTRUTH_FILEGLOB, gtflag=False)

# if the validation of results with isri-analytic tools is enabled, load the groundtruths which are used for comparison to results
if config.DO_ISRI_VAL:
    filestructs_gt = dh.get_groundtruths()

# load tableparse, which is the core class for the parsing process of single files
tableparser = TableParser(config)

table_ctr = 0

# possibility to delete dir on restart (comment if you don't wish overwrite)
tableparser.delete_output_dir()
tableparser.create_output_dir()

count = 1
for db in dh.db:
    print("Parsing database:", db)
    files = dh.get_tablenames_from_db(db)

    # get the filename
    temp = os.path.splitext(db)[0]
    db_keyname = os.path.basename(temp)  # this returns just the filename

    if config.DO_ISRI_VAL:
        # get the corresponding ground-truths for the key in database
        files_gt = filestructs_gt[db_keyname]

    for file in files:
        count += 1
        table = file
        dbpath = 'sqlite:////' + db
        print("Parsing table: ", table, "in database: ", dbpath)

        table_ctr += 1

        # parse the table ( which means combine all entries in database matching the table key), return generated
        # .txt files for validation against groundtruth
        path_created_file, additional_created_files = tableparser.parse_a_table(dbpath, table)

        # if validation is active search the corresponding groundtruth and check each
        if config.DO_ISRI_VAL:
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


# if validation was done there are lot's of validations done
if config.SUMMARIZE_ISRI_REPORTS is True:
    # for each result category create a summarized report for the inputs (for comparison)
    tableparser.create_isri_reports(dh.db, filestructs_gt, "abbyy")
    tableparser.create_isri_reports(dh.db, filestructs_gt, "ocro")
    tableparser.create_isri_reports(dh.db, filestructs_gt, "tess")
    
    # also create summarized reports for the configured results
    if config.DO_N_DIST_KEYING:
        tableparser.create_isri_reports(dh.db, filestructs_gt, "ndist_keying")
    if config.DO_MSA_BEST:
        tableparser.create_isri_reports(dh.db, filestructs_gt, "msa_best")
