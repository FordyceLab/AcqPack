import time

import serial as s
import yaml


class AsiController:
    """
    Low-level wrapper for the Applied Scientific Instrumentation (ASI) Controller.
    Config file must be defined.

    This class can control both an XY-axis (MS-2000 stage) and a Z-axis (LS-50 linear stage).
    Since this hardware was taken from an Illumina GaIIx, it assumes the controller's serial command-set requires an OEM
    prefix of 1h (Z-axis) or 2h (XY-axes). Both stages have a linear-encoder.

    Functions for Z-axis control are defined, but it is not initialized. If it is desired to be used, then a homing
    procedure needs to be defined in initialize().
    """
    def __init__(self, config_file, init=True):
        self.serial = s.Serial()  # placeholder
        
        f = open(config_file, 'r')
        self.config = yaml.load(f)
        f.close()
        
        self.config['conv'] = float(self.config['conv'])

        if init:
            self.initialize()

    def initialize(self):
        """
        1) Open serial connection
        2) Enable XY and Z motor control (one-time command)
        3) Move to XY stage stops (hall-effect)
        4) Move from switch limits 0.2 mm
        5) Zero stage
        """
        self.serial = s.Serial(**self.config['serial'])  # open serial connection

        self.cmd_xy('MC x+ y+')  # enable motor control for xy
        self.cmd_z('MC z+')      # enable motor control for z

        print "Initializing stage..."
        # TODO: should homing / initialization this be responsibility of the autosipper?
        # TODO: Implement zeroing commands?
        self.goto_xy(1000, -1000)  # move to switch limits (bottom right)
        self.move_relative_xy(-0.2, 0.2)  # move from switch limits 0.2 mm
        self.cmd_xy('HERE x y')  # establish current XY position as 0,0 (zero)

    def cmd(self, cmd_string):
        """
        Wraps core cmd_string with terminator specified in config, writes to serial, and returns response.

        :param cmd_string: (str) core command (w/o prefix nor terminator)
        :return: (str) device response
        """
        full_string = self.config['prefix'] + cmd_string + self.config['terminator']
        self.serial.write(full_string)
        time.sleep(0.05)
        response = self.serial.read(self.serial.inWaiting())
        return response
    
    def halt(self):
        """
        Sends halt command to both axes, interrupting execution of their current commands.
        Note that many commands are sent in 'blocking' mode, so this function will likely not be called until the
        axes finish executing their current command.

        In the future, it may be nice to implement a 'waiting' scheme.
        """
        self.halt_xy()
        self.halt_z()

    def exit(self):
        """
        Closes the device's serial connection.
        """
        self.serial.close()
    
    # XY ----------------------------------------------
    def cmd_xy(self, cmd_string, block=True):
        """
        Wraps core cmd_string with axes prefix (2h), passes to the cmd() function, and returns response.
        Optionally blocks programmatic flow (default=True).

        :param cmd_string: (str) core command (w/o prefix nor terminator)
        :param block: (bool) whether the command blocks program flow until action is complete
        :return: (str) device response
        """
        full_string = '2h ' + cmd_string
        response = self.cmd(full_string)
        
        while block and self.is_busy_xy():
            time.sleep(0.05)
            pass
         
        return response

    def is_busy_xy(self):
        """
        Sends status command, then parses response to determine if XY-axes are busy.

        :return: (bool) true if axes are executing a command
        """
        status = self.cmd('2h STATUS')[0]
        return status == 'B'

    def halt_xy(self):
        """
        Sends halt command to the XY-axes (stage), interrupting execution of its current command.
        Note that many commands are sent in 'blocking' mode, so this function will likely not be called until the
        axes finish executing their current command.

        In the future, it may be nice to implement a 'waiting' scheme.
        """
        self.cmd_xy('HALT', False)

    def home_xy(self):
        """
        Moves XY-axes to 0,0.
        """
        return self.goto_xy(0, 0)
    
    def where_xy(self):
        """
        Retrieves XY-axes' current position relative to zero point (w/ linear encoder).

        :return: (tup) current X and Y position [mm]
        """
        conv = self.config['conv']
        response = self.cmd_xy('WHERE X Y')
        if response.find('A'):
            pos_xy = response.split()[1:3]
            pos_x = round(float(pos_xy[0])/conv, 4)
            pos_y = round(float(pos_xy[1])/conv, 4)
            return pos_x, pos_y
        else:
            return None, None

    def goto_xy(self, x_mm, y_mm):
        """
        Moves XY-axes absolutely to the specified position.

        :param x_mm: (float) desired absolute X position [mm]
        :param y_mm: (float) desired absolute Y position [mm]
        :return: (str) device response
        """
        conv = self.config['conv']
        x_str = 'x=' + str(float(x_mm) * conv)
        y_str = 'y=' + str(float(y_mm) * conv)
        return self.cmd_xy(' '.join(['m', x_str, y_str]))
    
    def move_relative_xy(self, x_mm, y_mm):
        """
        Moves XY-axes relatively by the specified number of mm.

        :param x_mm: (float) desired relative movement [mm]
        :param y_mm: (float) desired relative movement [mm]
        :return: (str) device response
        """
        conv = self.config['conv']
        x_str = 'x=' + str(float(x_mm) * conv)
        y_str = 'y=' + str(float(y_mm) * conv)
        return self.cmd_xy(' '.join(['r', x_str, y_str]))

    # Z -----------------------------------------------
    def cmd_z(self, cmd_string, block=True):
        """
        Wraps core cmd_string with axis prefix (1h), passes to the cmd() function, and returns response.
        Optionally blocks programmatic flow (default=True).

        :param cmd_string: (str) core command (w/o prefix nor terminator)
        :param block: (bool) whether the command blocks program flow until action is complete
        :return: (str) device response
        """
        while block and self.is_busy_z():
            time.sleep(0.3)
        full_string = '1h ' + cmd_string
        return self.cmd(full_string)
    
    def is_busy_z(self):
        """
        Sends status command, then parses response to determine if Z-axis is busy.

        :return: (bool) true if axis is executing a command
        """
        status = self.cmd('1h STATUS')
        return status[0] == 'B'

    def halt_z(self):
        """
        Sends halt command to the Z-axis (linear motor), interrupting execution of its current command.
        Note that many commands are sent in 'blocking' mode, so this function will likely not be called until the
        axes finish executing their current command.

        In the future, it may be nice to implement a 'waiting' scheme.
        """
        self.cmd_z('HALT', False)

    def home_z(self):
        """
        Moves Z-axis to 0.
        """
        return self.goto_z(0)
        
    def where_z(self):
        """
        Retrieves Z-axis' current position relative to zero point (w/ linear encoder).

        :return: (tup) current Z position [mm]
        """
        response = self.cmd_z('WHERE Z')
        if response.find('A'):
            pos_z = float(response.split()[1:2])
            return pos_z
        else:
            return None    
    
    def goto_z(self, z_mm):
        """
        Moves Z-axis absolutely to the specified position.

        :param z_mm: (float) desired absolute Z position [mm]
        :return: (str) device response
        """
        conv = self.config['conv']
        z_str = 'z=' + str(float(z_mm) * conv)
        return self.cmd_z(' '.join(['m', z_str]))
    
    def move_relative_z(self, z_mm):
        """
        Moves Z-axis relatively by the specified number of mm.

        :param z_mm: (float) desired relative movement [mm]
        :return: (str) device response
        """
        conv = self.config['conv']
        z_str = 'z=' + str(float(z_mm) * conv)
        return self.cmd_z(' '.join(['r', z_str]))
