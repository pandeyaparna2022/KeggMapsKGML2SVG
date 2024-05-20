# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:46:15 2024

@author: Aparna
"""

import xml.etree.ElementTree as ET

import datetime
import time

import os
from preprocess_pathway_data import extract_png_info, xml_path_from_map_id,merge_json
from download_data import download_kgml,download_base_png_maps
#from svg_content_element_tree import SvgContent
from svg_content import create_svg_content
#from color_functions import add_linear_gradient_to_svg, color_all,color_custom_annotations


PROG_NAME = 'json2svg'
PROG_VER  = '01'
RUN_TIME  = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

# Set the main directry to work with
DATA_DIR = 'C:\\Users\\aparn\\Desktop\\masters_thesis\\Kegg_maps_aparna'
#print(DATA_DIR)

# move to the working directory
os.chdir(DATA_DIR)



class KEGGPathway:

    def __init__(self, map_id, fun=None, variables=None, reload=False, verbose = True):
        """
        Initialize a new instance of XML data to be converted to sgv
        Args:
            None
        Attributes:
           _root (None): The root element of the XML data.
           svg_content (str): The content of the SVG file.
           _json_data (None): The JSON data extracted from the XML.
           _org (None): The organism associated with the XML data.
           _pathway_id (None): The pathway ID of the XML data.
           _title (None): The title of the pathway.
           _data_dict (dict): A dictionary to store the converted data.        
        """
        
        self._kgml_data = None
        self._org =None
        self._pathway_id =None
        self._title = None      
        self._image = None
        self._height = None 
        self._width = None 
        self.organism =None
        self._map_id = map_id
        self._reload = reload
        self._verbose = verbose
        self._fun = fun
        self._variables = variables
        

    @property
    def kgml_data(self):
        if self._kgml_data is None:  # Check if json_data has been computed
            return "None"
        else:
            # returns the value of the _json_data
            return self._kgml_data

    @property
    def pathway_info(self):
        """
        This property method prints the pathway information, including the map, pathway ID, and title.
        """
        
        return  f"Map: {self._org}, Pathway: {self._pathway_id}, Title: {self._title}"
    
    @property
    def shape_info(self):
        """
        This property method prints the shape information for all shapes in the pathway map.
        """
        if self._shape_info is None:  # Check if json_data has been computed
            return "None"
        else:           
            # returns the value of the _json_data
            return self._shape_info
        
    def create_svg_map(self, color_function = None, *args):
        ko_path, ec_path, rn_path, org_path = xml_path_from_map_id(self._map_id)
              
        if not os.path.exists(ko_path) or not os.path.exists(ec_path) or not os.path.exists(rn_path):
            download_kgml([self._map_id], self._reload)
            
            download_base_png_maps([self._map_id], self._reload)
        if org_path is not None and not os.path.exists(org_path):
            
            download_kgml([self._map_id], self._reload)
        
        self._kgml_data, self._org, self._pathway_id, self._title, self.organism = merge_json(ko_path, ec_path, rn_path, org_path)
            
        self._height, self._width, self._image  = extract_png_info(self._pathway_id)

        svg_pathway_object,data = create_svg_content(self._kgml_data,self.organism,self._pathway_id, self._width, self._height,self._image,color_function, *args)
        
        
       
        # Create directory for SVG outputs
        OUT_DIR= f'{DATA_DIR}/SVG_output'
        os.makedirs(OUT_DIR, exist_ok=True)

        
        file_path = os.path.join(OUT_DIR, f"{self._org}{self._pathway_id}.svg")
        
        with open(file_path, 'wb') as file:
            file.write(b'\n')
            file.write(b'\n')
            file.write(ET.tostring(svg_pathway_object))
        
        
            
         


 #################################################################################################           
   
  
############################################################################################   
xml_file="hsa400.xml"
        
ap=KEGGPathway(xml_file)

#ap.create_svg_map()
ap.create_svg_map(add_linear_gradient_to_svg,['34','35','36','90'],['red','pink'])

