#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   utils.py: miscellaneous functions and classes use throughout code base
#
#   10/09/2023 - created at
#

from sys import argv, executable
import subprocess

class Point2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __sub__(self, other):
        if isinstance(other, int):
            return Point2(self.x + other, self.y + other)
        return Point2(self.x - other.x, self.y - other.y)
    
    def __add__(self, other):
        if isinstance(other, int):
            return Point2(self.x + other, self.y + other)
        return Point2(self.x + other.x, self.y + other.y)
        
    def abs(self):
        self.x = abs(self.x)
        self.y = abs(self.y)
        return self
        
    def get_shape(self):
        return (self.x, self.y)
    
    def get_subscript(self):
        return self.x, self.y

def get_args():
    return tuple( 
        [int(x) for x in argv[1:min(4,len(argv))] + [100, 10, 20][len(argv)-1:]] + 
        ([tuple(map(int, argv[4].split('x'))), (argv[5] if len(argv) > 5 else None)] if len(argv) > 4 else []) 
    )

# simple increment id
class __UIDFunctor:
    def __init__(self):
        self.__static_increment = -1
    def __call__(self):
        self.__static_increment += 1
        return self.__static_increment
make_uid = __UIDFunctor()

def check_dependencies():
    try:
        import matplotlib
    except ImportError:
        subprocess.check_call([executable, "-m", "pip", "install", 'matplotlib'])
    
    try:
        import pandas
    except ImportError:
        subprocess.check_call([executable, "-m", "pip", "install", 'pandas'])
        
    try:
        import numpy
    except ImportError:
        subprocess.check_call([executable, "-m", "pip", "install", 'numpy'])
        
    try:
        import plotly
    except ImportError:
        subprocess.check_call([executable, "-m", "pip", "install", 'plotly'])
    
    try:
        import kaleido
    except ImportError:
        subprocess.check_call([executable, "-m", "pip", "install", 'kaleido'])