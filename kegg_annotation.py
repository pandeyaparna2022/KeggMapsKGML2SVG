# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 16:47:56 2024

@author: Aparna
"""

from annotation_setting_ap import ANNOTATION_SETTINGS
from pathway_component import PathwayComponent
import os
from download_data import download_rest_data

class KeggAnnotation(PathwayComponent):
    def __init__(self, data,organism):
        super().__init__(data)
        self.org = organism
         
         
       
        
    def __repr__(self):
        return f'<KeggAnnotation: {self.anno_type} - {self.name}>'

      
    def get_description(self, anno_type, anno_name):
        
        """
            Use rest data to get the description of an annotation query.
        
            Args:
                anno_type (str): The first queryName of the annotation.
                anno_name (str): Type of annotation.
        
            Returns:
                str: The description for the given annotation or an empty string if not found.

        """
        data_dict = {}
        

        
        rest_file = ANNOTATION_SETTINGS[anno_type]['rest_file']
        if rest_file == 'org':
            rest_file = self.org
        file_path = f'./rest_data/{rest_file}.txt'
        if not os.path.exists(file_path):
            download_rest_data([rest_file], False)
        
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    data = line.strip().split('\t')
                    if len(data) < 2:
                        key = data[0]
                        value = ""
                    else:
                        if anno_type =='Gene':
                            key = data[0]
                            value = data[3]
                        else:
                            key, value = line.strip().split('\t')
                    
                    data_dict[key] = value
                    

            if anno_name in data_dict:
                result = data_dict[anno_name]
                result = result.replace("'", "")
                result = result.replace("<->", "(1->4)")
                result = result.replace("<=>", "(1->4)")
                return result
            else:
                return ""
        
        except FileNotFoundError:
            return "Undefined"

    #query1 = data_type
    # eg : ['enzyme', 'reaction']
    #query2 = info['name'][index]
    # eg: ['ec:1.3.1.79', 'rn:R00732 rn:R00733 rc:RC00125']

       
    def get_annotation(self,query1: list, query2: list):
        """
        Create annotation and get the description of the annotation.

        :param query1: description of query type 
        :param query: query to be annotated
        :return: description. If none is found, an empty string is returned and a warning is printed.
        """
        dictionary={}
        data_annotations = []
        html_classes = []
        title_descriptions = []

        queries = ['compound','map','enzyme','ortholog','reaction','gene','group','brite','other']
                
        for element in query1:
            assert element in queries

        for index in range(len(query1)):
            data_type = query1[index].lower()     
            
            data_names = query2[index].split()
            for part in data_names:
                parts = part.split(":", 1)
                if len(parts) <2:
                    anno_name=parts[0]
                else:
                    anno_name=parts[1]
                
                if data_type == 'compound' or data_type == 'reaction':
                    if parts[0] == "gl":
                        anno_type = "G"
                    if parts[0] == "dr":
                        anno_type = "D"
                    if parts[0] == "cpd":
                        anno_type = "C"
                    if parts[0] == "DG":
                        anno_type = "DG"
                    if parts[0] == "rn":
                        anno_type = "R"
                    if parts[0] == "rc":
                        anno_type = "RC"
                elif data_type == 'enzyme':
                    anno_type = "EC"
                elif data_type == 'ortholog':
                    anno_type = "K"
                elif data_type == 'brite':
                    anno_type = "BR" 
                elif data_type == 'map':
                    anno_type = "MAP" 
                    anno_name = 'map'+anno_name[-5:]
                elif data_type == 'group':
                    anno_type = "GR"        
                elif data_type == 'other':
                    anno_type = "O"     
                elif data_type == 'gene':
                    anno_type ='Gene'
                
                
                
                html_class = ANNOTATION_SETTINGS[anno_type]['html_class']
                html_classes.append(html_class)
                if anno_type == 'EC':
                    name="EC:"+anno_name
                elif anno_type == 'Gene':
                    name = f"{self.org}:"+ anno_name
                    anno_name = f"{self.org}:"+ anno_name
                else:
                    name=anno_name
                    

                description = self.get_description(anno_type, anno_name)
             
                
                if anno_type == 'EC' or anno_type == "RC" or anno_type == "R":
                    title_info = name 
                elif anno_type == 'MAP' or anno_type == 'BR':
                    title_info = name + ":" + description
                else :
                    title_info = name + " (" + description.split(';')[0].strip() +")"
 
                title_descriptions.append(title_info)
                
                #data_annotations.append(dict(type=anno_type, name=name,description=quote(description)))
                data_annotations.append(dict(type=anno_type, name=name,description=description
                                             ))
       
                
        dictionary.update(dict(title=title_descriptions, visualizatin_class=list(set(html_classes)), 
                                             data_annotation=data_annotations
                                             ))
    
        self.data_annotation = dictionary
     
        return self.data_annotation

#result = KeggAnnotation.get_annotation(['map', 'enzyme','reaction'],['path:ko00362', 'EC:1.3.1.79', 'rn:R00733 rc:RC00125'])          