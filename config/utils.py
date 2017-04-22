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

# I:
    # num_rc: (ct, ct) <tuple>
    # space_rc: (mm, mm) <tuple>
# O: 
    # position_table <pandas dataframe>
def generate_position_table(num_rc, space_rc, z, to_clipboard=False):
    temp = list()
    headers = ['n','s','r','c','name','x','y','z']
    
    for r in range(num_rc[0]):
        for c in range(num_rc[1]):
            n = c + (r)*num_rc[1]
            s = ((r+1)%2)*(c + r*num_rc[1]) + (r%2)*((r+1)*num_rc[1] - (c+1))
            name = chr(64+r+1) + '{:02d}'.format(c+1)
            x = float(c*space_rc[1])
            y = float(r*space_rc[0])
            z = float(z)
            temp.append([n, s, r, c, name, x, y, z])
    position_table = pd.DataFrame(temp, columns=headers)
    if to_clipboard:
        position_table.to_clipboard(index=False)
    return position_table

def spacing(num_rc,p1,p2):
    r,c =map(float,num_rc)
    return tuple(abs(np.nan_to_num(np.subtract(p2,p1)/(c-1,r-1))))

