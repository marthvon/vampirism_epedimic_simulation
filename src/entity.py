#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   entity.py: contains inherited class for all agents
#
#   10/09/2023 - created at
#

from pandas import DataFrame, concat
from utils import make_uid, Point2

class AbstractEntity:
    inst = dict()
    
    def __init__(self, parent_scn, uid=None):
        self._parent_scn = parent_scn
        self._uid = make_uid() if uid is None else uid
    
    def __del__(self):
        self._parent_scn.collision_map.unmap_entity(self)
        self.get_static_map().df.drop(self._uid, inplace=True)
        return self._uid
        
    def __repr__(self):
        return "Entity #" + str(self._uid) 
    
    def get_static_map(self):
        return AbstractEntity.inst[repr(self._parent_scn)]
    
    def set_position(self, position: Point2):
        self._parent_scn.collision_map.unmap_entity(self)
        self.get_static_map().df.loc[self._uid, 'x'] = position.x
        self.get_static_map().df.loc[self._uid, 'y'] = position.y
        self._parent_scn.collision_map.map_entity(self)
        
    def get_position(self):
        ref = self.get_static_map().df.loc[self._uid]
        return Point2(ref['x'], ref['y'])
    
    def process(self):
        pass
    
class InstanceDB:
    def __init__(self, type, attributes):
        self.df = DataFrame()
        self.type = type
        self.__buffer = []
        self.__index = []
        self.__columns = attributes
    
    def push(self, uid, data):
        self.__buffer.append(data)
        self.__index.append(uid)
    
    def flush(self):
        if not self.__buffer and not self.__index:
            return
        self.df = concat([self.df, DataFrame(data=self.__buffer, index=self.__index, columns=self.__columns)])
        self.__buffer = []
        self.__index = []
    
    def count(self):
        return self.df.shape[0]