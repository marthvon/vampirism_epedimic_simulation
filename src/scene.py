#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   scene.py: creates environment for program
#
#   10/09/2023 - created at
#

import numpy as np

from utils import Point2
from agents import Human, Vampire
from consumeable import Consumeable
from events import DeathEvent, SlainEvent, InfectEvent, ConsumeEvent
from collision_map import CollisionMap
from canvas import Canvas
from ostream import OStream

class Scene:
    _entity_types = [Human, Vampire, Consumeable]
    _event_types = [ConsumeEvent, DeathEvent, InfectEvent, SlainEvent]
    
    def __init__(self, humans_count=100, vampires_count=10, total_timesteps=20, dimensions=(256,256), seed=None):
        if seed is None:
            file = open("seed.txt", 'w')
            file.write(str(np.random.get_state()))
        else:
            file = open("seed.txt", 'r')
            istrm = file.read().split('(')[1:]
            args = [istrm[0].split(',')[0].strip["'"], None] 
            istrm = istrm[1].split(')')
            args += (lambda vals: [int(x) for x in vals[:-1]] + [float(vals[-1])])(istrm[1].split(',')[1:])
            istrm = istrm[0][1:].split(']')
            args[1] = np.array([int(x.strip()) for x in istrm[0].split(',')], dtype=istrm[1].split('=')[1])
            np.random.set_state(*tuple(args))
        
        for entity_type in self._entity_types:
            entity_type.use_on_scene(self)
        self.__entities = {}
            
        self._event_handlers = {event_type.name: event_type(self) for event_type in self._event_types}
            
        self.dimensions = Point2(*dimensions)
        self.collision_map = CollisionMap(self.dimensions)
        self._canvas = Canvas(repr(self), self._entity_types)
        self.os = OStream("log", repr(self))
        self.__timesteps = range(1, total_timesteps+1)
        
        self._ready(humans_count, vampires_count)
        
        for entity_type in self._entity_types:
            entity_type.inst[repr(self)].flush()
        
        for entity in self.__entities.values():
            self.collision_map.map_entity(entity)
        
    def __repr__(self):
        return super().__repr__()[-13:-1]
        
    def delete_entity(self, uid):
        if self.__entities.get(uid) is None:
            return
        self.collision_map.unmap_entity(self.__entities[uid])
        del self.__entities[uid]
    
    def add_entity(self, entity, position=None):
        if self.__entities.get(entity._uid) is not None:
            raise KeyError("Inserting Entity with the simillar UID to existing Entity within Scene.\n\tShared UID value "+\
                str(entity._uid)+"\n\tentity type: "+repr(entity)+"\n\tExisting entity type: "+repr(self.__entities.get(entity._uid)))
        self.__entities[entity._uid] = entity
        self.collision_map.map_entity(entity, position)
        
    def has_entity(self, entity):
        return self.__entities.get(entity._uid) is entity
    
    def _ready(self, *args, **kwargs):
        humans_count, vampires_count = args if len(args) == 2 else (kwargs['humans_count'], kwargs['vampires_count'])
        self.__entities = {**Human.generate(self, total=humans_count),
            **Vampire.generate(self, total=vampires_count),
            **Consumeable.generate(self, total=humans_count)}
    
    def start(self):
        self._canvas.draw(0)
        for step in self.__timesteps:
            self.os.reset(step)
            
            for entity in self.__entities.values():
                entity.process()
                
            self.collision_map.find_interaction_from(self.__entities.copy())
            
            for event_handler in self._event_handlers.values():
                event_handler.propagate()
            
            for entity_type in self._entity_types:
                entity_type.inst[repr(self)].flush()
            
            self._canvas.draw(step)
            
        self.os.close()
        self._canvas.final()