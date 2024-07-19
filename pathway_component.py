# -*- coding: utf-8 -*-
"""
Created on Thu May 30 16:41:56 2024

@author: aparn
"""

from geometry import Geometry
#from shape_annotation import ShapeAnnotation

class PathwayComponent:
   
    def __init__(self, entry:dict):
              
        self.entry = entry
        self.pathway_component_id = entry['id']        
        self.__pc_entry_shape_object = Geometry.geometry_info(entry)
        self.pathway_component_geometry =  self.__pc_entry_shape_object.geometry_coords
        self.pathway_component_geometry_shape = self.__pc_entry_shape_object.geometry_shape

    
    def retrive_pathway_annotation_data(self):
        entry_name = self.entry['name']
        entry_type =  self.entry['type']
        
        if "map" in entry_type[0]:   
            name = entry_name[0]               
            entry_name = ["map"+name[-5:]]
        
        self.pathway_annotation_data =  [{'name' : entry_name[0],'type':entry_type[0]}]
        
            
    
    def is_equivalent(self, existing_pcs):

        entry_id = self.pathway_component_id
        if entry_id in existing_pcs and  existing_pcs[entry_id].pathway_component_geometry == self.pathway_component_geometry:
            return {entry_id: existing_pcs[entry_id]}
        else:
            return None
        
    
    def merge_pathway_components(self, equivalent_pathway_component):
        entry_id = self.pathway_component_id
        existing_data_annotations = equivalent_pathway_component[entry_id].pathway_annotation_data

        anotation_exists = False
        for data in existing_data_annotations:
        
            if data["name"] == self.pathway_annotation_data[0]['name']:
                anotation_exists = True
                break

        if not anotation_exists:
            existing_data_annotations.append(self.pathway_annotation_data[0])
            equivalent_pathway_component[entry_id].pathway_annotation_data = existing_data_annotations
        

        return equivalent_pathway_component

    
    
    

            
            
            
        


    