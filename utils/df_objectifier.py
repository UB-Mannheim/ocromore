import pandas as pd
from utils.df_tools import get_con
import os

class DFObjectifier(object):

    def __init__(self,engine,tablename):
        self.stdkeys = ['ocr','ocr_profile','line_idx', 'word_idx', 'char_idx']
        self.tablename = tablename
        self.engine = engine
        self.df = pd.read_sql_table(tablename, get_con(engine)).set_index(self.stdkeys)

    def get_obj(self,*,ocr=None,ocr_profile=None,line_idx=None,word_idx=None,char_idx=None,col=None,query=None):
        # Need some explanation?
        # vars = represent the index-columns
        # col = select columns you want to get (+ index)
        # query = give some query conditions for the df
        vars = [ocr, ocr_profile, line_idx, word_idx, char_idx]
        for varidx, var in enumerate(vars):
            if var is None:
                vars[varidx] = (None)
            if not isinstance(var,tuple):
                vars[varidx] = (var,var,1)
        idx = pd.IndexSlice[slice(*vars[0]),slice(*vars[1]),slice(*vars[2]),slice(*vars[3]),slice(*vars[4])]
        if col is None:
            _df_ = self.df.loc(axis=0)[idx]
        else:
            _df_ = self.df.loc(axis=0)[idx].loc(axis=1)[col]
        if query is not None:
            _df_ = _df_.query(query)
        _df_ = _df_.reset_index().set_index(self.stdkeys[:2])
        df_dict1 = _df_.to_dict(orient="split")
        count = -1
        obj = Obj()
        lastgroup = tuple()
        for idx, group in enumerate(df_dict1["index"]):
            if group != lastgroup:
                count += 1
                lastgroup = group
                obj.data[count] = {}
                obj.data[count][self.stdkeys[0]] = group[0]
                obj.data[count][self.stdkeys[1]] = group[1]
                for kidx, key in enumerate(df_dict1["columns"]):
                    obj.data[count][key] = []
                    obj.data[count][key].append(df_dict1["data"][idx][kidx])
            else:
                for kidx, key in enumerate(df_dict1["columns"]):
                    obj.data[count][key].append(df_dict1["data"][idx][kidx])
        return obj

    def update(self,obj,col=None):
        combdata = {}
        for dataidx in obj.data:
            obj.data[dataidx][self.stdkeys[0]] = [obj.data[dataidx][self.stdkeys[0]]] * len(obj.data[dataidx]["line_idx"])
            obj.data[dataidx][self.stdkeys[1]] = [obj.data[dataidx][self.stdkeys[1]]] * len(obj.data[dataidx]["line_idx"])
            keys = obj.data[dataidx].keys()
            if col is not None:
                keys = self.stdkeys+col
            for key in keys:
                if key not in combdata: combdata[key] = []
                combdata[key] = combdata[key]+obj.data[dataidx].get(key,[])
        self.df.update(pd.DataFrame.from_dict(combdata).set_index(self.stdkeys))
        return

    def write2sql(self):
        con = get_con(self.engine)
        # try to create a table
        self.df.to_sql(self.tablename, con, if_exists='replace')
        print(f'The table:"{self.tablename}" was updated!')
        return

class Obj(object):

    def __init__(self):
        self.data = {}

    def get_text(self,ocr):
        if "char" in self.data[ocr]:
            return "".join([char.replace(""," ") for char in self.data[ocr]["char"]])
        else:
            return "No text to export!"