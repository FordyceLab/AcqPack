import serial as s
import time
import yaml

# TODO: get current position for relative move
class Motor:
    def __init__(self, config_file, init=True):
        self.serial = s.Serial() # placeholder

        f = open(config_file, 'r')
        self.config = yaml.load(f)
        f.close()
        
        if init:
            self.initialize()

    def initialize(self):
        self.serial = s.Serial(**self.config['serial']) # open serial connection
        
        # TODO set moving current
        # TODO set holding current
        self.set_velocity(self.config['velocity_limit'])  # set velocity
        self.home() # move motor to home
        
    def cmd(self, cmd_string, block=True):
        full_string = self.config['prefix'] + cmd_string + self.config['terminator']
        self.serial.write(full_string)
        
        time.sleep(0.15) # TODO: monitor for response?
        response = self.serial.read(self.serial.inWaiting()).decode('utf8', 'ignore')
        
        while block and self.is_busy():
            pass
           
        return response
    
    def is_busy(self):
        cmd_string = 'Q'
        time.sleep(0.05)
        response = self.cmd(cmd_string, False)
        return response.rfind('`') == -1
    
    
    # velocity: (usteps/sec) 
    def set_velocity(self, velocity):
        if velocity > self.config['velocity_limit']:
            velocity = self.config['velocity_limit']
            print 'ERR: Desired velocity exceeds velocity_limit; velocity now set to velocity_limit'
            
        cmd_string = 'V{}R'.format(velocity)
        return self.cmd(cmd_string)
       
    def halt(self):
        cmd_string = 'T'
        self.cmd(cmd_string)
    
    def home(self):
        cmd_string = 'Z{}R'.format(self.config['ustep_max'])
        return self.cmd(cmd_string)
    
    def move(self, mm, block=True):
        ustep = int(self.config['conv']*mm)
        if ustep > self.config['ustep_max']:
            ustep = self.config['ustep_max']
            print 'ERR: Desired move to {} mm exceeds max of {} mm; moving to max instead'.format(mm, self.config['ustep_max']/self.config['conv'])
        if ustep < self.config['ustep_min']:
            ustep = self.config['ustep_min']
            print 'ERR: Desired move to {} mm exceeds min of {} mm; moving to min instead'.format(mm, self.config['ustep_min']/self.config['conv'])
            
        cmd_string = 'A{}R'.format(ustep)
        
        return self.cmd(cmd_string, block)
        
    def move_relative(self, mm):
        ustep = int(self.config['conv']*mm)
        ustep_current = int(self.config['ustep_max']/2)  # TODO: limit movement (+ and -)
        
        if mm >= 0:
            if (ustep_current + ustep) > self.config['ustep_max']:
                ustep = self.config['ustep_max'] - ustep_current
                print 'ERR: Desired move of +{} mm exceeds max of {} mm; moving to max instead'.format(mm, self.config['ustep_max']/self.config['conv'])
            cmd_string = 'P{}R'.format(ustep)
        
        else:
            if (ustep_current + ustep) < self.config['ustep_min']:
                ustep = self.config['ustep_min'] - ustep_current
                print 'ERR: Desired move of {} mm exceeds min of {} mm; moving to min instead'.format(mm, self.config['ustep_min']/self.config['conv'])
            ustep = -1*ustep
            cmd_string = 'D{}R'.format(ustep)
        
        return self.cmd(cmd_string)
    
    def where(self):
        cmd_string = '?0'
        ustep = self.cmd(cmd_string)
        retrun float(ustep)/self.config['conv']
    
    def exit(self):
        self.serial.close()