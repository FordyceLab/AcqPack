import numpy as np
import pandas as pd

import utils as ut


class FractionCollector:
    """
    A high-level wrapper around an XY stage.
    """
    def __init__(self, xy):
        self.frames = pd.DataFrame(index=['trans', 'position_table'])
        self.add_frame('hardware')
    
        self.XY = xy

    def add_frame(self, name, trans=np.eye(3,3), position_table=None):
        """
        Adds coordinate frame. Frame requires affine transform to hardware coordinates; position_table optional. 
        
        :param name: (str) the name to be given to the frame (e.g. hardware)
        :param trans: (np.ndarray <- str) xyw affine transform matrix; if string, tries to load delimited file
        :param position_table: (None | pd.DataFrame <- str) position_table; if string, tries to load delimited file
        """
        if isinstance(trans, str):
            trans = ut.read_delim_pd(trans).select_dtypes(['number']).as_matrix()
        if isinstance(position_table, str):
            position_table = ut.read_delim_pd(position_table)

        assert(isinstance(trans, np.ndarray)) # trans: numpy array of shape (3,3)
        assert(trans.shape==(3,3))  # check size
        assert(np.array_equal(np.linalg.norm(trans[:-1,:-1]), 
                              np.linalg.norm(np.eye(2,2))))   # Frob norm rotation invariant (no scaling)
        assert(trans[-1,-1] != 0)  # cannot be singular matrix

        # position_table: DataFrame with x,y OR None
        if isinstance(position_table, pd.DataFrame):
            assert(set(list('xy')).issubset(position_table.columns))  # contains 'x','y' columns
        else:
            assert(position_table is None)
        
        self.frames[name] = None
        self.frames[name].trans = trans
        self.frames[name].position_table = position_table

    def where(self, frame=None):
        """
        Retrieves current hardware (x,y). If frame is specified, transforms hardware coordinates into
        frame's coordinates.

        :param frame: (str) name of frame to specify transform (optional)
        :return: (tup) current position
        """
        where = self.XY.where_xy()
        if frame is not None:
            where += (1,)
            x, y, _ = tuple(np.dot(where, np.linalg.inv(self.frames[frame].trans)))
            where = x, y
        return where

    def home(self):
        """
        Homes XY axes.
        """
        self.XY.home_xy()

    # TODO: if no columns specified, transform provided XY to hardware coordinates.
    # TODO: default frame?
    def goto(self, frame, lookup_columns, lookup_values):
        """
        Finds lookup_values in lookup_columns of frame's position_list; retrieves corresponding X,Y
        Transforms X,Y to hardware X,Y by frame's transform.
        Moves to hardware X,Y.

        :param frame: (str) frame that specifies position_list and transform
        :param lookup_columns: (str | list) column(s) to search in position_table
        :param lookup_values: (val | list) values(s) to find in lookup_columns
        """
        trans, position_table = self.frames[frame]

        if lookup_columns=='xy':
            lookup_values = tuple(lookup_values) + (1,)
            xh, yh = np.dot(lookup_values, trans)
        else:
            xy = tuple(ut.lookup(position_table, lookup_columns, lookup_values)[['x', 'y']].iloc[0])
            xyw = xy + (1,)  # concatenate for translation
            xh, yh, _ = np.dot(xyw, trans)  # get hardware coordinates

        self.XY.goto_xy(xh, yh)

    def exit(self):
        """
        Send exit command to XY.
        """
        self.XY.exit()
