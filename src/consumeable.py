#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   consumeable.py: all non-living agents of simulation
#
#   10/09/2023 - created at
#

from numpy.random import binomial, randint
import plotly.express as px

from entity import AbstractEntity, InstanceDB
import agents

class CONSUMEABLE_ENUMS:
    Food = ("Food", 30)
    Water = ("Water", 50)
    Garlic = ("Garlic", 100)

class Consumeable(AbstractEntity):
    inst = dict()
    def use_on_scene(scene):
        Consumeable.inst[repr(scene)] = InstanceDB("Consumeable", ['x', 'y', "Type", "Health Gain"])
    
    def generate(parent_scn, position=None, type=None, total=1, pool_rate=(0.445, 0.37, 0.185)):
        if type is not None:
            return {this._uid: this for this in [Consumeable(parent_scn, parent_scn.collision_map.randpos() if position is None else position+i, *type) for i in range(total)]}
        return {this._uid: this for this in [
                Consumeable(parent_scn, 
                    parent_scn.collision_map.randpos() if position is None else position, 
                    CONSUMEABLE_ENUMS.Food
                ) for _ in range(binomial(total, pool_rate[0]))
            ] + \
            [ 
                Consumeable(parent_scn, 
                parent_scn.collision_map.randpos() if position is None else position, 
                CONSUMEABLE_ENUMS.Water
                ) for _ in range(binomial(total, pool_rate[1]))
            ] + \
            [ 
                Consumeable(parent_scn, 
                parent_scn.collision_map.randpos() if position is None else position, 
                CONSUMEABLE_ENUMS.Garlic
                ) for _ in range(binomial(total, pool_rate[2]))
            ]}

    def draw(scn_id):
        return px.scatter(Consumeable.inst[scn_id].df, x='x', y='y', color="Type", color_discrete_map={"Food":"lightgreen", "Water":"lawngreen", "Garlic":"green"}, hover_data={'x':False, 'y':False, "Type":True, "Health Gain":True})
    
    def save(scn_id, filename):
        Consumeable.inst[scn_id].df.to_csv(filename+"_consumeable.csv")
    
    def __init__(self, parent_scn, position, food_type):
        super().__init__(parent_scn)
        try:
            self.get_static_map().push(self._uid, [position.x, position.y, *food_type])
            self._parent_scn.collision_map.map_entity(self, position)
        except KeyError:
            print("Entity of type Consumeable is not binded to Scene of "+str(type(parent_scn))[1:-1]+':'+repr(parent_scn)+"\n\tTry adding Consumeable class to list of '__entity_types' in "+str(type(parent_scn))[1:-1])
    
    def __repr__(self):
        x, y = self.get_position().get_subscript()
        return self.get_type() + ' ' + super().__repr__() + ", in position (" + str(x) + ", " + str(y) + ')'
        
    def get_static_map(self):
        return Consumeable.inst[repr(self._parent_scn)]
    
    def get_hp_gain(self):
        return int(self.get_static_map().df.loc[self._uid, "Health Gain"])
    
    def get_type(self):
        return str(self.get_static_map().df.loc[self._uid, "Type"])
    
    def consumed_by(self, others):
        others[randint(0, len(others))].consuming(self)
    
    def interact(self, other):
        if isinstance(other, agents.Human):
            self._parent_scn._event_handlers["consume"].push(self, other)
        return None