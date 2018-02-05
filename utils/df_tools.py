import pandas as pd
from sqlalchemy import create_engine

def get_con(dbpath):
    con = create_engine(dbpath, echo=True)
    return con

def get_query(tablename, dbpath,index=None, coerce_float=True, params=None, parse_dates=None, chunksize=None):
    # creating and appending database
    index_col = index
    engine = create_engine(dbpath, echo=True)
    # loading the query
    df = pd.read_sql_query(tablename, engine, index_col, coerce_float, params, parse_dates, chunksize)
    return df

def get_table(tablename, dbpath, schema=None, index=None, coerce_float=True, parse_dates=None, columns=None, chunksize=None):
    # creating and appending database
    index_col = index
    engine = create_engine(dbpath, echo=True)
    # loading the table
    df = pd.read_sql_table(tablename, engine, schema, index_col, coerce_float, parse_dates, columns, chunksize)
    return df
