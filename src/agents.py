#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   agents.py: has all living agents of simulation
#
#   10/09/2023 - created at
#

from numpy.random import choice, randint
import plotly.express as px

from entity import AbstractEntity, InstanceDB
from events import Signal

class _Agents(AbstractEntity):
    def __init__(self, parent_scn, movement : int, uid=None):
        super().__init__(parent_scn, uid)
        self.__movement = movement
        
    def moving(self):
        prev_pos = self.get_position()
        new_pos = choice(
            self._parent_scn.collision_map.find_unoccupied_from(
                self.get_position(), self.__movement
            )
        )
        self.set_position(new_pos)
        return new_pos - prev_pos
    
    def process(self):
        self.moving()
        
    def set_hp(self, hp):
        if hp <= 0:
            self._parent_scn._event_handlers["died"].push(self)
        self.get_static_map().df.loc[self._uid, "Health"] = hp
    
    def get_hp(self):
        return int(self.get_static_map().df.loc[self._uid, "Health"])
    
    def is_alive(self):
        return self.get_hp() > 0
    
class Human(_Agents):
    inst = dict()
    def use_on_scene(scene):
        Human.inst[repr(scene)] = InstanceDB("Human", ['x', 'y', "Type", "Health", "Age"])
        
    def generate(parent_scn, position=None, age=None, total=1):
        return {this._uid: this for this in [Human(parent_scn, 
            parent_scn.collision_map.randpos() if position is None else position+i, 
            randint(10, 50) if age is None else age
        ) for i in range(total)]}
    
    def draw(scn_id):
        return px.scatter(Human.inst[scn_id].df, x='x', y='y', color="Type", color_discrete_map={"Human":"blue"}, hover_data={'x':False, 'y':False, "Type":True, "Health":True, "Age":True})
    
    def save(scn_id, filename):
        Human.inst[scn_id].df.to_csv(filename+"_human.csv")
    
    def __init__(self, parent_scn, position, age):
        super().__init__(parent_scn, 4)
        try:
            self.get_static_map().push(self._uid, [position.x, position.y, "Human", 100, age])
            self._parent_scn.collision_map.map_entity(self, position)
        except KeyError:
            raise KeyError("Entity of type Human is not binded to Scene of "+str(type(parent_scn))[1,-1]+':'+repr(parent_scn)+"\n\tTry adding Human class to list of '__entity_types' in "+str(type(parent_scn))[1:-1])
    
    def __repr__(self):
        x, y = self.get_position().get_subscript()
        return "Human " + super().__repr__() + ", in position (" + str(x) + ", " + str(y) + ')'
    
    def get_static_map(self):
        return Human.inst[repr(self._parent_scn)]
    
    def increment_age(self):
        self.get_static_map().df.loc[self._uid, "Age"] += 1
        if self.get_age() > 70:
            self._parent_scn._event_handlers["died"].push(self)
    
    def get_age(self):
        return int(self.get_static_map().df.loc[self._uid, "Age"])
    
    def is_alive(self):
        return super().is_alive() or self.get_age() <= 70
    
    def process(self):
        delta_pos = super().moving().abs()
        self.set_hp(self.get_hp() - (delta_pos.x + delta_pos.y))
        self.increment_age()
        
    def stealing_from(self, other, log=True):
        if log:
            self._parent_scn.os.log(repr(self), "[Health +20], stole from", repr(other), "[Health -20]")
        self.set_hp(self.get_hp() + 20)
        return other._uid, Signal(by=self, callback=lambda: other.robbed_by(self, log=False))
    
    def robbed_by(self, other, log=True):
        if log:
            self._parent_scn.os.log(repr(self), "[Health -20], was robbed by", repr(other), "[Health +20]")
        self.set_hp(self.get_hp() - 20)
        return other._uid, Signal(by=self, callback=lambda: other.stealing_from(self, log=False))
    
    def helping(self, other, log=True):
        if log:
            self._parent_scn.os.log(repr(self), "[Health +10], helped each other with", repr(other), "[Health +10]")
        self.set_hp(self.get_hp() + 10)
        return other._uid, Signal(by=self, callback=lambda: other.helping(self, log=False))
    
    def infected_by(self, other):
        self._parent_scn._event_handlers["infect"].push(self)
        return None
    
    def killing(self, other):
        self._parent_scn.os.log(repr(self)+", has slain", repr(other))
        return other._uid, Signal(by=self, callback=lambda: other.slain_by(self))
    
    def infection(self):
        return Vampire(self._parent_scn, self.get_position(), self.get_hp(), self._uid)
    
    def consuming(self, other):
        heal = other.get_hp_gain()
        self._parent_scn.os.log(repr(self), "[Health +"+str(heal)+"], has consumed", repr(other))
        self.set_hp(self.get_hp() + heal)
    
    def interact(self, other):
        if isinstance(other, Human):
            if randint(0,5) < 2:
                return self.stealing_from(other) if randint(0,2) else self.robbed_by(other)
            else:
                return self.helping(other)
        elif isinstance(other, Vampire):
            return self.killing(other) if randint(0, 10) < 3 else self.infected_by(other)
        return None
        

class Vampire(_Agents):
    inst = dict()
    def use_on_scene(scene):
        Vampire.inst[repr(scene)] = InstanceDB("Vampire", ['x', 'y', "Type", "Health"])
    
    def generate(parent_scn, position=None, hp=100, total=1, uid=None):
        return {this._uid: this for this in [Vampire(parent_scn, 
            parent_scn.collision_map.randpos() if position is None else position+i, 
            hp, uid
        ) for i in range(total)]}
        
    def draw(scn_id):
        return px.scatter(Vampire.inst[scn_id].df, x='x', y='y', color="Type", color_discrete_map={"Vampire":"red"}, hover_data={'x':False, 'y':False, "Type":True, "Health":True})
    
    def save(scn_id, filename):
        Vampire.inst[scn_id].df.to_csv(filename+"_vampire.csv")
    
    def __init__(self, parent_scn, position, hp, uid=None):
        super().__init__(parent_scn, 8, uid)
        try:
            self.get_static_map().push(self._uid, [position.x, position.y, "Vampire", hp])
            self._parent_scn.collision_map.map_entity(self, position)
        except KeyError:
            raise KeyError("Entity of type Vampire is not binded to Scene of "+str(type(parent_scn))[1,-1]+':'+repr(parent_scn)+"\n\tTry adding Vampire class to list of '__entity_types' in "+str(type(parent_scn))[1:-1])
    
    def __repr__(self):
        x, y = self.get_position().get_subscript()
        return "Vampire " + super().__repr__() + ", in position (" + str(x) + ", " + str(y) + ')'
    
    def get_static_map(self):
        return Vampire.inst[repr(self._parent_scn)]
    
    def biting(self, other, log=True):
        if log:
            self._parent_scn.os.log(repr(self), "[Health -20], bit each other", repr(other), "[Health -20]")
        self.set_hp(self.get_hp() - 20)
        return other._uid, Signal(by=self, callback=lambda: other.biting(self, log=False))
    
    def infecting(self, other):
        self._parent_scn.os.log(repr(self)+", infected ", repr(other))
        return other._uid, Signal(by=self, callback=lambda: other.infected_by(self))
    
    def slain_by(self, other):
        self._parent_scn._event_handlers["slain"].push(self)
        return None
    
    def interact(self, other):
        if isinstance(other, Human):
            return self.slain_by(other) if randint(0, 10) < 3 else self.infecting(other)
        elif isinstance(other, Vampire):
            return self.biting(other)
        return None
    