import pandas as pd

class DFObjectifier(object):

    def __init__(self,con,tablename):
        self.df = pd.read_sql_table(tablename, con).set_index(['ocr','ocr_profile','line_idx', 'word_idx', 'char_idx'])


    def get_obj(self,*,ocr=None,ocr_profile=None,line_idx=None,word_idx=None,char_idx=None,col=None):
        idx = pd.IndexSlice[slice(ocr),slice(ocr_profile),slice(line_idx),slice(word_idx),slice(char_idx)]
        if col is None:
            _df_ = self.df.loc(axis=0)[idx]
        else:
            _df_ = self.df.loc(axis=0)[idx].loc(axis=1)[col]
        _df_ = _df_.reset_index().set_index(['ocr', 'ocr_profile'])
        df_dict1 = _df_.to_dict(orient="split")
        count = -1
        table = Table()
        lastgroup = tuple()
        for idx, group in enumerate(df_dict1["index"]):
            if group != lastgroup:
                count += 1
                lastgroup = group
                table.data[count] = {}
                table.data[count]["ocr"] = group[0]
                table.data[count]["ocr_profile"] = group[1]
                for kidx, key in enumerate(df_dict1["columns"]):
                    table.data[count][key] = []
                    table.data[count][key].append(df_dict1["data"][idx][kidx])
            else:
                for kidx, key in enumerate(df_dict1["columns"]):
                    table.data[count][key].append(df_dict1["data"][idx][kidx])
        return table

    def update(self,obj):
        return

class Table(object):

    def __init__(self):
        self.data = {}

    def get_text(self,ocr):
        if "char" in self.data[ocr]:
            return "".join([char.replace(""," ") for char in self.data[ocr]["char"]])
        else:
            return "No text to export!"