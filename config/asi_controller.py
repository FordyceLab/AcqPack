class ASI_Controller:
    def __init__(self, config_file, init=True):
        self.serial = s.Serial() # placeholder
        
        f = open(config_file, 'r')
        self.config = yaml.load(f)
        f.close()
        
        if init:
            self.initialize()

    def initialize(self):
        self.serial = s.Serial(**self.config['serial']) # open serial connection

        self.cmd_xy('mc x+ y+')  # enable motor control for xy
        self.cmd_z('mc z+') # enable motor control for z

        print "Initializing stage..."
        self.move_xy(2000, -2000)  # move to switch limits (bottom right)
        self.r_xy(-0.2, 0.2)  # move from switch limits 0.2 mm


    def cmd(self, cmd_string):
        full_string = self.config['prefix'] + cmd_string + self.config['terminator']
        self.serial.write(full_string)
        time.sleep(0.05)
        response = self.serial.read(self.serial.inWaiting())
        return response
    
    def halt(self):
        self.halt_xy()
        self.halt_z()
    
    
    # XY ----------------------------------------------
    def cmd_xy(self, cmd_string, block=True):
        full_string = '2h ' + cmd_string
        response = self.cmd(full_string)
        
        while block and self.is_busy_xy():
            time.sleep(0.05)
            pass
         
        return response
    
    def is_busy_xy(self):
        status = self.cmd('2h STATUS')[0]
        return status == 'B'

    def halt_xy(self):
        self.cmd_xy('HALT', False)
    
    def where_xy(self):
        response = self.cmd_xy('WHERE X Y')
        if response.find('A'):
            pos_xy = response.split()[1:3]
            pos_x = float(pos_xy[0])
            pos_y = float(pos_xy[1])
            return pos_x, pos_y
        else:
            return None, None 

    def move_xy(self, x_mm, y_mm):
        conv = self.config['conv']
        xStr = 'x=' + str(float(x_mm) * conv)
        yStr = 'y=' + str(float(y_mm) * conv)
        return self.cmd_xy(' '.join(['m', xStr, yStr]))
    
    def r_xy(self, x_mm, y_mm):
        conv = self.config['conv']
        xStr = 'x=' + str(float(x_mm) * conv)
        yStr = 'y=' + str(float(y_mm) * conv)
        return self.cmd_xy(' '.join(['r', xStr, yStr]))

    # Z -----------------------------------------------
    def cmd_z(self, cmd_string, block=True):
        while block and self.is_busy_z():
            time.sleep(0.3)
        full_string = '1h ' + cmd_string
        return self.cmd(full_string)
    
    def is_busy_z(self):
        status = self.cmd('1h STATUS')
        return status[0] == 'B'

    def halt_z(self):
        self.cmd_z('HALT', False)
        
    def where_z(self):
        response = self.cmd_z('WHERE Z')
        if response.find('A'):
            pos_z = float(response.split()[1:2])
            return pos_z
        else:
            return None    
    
    def move_z(self, z_mm):
        conv = self.config['conv']
        zStr = 'z=' + str(float(z_mm) * conv)
        return self.cmd_z(' '.join(['m', zStr]))   
    
    def r_z(self, z_mm):
        conv = self.config['conv']
        zStr = 'z=' + str(float(z_mm) * conv)
        return self.cmd_z(' '.join(['r', zStr]))
    
    def exit(self):
        self.serial.close()