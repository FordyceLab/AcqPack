import numpy as np
import pandas as pd

import utils as ut


class Autosampler:
    """
    A high-level wrapper that coordinates XY and Z axes to create an autosampler.
    """
    def __init__(self, z, xy):
        self.Z = z  # must be initialized first!!! (avoid collisions)
        self.XY = xy

        # TODO: should transforms be a property of the position table?
        self.frames = pd.DataFrame(index=['transform', 'position_table'])
        self.add_frame('hardware')
        # TODO: load in deck transform
        deck_transform = np.array([[-1, 0, 0],
                                   [0, 1, 0],
                                   [0, 0, -1],
                                   [0, 0, 93]])
        self.add_frame('deck', deck_transform)
        # TODO: option to add plates here

    def add_frame(self, name, transform=np.eye(4, 3), position_table=None):
        # self.frames.assign(name=[np.eye(4,3),None]) # returns new frame with appended col
        self.frames[name] = None
        self.frames[name].transform = transform
        self.frames[name].position_table = position_table

    # ref_frame gives reference frame; its offset is ignored
    def add_plate(self, name, filepath, ref_frame='deck'):
        # move to bottom of first well, i.e. plate origin (using GUI)

        # store offset (translation)
        offset = self.where()  # hardware_xyz - plate_xyz (0,0,0)

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

                # B) go to final well and generate position table
                # move to bottom of last well (using GUI)
                # prompt for num of rows, columns
                # num_rc = raw_input()
                # last_well_h = # move to (x,y,z) + (1,)
                # p1 = (0,0)
                # p2 = np.dot(last_well_h, np.linalg.inv(transform)) # transform to plate coordinates
                # space_rc = ut.spacing(num_rc, p1, p2)
                # position_table = ut.generate_position_table(num_rc, space_rc, z)
                # save??

        # check that all positions in list are within range
        # if are out of range, alert user and remove those entries
        # xmax =
        # ymax =
        # zmax =
        # print 'Given plates transform and , '
        # print 'Remove from position list and continue?'

        # add frame
        self.add_frame(name, transform, position_table)

    def where(self):
        """
        Retrieves current (X,Y,Z) position.

        :return: (tup) current position
        """
        return self.XY.where_xy() + self.Z.where()

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
        transform, position_table = self.frames[frame]

        xyz = tuple(ut.lookup(position_table, lookup_columns, lookup_values)[['x', 'y', 'z']].iloc[0])
        xyzw = xyz + (1,)  # concatenate for translation
        xh, yh, zh = np.dot(xyzw, transform)  # get hardware coordinates

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
