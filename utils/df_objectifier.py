import pandas as pd
import numpy as np
from utils.df_tools import get_con, spinner
import math
import copy
import collections
import sys
from sklearn import cluster, neighbors

class PParam(object):
    def __init__(self):
        self.y0 = None
        self.y1 = None
        self.diff = 0
        self.diffmid = 0
        self.y1_max = 0
        self.max_row = 0
        self.lineIdx = 0

class DFObjectifier(object):
    """
    This class serves as cross-plattform between sql-dataframe(df)-obj for ocr output data
    with properties and methods to create and update each of them.
    It also contains methods for preprocessing the data.
    =======
    METHODS
    =======
       Preprocessing
       -----------------------------------------------------------------------------------------------------------------
            match_line  -   Match lines over all datasets
            unspace     -   Unspace datasets compared to a pivot
            match_words -   Match words for each line over all datasets

        Create Obj
       -----------------------------------------------------------------------------------------------------------------
                            Info: There are three types of obj -
                            SelObj (selection)  -   Contains data, serves for calcuation
                            ResObj (result)     -   Contains 0 data, serves to store for the calculated results
                            EmptyObj            -   Contains 0 data, serves as a replacement for lines,
                                                    where no data exists in one or more of the datasets
            get_obj     -   Returns an obj with the specified parameters for all datasets
            get_line_obj-   Returns obj for each line with specified parameters for all datasets

        Update
       -----------------------------------------------------------------------------------------------------------------
            update      -   updates the main dataframe (df)

        Write
       -----------------------------------------------------------------------------------------------------------------
            write2sql   -   writes the current state of the df to the sql
            write2file  -   write the current state of the df to a specific file (e.g. txt, hocr)
    """

    def __init__(self,engine,tablename):
        """
        Initialize the DFObject-Handler
        :param engine: Connection to the db
        :param tablename: Name of the table to be loaded

        :prop idxkeys: Index Keys
        :prop imkeys: Immutable Keys
        :prop df: Main dataframe
        :prop res_df: Result dataframe
        """
        self.idxkeys = ['ocr','ocr_profile','line_idx', 'word_idx', 'char_idx']
        self.imkeys = ['char','x_confs','x_wconf','line_x0','line_x1','line_y0','line_y1', 'word_x0','word_x1','word_y0','word_y1']
        self.tablename = tablename
        self.engine = engine
        self.df = pd.read_sql_table(tablename, get_con(engine)).set_index(self.idxkeys)
        self.res_df = self._init_res_df()

    def _init_res_df(self):
        """
        Initialize the result dataframe
        :return:
        """
        res_df = pd.DataFrame(columns=self.df.reset_index().columns)
        try:
            for value in list(res_df):
                if not value in [*self.idxkeys,*self.imkeys]:
                    del res_df[value]
        except:
            pass
        res_df["UID"] = []
        return res_df

    def get_line_obj(self,*,ocr=None,ocr_profile=None,line_idx=None,word_idx=None,char_idx=None,col=None,query=None,res=False, empty=False):
        """
        Gets an Object with all lines
        :param ocr: Index param
        :param ocr_profile: Index param
        :param line_idx: Index param
        :param word_idx: Index param
        :param char_idx: Index param
        :param col: select columns you want to get (+ index)
        :param query: 'column op "val"' (query conditions for the df)
        :param res: Creates an result obj (bool)
        :param empty: Creates an empty obj (bool)
        :return:
        """
        #if res:
        #    return DFResObj("Result",self.res_df,self.idxkeys,self.imkeys,self.res_df.shape[0])
        if empty:
            empty_df = pd.DataFrame(columns=self.df.reset_index().columns)
            empty_df["UID"] = []
            return DFEmptyObj("Empty",empty_df,self.idxkeys,self.imkeys,empty_df.shape[0])
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
        #if query is not None:
            #_df_ = _df_.query(query)
        _df_ = _df_.reset_index().set_index("calc_line_idx")
        obj = {}
        resobj = {}
        idxgroups = _df_.groupby(level=['calc_line_idx'])
        for idxname, idxgroup in idxgroups:
            obj[idxname] = []
            if res:
                #resobj[idxname] = []
                resobj[idxname] = DFResObj("Result",self.res_df,self.idxkeys,self.imkeys,self.res_df.shape[0],lidx=idxname)
            grouped = idxgroup.set_index(['ocr','ocr_profile']).groupby(level=['ocr', 'ocr_profile'])
            for name, group in grouped:
                #Needs to be copied cos of the addition of "UID"
                cpgroup = group.copy(deep=True)
                size = cpgroup.shape[0]
                if size != 0:
                    cpgroup["UID"] = np.arange(0,size)
                    obj[idxname].append(DFSelObj(name,cpgroup,self.idxkeys,self.imkeys))
                    del cpgroup
        if res:
            return obj, resobj
        else:
            return obj

    def get_obj(self,*,ocr=None,ocr_profile=None,line_idx=None,word_idx=None,char_idx=None,col=None,query=None,res=False, empty=False):
        """
        Gets an Object for the specifc parameters
        :param ocr: Index param
        :param ocr_profile: Index param
        :param line_idx: Index param
        :param word_idx: Index param
        :param char_idx: Index param
        :param col: select columns you want to get (+ index)
        :param query: 'column op "val"' (query conditions for the df)
        :param res: Creates an result obj (bool)
        :param empty: Creates an empty obj (bool)
        :return:
        """
        if res:
            res_df = self.res_df
            return DFResObj("Result",res_df,self.idxkeys,self.imkeys,self.res_df.shape[0])
        if empty:
            empty_df = pd.DataFrame(columns=self.df.reset_index().columns)
            empty_df["UID"] = []
            return DFEmptyObj("Empty",empty_df,self.idxkeys,self.imkeys,empty_df.shape[0])
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
        #if query is not None:
            #_df_ = _df_.query(query)
        _df_ = _df_.reset_index().set_index(self.idxkeys[:2])
        grouped = _df_.groupby(level=['ocr', 'ocr_profile'])
        obj = []
        for name, group in grouped:
            #Needs to be copied cos of the addition of "UID"
            cpgroup = group.copy(deep=True)
            size = cpgroup.shape[0]
            cpgroup["UID"] = np.arange(0,size)
            obj.append(DFSelObj(name,cpgroup,self.idxkeys,self.imkeys))
            del cpgroup
        return obj

    def update(self,objlist,col=None):
        """
        Updates the main dataframe (df)
        :param objlist: Obj or list of Objs which should be used to update the df
        :param col: Specifies the columns which should be updated
        """
        if not isinstance(objlist,list): objlist = [objlist]
        for obj in objlist:
            obj.update_df(col)
            idx = self.idxkeys if not obj.result else "UID"
            new_df = obj.orig_df.reset_index().set_index(idx)
            if col is not None:
                if isinstance(col,list): col = [col]
                new_df = new_df.loc[idx+col]
            if obj.result:
                obj.maxuid = self.res_df.shape[0]
                self.res_df.update(new_df)
            else:
                self.df.update(new_df)
        return

    def clean_data(self, outliercleaner = True,iqrmul=2.0, outlierex = None):
        """
        Unspaces the words in the dataset based on a pivot
        :param sort_by: Set the pivot selectin order
        :param pad: Set the multiplicator which calculats the padding value for the matching algo.
                    Pad = Multiplicator * (Height of Line)
        :param padrb: Special padding for right border
        :return:
        """
        if outlierex is None:
            outlierex = ["\"","§","'","*","A","O","Y","°","^","`"]
        linedict = {}
        tdf = self.df.reset_index().loc(axis=1)[
            "ocr", "ocr_profile", 'calc_char','line_idx', 'word_idx', 'char_idx', "line_x0", "line_x1", "line_y0", "line_y1","word_x0", "word_x1", "word_y0", "word_y1", "x_wconf", "x_confs"]
        lgroups = tdf.groupby(["line_idx", "ocr", "ocr_profile"])
        for lidx, groups in lgroups:
            if not lidx[0] in linedict:
                linedict[lidx[0]] = {}
                linedict[lidx[0]]["orig"] = {}
            linedict[lidx[0]]["orig"][(lidx[1], lidx[2])] = groups.to_dict(orient="list")
            linedict[lidx[0]]["orig"][(lidx[1], lidx[2])]["ocr"] = [lidx[1]]*len(linedict[lidx[0]]["orig"][(lidx[1], lidx[2])]["line_idx"])
            linedict[lidx[0]]["orig"][(lidx[1], lidx[2])]["ocr_profile"] = [lidx[2]]*len(linedict[lidx[0]]["orig"][(lidx[1], lidx[2])]["line_idx"])
        tdf = pd.DataFrame()
        maxlines = max(set(linedict.keys()))
        for line in linedict:
            print(f"Clean data in line: {int(line)}/{int(maxlines)}")
            for ocr in sorted(linedict[line]["orig"].keys()):
                if outliercleaner:
                    linf = linedict[line]["orig"][ocr]["word_y0"]
                    quartile_1, quartile_3 = np.percentile(linf, [25, 75])
                    iqr = quartile_3 - quartile_1
                    lower_bound = quartile_1 - (iqr * iqrmul)
                    outlierspos = np.where(linf < lower_bound)[0]
                    for outlierpos in outlierspos:
                        if outlierpos == 0 or outlierpos == len(linf)-1:
                            wordidxarr = linedict[line]["orig"][ocr]["word_idx"]
                            outlierwidx = wordidxarr[outlierpos]
                            if len(np.where(np.array(wordidxarr) == outlierwidx)[0]) == 1:
                                if not linedict[line]["orig"][ocr]["calc_char"][outlierpos] in outlierex:
                                    if outlierpos == 0:
                                        minx0 = np.array(linf[outlierpos + 1:]).min()
                                    else:
                                        minx0 = np.array(linf[:outlierpos]).min()
                                    linf[outlierpos] = minx0
                                    #linedict[line]["orig"][ocr]["calc_char"][outlierpos] = "_"
                                    linedict[line]["orig"][ocr]["x_confs"][outlierpos] = 49.0
                                    linedict[line]["orig"][ocr]["line_y0"] = [minx0]*len(linedict[line]["orig"][ocr]["line_y0"])
                                    print(f"Clean data from outlier in {ocr[0]} ✓")
                if tdf.empty:
                    tdf = pd.DataFrame.from_dict(linedict[line]["orig"][ocr])
                else:
                    tdf = tdf.append(pd.DataFrame.from_dict(linedict[line]["orig"][ocr]), ignore_index=True)
        if not tdf.empty:
            self.df.update(tdf.reset_index().set_index(self.idxkeys))
        print("Clean data ✓")
        return

    def match_line(self,force=False,pad=2,padmid=0.575,lhm=2):
        #TODO: rework other preprocesses...
        """
        Matches the lines over all datasets
        :param force: Force to calculate the matching lines (overwrites old values)
        :param pad: Padding area where to find similar lines (0.25 -> 25 prc)
        :param max_col: Maximum value for matching lines (prevent infinity loops)
        :return:
        """
        try:
            if force:
                self.df["calc_line_idx"] = -1
            if self.df.loc[self.df["calc_line_idx"] == -1].empty: return False
            print("Start line matching")
            tdf = self.df.reset_index()
            tdf["line_height"] = tdf["line_y1"] - tdf["line_y0"]
            linedict = tdf.to_dict(orient="list")
            pparam = PParam()
            pparam.max_row = max(linedict["line_idx"])*3
            pparam.y1_max = max(linedict["line_y1"])+1
            while True:
                print(f"Match line: {pparam.lineIdx}")
                pparam.y0 = min(linedict["line_y0"])
                pparam.y1 = linedict["line_y1"][linedict["line_y0"].index(pparam.y0)]
                if pparam.y0 > pparam.y1:
                    linedict["line_y1"][linedict["line_y0"].index(pparam.y0)] = pparam.y0+1
                    pparam.y1 = pparam.y0+1
                if -1 not in linedict["calc_line_idx"]:
                    print("Match lines ✓")
                    break
                pparam.diff = (pparam.y1 - pparam.y0) * pad
                pparam.diffmid = pparam.diff
                if pad > padmid: pparam.diffmid = (pparam.y1 - pparam.y0) * padmid
                # Select all y0 which are smaller as y0+25%diff and greater as y0+25%diff
                con =  ((pparam.y1-pparam.y0) < np.array([x*lhm for x in linedict['line_height']])) & \
                       ((pparam.y0 - pparam.diff) < np.array(linedict['line_y0'])) & \
                       ((pparam.y0 + pparam.diffmid) > np.array(linedict['line_y0'])) & \
                       ((pparam.y1 - pparam.diffmid) < np.array(linedict['line_y1'])) & \
                       ((pparam.y1 + pparam.diff) > (np.array(linedict['line_y1'])))
                old_lidx = None
                old_idx = None
                offset = 0
                engine_stat = None
                for idx in np.nonzero(con)[0].tolist():
                    if engine_stat is None: engine_stat = (linedict["ocr"][idx],linedict["ocr_profile"][idx])
                    if engine_stat != (linedict["ocr"][idx],linedict["ocr_profile"][idx]):
                        offset = 0
                        engine_stat = (linedict["ocr"][idx], linedict["ocr_profile"][idx])
                    if old_lidx is None:
                        old_lidx = linedict["line_idx"][idx]
                    if linedict["line_idx"][idx] != old_lidx:
                        old_lidx = linedict["line_idx"][idx]
                        offset = linedict["word_idx"][old_idx]+1
                    linedict["calc_line_idx"][idx] = pparam.lineIdx
                    linedict["word_idx"][idx] = linedict["word_idx"][idx]+offset
                    linedict["line_y0"][idx] = pparam.y1_max
                    old_idx = idx
                pparam.lineIdx += 1
                if pparam.lineIdx == pparam.max_row:
                    print("Match lines ✗")
                    print(f"The max of {pparam.max_row} col was reached. Maybe something went wrong?")
                    break
            self.df["calc_line_idx"] = linedict["calc_line_idx"]
            self.df["calc_word_idx"] = linedict["word_idx"]
        except Exception as e:
            print(f"Exception: {e}")
            pass
        return True

    def obsolete_match_line(self,force=False, pad=5, padmid=0.55,lhm=2):
        """
        Matches the lines over all datasets
        :param force: Force to calculate the matching lines (overwrites old values)
        :param pad: Padding area where to find similar lines (0.25 -> 25 prc)
        :param max_col: Maximum value for matching lines (prevent infinity loops)
        :return:
        """
        try:
            if force:
                self.df["calc_line_idx"] = -1
            if self.df.loc[self.df["calc_line_idx"] == -1].empty: return False
            orig_idx = self.df.index
            self.df.reset_index()
            lineIdx = 0
            print("Start line matching")
            max_row = self.df.reset_index().groupby(["ocr","ocr_profile"])["line_idx"].max().sum()
            while True:
                #sys.stdout.write(f"Match lines {next(spinner)} \r")
                #sys.stdout.flush()
                print(f"Match line: {lineIdx}")
                tdf = self.df.loc[self.df["calc_line_idx"] == -1]
                tdf = tdf[["line_y0", "line_y1", "calc_line_idx","calc_word_idx"]]
                y0_min = tdf['line_y0'].min()
                if math.isnan(y0_min):
                    print("Match lines ✓")
                    break
                y1_min = tdf.loc[tdf['line_y0'] == y0_min]["line_y1"].min()
                y_diff = (y1_min - y0_min) * pad
                y_diffmid = y_diff
                if pad > padmid: y_diffmid =(y1_min - y0_min)*padmid
                tdf["line_height"] = tdf["line_y1"]-tdf["line_y0"]
                # Select all y0 which are smaller as y0+25%diff and greater as y0+25%diff
                tdf = tdf.loc[((tdf['line_height']*lhm) > (y1_min-y0_min))&
                              (tdf['line_y0'] > (y0_min - y_diff)) &
                              (tdf['line_y0'] < (y0_min + y_diffmid)) &
                              (tdf['line_y1'] > (y1_min - y_diffmid)) &
                              (tdf['line_y1'] < (y1_min + y_diff))]
                # Select all y1 which are smaller as y1+25%diff and greater as y1+25%diff
                #tdf = tdf.loc[tdf['line_y1'] > (y1_min - y_diffmid)].loc[tdf['line_y1'] < (y1_min + y_diff)]
                tdfgroups = tdf.reset_index().groupby(["ocr","ocr_profile"])
                for name,group in tdfgroups:
                    if len(group["line_idx"].unique().tolist()) > 1:
                        offset = 0.0
                        for lidx in group["line_idx"].unique().tolist():
                            idx = pd.IndexSlice
                            tdf.loc[idx[name[0],name[1],lidx,:,:],["calc_word_idx"]] = tdf.loc[idx[name[0],name[1],lidx,:,:],["calc_word_idx"]].add(offset)
                            #tdf.reset_index().update(rtdf)
                            offset = tdf.loc[idx[name[0],name[1],lidx,:,:],["calc_word_idx"]].max()+1.0


                tdf["calc_line_idx"] = lineIdx

                self.df.update(tdf)

                lineIdx += 1

                if lineIdx == max_row:
                    print("Match lines ✗")
                    print(f"The max of {max_row} col was reached. Maybe something went wrong?")
                    break
            self.df.set_index(orig_idx)
        except Exception as e:
            print("Match lines ✗")
            print("Something went wrong while matching lines.")
            print(f"Error:{e}")
            pass
        return True

    def unspace(self, sort_by=None, pad=1.0, padrb=0.00):
        """
        Unspaces the words in the dataset based on a pivot
        :param sort_by: Set the pivot selectin order
        :param pad: Set the multiplicator which calculats the padding value for the matching algo.
                    Pad = Multiplicator * (Height of Line)
        :param padrb: Special padding for right border
        :return:
        """
        if sort_by is None:
            sort_by = ["Tess", "Abbyy", "Ocro"]
        linedict = {}
        tdf = self.df.reset_index().loc(axis=1)["ocr", "ocr_profile",'line_idx', 'word_idx', 'char_idx',"word_x0", "word_x1","word_y0","word_y1","calc_line_idx", "calc_word_idx"]
        # df_dict = self.df.reset_index().set_index(self.idxkeys+["calc_line_idx"]).to_dict(orient="list")
        lgroups = tdf.groupby(["calc_line_idx", "ocr", "ocr_profile"])
        for lidx, groups in lgroups:
            if not lidx[0] in linedict:
                linedict[lidx[0]] = {}
                linedict[lidx[0]]["orig"] = {}
                linedict[lidx[0]]["calc"] = {"ocr": [], "ocr_profile": [],'line_idx':[], 'word_idx':[], 'char_idx':[], "calc_word_idx": [], "calc_line_idx": [],
                                             "word_x0": [], "word_x1": []}
            linedict[lidx[0]]["orig"][(lidx[1], lidx[2])] = groups.to_dict(orient="list")
        tdf = pd.DataFrame()
        maxlines = max(set(linedict.keys()))
        for line in linedict:
            print(f"Unspace words in line: {int(line)}/{int(maxlines)}")
            maxx1 = 0
            curline = linedict[line]["orig"]
            for ocr in sorted(linedict[line]["orig"].keys(), key=lambda x: sort_by.index(x[0])):
                if maxx1 < max(set(curline[ocr]["word_x1"])):maxx1 = max(set(curline[ocr]["word_x1"]))
            maxx1 = maxx1*2
            for ocrO in sorted(linedict[line]["orig"].keys(), key=lambda x: sort_by.index(x[0])):
                while True:
                    if all([True if item == maxx1 else False for item in curline[ocrO]["word_x0"]]): break
                    x0arr = curline[ocrO]["word_x0"]
                    minx0 = min(set(x0arr))
                    posx0 = np.where(np.array(list(x0arr)) == minx0)[0][0]
                    minx1 = curline[ocrO]["word_x1"][posx0]
                    diff = (curline[ocrO]["word_y1"][posx0]-curline[ocrO]["word_y0"][posx0])*pad
                    if diff > (minx1-minx0)/2: diff = (minx1-minx0)/2
                    if diff < 0:
                        print("Warning: X0 smaller than X1")
                        diff = 0
                        minx1=minx0
                    for ocrI in sorted(linedict[line]["orig"].keys(), key=lambda x: sort_by.index(x[0])):
                        x0arr = curline[ocrI]["word_x0"]
                        result = np.where((np.array(list(x0arr))>=minx0-diff)&(np.array(list(x0arr)) <= minx1-(diff*padrb)))[0]
                        if result.size >0:
                            widx = curline[ocrI]["calc_word_idx"][min(set(result))]
                            max_widx = curline[ocrI]["calc_word_idx"][max(set(result))]
                            if widx != max_widx:
                                for idx in np.where(np.array(list(x0arr)) > max_widx)[0]:
                                    curline[ocrI]["calc_word_idx"][idx] = curline[ocrI]["calc_word_idx"][idx]-(max_widx-widx)
                        for idx in reversed(result):
                            linedict[line]["calc"]["ocr"].append(ocrI[0])
                            linedict[line]["calc"]["ocr_profile"].append(ocrI[1])
                            linedict[line]["calc"]["line_idx"].append(curline[ocrI]["line_idx"][idx])
                            linedict[line]["calc"]["word_idx"].append(curline[ocrI]["word_idx"][idx])
                            linedict[line]["calc"]["char_idx"].append(curline[ocrI]["char_idx"][idx])
                            linedict[line]["calc"]["calc_word_idx"].append(widx)
                            linedict[line]["calc"]["calc_line_idx"].append(line)
                            linedict[line]["calc"]["word_x1"].append(curline[ocrI]["word_x1"][idx])
                            linedict[line]["calc"]["word_x0"].append(curline[ocrI]["word_x0"][idx])
                            curline[ocrI]["calc_word_idx"][idx] = widx
                            curline[ocrI]["word_x0"][idx] = maxx1
            if tdf.empty:
                tdf = pd.DataFrame.from_dict(linedict[line]["calc"])
            else:
                tdf = tdf.append(pd.DataFrame.from_dict(linedict[line]["calc"]),ignore_index=True)

        self.df.update(tdf.set_index(self.idxkeys))
        print("Unspace lines ✓")
        return

    def match_words(self, force=False,pad=1.0, diffmul=2.175):
        """
        Matches the words together this can also meant that one word is match on two for a different dataset
        :param force: Force the process
        :pad: 1.0 default
        :diffmul: 2.0 default
        :return:
        """
        self.df["word_match"]=-1
        linedict = {}
        tdf = self.df.reset_index().loc(axis=1)["ocr","ocr_profile","word_x0", "word_x1","word_y0","word_y1","calc_line_idx", "calc_word_idx","word_match"]
        #df_dict = self.df.reset_index().set_index(self.idxkeys+["calc_line_idx"]).to_dict(orient="list")
        lgroups = tdf.groupby(["calc_line_idx","ocr","ocr_profile"])
        for lidx, groups in lgroups:
            if not lidx[0] in linedict:
                linedict[lidx[0]] ={}
                linedict[lidx[0]]["orig"] = {}
                linedict[lidx[0]]["calc"] = {"ocr":[],"ocr_profile":[],"calc_word_idx":[],"calc_line_idx":[],"word_x0":[],"word_x1":[],"word_y0":[],"word_y1":[],"word_match":[]}
            linedict[lidx[0]]["orig"][(lidx[1],lidx[2])]= groups.to_dict(orient="list")
        for line in linedict:
            for ocr in linedict[line]["orig"]:
                for widx in set(linedict[line]["orig"][ocr]["calc_word_idx"]):
                    warr = np.where(np.array(list(linedict[line]["orig"][ocr]["calc_word_idx"])) == widx)[0]
                    linedict[line]["calc"]["ocr"].append(ocr[0])
                    linedict[line]["calc"]["ocr_profile"].append(ocr[1])
                    linedict[line]["calc"]["calc_word_idx"].append(widx)
                    linedict[line]["calc"]["calc_line_idx"].append(line)
                    linedict[line]["calc"]["word_x0"].append(linedict[line]["orig"][ocr]["word_x0"][warr.min()])
                    linedict[line]["calc"]["word_x1"].append(linedict[line]["orig"][ocr]["word_x1"][warr.max()])
                    linedict[line]["calc"]["word_y0"].append(linedict[line]["orig"][ocr]["word_y0"][warr.min()])
                    linedict[line]["calc"]["word_y1"].append(linedict[line]["orig"][ocr]["word_y1"][warr.max()])
                    linedict[line]["calc"]["word_match"].append(-1)
        tdf = pd.DataFrame()
        maxlines = max(set(linedict.keys()))
        for line in linedict:
            print(f"Match words in line: {int(line)}/{int(maxlines)}")
            widx = 0.0
            curline = copy.deepcopy(linedict[line]["calc"])
            maxx1 = max(set(linedict[line]["calc"]["word_x1"]))+1
            while True:
                if all([True if item >= 0.0 else False for item in linedict[line]["calc"]["word_match"]]):break
                if all([True if item > maxx1-1 else False for item in curline["word_x0"]]): break
                x0arr = curline["word_x0"]
                minx0 = min(set(x0arr))
                posx0 = np.where(np.array(list(x0arr)) == minx0)[0][0]
                minx1 = curline["word_x1"][posx0]
                if minx1 < minx0: minx1 = minx0+1
                diff = (curline["word_y1"][posx0] - curline["word_y0"][posx0]) * pad
                if diff > (minx1-minx0)/2: diff = (minx1-minx0)/2
                result = np.where(np.array(list(x0arr)) < minx1-diff)[0]
                lmaxx1 = minx1
                for idx in reversed(result):
                    linedict[line]["calc"]["word_match"][idx] = widx
                    curline["word_x0"][idx] = maxx1
                    if curline["word_x1"][idx] > lmaxx1: lmaxx1 = curline["word_x1"][idx]
                    curline["word_x1"][idx] = maxx1        
                if lmaxx1-diffmul*diff > minx1:
                    resultmax1 = np.where(np.array(list(curline["word_x1"])) < lmaxx1+diff)[0]
                    for idx in reversed(resultmax1):
                        linedict[line]["calc"]["word_match"][idx] = widx
                        curline["word_x0"][idx] = maxx1
                        curline["word_x1"][idx] = maxx1
                widx += 1.0
            if tdf.empty: tdf = pd.DataFrame.from_dict(linedict[line]["calc"])
            else: tdf = tdf.append(pd.DataFrame.from_dict(linedict[line]["calc"]),ignore_index=True)
        df1 = self.df.reset_index().set_index(["ocr","ocr_profile","calc_line_idx","calc_word_idx"])
        df2 = tdf.set_index(["ocr","ocr_profile","calc_line_idx","calc_word_idx"])
        df1.update(df2["word_match"])
        df1 = df1.reset_index().set_index(self.idxkeys)
        self.df.update(df1)
        print("Match words ✓")
        return

    def write2sql(self,result=False,engine=None):
        """
        Writes the current state of the df to the db. The table will be replaced with the new one.
        :param result:
        :param engine:
        :return:
        """
        if engine is None:
            engine = self.engine
        con = get_con(engine)
        # try to create a table
        if not result:
            self.df.to_sql(self.tablename, con, if_exists='replace')
            print(f'The table:"{self.tablename}" was updated!')
        else:
            if engine != self.engine:
                self.res_df.to_sql(self.tablename, con, if_exists='replace')
                print(f'The result table:"{self.tablename}" was updated!')
        return

    def write2file(self,path=None,fname=None,ftype='txt',calc=True,result=False,lhnorm = True):
        """
        Writes the current state of the df to a file (e.g. hocr, text)
        :param path:
        :param fname:
        :param ftype:
        :param calc:
        :param result:
        :param line_height_normalization:
        :return:
        """
        if ftype == 'txt':
            if result:
                self._writeRes2txt(path, fname, lhnorm=lhnorm)
            else:
                self._writeGrp2txt(path, fname, calc=calc,lhnorm=lhnorm)
        if ftype == 'hocr':
            if result:
                self._writeRes2hocr(path, fname)
            else:
                self._writeGrp2hocr(path, fname, calc)
        return

    def _writeGrp2txt(self,path=None,fname=None, calc = True,lhnorm = True, maxlhinsert=2):
        if path is None:
            path = "./Testfiles/txt/"
        if fname is None:
            fname = "_orig_"
        groups = self.df.reset_index().groupby(["ocr", "ocr_profile"])
        if calc:
            line, word, char = "calc_line_idx", "calc_word_idx", "calc_char"
        else:
            line, word, char = "line_idx","word_idx","char"
        for name, group in groups:
            groupl = group[line]
            lidxarr = groupl.unique()
            lhmean = None
            if lhnorm:
                lhmean = self._get_mean_lineheight(group,line,lidxarr)
            eol = None
            with open(path+fname+"".join(name), 'w+', encoding='utf-8') as infile:
                for lidx in lidxarr:
                    if eol is not None and lhnorm and lhmean is not None:
                        sol = group[groupl == lidx]["line_y1"].max()
                        lc = int(round((sol-eol)/lhmean))-1
                        if lc > maxlhinsert: lc = maxlhinsert
                        for emptyln in range(0,lc):
                                infile.write("\n")
                    groupw = group[groupl == lidx][word]
                    widxarr = groupw.unique()
                    txtline = []
                    for widx in widxarr:
                        txtline.append("".join(group.loc[groupl==lidx].loc[groupw == widx][char].tolist()))
                    infile.write(" ".join(txtline)+"\n")
                    eol = group[groupl == lidx]["line_y1"].min()
        return

    def _writeRes2txt(self,path, fname=None, lhnorm = True):
        return

    def _writeGrp2hocr(self,path, fname=None, calc = True):
        """
        if path is None:
            path = "./Testfiles/hocr/"
        if fname is None:
            fname = "_orig_"
        groups = self.df.reset_index().groupby(["ocr", "ocr_profile"])
        if calc:
            line, word, char = "calc_line_idx", "calc_word_idx", "calc_char"
        else:
            line, word, char = "line_idx","word_idx","char"
        for name, group in groups:
            groupl = group[line]
            lidxarr = groupl.unique()
            with open(path+fname+"".join(name), 'w+', encoding='utf-8') as infile:
                hocrparse = ET.parse(StringIO(f'''
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
                <head>
                <title>OCR Results</title>
                <meta http-equiv="content-type" content="text/html; charset=utf-8" />
                <meta name='AKF-OCR' content='{name[0]}-{name[1]}' />
                <meta name='ocr-capabilities' content='ocr_line ocrx_word'/>
                </head>
                </html>
                '''))
                "< div class ='ocr_page' title='image /media/sf_ShareVB/many_years_firmprofiles_output/long//1957ocropy/2018-01-25_T14H16M/0140_1957_hoppa-405844417-0050_0172/0001.bin.png; bbox 0 0 1974 15065' >"
                hocrroot = hocrparse.getroot()
                hocrtess = ET.fromstring(api.GetHOCRText(0))
                hocrtess.set("title", "image " + file + "; bbox" + hocrtess.get("title").split("bbox")[-1])
                allwordinfo = hocrtess.findall('.//div/p/span/span')
                for lidx in lidxarr:
                    groupw = group[groupl == lidx][word]
                    widxarr = groupw.unique()
                    txtline = []
                    for widx in widxarr:
                        txtline.append("".join(group.loc[groupl==lidx].loc[groupw == widx][char].tolist()))
                    infile.write(" ".join(txtline)+"\n")
        self.df.to_html
        self.df.groupby["ocr","ocr_profile"]:
        parameters = get_param(tess_profile)
        with PyTessBaseAPI(**parameters) as api:
            set_vars(api, file, tess_profile)
            ri = api.GetIterator()
            # TODO: Need to fix header ...
            # lang = api.GetInitLanguagesAsString()
            version = api.Version()


            level = RIL.SYMBOL
            bbinfo = tuple()
            conf = ""
            charinfo = {}
            for r in iterate_level(ri, level):
                if bbinfo != r.BoundingBoxInternal(RIL.WORD):
                    if bbinfo != ():
                        bbox = "bbox " + " ".join(map(str, bbinfo))
                        for wordinfo in allwordinfo:
                            if bbox in wordinfo.get("title"):
                                wordinfo.set("title", wordinfo.get("title") + ";x_confs" + conf)
                                allwordinfo.remove(wordinfo)
                                break
                        conf = ""
                    bbinfo = r.BoundingBoxInternal(RIL.WORD)
                conf += " " + str(r.Confidence(level))
                # symbol = r.GetUTF8Text(level)
                # if symbol not in charinfo:
                #    charinfo[symbol]=[r.Confidence(level)]
                # else:
                #    charinfo[symbol].append(r.Confidence(level))
        bbox = "bbox " + " ".join(map(str, bbinfo))
        for wordinfo in allwordinfo:
            if bbox in wordinfo.get("title"):
                wordinfo.set("title", wordinfo.get("title") + ";x_confs" + conf)
        # with open(fileout+"_charinfo.json", "w") as output:
        #    json.dump(charinfo, output, indent=4)
        hocrbody = ET.SubElement(hocrroot, "body")
        hocrbody.append(hocrtess)
        hocrparse.write(fileout + ".hocr", xml_declaration=True, encoding='UTF-8')
        """
        return

    def _writeRes2hocr(self,path, fname=None):
        return

    def _get_mean_lineheight(self, df,linetype,lidxarr):
        try:
            lhu = []
            lharr = df["line_y1"] - df["line_y0"]
            for idx, lidx in enumerate(lidxarr[:-1]):
                gap = df[df[linetype] == lidxarr[idx + 1]]["line_y0"].max() - df[df[linetype] == lidx]["line_y1"].min()
                if gap > 0.0:
                    lhu.append(gap)
            lh = np.array(lhu)
            lh = lh.reshape(-1, 1)
            bandwidth = cluster.estimate_bandwidth(lh, quantile=0.3)
            ms = cluster.MeanShift(bandwidth=bandwidth, bin_seeding=True)
            ms.fit(lh)
            lhmean = ms.cluster_centers_[0][0]
            lhmean = lhmean + np.median(lharr)
        except:
            print("Lineheight calculation failed!")
            return None
        return lhmean

    # ######## #
    # OBSOLETE #
    # ######## #

    def _obsolete_update_(self,obj,col=None):
        """""
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
        """""
        return

    def _obsolete_match_words_(self):
        """
        for name, group in groups:
            count = 0
            print(f"Match words in line: {name}")
            while True:
                tgdf = group.loc[group["word_match"] == -1]
                if tgdf.empty: break
                minx0 = tgdf["word_x0"].min()
                maxx1 = tgdf.loc[tgdf["word_x0"] == minx0]["word_x1"].max()
                if isinstance(minx0,float) and isinstance(maxx1,float):
                    found = group[group["word_x0"] >= minx0][group["word_x0"] <= maxx1]
                    found["word_match"] = count
                    group.update(found)
                    count += 1
            tdf.update(group)
        self.df.update(tdf)
        """
        return

    def _obsolete_unspace_(self, sort_by=None, pad=0.7):
        """
        Unspaces the words in the dataset based on a pivot
        :param sort_by: Set the pivot selectin order
        :param pad: Set the multiplicator which calculats the padding value for the matching algo.
                    Pad = Multiplicator * (Height of Line)
        :return:
        """
        """
        if sort_by is None:
            sort_by = ["Tess", "Abbyy", "Ocro"]
        # self.df["word_match"] = -1
        tdf = self.df.reset_index().loc(axis=1)[
            "ocr", "ocr_profile", "word_y0", "word_y1", "word_x0", "word_x1", "calc_line_idx", "calc_word_idx"]
        groups = tdf.groupby(["ocr", "ocr_profile"])
        groupnames = sorted(groups.indices.keys(), key=lambda x: sort_by.index(x[0]))
        max_lidx = groups['calc_line_idx'].max().max()
        for lidx in np.arange(0, max_lidx):
            # sys.stdout.write(f"Unspace lines {next(spinner)} \r")
            # sys.stdout.flush()
            print(f"Unpsace words in line: {lidx}")
            max_widx = tdf.loc[tdf['calc_line_idx'] == lidx]["calc_word_idx"].max()
            for widx in np.arange(0, max_widx):
                x0 = None
                x1 = None
                for name in groupnames:
                    group = groups.get_group(name)
                    group = group.loc[group["calc_line_idx"] == lidx]
                    if group.shape[0] != 0:
                        if x0 is None:
                            if widx != max_widx:
                                groupnext = group.loc[group["calc_word_idx"] == widx + 1.0]
                                if groupnext.shape[0] != 0:
                                    x1 = groupnext["word_x0"].iloc[0]
                            group = group.loc[group["calc_word_idx"] == widx]
                            if group.shape[0] == 0: break
                            x0 = group["word_x0"].iloc[0]
                            if x1 is None: x1 = group["word_x1"].iloc[0]
                            diff = (group["word_y1"].iloc[0] - group["word_y0"].iloc[0]) * pad
                        else:
                            # Select all the words in the other groups which have the same borders
                            tmpgroup = group.loc[group['word_x0'] > (x0 - diff)].loc[group['word_x0'] < (x1 - diff)]
                            max_widx = tmpgroup["calc_word_idx"].max()
                            min_widx = tmpgroup["calc_word_idx"].min()
                            tmpgroup["calc_word_idx"] = min_widx
                            if not np.isnan(max_widx):
                                group.update(tmpgroup)
                                tmpgroup = group.loc[group["calc_word_idx"] > max_widx]["calc_word_idx"].sub(
                                    max_widx - min_widx)
                                group.update(tmpgroup)
                            tdf.update(group)
        print("Unspace lines ✓")
        self.df.update(tdf.reset_index().set_index(self.df.index))
        """

class DFSelObj(object):
    """
    This class serves as container for a selection of the data from the main dataframe (see DFObject).
    It capsulated the data and you can work more OO as with the dataframe.
    To store the changes into the db you have to update the main df.

    =======
    METHODS
    =======
        Get&Set
        ----------------------------------------------------------------------------------------------------------------
            value               -   Set or get a value from a specific column
            text                -   Modifies the character of a the textstr

        Update
        ----------------------------------------------------------------------------------------------------------------
            update_textspace    -   Updates the calculated text at the moment you can add or remove wildcards (wc)
                                    or whitespaces (ws) on line or word (widx) base.
            update_df           -   Updates the internal dataframe which later updates the main dataframe

    ==========
    PROPERTIES
    ==========
        textstr     -   Represents the calc_char seperated by whitespaces
        ----------------------------------------------------------------------------------------------------------------
        word        -   Represents the calc_char seperated by match_word in segments
        ----------------------------------------------------------------------------------------------------------------
    """

    def __init__(self,name,df,idxkeys,imkeys):
        self.name = name
        self.data = self._get_data(df)
        self.idxkeys = idxkeys
        self.result = False
        self.empty = False
        self.imkeys = imkeys
        self.mkeys = list(set(self.data.keys()).difference(set(imkeys + idxkeys)))
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

    def text(self,pos,val=None,cmd="insert",insertfront=False):
        if cmd == "insert" and val is not None:
            self.data["calc_char"].insert(pos,val)
            self.data["UID"].insert(pos, -1)
            self.data["char_weight"].insert(pos,-1)
            i = 1 if pos != 0 else 0
            if insertfront: i = 0
            self.data["calc_word_idx"].insert(pos, self.data["calc_word_idx"][pos - i])
            if "word_match" in self.data:
                self.data["word_match"].insert(pos, self.data["word_match"][pos - i])
        if cmd == "pop":
            if pos <= len(self.data["UID"]):
                for key in self.mkeys:
                    self.data[key].pop(pos)
        if cmd == "replace":
            self.data["calc_char"][pos] = val


    def update_stuff_at(self, index_from, index_to, new_value_wm, new_value_cwi):

        self.data["word_match"][index_from:index_to] = [new_value_wm]*(index_to-index_from)
        self.data["calc_word_idx"][index_from:index_to] = [new_value_cwi]*(index_to-index_from)


    def delete_stuff_at(self, index_from, index_to):
        del self.data["word_match"][index_from:index_to]
        del self.data["calc_word_idx"][index_from:index_to]
        del self.data["UID"][index_from:index_to]
        del self.data["calc_char"][index_from:index_to]
        del self.data["char_weight"][index_from:index_to]


    def update_textspace(self, text, wc=None, widx=None):

        # wc = wildcards
        # widx = word index
        # word2text = update text with word elements
        offset = 0
        if widx is not None:
            # if the given wordindex matches existing word_indices wmidxset is not 0
            wmidxset = set(np.where(np.array(list(self.data["word_match"])) == widx)[0].tolist())
            if len(wmidxset) != 0:
                offset = min(set(list(wmidxset)))
            else:
                if max(set(self.data["word_match"])) > widx:
                    nextidx = min(set(self.data["word_match"]).difference(x for x in np.arange(0.0,widx)))
                    pos = min(np.where(np.array(list(self.data["word_match"])) == nextidx)[0])
                    self.data["word_match"] = self.data["word_match"][:pos]+[widx]*len(text)+self.data["word_match"][pos:]
                    self.data["calc_char"] = self.data["calc_char"][:pos] + [wc] * len(text) + self.data["calc_char"][pos:]
                    self.data["UID"] = self.data["UID"][:pos] + [-1] * len(text) + self.data["UID"][pos:]
                    self.data["char_weight"] = self.data["char_weight"][:pos] + [-1] * len(text) + self.data["char_weight"][pos:]
                    cwidx = min(set(self.data["calc_word_idx"]))-1.0
                    if cwidx >= -1.0: cwidx = -2.0
                    self.data["calc_word_idx"] = self.data["calc_word_idx"][:pos] + [cwidx] * len(text) + self.data["calc_word_idx"][pos:]
                else:
                    self.data["word_match"].extend([widx]*len(text))
                    self.data["calc_char"].extend([wc] * len(text))
                    self.data["UID"].extend([-1] * len(text))
                    self.data["char_weight"].extend([-1] * len(text))
                    cwidx = min(set(self.data["calc_word_idx"])) - 1.0
                    if cwidx >= -1.0: cwidx = -2.0
                    self.data["calc_word_idx"].extend([cwidx] * len(text))
                return
        else:
            if text == self.textstr:return

        if wc is not None:
            if wc in text:
                self._update_wildcard(text,wc,offset)
        if widx is not None:
            # create a textarray with new word information and also the existing words
            textarr = []
            for idx in self.word["text"]:
                if widx != idx:
                    textarr.append(self.word["text"][idx])
                else:
                    textarr.append(text)
                    text = ""
            # create a text variable from the newly created array seperated by spaces for each word
            text = " ".join(textarr)+" "+text
            text.strip()
        if text != self.textstr:
            # the new array has different values than the old
            wsarr = np.where(np.array(list(text)) == " ")[0]
            if len(wsarr)>0:
                if max(wsarr) <= len(self.data["calc_word_idx"]):
                    lidx = 0
                    wscount = 0
                    for line, idx in enumerate(np.nditer(wsarr)):
                        if idx != 0:
                            self.data["calc_word_idx"][lidx:idx-wscount] = [line]*(idx-lidx-wscount)
                        lidx = idx-wscount
                        wscount += 1
                    self.data["calc_word_idx"][idx-wscount+1:] = [line+1] * len(self.data["calc_word_idx"][idx-wscount+1:])

    def _update_wildcard(self,text,wc,offset=0):
        #wc = wildcards
        chararr = np.array(list(text))
        try:
            for idx in np.nditer(np.where(chararr == wc)):
                front = False
                if idx == 0:
                    front = True
                    ws = 0
                else:
                    if text[idx-1] == " ": front = True
                    ws = len(np.where(np.array(list(text[:idx+1])) == " ")[0])
                self.text(offset+idx-ws,wc,insertfront=front)
        except Exception as ex:
            print("Wildcard matching exception: ",ex,"\t✗")

    def _update_wordspace(self,text,wc,widx):
        if text == self.textstr: return
        if wc is not None:
            if wc in text:
                self._update_word_wildcard(text, wc)
        if text != self.textstr:
            wsarr = np.where(np.array(list(text)) == " ")[0]
            if len(wsarr) > 0:
                if max(wsarr) <= len(self.data["calc_word_idx"]):
                    lidx = 0
                    for line, idx in enumerate(np.nditer(wsarr)):
                        if idx != 0:
                            self.data["calc_word_idx"][lidx:idx] = [line] * (idx - lidx)
                        lidx = idx

        wmidxarr = np.where(np.array(list(self.data["word_match"])) == widx)[0]
        for wmidx in wmidxarr:
            print(wmidx)
        return

    def _update_word_wildcard(self, text, wc):
        # wc = wildcards
        chararr = np.array(list(text))
        try:
            for idx in np.nditer(np.where(chararr == wc)):
                front = False
                if idx == 0:
                    front = True
                    ws = 0
                else:
                    if text[idx - 1] == " ": front = True
                    ws = len(np.where(np.array(list(text[:idx + 1])) == " ")[0])
                self.text(idx - ws, wc, insertfront=front)
        except Exception:
            print("Cant update text. Seems that the wildcards matching seems wrong.")

    @property
    def textstr(self):
        if "calc_char" in self.data:
            str = ""
            if len(self.data["calc_word_idx"]) > 0:
                lidx = self.data["calc_word_idx"][0]
                for pos,idx in enumerate(self.data["calc_word_idx"]):
                    if idx != lidx:
                        str +=" "
                        lidx = idx
                    str+=self.data["calc_char"][pos]
            return str
        else:
            return "No text to export!"

    @property
    def word(self):
        if "word_match" in self.data:
            wordarr = {'text':{},'UID':{}}
            for idx in set(self.data["word_match"]):
                wordstr = ""
                uidarr = []
                widxarr = np.where(np.array(self.data["word_match"]) == idx)[0]
                last_widx = None
                for widx in widxarr:
                    if last_widx != None and last_widx != self.data["calc_word_idx"][widx]:
                        wordstr += " "
                    wordstr += self.data["calc_char"][widx]
                    last_widx = self.data["calc_word_idx"][widx]
                    uidarr.append(last_widx)
                wordarr['text'][idx] = wordstr
                wordarr['UID'][idx] = uidarr
            return wordarr

    def value(self,attr,pos,val=None,widx=None,wsval=75,):
        if attr in self.data.keys():
            self.ivalue.attr = attr
            self.ivalue.ws = len(np.where(np.array(list(self.textstr[:pos+1])) == " ")[0])
            self.ivalue.wsval = wsval
            self.ivalue.pos = pos-self.ivalue.ws
            if widx != None:
                wmidxset = set(np.where(np.array(list(self.data["word_match"])) == widx)[0].tolist())
                if len(wmidxset) != 0:
                    self.ivalue.pos += list(wmidxset)[0]
                else:
                    self.ivalue.val = None
                    return
            if val is not None:
                self._set_value(val)
            else:
                self._get_value()
            return self.ivalue.val

    def _get_value(self):
        if self.ivalue.pos >= len(self.data["UID"]):
            self.ivalue.val = None
            return
        if self.textstr[self.ivalue.pos+self.ivalue.ws] == " ":
            if self.ivalue.attr == "x_confs":
                self.ivalue.val = self.ivalue.wsval
            elif self.ivalue.attr == "calc_char":
                self.ivalue.val = " "
            else: self.ivalue.val = None
            return self.ivalue.val
        idx = self.data["UID"][self.ivalue.pos]
        if self.ivalue.attr not in self.mkeys and not self.result:
            if idx != -1:
                self.ivalue.val = self.data[self.ivalue.attr][idx]
            else:
                self.ivalue.val = None
        else:
            self.ivalue.val = self.data[self.ivalue.attr][self.ivalue.pos]

    def _set_value(self,val):
        if self.ivalue.attr not in self.idxkeys+["char","UID"] or self.result:
            self.ivalue.val = val
            self.data[self.ivalue.attr][self.ivalue.pos] = val

    def store(self,col=None):
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

    def restore(self):
        df_dict = self.orig_df.to_dict(orient="split")
        self.data = {}
        for kidx, key in enumerate(df_dict["columns"]):
            if key not in self.data:
                self.data[key] = []
            for didx, dataset in enumerate(df_dict["data"]):
                self.data[key].append(df_dict["data"][didx][kidx])
        return

class DFResObj(DFSelObj):
    """
    Derivates from DFSelObj
    Contains zero data from the start.
    It serves to store the result.
    """

    def __init__(self, name, df, idxkeys, imkeys,maxuid, lidx=None):
        DFSelObj.__init__(self,name,df,idxkeys,imkeys)
        self.result = True
        self.empty = False
        self.maxuid = maxuid
        self.lineidx = int(lidx)
        self.wordidx = 0
        self.charidx = 0

    def append(self,lineobj,UID):#
        if UID == -1:
            self.wordidx += 1
            self.charidx = 0
            return
        self.data["ocr"].append(lineobj.name[0])
        self.data["ocr_profile"].append(lineobj.name[1])
        self.data["UID"].append(UID)
        self.data["line_idx"].append(self.lineidx)
        self.data["word_idx"].append(self.wordidx)
        self.data["char_idx"].append(self.charidx)
        for item in ["char","x_confs","x_wconf","line_x0","line_x1","line_y0","line_y1","word_x0","word_x1","word_y0","word_y1"]:
            self.data[item].append(lineobj.data[item][UID])
        self.charidx += 1

    def text(self,pos,val=None,cmd="insert",insertfront=False):
        if cmd == "insert":
            for key in self.data.keys():
                if key == "calc_char":
                    self.data["calc_char"].insert(pos,val)
                if key == "UID":
                    self.data["UID"].insert(pos, -1)
                else:
                    self.data[key].insert(pos,None)
        if cmd == "pop":
            if pos <= len(self.data["UID"]):
                for key in self.data.keys():
                    self.data[key].pop(pos)
        if cmd == "replace":
            self.data["calc_char"][pos] = val

    def update_textspace(self, text, wc=None, widx=None):
        # wc = wildcards
        if widx is not None:
            prevtxt = self.word["text"]
            if self.data["word_match"]==[]:
                self.data["word_match"] = [widx] * len(text)
            else:
                if max(set(self.data["word_match"])) > widx:
                    nextidx = min(set(self.data["word_match"]).difference(x for x in np.arange(0.0,widx)))
                    pos = min(np.where(np.array(list(self.data["word_match"])) == nextidx)[0])
                    arr = [widx] * len(text)
                    self.data["word_match"] = self.data["word_match"][:pos]+arr+self.data["word_match"][pos:]
                else:
                    self.data["word_match"].extend([widx]*len(text))
                textarr = []
                for idx in prevtxt:
                    if widx != idx:
                        textarr.append(prevtxt[idx])
                    else:
                        textarr.append(text)
                        text = ""
                text = "".join(textarr)+text
        self.data["calc_char"] = list(text)
        self.data["UID"] = [-1]*len(text)
        self.data["char_weight"] = [-1] * len(text)
        self.data["calc_word_idx"] = [-1] * len(text)
        if widx is not None:
            self.data["calc_word_idx"] = self.data["word_match"]

    def update_df(self,lineobj,res,col=None):


        self.orig_df.append()
        if col is not None:
            keys = ["UID"]+col
        else:
            keys = self.data.keys()
        dfdict = {}
        for idx, uidx in enumerate(self.data["UID"]):
            if uidx == 1:
                uidx = self.maxuid
                self.maxuid += 1
            for col in keys:
                if col not in dfdict:
                    dfdict[col] = []
                    if col == "UID":
                        dfdict[col].append(uidx)
                    else:
                        dfdict[col].append(self.data[col][idx])
        df = pd.DataFrame.from_dict(dfdict).set_index("UID")
        self.orig_df.reset_index().set_index("UID").update(df)

class DFEmptyObj(DFSelObj):
    """
    Derivates from DFSelObj.
    Contains zero data from the start.
    It serves as a replacement for lines, where no data exists in one or more of the datasets
    """
    def __init__(self, name, df, idxkeys, imkeys,maxuid):
        DFSelObj.__init__(self,name,df,idxkeys,imkeys)
        self.empty = True
        self.maxuid = maxuid

    def update_textspace(self, text, wc=None, widx=None):
        # wc = wildcards
        if widx is not None:
            prevtxt = self.word["text"]
            if self.data["word_match"]==[]:
                self.data["word_match"] = [widx] * len(text)
            else:
                if max(set(self.data["word_match"])) > widx:
                    nextidx = min(set(self.data["word_match"]).difference(x for x in np.arange(0.0,widx)))
                    pos = min(np.where(np.array(list(self.data["word_match"])) == nextidx)[0])
                    arr = [widx] * len(text)
                    self.data["word_match"] = self.data["word_match"][:pos]+arr+self.data["word_match"][pos:]
                else:
                    self.data["word_match"].extend([widx]*len(text))
                textarr = []
                for idx in prevtxt:
                    if widx != idx:
                        textarr.append(prevtxt[idx])
                    else:
                        textarr.append(text)
                        text = ""
                text = "".join(textarr)+text
        self.data["calc_char"] = list(text)
        self.data["UID"] = [-1]*len(text)
        self.data["char_weight"] = [-1] * len(text)
        self.data["calc_word_idx"] = [-1] * len(text)
        if widx is not None:
            self.data["calc_word_idx"] = self.data["word_match"]

class Value(object):
    """
    This servers as data container for get and set value methods in the Sel-,Res- and EmptyObj
    """
    def __init__(self):
        """
        :prop pos: Postion
        :prop attr: Attribut (column name)
        :prop val: Value
        :prop ws:  Whitespace
        :prop wsval: Charconf value of the whitespace
        """
        self.pos = None
        self.attr = None
        self.val = None
        self.ws = 0
        self.wsval = None

