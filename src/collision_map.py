#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   simulation.py: search for interactions between entities in scene
#
#   10/09/2023 - created at
#

import numpy as np

from utils import Point2
from numpy.random import randint

class CollisionMap:
    def reset(self): 
        self.__map = np.full(self.__shape, None)
    
    def __init__(self, dimensions : Point2):
        self.__shape = dimensions.get_shape()
        self.reset()
        
    def is_occupied(self, position : Point2):
        return self.__map[position.get_subscript()] is not None
    
    def within_boundary(self, position):
        return position.x >= 0 and position.y >= 0 and position.x < self.__shape[0] and position.y < self.__shape[1]
    
    def map_entity(self, entity, position=None):
        self.__map[(entity.get_position() if position is None else position).get_subscript()] = entity
    
    def unmap_entity(self, entity):
        self.__map[entity.get_position().get_subscript()] = None
        
    def randpos(self):
        x, y = self.__map.shape
        while True:
            temp = Point2(randint(0, x), randint(0, y))
            if not self.is_occupied(temp):
                break
        return temp
    
    def find_unoccupied_from(self, pos, spaceof):
        res = []
        for step in range(spaceof, -1, -1):
            for i in range(pos.x-step,pos.x+step+1):
                for j in range(pos.y-(spaceof-step),pos.y+(spaceof-step)+1,1 if spaceof == step else (spaceof-step)*2):
                    if self.within_boundary(Point2(i,j)) and self.__map[i, j] is None:
                        res.append(Point2(i,j))
        return res
    
    def find_nearest(self, pos, space):
        res = []
        for step in range(space, -1, -1):
            for i in range(pos.x-step,pos.x+step+1):
                for j in range(pos.y-(space-step),pos.y+(space-step)+1,1 if space == step else (space-step)*2):
                    if self.within_boundary(Point2(i,j)) and self.__map[i, j] is not None and (i != pos.x or j != pos.y):
                        res.append(self.__map[i, j])
        return res
    
    def find_interaction_from(self, entities : dict):
        results = dict()
        while entities:
            buffer = [entities.popitem()[1]]
            while buffer:
                entity = buffer.pop(0)
                neighbors = self.find_nearest(entity.get_position(), 8)
                
                exclude = [] if results.get(entity._uid) is None else results[entity._uid]
                for signal in exclude:
                    signal.emit()
                    neighbors.remove(signal.by)
                
                for neighbor in neighbors:
                    ret = entity.interact(neighbor)
                    if ret is not None:
                        uid, signal = ret
                        if results.get(uid) is None:
                            results[uid] = [signal]
                        else:
                            results[uid].append(signal)
                            
                    if entities.get(neighbor._uid) is not None:        
                        buffer.append(entities.pop(neighbor._uid))