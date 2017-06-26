import time

import serial as s
import yaml


# TODO: get current position for relative move
class Motor:
    """
    Low-level wrapper for the Lin Engineering (LE) CO-4118S-09.
    Config file must be defined.

    The LE CO-4118S-09 has an integrated controller with a documented serial command-set. It lacks an encoder, and so
    relies on dead-reckoning for position. It does have an optical sensor that allows it to get a positional fix (home).
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
        2) Set velocity to velocity specified in config file
        3) Home the motor
        """
        self.serial = s.Serial(**self.config['serial'])  # open serial connection

        # TODO set moving current
        # TODO set holding current
        self.set_velocity(self.config['velocity_limit'])  # set velocity
        self.home()  # move motor to home

    def cmd(self, cmd_string, block=True):
        """
        Wraps core cmd_string with prefix and terminator specified in config, writes to serial, and returns response.
        Optionally blocks programmatic flow (default=True).

        :param cmd_string: (str) core command (w/o prefix nor terminator)
        :param block: (bool) whether the command blocks program flow until action is complete
        :return: (str) device response
        """
        full_string = self.config['prefix'] + cmd_string + self.config['terminator']
        self.serial.write(full_string)

        time.sleep(0.15)  # TODO: monitor for response?
        response = self.serial.read(self.serial.inWaiting()).decode('utf8', 'ignore')

        while block and self.is_busy():
            pass

        return response

    def is_busy(self):
        """
        Sends query command, then parses response to determine if motor is busy.

        :return: (bool) true if motor is executing a command
        """
        cmd_string = 'Q'
        time.sleep(0.05)
        response = self.cmd(cmd_string, False)
        return response.rfind('`') == -1

    def set_velocity(self, velocity):
        """
        Checks requested velocity against the velocity limit, then sets motor velocity in usteps/sec.

        :param velocity: (int) velocity
        :return: (str) device response
        """
        if velocity > self.config['velocity_limit']:
            velocity = self.config['velocity_limit']
            print 'ERR: Desired velocity exceeds velocity_limit; velocity now set to velocity_limit'

        cmd_string = 'V{}R'.format(velocity)
        return self.cmd(cmd_string)

    def halt(self):
        """
        Sends halt command to motor, which stops it from executing its current command.
        Note that many commands are sent in 'blocking' mode, so this function will likely not be called until the
        motor finishes executing its current command.

        In the future, it may be nice to implement a 'waiting' scheme.
        """
        cmd_string = 'T'
        self.cmd(cmd_string)

    def home(self):
        """
        Homes the motor until the optical sensor is triggered. Zero position is reset (motor gets positional fix).

        :return: (str) device response
        """
        cmd_string = 'Z{}R'.format(self.config['ustep_max'])
        return self.cmd(cmd_string)

    def goto(self, mm, block=True):
        """
        Moves motor absolutely to the specified position.

        :param mm: (float) desired absolute position [mm]
        :param block: (bool) whether the command blocks program flow until action is complete
        :return: (str) device response
        """
        ustep = int(self.config['conv'] * mm)

        if ustep > self.config['ustep_max']:
            ustep = self.config['ustep_max']
            print 'ERR: Desired move to {} mm exceeds max of {} mm; moving to max instead'.format(mm, self.config[
                'ustep_max'] / self.config['conv'])
        if ustep < self.config['ustep_min']:
            ustep = self.config['ustep_min']
            print 'ERR: Desired move to {} mm exceeds min of {} mm; moving to min instead'.format(mm, self.config[
                'ustep_min'] / self.config['conv'])

        cmd_string = 'A{}R'.format(ustep)

        return self.cmd(cmd_string, block)

    def move_relative(self, mm):
        """
        Moves motor relatively by the specified number of mm.

        :param mm: (float) desired relative movement [mm]
        :return: (str) device response
        """
        ustep = int(self.config['conv'] * mm)
        ustep_current = int(self.config['ustep_max'] / 2)  # TODO: limit movement (+ and -)

        if mm >= 0:
            if (ustep_current + ustep) > self.config['ustep_max']:
                ustep = self.config['ustep_max'] - ustep_current
                print 'ERR: Desired move of +{} mm exceeds max of {} mm; moving to max instead'.format(mm, self.config[
                    'ustep_max'] / self.config['conv'])
            cmd_string = 'P{}R'.format(ustep)

        else:
            if (ustep_current + ustep) < self.config['ustep_min']:
                ustep = self.config['ustep_min'] - ustep_current
                print 'ERR: Desired move of {} mm exceeds min of {} mm; moving to min instead'.format(mm, self.config[
                    'ustep_min'] / self.config['conv'])
            ustep = -1 * ustep
            cmd_string = 'D{}R'.format(ustep)

        return self.cmd(cmd_string)

    def where(self):
        """
        Retrieves motor's current position relative to zero-position (by dead reckoning).

        :return: (tup) current position of the motor [mm]
        """
        cmd_string = '?0'
        response = str(self.cmd(cmd_string))
        strt = response.rfind('`') + 1
        for end, c in enumerate(response[strt:]):
            if c not in str(range(0, 11)):
                break
        ustep = response[strt:strt + end]
        return round(float(ustep) / self.config['conv'], 4),  # tuple

    def exit(self):
        """
        Closes the device's serial connection.
        """
        self.serial.close()
