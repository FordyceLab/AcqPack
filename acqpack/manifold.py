from pymodbus.client.sync import ModbusTcpClient

import utils as ut


class Manifold:
    """
    Provides a wrapper for the manifold, which is controlled by the Wago nModbus
    """
    def __init__(self, ip_address, valvemap_path, read_offset=512):
        self.client = ModbusTcpClient(ip_address)
        self.read_offset = read_offset
        self.valvemap = None
        self.load_valvemap(valvemap_path)

    def load_valvemap(self, valvemap_path):
        """
        Stores valvemap.
        To work with open/close, valvemap should have one column named 'valve'.

        :param valvemap_path: (str) path to valvemap
        """
        self.valvemap = ut.read_delim_pd(valvemap_path)

    def read_valve(self, valve_num):
        """
        Reads the state of the register associated with the specified valve.

        :param valve_num: (int) register number to read
        :return: () state of the register (True: depressurized, False: pressurized)
        """
        register_num = valve_num + self.read_offset
        return self.client.read_coils(register_num, 1).bits[0]

    def pressurize(self, valve_num):
        """
        Pressurizes valve at the specified register.

        :param valve_num: (int) valve to pressurize
        """
        state = self.read_valve(valve_num)
        if state:
            self.client.write_coil(valve_num, False)

    def depressurize(self, valve_num):
        """
        Depressurizes valve at the specified register.

        :param valve_num: (int) valve to depressurize
        """
        state = self.read_valve(valve_num)
        if not state:
            self.client.write_coil(valve_num, True)

    def close(self, lookup_cols, lookup_vals):
        """
        Finds lookup_vals in lookup_cols of valvemap; retrieves corresponding valve_num.
        Closes valve_num.

        :param lookup_cols: (str | list) column(s) to search in valvemap
        :param lookup_vals: (val | list) value(s) to find in lookup_cols
        """
        # TODO: default lookup_cols
        valve_num = ut.lookup(self.valvemap, lookup_cols, lookup_vals)[['valve']].iloc[0]
        self.pressurize(valve_num)

    def open(self, lookup_cols, lookup_vals):
        """
        Finds lookup_vals in lookup_cols of valvemap; retrieves corresponding valve_num.
        Opens valve_num.

        :param lookup_cols: (str | list) column(s) to search in valvemap
        :param lookup_vals: (val | list) value(s) to find in lookup_cols
        """
        valve_num = ut.lookup(self.valvemap, lookup_cols, lookup_vals)[['valve']].iloc[0]
        self.depressurize(valve_num)

    def exit(self):
        """
        Closes the device's serial connection.
        """
        self.client.close()
