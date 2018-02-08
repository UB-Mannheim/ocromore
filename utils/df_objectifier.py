import pandas as pd
import numpy as np
from utils.df_tools import get_con

class DFObjectifier(object):

    def __init__(self,engine,tablename):
        self.idxkeys = ['ocr','ocr_profile','line_idx', 'word_idx', 'char_idx']
        self.imkeys = ['char','x_confs','x_wconf','line_x0','line_x1','line_y0','line_y1', 'word_x0','word_x1','word_y0','word_y1']
        self.tablename = tablename
        self.engine = engine
        self.df = pd.read_sql_table(tablename, get_con(engine)).set_index(self.idxkeys)
        self.res_df = self._init_res_df()

    def _init_res_df(self):
        res_df = pd.DataFrame(columns=self.df.reset_index().columns)
        try:
            del res_df["ocr"]
            del res_df["ocr_profile"]
        except:
            pass
        res_df["UID"] = []
        return res_df

    def get_obj(self,*,ocr=None,ocr_profile=None,line_idx=None,word_idx=None,char_idx=None,col=None,query=None,res=False):
        # Need some explanation?
        # vars = represent the index-columns
        # col = select columns you want to get (+ index)
        # query = params: 'column op "val"' (query conditions for the df)
        if res:
            res_df = self.res_df
            size = self.res_df.shape[0]
            return ResObj("Result",res_df,self.idxkeys,self.imkeys)
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
        _df_ = _df_.reset_index().set_index(self.idxkeys[:2])
        grouped = _df_.groupby(level=['ocr', 'ocr_profile'])
        obj = []
        for name, group in grouped:
            size = group.shape[0]
            group["UID"] = np.arange(0,size)
            obj.append(Obj(name,group,self.idxkeys,self.imkeys))
        return obj

    def update(self,objlist,col=None):
        if not isinstance(objlist,list): objlist = [objlist]
        for obj in objlist:
            obj.update(col)
            new_df = obj.orig_df.reset_index().set_index(self.idxkeys)
            if col is not None:
                if isinstance(col,list): col = [col]
                new_df = new_df.loc[self.idxkeys+col]
            if obj.name == "Result":
                self.res_df._update_res_df(new_df,self.res_df.shape[0])
            else:
                self.df.update(new_df)
        return

    def _update_obsolete(self,obj,col=None):
        combdata = {}
        for dataidx in obj.data:
            obj.data[dataidx][self.idxkeys[0]] = [obj.data[dataidx][self.idxkeys[0]]] * len(obj.data[dataidx]["line_idx"])
            obj.data[dataidx][self.idxkeys[1]] = [obj.data[dataidx][self.idxkeys[1]]] * len(obj.data[dataidx]["line_idx"])
            keys = obj.data[dataidx].keys()
            if col is not None:
                keys = self.idxkeys+col
            for key in keys:
                if key not in combdata: combdata[key] = []
                combdata[key] = combdata[key]+obj.data[dataidx].get(key,[])
        self.df.update(pd.DataFrame.from_dict(combdata).set_index(self.idxkeys))
        return

    def write2sql(self):
        con = get_con(self.engine)
        # try to create a table
        self.df.to_sql(self.tablename, con, if_exists='replace')
        print(f'The table:"{self.tablename}" was updated!')
        return

class Obj(object):

    def __init__(self,name,df,idxkeys,imkeys):
        self.idxkeys = idxkeys
        self.imkeys = imkeys
        self.name = name
        self.data = self._get_data(df)
        self.orig_df = df
        self.orig_text = self._orig_text()
        self.ivalue = Value()

    def _get_data(self,df):
        data = {}
        df_dict = df.to_dict(orient="split")
        for kidx, key in enumerate(df_dict["columns"]):
            if key not in data:
                data[key] = []
            for didx, dataset in enumerate(df_dict["data"]):
                data[key].append(df_dict["data"][didx][kidx])
        return data

    def _orig_text(self):
        if "char" in self.data:
            str = ""
            if len(self.data["word_idx"]) > 0:
                lidx = self.data["word_idx"][0]
                for pos, idx in enumerate(self.data["word_idx"]):
                    if idx != lidx:
                        str += " "
                        lidx = idx
                    str += self.data["char"][pos]
            return str
        else:
            return "No text to export!"

    def text(self,pos,val=None,cmd="insert"):
        if cmd == "insert":
            self.data["calc_char"].insert(pos,val)
            self.data["UID"].insert(pos, -1)
            self.data["char_weight"].insert(pos,-1)
            i = 1 if pos != 0 else 0
            self.data["calc_line"].insert(pos, self.data["calc_line"][pos - i])
            self.data["calc_word"].insert(pos, self.data["calc_word"][pos - i])
        if cmd == "pop":
            self.data["calc_char"].pop(pos)
            self.data["UID"].pop(pos)
        if cmd == "replace":
            self.data["calc_char"][pos] = val

    @property
    def textstr(self):
        if "calc_char" in self.data:
            str = ""
            if len(self.data["UID"]) > 0:
                lidx = self.data["UID"][0]
                for pos,idx in enumerate(self.data["UID"]):
                    if idx != lidx:
                        str +=" "
                        lidx = idx
                    str+=self.data["calc_char"][pos]
            return str
        else:
            return "No text to export!"

    def value(self,attr,pos,val=None):
        if attr in self.data.keys():
            self.ivalue.attr = attr
            self.ivalue.pos = pos
            if val is not None:
                self._set_value(val)
            else:
                self._get_value()
            return self.ivalue.val

    def _get_value(self):
        idx = self.data["UID"][self.ivalue.pos]
        if self.ivalue.attr in self.idxkeys+["char"] and self.name != "Result":
            if idx != -1:
                self.ivalue.val = self.data[self.ivalue.attr][idx]
        else:
            self.ivalue.val = self.data[self.ivalue.attr][self.ivalue.pos]

    def _set_value(self,val):
        if self.ivalue.attr not in self.idxkeys+["char","UID"] or self.name == "Result":
            self.ivalue.val = val
            self.data[self.ivalue.attr][self.ivalue.pos] = val

    def update(self,col=None):
        if col is not None:
            legalcol = list(set(col).difference(set(self.idxkeys+self.imkeys)))
            keys = ["UID"]+legalcol
        else:
            keys = set(self.data.keys()).difference(set(self.idxkeys+self.imkeys))
        dfdict = {}
        for idx,uidx in enumerate(self.data["UID"]):
            if uidx != -1:
                for col in keys:
                    if col not in dfdict:
                        dfdict[col] = []
                    if col == "UID":
                        dfdict[col].append(uidx)
                    else:
                        dfdict[col].append(self.data[col][idx])
        df = pd.DataFrame.from_dict(dfdict).set_index("UID")
        orig_df = self.orig_df
        orig_df = orig_df.reset_index().set_index("UID")
        orig_df.update(df)
        self.orig_df = orig_df

    def store(self):
        return

class ResObj(Obj):

    def __init__(self, name, df, idxkeys, imkeys):
        Obj.__init__(self,name,df,idxkeys,imkeys)

    def _update_res_df(self,maxuid,col=None):
        if col is not None:
            keys = ["UID"]+col
        else:
            keys = self.data.keys()
        dfdict = {}
        for idx, uidx in enumerate(self.data["UID"]):
            if uidx == 1:
                uidx = maxuid
                maxuid += 1
            for col in keys:
                if col not in dfdict:
                    dfdict[col] = []
                    if col == "UID":
                        dfdict[col].append(uidx)
                    else:
                        dfdict[col].append(self.data[col][idx])
        df = pd.DataFrame.from_dict(dfdict).set_index("UID")
        orig_df = self.orig_df
        orig_df = orig_df.reset_index().set_index("UID")
        orig_df.update(df)
        self.orig_df = orig_df

class Value(object):
    def __init__(self):
        self.pos = None
        self.attr = None
        self.val = None