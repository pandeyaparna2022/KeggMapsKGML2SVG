# -*- coding: utf-8 -*-
"""
Created on Wed May 29 20:03:55 2024

@author: aparn
"""
import os
from xml.etree import ElementTree as ET
from pathlib import Path
from download_data import download_rest_data, download_base_png_maps, download_kgml, check_input
from pathway import Pathway
from base_image import BaseImage
from svg_content import create_svg_content
from color_function_base import color_all, color_custom_annotations
from color_functions_linera_gradient import add_linear_gradient_to_svg, add_linear_gradient_groups
#from annotation_setting_ap import ANNOTATION_SETTINGS
DATA_DIR = os.environ['KEGG_MAP_WIZARD_DATA']

class KeggPathwayMap:
    """
    Class to create a KeggPathwayMap object
    arg:
        
    """
    DATA_DIR = DATA_DIR
    def __init__(self, map_id, reload = False):
        print(f"Initializing an instance of {self.__class__.__name__}")
        print("Retreiving/downloading required resources.")
        self._map_id = check_input([map_id])
        self._pathway = None
        self._image_data = None
        self._organism = None
        self._reload = reload
        self.__file_exists()

    #To do : add title
    @property
    def map_id(self):
        """
        If the map ID is not in coorect format it returns and empty string,
        else it returns the map ID.

        Returns
        -------
        str
            the map id of the pathway.

        """
        if len(self._map_id) == 0:
            map_id = ''
        else:
            map_id = self._map_id[0]
        return map_id

    @property
    def organism(self):
        if self._organism is None:
            if self.map_id[:-5]  not in ['ko','ec','rn','']:
                file_path = self.DATA_DIR / Path("kgml_data") / Path('orgs') / Path(f"{self.map_id}.xml")
                if os.path.exists(file_path):
                    organism = self.map_id[:-5]
                else:
                    print(f"{self.map_id[:-5]} file does not exist for {self.map_id[-5:]}" )
                    organism = None
            else:
                organism = None
        else:
            organism = self._organism
        self._organism = organism
        return self._organism

    @property
    def pathway(self):
        if self._pathway is None:
            self._pathway = self.__create_pathway()
        return self._pathway

    @property
    def base_image(self):
        if self._image_data is None:
            self._image_data = self.__base_image()
        return self._image_data

    def __file_exists(self):
        if self.map_id != '':
            download_kgml([self.map_id],self._reload)
            download_base_png_maps([self.map_id], self._reload)

            if self.organism is not None:
                kgml_file_path = self.DATA_DIR / Path("kgml_data") / Path('orgs') / Path(f"{self.map_id}.xml")
                if os.path.exists(kgml_file_path):
                    print('hello')
                    rest_file = self.organism
                    download_rest_data([rest_file], self._reload)

    def __file_types(self):
        existing_file_types = []
        base_file_types = ['ko','ec','rn']

        for file_type in base_file_types:
            file_path = self.DATA_DIR / Path("kgml_data") / Path(file_type) / Path(f"{file_type}{self.map_id[-5:]}.xml")
            if os.path.exists(file_path):
                existing_file_types.append(file_type)

        if self.organism is not None:
            kgml_file_path = self.DATA_DIR / Path("kgml_data") / Path('orgs') / Path(f"{self.map_id}.xml")
            if os.path.exists(kgml_file_path):
                existing_file_types.append('orgs')
        return existing_file_types

    def __create_pathway(self):
        pathway = None
        file_types = self.__file_types()
        if len(file_types) != 0:
            #pathway = Pathway(self.map_id)
            #if self.organism is not None:
            if 'orgs' in file_types:
                pathway = Pathway(self.map_id,file_types)
            else:
                pathway = Pathway(self.map_id[-5:],file_types)
        if pathway is None:
            print('No pathway to create')
        return pathway

    def __base_image(self):
        base_image = None
        image_path = self.DATA_DIR / Path("maps_png") / Path(f"map{self.map_id[-5:]}.png.json")
        if os.path.exists(image_path):
            base_image = BaseImage.from_png(self.map_id,image_path)
        return  base_image

    def create_svg_map(self, color_function = None,*args ):
        if self.base_image is None or self.pathway is None:
            print('No pathway to create')
            svg_pathway_object = None
        else:
            print(args)
            svg_pathway_object = create_svg_content(self.pathway,self.base_image,color_function, *args)
            # Create directory for SVG outputs
            out_dir=  self.DATA_DIR / Path("SVG_output")
            os.makedirs(out_dir, exist_ok=True)
            file_path = out_dir / Path(f"{self.pathway.org}{self.map_id[-5:]}.svg")
            with open(file_path, 'wb') as file:
                file.write(b'\n')
                file.write(b'\n')
                file.write(ET.tostring(svg_pathway_object))
        return svg_pathway_object
