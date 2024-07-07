#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   events.py: has Events classes and Signal classes
#
#   10/09/2023 - created at
#

import agents

class Signal:
    def __init__(self, by, callback = None):
        self.by = by
        self.result = callback
        
    def emit(self):
        if self.result is not None:
            self.result()
    
class _Events:
    def __init__(self, scn):
        self._scn = scn
        self._buffer = []
        
    def push(self, entity):
        self._buffer.append(entity)
               
class SlainEvent(_Events):
    name = "slain"
    
    def propagate(self):
        for entity in self._buffer:
            self._scn.delete_entity(entity._uid)
        self._buffer = []

class InfectEvent(_Events):
    name = "infect"
    
    def propagate(self):
        for entity in self._buffer:
            if not self._scn.has_entity(entity):
                continue
            position = entity.get_position()
            new_vampire = entity.infection()
            self._scn.delete_entity(entity._uid)
            self._scn.add_entity(new_vampire, position)
        self._buffer = []

class DeathEvent(_Events):
    name = "died"
    
    def propagate(self):
        for entity in self._buffer:
            if not self._scn.has_entity(entity) or entity.is_alive():
               continue
            self._scn.os.log(repr(entity)+", has died")
            self._scn.delete_entity(entity._uid)
        self._buffer = []
                
class ConsumeEvent:
    name = "consume"
    
    def __init__(self, scn):
        self._scn = scn
        self._buffer = dict()
    
    def push(self, entity, other):
        if self._buffer.get(entity._uid) is None:
            self._buffer[entity._uid] = [entity]
        self._buffer[entity._uid].append(other)
        
    def propagate(self):
        while self._buffer:
            uid, entities = self._buffer.popitem()
            entities[0].consumed_by(entities[1:])
            self._scn.delete_entity(uid)
        self._buffer = dict()