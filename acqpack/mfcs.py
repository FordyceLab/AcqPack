import utils as ut

import os
import time
import yaml
from ctypes import *


DLL_FILENAME = 'mfcs_64.dll'  # dll packaged with acqpack (todo: 'package resources')
DLL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DLL_FILENAME)
# TODO: 
# - config file vs chanmap_path
# - which device
# - kwargs/channel default in read, set, pid?
class Mfcs:
    """
    Class to control the MFCS-EZ.
    """
    def __init__(self, config_file, chanmap_path):
        
        with open(config_file) as file:
            self.config = yaml.load(file)
        
        self.config['conversion_to_mbar'] = float(self.config['conversion_to_mbar'])  # ensure conversion factor is float
        self.dll = cdll.LoadLibrary(DLL_PATH)  # load dll (i.e. MFCS API)
        self.c_status = c_char()  # placeholder for status
        self.c_serial = c_ushort(0)  # placeholder for serial number
        
        # self.detect()
        self.connect()
        self.load_chanmap(chanmap_path)

    def __del__(self):
        self.exit()
    
    def detect(self):
        """
        Detects up to 8 connected MFCS devices; returns serial numbers of connected devices.
        
        :return: (list) detected MFCS serial numbers as ints
        """
        c_table = (c_ushort*8)(0,0,0,0,0,0,0,0)
        c_error = self.dll.mfcsez_detect(byref(c_table))
        return [sn for sn in c_table if sn != 0]

    def connect(self):
        """
        Initializes the MFCS.
        Makes connection, checks status, and sets the PID alpha parameter of all channels to 2.
        """
        self.handle = self.dll.mfcsez_initialisation(self.config['serial_number'])
        time.sleep(0.6)  # wait to check serial
        c_error = self.dll.mfcs_get_serial(self.handle, byref(self.c_serial))
        
        if self.c_serial.value == 0:  # serial==0 means no connection
            print('Error: Could not connect to MFCS')
            self.exit()
        else:
            print('MFCS initialized. SN: {}'.format(self.c_serial.value))
            self.pid(0, self.config['alpha_default'])
            print('PID alpha: {}'.format(self.config['alpha_default']))
            print('Pressure units: {}'.format(self.config['pressure_unit']))
            
            s, status = self.status()
            time.sleep(0.1)
            if s != 1:
                print('Warning: Connected to MFCS, but status not normal. Status {}: {}'.format(s, status))
            
    def status(self):
        """
        Gets and returns status of the MFCS.
        0: 'MFCS is reset - press "Play"'
        1: 'normal'
        2: 'overpressure'
        3: 'need to rearm'

        :return: (tup) status int [0-3], status string
        """
        statuses = {0: 'MFCS is reset - press "Play"',
                    1: 'normal',
                    2: 'overpressure',
                    3: 'need to rearm'}
        c_error = self.dll.mfcs_get_status(self.handle, byref(self.c_status))
        k = ord(self.c_status.value)
        return k, statuses[k]
    
    def pid(self, chan, a):
        """
        Sets alpha parameter of the PID controller for the given channel.
        Lower values of alpha (1-2) are typically more stable at lower pressures, but take slightly
        longer to equilibrate. 
        
        For some reason, the python kernel would crash when 'channel' and 'alpha' were used
        as keywords. C-types...

        :param chan: (int) channel [1-4] to set; 0 sets for all channels
        :param a: (int) desired alpha value for PID
        """
        c_error = self.dll.mfcs_set_alpha(self.handle, chan, a)

    def load_chanmap(self, chanmap_path):
        """
        Stores channel map.

        :param chanmap_path: (str) path to chanmap
        """
        self.chanmap = ut.read_delim_pd(chanmap_path)
        
    def exit(self):
        """
        Safely closes the MFCS. 
        First closes device connection, then releases the DLL.
        """
        try:
            c_error = self.dll.mfcs_get_serial(self.handle, byref(self.c_serial))
            if self.dll.mfcs_close(self.handle):  # Close communication port 
                print('Closed connection to device with SN {}'.format(self.c_serial.value))
            else:
                print('Failed to close connection to device with SN {}'.format(self.c_serial.value))
        except IOError:
            print('MFCS connection error: {}'.format(c_error))
        finally:
            windll.kernel32.FreeLibrary(self.dll._handle) # Release the DLL
            del self.dll
            print('MFCS library released')
        
    def set(self, lookup_cols, lookup_vals, pressure=0.0):
        """
        Sets pressure of specified channel.
        
        :param lookup_cols: (str | list) column(s) to search in chanmap
        :param lookup_vals: (val | list) value(s) to find in lookup_cols
        :param pressure: (float) desired pressure; units specified in config file
        """
        channel = ut.lookup(self.chanmap, lookup_cols, lookup_vals)[['channel']].iloc[0]
        channel = int(channel)
        mbar = pressure * self.config['conversion_to_mbar']
        c_error = self.dll.mfcs_set_auto(self.handle, channel, c_float(mbar))

    def read(self, lookup_cols, lookup_vals):
        """
        Reads current pressure of the channel.
        
        :param lookup_cols: (str | list) column(s) to search in chanmap
        :param lookup_vals: (val | list) value(s) to find in lookup_cols
        :return: (float) current pressure; units specified in config file
        """
        pressure = c_float()
        timer = c_ushort()

        channel = ut.lookup(self.chanmap, lookup_cols, lookup_vals)[['channel']].iloc[0]
        channel = int(channel)
        c_error = self.dll.mfcs_read_chan(self.handle, channel, pointer(pressure), pointer(timer))
        
        mbar = pressure.value
        return mbar/self.config['conversion_to_mbar']