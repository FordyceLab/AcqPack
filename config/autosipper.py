from utils import lookup, read_delim_pd
import numpy as np

class Autosipper:
    def __init__(self, z, xy):
        self.Z = z    # must be initialized first!
        self.XY = xy
        
        while True:
            fp = raw_input('Type in plate map file:')
            try:
                self.load_platemap(fp)  # load platemap
                break
            except IOError:
                print 'No file', fp

        raw_input('Place dropper above reference (press enter when done)')
        self.XY.cmd_xy('here x y')  # establish current position as 0,0
    
    def load_platemap(self, filepath):
        self.platemap = read_delim_pd(filepath)

    def go_to(self, columns, values):
        x1,y1,z1 = np.array(lookup(self.platemap, columns, values)[['x','y','z']])[0]

        self.Z.home()          # move needle to travel height (blocking)
        self.XY.move_xy(x1,y1) # move stage (blocking)
        self.Z.move(z1)        # move needle to bottom of well (blocking)
        
    def where(self):
        pos_x, pos_y = XY.where_xy()
        pos_z = Z.where()
        return pos_x, pos_y, pos_z
        
    
    def exit(self):
        self.XY.exit()
        self.Z.exit()