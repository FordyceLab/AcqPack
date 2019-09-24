from __future__ import print_function 
import serial
import argparse
import logging
import time

def remove_crud(string):
    """Return string without useless information.
     Return string with trailing zeros after a decimal place, trailing
     decimal points, and leading and trailing spaces removed.
     """
    if "." in string:
        string = string.rstrip('0')

    string = string.lstrip('0 ')
    string = string.rstrip(' .')

    return string

class Chain(serial.Serial):
    """Create Chain object.
    Harvard syringe pumps are daisy chained together in a 'pump chain'
    off a single serial port. A pump address is set on each pump. You
    must first create a chain to which you then add Pump objects.
    Chain is a subclass of serial.Serial. Chain creates a serial.Serial
    instance with the required parameters, flushes input and output
    buffers (found during testing that this fixes a lot of problems) and
    logs creation of the Chain.
    """
    def __init__(self, port, baud=115200):
        serial.Serial.__init__(self, port=port, baudrate=baud, stopbits=serial.STOPBITS_TWO, parity=serial.PARITY_NONE, timeout=2)
        self.flushOutput()
        self.flushInput()
        logging.info('Chain created on %s',port)

class Pump:
    """Create Pump object for Harvard Pump 11.
    Argument:
        Chain: pump chain
    Optional arguments:
        address: pump address. Default is 0.
        name: used in logging. Default is Pump 11.
    """
    def __init__(self, chain, address=0, name='Pump 11'):
        self.name = name
        self.serial = chain
        self.address = '{0:02.0f}'.format(address)
        self.diameter = None
        self.flowrate = None
        self.targetvolume = None
        self.terminator = '\r'

        """Query model and version number of firmware to check pump is
        OK. Responds with a load of stuff, but the last three characters
        are XXY, where XX is the address and Y is pump status. :, > or <
        when stopped, running forwards, or running backwards. Confirm
        that the address is correct. This acts as a check to see that
        the pump is connected and working."""
        # try:
        resp = self.cmd('POLL off')

        logging.info('%s: created at address %s on %s', self.name,
                      self.address, self.serial.port)

    def __repr__(self):
        string = ''
        for attr in self.__dict__:
            string += '%s: %s\n' % (attr,self.__dict__[attr]) 
        return string

    def write(self, cmd_str, gui_update=True):
        gu=''
        if gui_update:
            gu = ''
        else:
            gu = '@'
        self.serial.write('{}{}{}{}'.format(self.address, gu, cmd_str, self.terminator))

    def read(self):
        return self.serial.read_all()

    def cmd(self, cmd_str, gui_update=False, response_delay=.11):
        self.write(cmd_str, gui_update)
        time.sleep(response_delay)
        return self.read()

    def status():
        pass

    def withdraw(self, ul, ul_per_mn):
        self.cmd('cvolume {} um'.format(ul_per_mn))
        self.cmd('tvolume {} u'.format(ul))
        self.cmd('wrate {} um'.format(ul_per_mn))
        self.cmd('wrun')

    def infuse(self, ul, ul_per_mn):
        self.cmd('cvolume {} um'.format(ul_per_mn))
        self.cmd('tvolume {} u'.format(ul))
        self.cmd('irate {} um'.format(ul_per_mn))
        self.cmd('irun')


    def set_syringe():
        pass

    def setdiameter(self, diameter):
        """Set syringe diameter (millimetres).
        Pump 11 syringe diameter range is 0.1-35 mm. Note that the pump
        ignores precision greater than 2 decimal places. If more d.p.
        are specificed the diameter will be truncated.
        """
        if diameter > 35 or diameter < 0.1:
            raise PumpError('%s: diameter %s mm is out of range' % 
                            (self.name, diameter))

        # TODO: Got to be a better way of doing this with string formatting
        diameter = str(diameter)

        # Pump only considers 2 d.p. - anymore are ignored
        if len(diameter) > 5:
            if diameter[2] is '.': # e.g. 30.2222222
                diameter = diameter[0:5]
            elif diameter[1] is '.': # e.g. 3.222222
                diameter = diameter[0:4]

            diameter = remove_crud(diameter)
            logging.warning('%s: diameter truncated to %s mm', self.name,
                            diameter)
        else:
            diameter = remove_crud(diameter)

        # Send command   
        self.write('DIAMETER' + diameter)
        resp = self.read()

        # Pump replies with address and status (:, < or >)        
        if (resp[-1] == ':' or resp[-1] == '<' or resp[-1] == '>'):
            # check if diameter has been set correctlry
            self.write('DIAMETER')
            resp = self.read()
            returned_diameter = remove_crud(resp[3:9])
            
            # Check diameter was set accurately
            if returned_diameter != diameter:
                logging.error('%s: set diameter (%s mm) does not match diameter'
                              ' returned by pump (%s mm)', self.name, diameter,
                              returned_diameter)
            elif returned_diameter == diameter:
                self.diameter = float(returned_diameter)
                logging.info('%s: diameter set to %s mm', self.name,
                             self.diameter)
        else:
            raise PumpError('%s: unknown response to setdiameter' % self.name)

    def setflowrate(self, flowrate):
        """Set flow rate (microlitres per minute).
        Flow rate is converted to a string. Pump 11 requires it to have
        a maximum field width of 5, e.g. "XXXX." or "X.XXX". Greater
        precision will be truncated.
        The pump will tell you if the specified flow rate is out of
        range. This depends on the syringe diameter. See Pump 11 manual.
        """
        flowrate = str(flowrate)

        if len(flowrate) > 5:
            flowrate = flowrate[0:5]
            flowrate = remove_crud(flowrate)
            logging.warning('%s: flow rate truncated to %s uL/min', self.name, 
                             flowrate)
        else:
            flowrate = remove_crud(flowrate)

        self.write('IRATE' + flowrate)
        resp = self.read()
        
        if (resp[-1] == ':' or resp[-1] == '<' or resp[-1] == '>'):
            # Flow rate was sent, check it was set correctly
            self.write('RAT')
            resp = self.read()
            returned_flowrate = remove_crud(resp[2:8])

            if returned_flowrate != flowrate:
                logging.error('%s: set flowrate (%s uL/min) does not match'
                              'flowrate returned by pump (%s uL/min)',
                              self.name, flowrate, returned_flowrate)
            elif returned_flowrate == flowrate:
                self.flowrate = returned_flowrate
                logging.info('%s: flow rate set to %s uL/min', self.name,
                              self.flowrate)
        elif 'OOR' in resp:
            raise PumpError('%s: flow rate (%s uL/min) is out of range' %
                           (self.name, flowrate))
        else:
            raise PumpError('%s: unknown response' % self.name)
            
    # def infuse(self):
    #     """Start infusing pump."""
    #     self.write('RUN')
    #     resp = self.read()
    #     while resp[-1] != '>':
    #         if resp[-1] == '<': # wrong direction
    #             self.write('REV')
    #         else:
    #             raise PumpError('%s: unknown response to to infuse' % self.name)
    #         resp = self.serial.read()
        
    #     logging.info('%s: infusing',self.name)

    # def withdraw(self):
    #     """Start withdrawing pump."""
    #     self.write('REV')
    #     resp = self.read()
        
    #     while resp[-1] != '<':
    #         if resp[-1] == ':': # pump not running
    #             self.write('RUN')
    #         elif resp[-1] == '>': # wrong direction
    #             self.write('REV')
    #         else:
    #             raise PumpError('%s: unknown response to withdraw' % self.name)
    #             break
    #         resp = self.read()

    #     logging.info('%s: withdrawing',self.name)

    def stop(self):
        """Stop pump."""
        self.cmd('STP')
        logging.info('%s: stopped',self.name)

    def settargetvolume(self, targetvolume):
        """Set the target volume to infuse or withdraw (microlitres)."""
        self.write('MLT' + str(targetvolume))
        resp = self.read()

        # response should be CRLFXX:, CRLFXX>, CRLFXX< where XX is address
        # Pump11 replies with leading zeros, e.g. 03, but PHD2000 misbehaves and 
        # returns without and gives an extra CR. Use int() to deal with
        if resp[-1] == ':' or resp[-1] == '>' or resp[-1] == '<':
            self.targetvolume = float(targetvolume)
            logging.info('%s: target volume set to %s uL', self.name,
                         self.targetvolume)
        else:
            raise PumpError('%s: target volume not set' % self.name)

    def waituntiltarget(self):
        """Wait until the pump has reached its target volume."""
        logging.info('%s: waiting until target reached',self.name)
        # counter - need it to check if it's the first loop
        i = 0
    
        while True:
            # Read once
            self.serial.write(self.address + 'VOL\r')
            resp1 = self.read()

            if ':' in resp1 and i == 0:
                raise PumpError('%s: not infusing/withdrawing - infuse or '
                                'withdraw first', self.name)
            elif ':' in resp1 and i != 0:
                # pump has already come to a halt
                logging.info('%s: target volume reached, stopped',self.name)
                break

            # Read again
            self.serial.write(self.address + 'VOL\r')
            resp2 = self.read()

            # Check if they're the same - if they are, break, otherwise continue
            if resp1 == resp2:
                logging.info('%s: target volume reached, stopped',self.name)
                break

            i = i+1
