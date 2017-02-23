# written by Scott Longwell
# TODO: Fix serial.read encoding
import serial as s
import yaml
import csv
import time


class Instrument:
    def __init__(self, configFile, init=True):
        f = open(configFile, 'r')
        self.config = yaml.load(f)
        self.serial = s.Serial() # placeholder
        self.plateMap = None

        if init:
            self.initialize()


    def initialize(self):
        self.serial = s.Serial(**self.config['serial']) # open serial connection

        self.cmd_xy('mc x+ y+')  # enable motor control for xy
        # self.cmd_z('mc z+') # enable motor control for z

        print "Initializing stage..."
        self.m_xy(2000, -2000)  # move to switch limits (bottom right)
        self.r_xy(-0.5, 0.5)  # move from switch limits 0.5 mm

        while True:
            fp = raw_input('Type in plate map file:')
            try:
                self.loadPlateMap(fp)  # load platemap
                break
            except IOError:
                print 'No file', fp

        raw_input('Place dropper above well A1 (press enter when done)')
        self.cmd_xy('here x y')  # establish current position as 0,0

    def isBusy_xy(self):
        status = self.cmd('2h STATUS')[0]
        return status == 'B'

    def isBusy_z(self):
        status = self.cmd('1h STATUS')[0]
        return status == 'B'

    def halt(self):
        self.halt_xy()
        self.halt_z()

    def halt_xy(self):
        self.cmd_xy('HALT', False)

    def halt_z(self):
        self.cmd_z('HALT', False)

    def cmd(self, inStr):
        inStr = inStr + self.config['terminator']
        self.serial.write(inStr)
        repr(inStr)
        time.sleep(0.05)
        inBytes = self.serial.inWaiting()
        ret = self.serial.read(inBytes)
        return ret

    def cmd_xy(self, inStr, wait=True):
        while self.isBusy_xy() and wait:
            time.sleep(0.3)
        inStr = '2h ' + inStr
        return self.cmd(inStr)

    def cmd_z(self, inStr, wait=True):
        while self.isBusy_z() and wait:
            time.sleep(0.3)
        inStr = '1h ' + inStr
        return self.cmd(inStr)

    def r_xy(self, x_mm, y_mm):
        conv = self.config['conv']
        xStr = 'x=' + str(float(x_mm) * conv)
        yStr = 'y=' + str(float(y_mm) * conv)
        return self.cmd_xy(' '.join(['r', xStr, yStr]))

    def r_z(self, z_mm):
        conv = self.config['conv']
        zStr = 'z=' + str(float(z_mm) * conv)
        return self.cmd_z(' '.join(['r', zStr]))

    def m_xy(self, x_mm, y_mm):
        conv = self.config['conv']
        xStr = 'x=' + str(float(x_mm) * conv)
        yStr = 'y=' + str(float(y_mm) * conv)
        return self.cmd_xy(' '.join(['m', xStr, yStr]))

    def m_z(self, z_mm):
        conv = self.config['conv']
        zStr = 'z=' + str(float(z_mm) * conv)
        return self.cmd_z(' '.join(['m', zStr]))

    def loadPlateMap(self, filepath):
        self.plateMap = delimRead(filepath)

    def goToWell(self, tubeNum=0):
        if tubeNum > len(self.plateMap):
            print tubeNum, "out of range: there are ", len(self.plateMap), "plate wells. "
        else:
            xPos = self.plateMap[tubeNum][0]
            yPos = self.plateMap[tubeNum][1]

            self.m_xy(xPos, yPos)

    def exit(self):
        self.serial.close()


# I: filepath of delimited file
# P: detect delimiter/header read file accordingly
# O: list of records (no header)
def delimRead(filepath):
    f = open(filepath, 'r')
    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    hasHeader = csv.Sniffer().has_header(f.read(1024))
    f.seek(0)
    reader = csv.reader(f, dialect)

    if hasHeader:
        reader.next()

    ret = [line for line in reader]
    return ret
