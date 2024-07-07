#
#   Author: Mamert Vonn G. Santelices
#   ID:     90026174
#
#   canvas.py: buffer that draws on scene per frame/step
#
#   10/09/2023 - created at
#

import plotly.graph_objects as go
import matplotlib.pyplot as plt

class Canvas:
    def __init__(self, scn_id, entity_types, is_save=True, is_show=False):
        self.__entity_types = entity_types
        self.__scn_id = scn_id
        self.__is_save = is_save
        self.__is_show = is_show
        self.__data = {entity_type.inst[scn_id].type: [] for entity_type in entity_types}
    
    def draw(self, step):
        filename = self.__scn_id + "_step" + str(step)
        figs = []
        for entity_type in self.__entity_types:
            figs.append(entity_type.draw(self.__scn_id))
            inst = entity_type.inst[self.__scn_id]
            self.__data[inst.type].append(inst.df["Type"].count())
            if self.__is_save:
                entity_type.save(self.__scn_id, filename)
                
        data = figs[0].data
        for fig in figs[1:]:
            data += fig.data
        plot = go.Figure(data=data)
        
        if self.__is_save:
            plot.write_image(file=filename+"_plot.png")
            plot.write_html(file=filename+"_plot_interactive.html")
        if self.__is_show:
            plot.show()
            
    def final(self):
        colors = ["blue", "red", "green"]
        for key, val in self.__data.items():
            plt.plot(range(len(val)), val, label=key, color=colors.pop(0))
        plt.legend()
        if self.__is_save:
            plt.savefig(self.__scn_id+"_population_overtime.png")
        if self.__is_show:
            plt.show()
            