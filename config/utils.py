import pandas as pd
import csv

# I: filepath of delimited file
# P: detect delimiter/header read file accordingly
# O: list of records (no header)
def read_delim(filepath):
    f = open(filepath, 'r')
    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    hasHeader = csv.Sniffer().has_header(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    if hasHeader:
        reader.next()

    ret = [line for line in reader]
    return ret

def read_delim_pd(filepath):
    f = open(filepath)
    has_header = None
    if csv.Sniffer().has_header(f.read(1024)):
        has_header = 0
    f.seek(0)
    return pd.read_csv(f, header=has_header, sep=None, engine='python')

def lookup(table, columns, values):
    temp_df = pd.DataFrame(data=[values], columns = columns, copy=False)
    return table.merge(temp_df, copy=False)