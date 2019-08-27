import pandas as pd
import IPython.display as disp
import inspect
import types
import time

# TODO:
# - use python built-in logging backend (cross-notebook)?
# - fix signature of wrapper [e.g. f.goto(lookup, blah,...)]
class Log():
    """
    Creates a pandas df for logging function calls.
    The columns of the df are:
    't_in','ts_in','t_out','ts_out','class','fn','in','out'
    
    Provides functions for replacing:
     a) functions [.track_fn(f)]
     b) classes [.track_classes(classes)]
    with wrapped versions that log calls to the df.
    
    Example: ------------------------------
    l = Log()
    
    # create tracked function (1st way)
    @l.track_fn
    def f1(input):
        output = input
        return output
    
    # create tracked function (2nd way)
    def f2(input):
        output = input
        return output
    f2 = l.track_fn(f2)
    
    # replace classes with versions whose
    # functions are all tracked
    l.track_classes([Class1, Class2, ...])
    
    # manually write to log 
    l.write('A note')
    
    # make function calls as normal
    f1('input')
    f2('input')
    Class1.f('input')
    
    # display log
    l.show()
    
    # access log
    l.df
        
    """
    def __init__(self):
        self.df = pd.DataFrame(columns=['t_in', 'ts_in', 't_out', 'ts_out',
                                        'class', 'fn', 'in', 'out'])
        self.write = self.track_fn(self.write)
        self.write('init')
    
    
    def format_time(self, time_s):
        return time.strftime("%Y%m%d_%H:%M:%S", time.localtime(time_s))
    
    
    def show(self, ascending=False, clear_display=False):
        if clear_display:
            disp.clear_output(wait=True)
        disp.display(self.df[['ts_in', 'ts_out',
                             'class', 'fn', 'in', 'out']].sort_index(ascending=ascending)
                     .style
                     .set_properties(subset=['in','out'], **{'text-align': 'left'})
                     .set_table_styles([dict(selector='th', props=[('text-align', 'left')] ) ]))
    
    def write(self, msg):
        pass
    
    def track_fn(self, f):
        def wrapper(*args):
            if f.__class__.__name__ == 'instancemethod':
                cls = f.im_class.__name__
                if cls!='Log':
                    inputs = args[1:]
                else:
                    inputs = args
            else:
                cls = ''
                inputs = args
            #obj = str(args[0])[str(args[0]).find('at ')+3:-1]
            fn = f.__name__
            i = len(self.df)
            
            t = time.time()
            self.df.loc[i, ['t_in','ts_in','class','fn','in']] = [t, self.format_time(t), cls, fn, inputs]
            outputs = f(*args)
            t = time.time()
            self.df.loc[i, ['t_out','ts_out','out']] = [t, self.format_time(t), outputs]
            
            return outputs 
        wrapper.__doc__ = f.__doc__
        return wrapper
    
    def track_classes(self, classes):
        for cls in classes:
            for name, f in inspect.getmembers(cls):
                if isinstance(f, types.UnboundMethodType):
                    setattr(cls, name, self.track_fn(f))
        
l = Log()
l.show()