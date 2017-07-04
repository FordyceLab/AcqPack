import csv
import json

import numpy as np
import pandas as pd


def read_delim(filepath):
    """
    Reads delimited file (auto-detects delimiter + header). Returns list.

    :param filepath: (str) location of delimited file
    :return: (list) list of records w/o header
    """
    f = open(filepath, 'r')
    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    has_header = csv.Sniffer().has_header(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    if has_header:
        reader.next()

    ret = [line for line in reader]
    return ret


def read_delim_pd(filepath):
    """
    Reads delimited file (auto-detects delimiter + header). Returns pandas DataFrame.

    :param filepath: (str) location of delimited file
    :return: (DataFrame)
    """
    f = open(filepath)
    has_header = None
    if csv.Sniffer().has_header(f.read(1024)):
        has_header = 0
    f.seek(0)
    return pd.read_csv(f, header=has_header, sep=None, engine='python')


def lookup(table, lookup_cols, lookup_vals, output_cols=None, output_recs=None):
    """
    Looks up records where lookup_cols == lookup_vals.
    Optionally returns only specified output_cols and/or specified output_recs.

    :param table: (DataFrame) the pandas DataFrame to use as a lookup table
    :param lookup_cols: (str | list)
    :param lookup_vals: (val | list)
    :param output_cols:
    :param output_recs:
    :return:
    """
    if type(lookup_cols) == str:
        lookup_cols = [lookup_cols]

    lookup_vals = [lookup_vals]
    temp_df = pd.DataFrame(data=lookup_vals, columns=lookup_cols, copy=False)
    output = table.merge(temp_df, copy=False)

    if output_cols is not None:
        if type(output_cols) == str:
            output_cols = [output_cols]
        output = output[output_cols]

    if output_recs is not None:
        output = output.iloc[output_recs]

    return output


def generate_position_table(num_rc, space_rc, z, to_clipboard=False):
    """
    Generates a position table.

    :param num_rc: (tup) number of rows and columns (num_rows, num_cols)
    :param space_rc: (tup) spacing for rows and columns [mm] (spacing_rows, spacing_cols)
    :param z: (float) z value in table [mm]
    :param to_clipboard: (bool) whether to copy the position_table to the OS clipboard
    :return: (DataFrame)
    """
    temp = list()
    headers = ['n', 's', 'r', 'c', 'name', 'x', 'y', 'z']

    for r in range(num_rc[0]):
        for c in range(num_rc[1]):
            n = c + r * num_rc[1]
            s = ((r + 1) % 2) * (c + r * num_rc[1]) + (r % 2) * ((r + 1) * num_rc[1] - (c + 1))
            name = chr(64 + r + 1) + '{:02d}'.format(c + 1)
            x = float(c * space_rc[1])
            y = float(r * space_rc[0])
            z = float(z)
            temp.append([n, s, r, c, name, x, y, z])
    position_table = pd.DataFrame(temp, columns=headers)
    if to_clipboard:
        position_table.to_clipboard(index=False)
    return position_table


def spacing(num_rc, p1, p2):
    r, c = map(float, num_rc)
    return tuple(abs(np.nan_to_num(np.subtract(p2, p1) / (c - 1, r - 1))))


def load_mm_positionlist(filepath):
    """
    Takes a MicroManager position list and converts it to a pandas DataFrame.

    :param filepath: (str)
    :return: (DataFrame) position list with headers = "r, c, name, x, y"
    """
    with open(filepath) as f:
        data = json.load(f)

    df1 = pd.io.json.json_normalize(data, ['POSITIONS']).drop(
        ['DEFAULT_XY_STAGE', 'DEFAULT_Z_STAGE', 'DEVICES', 'PROPERTIES'], 1)
    df1 = df1[['GRID_ROW', 'GRID_COL', 'LABEL']]
    df2 = pd.io.json.json_normalize(data, ['POSITIONS', 'DEVICES']).drop(['DEVICE', 'AXES', 'Z'], 1)
    df = pd.concat([df1, df2], axis=1)

    rename = {'GRID_ROW': 'r',
              'GRID_COL': 'c',
              'LABEL': 'name',
              'X': 'x',
              'Y': 'y'}

    return df.rename(columns=rename)


def generate_grid(c0, c1, l_img, p):
    """
    Based on two points, creates a 2D-acquisition grid similar to what MicroManager would produce.

    :param c0: (arr) first point; numpy 1d array of len 2
    :param c1: (arr) second point; numpy 1d array of len 2
    :param l_img: (float)
    :param p: (float) desired percent overlap
    :return: (DataFrame) position_list in the same format as load_mm_positionlist
    """
    # TODO: does generate_grid subsume generate_position_table?
    # n -> number of stage positions on an axis
    n = 1 + np.ceil(np.abs(c1 - c0) / ((1 - p) * l_img))  # ct,ct
    n = n.astype('int')

    # l_acq = total_movement + l_img
    # l_acq = l_img * (n - n*p + p)  # um,um
    sign = np.sign(c1 - c0)

    # could also use cartesian product (itertools.product OR np.mgrid, stack)
    # https://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
    position_list = pd.DataFrame(columns=['r', 'c', 'name', 'x', 'y'], )
    for j in xrange(n[1]):  # iter y
        y = sign[1] * j * l_img * (1 - p) + c0[1]
        for i in xrange(n[0]) if not (j % 2) else reversed(xrange(n[0])):  # iter x (serp)
            x = sign[0] * i * l_img * (1 - p) + c0[0]

            r = j
            c = i
            name = '1-Pos_{:03}_{:03}'.format(c, r)
            position_list.loc[len(position_list)] = [r, c, name, x, y]

    position_list[['r', 'c']] = position_list[['r', 'c']].astype(int)
    return position_list
