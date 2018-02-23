import pandas as pd
from sqlalchemy import create_engine
from itertools import cycle

def get_con(dbpath, echo=False):
    con = create_engine(dbpath, echo=echo)
    return con

def get_query(tablename, dbpath,index=None, coerce_float=True, params=None, parse_dates=None, chunksize=None, echo=False):
    # creating and appending database
    index_col = index
    engine = create_engine(dbpath, echo=echo)
    # loading the query
    df = pd.read_sql_query(tablename, engine, index_col, coerce_float, params, parse_dates, chunksize)
    return df

def get_table(tablename, dbpath, schema=None, index=None, coerce_float=True, parse_dates=None, columns=None, chunksize=None, echo=False):
    # creating and appending database
    index_col = index
    engine = create_engine(dbpath, echo=echo)
    # loading the table
    df = pd.read_sql_table(tablename, engine, schema, index_col, coerce_float, parse_dates, columns, chunksize)
    return df

def spinner():
    # Contains unicode snippets to create a spinner animation for loading processess
    spinner = cycle([u'⣾',u'⣷',u'⣯',u'⣟',u'⡿', u'⢿',u'⣻', u'⣽'])
    return spinner
