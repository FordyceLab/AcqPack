import numpy as np
import pandas as pd

import utils as ut


class FractionCollector:
    """
    A high-level wrapper around an XY stage.
    """
    def __init__(self, xy):
        self.XY = xy

        # TODO: should transforms be a property of the position table?
        self.frames = pd.DataFrame(index=['transform', 'position_table'])
        self.add_frame('hardware')
        # TODO: load in deck transform
        deck_transform = np.array([[-1, 0, 0],
                                   [0, 1, 0],
                                   [0, 0, 0]])
        self.add_frame('deck', deck_transform)
        # TODO: option to add plates here

    def add_frame(self, name, transform=np.eye(3, 2), position_table=None):
        # self.frames.assign(name=[np.eye(4,3),None]) # returns new frame with appended col
        self.frames[name] = None
        self.frames[name].transform = transform
        self.frames[name].position_table = position_table

    # ref_frame gives reference frame; its offset is ignored
    def add_plate(self, name, filepath, ref_frame='deck'):
        # move to bottom of first well, i.e. plate origin (using GUI)

        # store offset (translation)
        offset = self.where()  # hardware_xy - plate_xy (0,0,0)

        # determine transform
        transform = self.frames[ref_frame].copy()
        transform[-1] = offset

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
        self.add_frame(name, transform, position_table)

    def where(self):
        """
        Retrieves current (X,Y) position.

        :return: (tup) current position
        """
        return self.XY.where_xy()

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
        Moves to hardware X,Y

        :param frame: (str) frame that specifies position_list and transform
        :param lookup_columns: (str | list) column(s) to search in position_table
        :param lookup_values: (val | list) values(s) to find in lookup_columns
        """
        transform, position_table = self.frames[frame]

        xy = tuple(ut.lookup(position_table, lookup_columns, lookup_values)[['x', 'y']].iloc[0])
        xyw = xy + (1,)  # concatenate for translation
        xh, yh = np.dot(xyw, transform)  # get hardware coordinates

        self.XY.goto_xy(xh, yh)

    def exit(self):
        """
        Send exit command to XY.
        """
        self.XY.exit()
