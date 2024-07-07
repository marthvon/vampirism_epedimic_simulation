#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   ostream.py: configures output stream of scene
#
#   10/09/2023 - created at
#

class OStream:
    def __init__(self, filename=None, scn_id=''):
        self.__filename = filename
        self.__scn_id = scn_id
        self.__file = None
    
    def __del__(self):
        self.close()
    
    def reset(self, step):
        if self.__file is not None:
            self.__file.close()
        if self.__filename is not None:
            self.__file = open(self.__scn_id+"_step_"+str(step)+self.__filename+".txt", 'w')
    
    def close(self):
        if self.__file is not None:
            self.__file.close()

    def log(self, *args):
        print(*args)
        if self.__file is not None:
            sbuf = ''
            for val in args:
                sbuf += val + ' '
            self.__file.write(sbuf[:-1]+'\n')