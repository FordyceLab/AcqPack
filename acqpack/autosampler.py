import numpy as np
import pandas as pd

import utils as ut


class Autosampler:
    """
    A high-level wrapper that coordinates XY and Z axes to create an autosampler.
    Incorporates a deck.
    """
    def __init__(self, z, xy):
        # TODO: ditch frames; just have position_tables, each of which stores should transforms be a property of the position table?
        self.frames = pd.DataFrame(index=['trans', 'position_table'])
        self.add_frame('hardware')
    
        self.Z = z  # must be initialized first!!! (avoid collisions)
        self.XY = xy

    def add_frame(self, name, trans=np.eye(4,4), position_table=None):
        """
        Adds coordinate frame. Frame requires affine transform to hardware coordinates; position_table optional. 
        
        :param name: (str) the name to be given to the frame (e.g. hardware)
        :param trans: (np.ndarray <- str) xyzw affine transform matrix; if string, tries to load delimited file
        :param position_table: (None | pd.DataFrame <- str) position_table; if string, tries to load delimited file
        """
        if isinstance(trans, str):
            trans = ut.read_delim_pd(trans).select_dtypes(['number']).as_matrix()
        if isinstance(position_table, str):
            position_table = ut.read_delim_pd(position_table)

        assert(isinstance(trans, np.ndarray)) # trans: numpy array of shape (4,4)
        assert(trans.shape==(4,4))  # check size
        assert(np.array_equal(np.linalg.norm(trans[:-1,:-1]), 
                              np.linalg.norm(np.eye(3,3))))   # Frob norm rotation invariant (no scaling)
        assert(trans[-1,-1] != 0)  # cannot be singular matrix

        # position_table: DataFrame with x,y,z OR None
        if isinstance(position_table, pd.DataFrame):
            assert(set(list('xyz')).issubset(position_table.columns))  # contains 'x','y','z' columns
        else:
            assert(position_table is None)

        self.frames[name] = None
        self.frames[name].trans = trans
        self.frames[name].position_table = position_table

    # ref_frame gives reference frame; its offset is ignored
    def add_plate(self, name, filepath, ref_frame='deck'):
        """
        TODO: UNDER DEVELOPMENT
        """
        # move to bottom of first well, i.e. plate origin (using GUI)

        # store offset (translation)
        offset = self.where()  # hardware_xyz - plate_xyz (0,0,0)

        # determine transform
        trans = self.frames[ref_frame].copy()
        trans[-1] = offset

        # add position_table - either:
        # A) add from file
        while True:
            filepath = raw_input('Enter filepath to plate position_table:')
            try:
                position_table = ut.read_delim_pd(filepath)
                break
            except IOError:
                print 'No file:', filepath

        # add frame
        self.add_frame(name, trans, position_table)

    def where(self, frame=None):
        """
        Retrieves current hardware (x,y,z). If frame is specified, transforms hardware coordinates into
        frame's coordinates.

        :param frame: (str) name of frame to specify transform (optional)
        :return: (tup) current position
        """
        where = self.XY.where_xy() + self.Z.where()
        if frame is not None:
            where += (1,)
            x, y, z, _ = tuple(np.dot(where, np.linalg.inv(self.frames[frame].trans)))
            where = x, y, z
        return where

    def home(self):
        """
        Homes Z axis, then XY axes.
        """
        self.Z.home()
        self.XY.home_xy()

    # TODO: if no columns specified, transform provided XYZ to hardware coordinates.
    # TODO: default frame?
    def goto(self, frame, lookup_columns, lookup_values, zh_travel=0):
        """
        Finds lookup_values in lookup_columns of frame's position_list; retrieves corresponding X,Y,Z.
        Transforms X,Y,Z to hardware X,Y,Z by frame's transform.
        Moves to hardware X,Y,Z, taking into account zh_travel.

        :param frame: (str) frame that specifies position_list and transform
        :param lookup_columns: (str | list) column(s) to search in position_table
        :param lookup_values: (val | list) values(s) to find in lookup_columns
        :param zh_travel: (float) hardware height at which to travel
        """
        trans, position_table = self.frames[frame]

        if lookup_columns=='xyz':
            lookup_values = tuple(lookup_values) + (1,)
            xh, yh, zh, _ = np.dot(lookup_values, trans)
        else:
            xyz = tuple(ut.lookup(position_table, lookup_columns, lookup_values)[['x', 'y', 'z']].iloc[0])
            xyzw = xyz + (1,)  # concatenate for translation
            xh, yh, zh, _ = np.dot(xyzw, trans)  # get hardware coordinates

        if zh_travel:
            self.Z.goto(zh_travel)
        else:
            self.Z.home()

        self.XY.goto_xy(xh, yh)
        self.Z.goto(zh)

    def exit(self):
        """
        Send exit command to XY and Z
        """
        self.XY.exit()
        self.Z.exit()
