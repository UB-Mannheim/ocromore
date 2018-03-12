from utils.hocr_converter import HocrConverter
from utils.hocr_charinfo import merge_charinfo
from utils.df_tools import get_con
from utils.df_objectifier import DFObjectifier
import glob
from itertools import chain
import inspect

import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#import pandas as pd
import os
import shutil
from pathlib import Path


class FileToDatabaseHandler():

    @staticmethod
    def fetch_groundtruths(fileglob, filetypes):
        groundtruths= []
        files = chain.from_iterable(
            glob.iglob(fileglob + filetype, recursive=True) for filetype in filetypes)


        for file in files:
            groundtruths.append(file)


        return groundtruths
        print("asd")

    @staticmethod
    def fetch_dbs_and_files(fileglob, filetypes, dbdir):

        files = chain.from_iterable(
            glob.iglob(fileglob + filetype, recursive=True) for filetype in filetypes)

        dbs_and_files = {}

        dbnamelast = ""
        for file in files:
            fpath = Path(file)
            ocr_profile = fpath.parts[-2]
            # dbname = fpath.name.split("_")[1]
            fp_dir_split = os.path.dirname(fpath).split('/')
            dbname = fp_dir_split[0] + "_" + fp_dir_split[
                1]  # new db name, todo @jk please create more common interface for dbname generation here

            if dbname != dbnamelast:
                db_fullname = dbdir + '/' + dbname + '.db'
                dbs_and_files[db_fullname] = []
                dbnamelast = dbname

            dbs_and_files[db_fullname].append((file, ocr_profile))

        return dbs_and_files

    @staticmethod
    def convert_files_to_dbs(dbs_and_files, delete_and_create_dir=True, dbdir=None):

        if delete_and_create_dir is True:
            # delete and recreate database directory
            if os.path.exists(dbdir):
                shutil.rmtree(dbdir)
            os.makedirs(dbdir)

        exceptions = []
        for db_fullname in dbs_and_files:
            current_con = get_con(db_fullname)

            values = dbs_and_files[db_fullname]
            for (file, ocr_profile) in values:
                print(f"\nConvert to sql:\t{file}")
                try:
                    HocrConverter().hocr2sql(file, current_con, ocr_profile)
                except Exception as ex:
                    print("Exception parsing file ", file, ":", ex)
                    exceptions.append(ex)

        return exceptions

    @staticmethod
    def do_preprocessing(dbs_and_files):
        print("doing preprocessing")
        exceptions = []

        for db in dbs_and_files:
            files = dbs_and_files[db]
            print("preprocessing database:", db)
            for (file, othervar) in files:

                table_name = FileToDatabaseHandler.get_table_name_from_filename(file)

                try:
                    dataframe_wrapper = DFObjectifier(db, table_name)

                    # Linematcher with queries
                    if dataframe_wrapper.match_line(force=True):
                        # Unspacing
                        dataframe_wrapper.unspace()

                        # Match words or segments of words into "word_match"
                        dataframe_wrapper.match_words()

                        # Write the calulated values into the db
                        dataframe_wrapper.write2sql()
                except Exception as ex:
                    tr = inspect.trace()
                    print("Exception parsing table ", table_name, ":", ex, "trace", tr)
                    exceptions.append(ex)

        return exceptions

    @staticmethod
    def get_table_name_from_filename(file):
        filename = os.path.basename(file)
        table_name = filename.split('.')[0]
        return table_name

    @staticmethod
    def work_with_object(dbs_and_files):

        # get first db and first table/filename for the operation
        my_db = list(dbs_and_files.keys())[0]
        filename, somestuff = dbs_and_files[my_db][0]
        table_name = FileToDatabaseHandler.get_table_name_from_filename(filename)
        dfXO = DFObjectifier(my_db, table_name)

        # for file in files:
        #    fpath = Path(file)
        #    dbname = fpath.name.split("_")[1]
        #    if dbname != dbnamelast:
        #        dbnamelast = dbname

        #    #dfXO = DFObjectifier(dbdir + '/1957.db','0140_1957_hoppa-405844417-0050_0172')
        #    dfXO = DFObjectifier(dbdir + '/'+dbname+'.db', fpath.name.split(".")[0])

        # Linematcher with queries
        #    dfXO.match_line()
        #    dfXO.write2sql()

        # dfXO.write2file()

        # Example for selecting all line with calc_line == 10
        # dfSelO = dfXO.get_obj(query="calc_line == 10")
        max_line = dfXO.df["calc_line_idx"].max()
        # for idx in np.arange(0,max_line):
        # dfXO.get_obj(query="calc_line_idx == 10")
        # print(idx)
        object = dfXO.get_obj(empty=True)
        object.update_textspace(">>  >>", widx=1.0)
        object.update_textspace(">>  >>", widx=3.0)
        object.update_textspace(">>  >>", widx=2.0)
        object.restore()
        dfSelO = dfXO.get_line_obj()
        for idx, lidx in enumerate(dfSelO):
            print(idx)
            for items in dfSelO[lidx]:
                print(items.textstr)
                for word in items.word["text"]:
                    if "maßgeblich" in items.word["text"][word]:
                        stio = "STIO"
                    print(items.word["text"][word] + "\t", end="")
                print("\n")
        for lidx in dfSelO:
            for items in dfSelO[lidx]:
                # test_word(items)
                print(items.textstr)
                print(items)
                txt = items.textstr
                txt = txt[:1] + "|" + txt[1:]
                if "Riekeberg" in txt:
                    items.update_textspace("¦Dipl.¦¦¦¦¦", "¦", widx=0.0)
                    items.update_textspace("¦-Ing.", "¦", widx=1.0)
                    items.update_textspace("@@@@@", "@", widx=3.0)
                    items.restore()

                    txt = txt[:0] + "||||||" + txt[0:]
                # items.update_textspace(txt,"|")
                print(items.textstr)
                print(items.value("x_confs", 3))
                print(items.value("calc_char", 3))
                print(items.value("char", 3))
                print(items.value("x_confs", 10))
                print(items.value("calc_char", 10))
                print(items.value("char", 9))
                print(items.value("x_confs", 9, wsval=10.0))
                print(items.value("calc_char", 9))
                print(items.value("char", 10))
                print(items.data["UID"])
                print(items.value("x_confs", 2))
                print(items.value("calc_char", 4))
                print(items.value("x_confs", 4))
        return
        text2 = dfSelO[1].textstr
        text = text[:1] + "|" + text[1:]
        text = text[:3] + "|" + text[3:]
        text = text[:5] + " " + text[5:]
        text = text[:3] + " " + text[3:]
        dfSelO[0].update_textspace(text, "@")
        dfSelO.update(dfResO)
        dfSelO[0].text(1, "A")
        dfSelO[0].text(3, "C")
        dfSelO[0].text(0, cmd="pop")
        dfSelO[0].value("calc_line_idx", 4, 10)
        # obj[0].update()  - Optional
        dfXO.update(dfSelO)

    @staticmethod
    def plot_charinfo(charinfo, date, GROUPS=False, years=False, plot="Histo"):
        # Plot Group
        if years:
            groupmembers = ["Zeichen", "Buchstaben", "Zahlen", "Satzzeichen"]
            for ocr in charinfo:
                for member in groupmembers:
                    data = []
                    labels = []
                    for year in charinfo[ocr]:
                        labels.append(year)
                        data.append([float(x) for x in charinfo[ocr][year].get(member, {}).get("Confs", [])])
                    output = "/home/jkamlah/Coding/python_ocr/Testfiles/charconfs/figs/"
                    bins_input = 10

                    fileformat = ".png"

                    # Plot
                    sns.set()
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    bplot1 = ax.boxplot(data, vert=True, patch_artist=True, labels=labels, showfliers=False)
                    ax.set_title("Vergleich " + ocr + "_allYears_" + member)
                    ax.yaxis.grid(True)
                    fig.tight_layout()
                    plt.savefig(output + "compare_" + ocr + "_allYears_" + member + fileformat)
                    plt.close()
        elif GROUPS:
            groupmembers = ["Zeichen", "Buchstaben", "Zahlen", "Satzzeichen"]
            for ocr in charinfo:
                data = []
                for member in groupmembers:
                    data.append([float(x) for x in charinfo[ocr].get(member, {}).get("Confs", [])])
                # data = ([float(x) for x in charinfosdict[ocr].get("Zeichen", {}).get("Confs", [])],
                #        [float(x) for x in charinfosdict[ocr].get("Buchstaben", {}).get("Confs", [])],
                #        [float(x) for x in charinfosdict[ocr].get("Zahlen", {}).get("Confs", [])],
                #        [float(x) for x in charinfosdict[ocr].get("Satzzeichen", {}).get("Confs", [])])
                # Settings
                output = "/home/jkamlah/Coding/python_ocr/Testfiles/charconfs/figs/"
                bins_input = 10

                fileformat = ".png"

                # Plot
                sns.set()
                fig = plt.figure()
                ax = fig.add_subplot(111)
                if plot == "Histo":
                    # the histogram of the data
                    # ax.hist(data, bins_input, histtype='bar',stacked=True)
                    colors = ['red', 'tan', 'lime', 'blue']
                    ax.hist(data, bins_input, density=True, histtype='bar', color=colors, label=groupmembers)
                    plt.legend(loc='best')
                    # label_patch = mpatches.Patch(color=, label=["Zeichen","Buchstaben","Zahlen","Satzzeichen"])
                    # plt.legend(['red', 'tan', 'lime','blue'],["Zeichen","Buchstaben","Zahlen","Satzzeichen"])

                else:
                    bplot1 = ax.boxplot(data, vert=True, patch_artist=True, labels=groupmembers, showfliers=False)
                    # plt.ylim((75, 100))
                ax.set_title("Vergleich " + ocr + date)
                ax.yaxis.grid(True)
                fig.tight_layout()
                plt.savefig(output + "compare_" + ocr + date + fileformat)
                plt.close()

        # Plot single Character
        else:
            for char in (charinfo["ocro"].keys() | charinfo["tess"].keys()):
                # Data
                data = ([float(x) for x in charinfo["ocro"].get(char, {}).get("Confs", [])],
                        [float(x) for x in charinfo["tess"].get(char, {}).get("Confs", [])])
                # Settings
                output = "/home/jkamlah/Coding/python_ocr/Testfiles/charconfs/figs/"
                bins_input = 10
                colors = ['red', 'lime']
                labels = ["Ocropus", "Tesseract"]
                fileformat = ".png"

                # Plot
                sns.set()
                fig = plt.figure()
                ax = fig.add_subplot(111)
                plot = "Histo"
                if plot == "Histo":
                    # the histogram of the data
                    # ax.hist(data, bins_input, histtype='bar',stacked=True)
                    ax.hist(data, bins_input, density=True, histtype='bar', color=colors, label=labels)
                    plt.legend(loc='best')
                    # label_patch = mpatches.Patch(color=, label=["Zeichen","Buchstaben","Zahlen","Satzzeichen"])
                    # plt.legend(['red', 'tan', 'lime','blue'],["Zeichen","Buchstaben","Zahlen","Satzzeichen"])

                else:
                    bplot1 = ax.boxplot(data, vert=True, patch_artist=True, labels=labels, showfliers=False)
                    # plt.ylim((75, 100))
                ax.set_title("Vergleich von: " + char)
                ax.yaxis.grid(True)
                fig.tight_layout()
                plt.savefig(output + char + fileformat)
                plt.close()
        return 0

    ### TEST FUNCTION
    @staticmethod
    def test_word(items):
        try:
            word1 = items.word["text"].get(1.0, None)
            if word1 != None:
                word1 = word1[:-2] + "| |" + word1[-2:]
                items.update_textspace(word1, "|", widx=1.0)
                word2 = items.word["text"].get(2.0, None)
                if word2 != None:
                    word2 = word2[:-2] + "| |" + word2[-2:]
                    items.update_textspace(word2, "|", widx=2.0)
                    print(items.value("x_confs", 2, widx=2.0))
                    print(items.value("calc_char", 2, widx=2.0))
            print(items.textstr)
            print(items.value("x_confs", 3))
            print(items.value("calc_char", 3))
        except Exception as ex:
            print("TEST WORD FAILED: ", ex)
        finally:
            print("TEST WORD PASSED!")

    @staticmethod
    def test_linematching(dfXO):
        max_line = dfXO.df["calc_line"].max()
        grps = dfXO.df.groupby(["ocr", "ocr_profile"])
        for lidx in np.arange(0.0, max_line):
            for name, group in grps:
                print(name[0])
                arr = group["calc_line"]
                if lidx in group["calc_line"].tolist():
                    print(group.loc[group["calc_line"] == lidx]["char"].tolist())
                    # "".join(group.loc[group["calc_line"] == lidx]["char"].tolist())
                else:
                    print("No line found!")
        return