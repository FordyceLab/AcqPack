from utils import *
from pymodbus.client.sync import ModbusTcpClient

class Manifold:
    def __init__(self, ip_address, valvemap_path, read_offset=0):
        self.client = ModbusTcpClient(ip_address)
        self.read_offset = read_offset
        self.load_valvemap(valvemap_path)
           
    def pressurize(self, valve_num):
        """
        Function to pressurize the valve of a given number
        Args:
        - valve_num (int): number of valve to pressurize
        """
        # Read the state of the valve in question
        state = self.read_valve(valve_num)

        # Valve is currently depressurized if the register state is True
        if state:
            self.client.write_coil(valve_num, False)

    def depressurize(self, valve_num):
        """
        Function to depressurize the valve of a given number
        Args:
        - valve_num (int): number of valve to pressurize
        """
        # Read the state of the valve in question
        state = self.read_valve(valve_num)

        # Valve is currently pressurized if the register state is False
        if not state:
            a = self.client.write_coil(valve_num, True)
      
    def read_valve(self, valve_num):
        """
        Function to read a specific register number
        Args:
        - valve_num (int): valve number to read
        Returns:
        - state of the register (True: depressurized, False: pressurized)
        """
        register_num = valve_num + self.read_offset
        return self.client.read_coils(register_num, 1).bits[0]
    
    def load_valvemap(self, valvemap_path):
        self.valvemap = read_delim_pd(valvemap_path)
    
    def exit(self):
        self.client.close()