from utils.df_objectifier import DFObjectifier
from pathlib import Path
from n_dist_keying.ocr_comparison import OCRcomparison
from n_dist_keying.ocr_set import OCRset
from n_dist_keying.database_handler import DatabaseHandler


DB_DIR = './Testfiles/sql/'
NUMBER_OF_INPUTS = 3 # number of ocr inputs which will be compared, todo make this dynmically with maxlen or smth



dbdir_abs = 'sqlite:///' + str(Path(DB_DIR).absolute())

dataframe_wrapper = DFObjectifier(dbdir_abs + '/1957.db', '0237_1957_hoppa-405844417-0050_0290')
lObject = dataframe_wrapper.get_line_obj()
database_handler = DatabaseHandler(dataframe_wrapper, NUMBER_OF_INPUTS)
ocr_comparison = database_handler.create_ocr_comparison()

dfSelO = dataframe_wrapper.get_line_obj()


for lidx in dfSelO:
    for items in dfSelO[lidx]:
        print(items.textstr)
        txt = items.textstr
        txt = txt[:1] + "|||" + txt[1:]
        items.update_textspace(txt, "|")
        print(items.textstr)
        print(items.data["UID"])
        print(items.value("calc_char", 2))
        print(items.value("x_confs", 2))
        print(items.value("calc_char", 4))
        print(items.value("x_confs", 4))