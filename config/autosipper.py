import utils as ut
import numpy as np
import pandas as pd

class Autosipper:
    def __init__(self, z, xy):
        self.Z = z    # must be initialized first!!! (avoid collisions)
        self.XY = xy

        self.coord_frames = pd.DataFrame(index=['transform','position_table'])
        self.add_coord_frame('hardware')
        # TODO: load in deck transform
        deck_transform = np.array([-1,0,0],
                                [0,1,0],
                                [0,0,-1],
                                [0,0,0])
        self.add_coord_frame('deck', deck_transform)

        # TODO: option to add plates here

        # TODO: determine if this line is necessary
        self.XY.cmd_xy('here x y')  # establish current position as 0,0
    

    def add_coord_frame(self, name, transform=np.eye(4,3), position_table=None):
        # self.coord_frames.assign(name=[np.eye(4,3),None]) # returns new frame with appended col
        self.coord_frames[name] = None
        self.coord_frames[name].transform = transform
        self.coord_frames[name].position_table = position_table


    # ref_frame gives reference coord_frame; its offset is ignored
    def add_plate(self, name, filepath, ref_frame='deck'):
        # move to bottom of first well, i.e. plate origin (using GUI)
        
        # store offset (translation)
        offset = self.where() # hardware_xyz - plate_xyz (0,0,0)

        # determine transform
        transform = self.coord_frames[ref_frame].copy()
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
        # p2 = np.dot(last_well_h, np.linalg.inv(transform)) # tranform to plate coordinates
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

        # add coord_frame
        self.add_coord_frame(name, transform, position_table)

    def where(self):
        return self.XY.where_xy() + self.Z.where()


    def go_to(self, frame, lookup_columns, lookup_values, zh_travel = 0):
        transform, position_table = self.coord_frames['frame']

        # lookup values in columns, return corresponding hardware X, Y, Z
        # if no columns specified, transform provided XYZ to hardware coordinates
        xyz = np.array(ut.lookup(position_table, lookup_coumns, lookup_values)[['x','y','z']])[0]
        xyzw = xyz + (1,) # concatenate for translation
        xh, yh, zh = np.dot(xyzw, transform) # get hardware coordinates

        # move Z to travel height (blocking)
        if zh_travel:
            self.Z.move(zh_travel)
        else:
            self.Z.home()

        self.XY.move(xh, yh) # make XY movement (blocking)
        self.Z.move(zh)      # make Z movement (blocking)
    

    def exit(self):
        self.XY.exit()
        self.Z.exit()
