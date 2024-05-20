# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 16:46:15 2024

@author: Aparna
"""

import xml.etree.ElementTree as ET
import re
import datetime
import time
import json
import os



PROG_NAME = 'json2svg'
PROG_VER  = '01'
RUN_TIME  = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

# Set the main directry to work with
DATA_DIR = 'C:\\Users\\aparn\\Desktop\\masters_thesis\\Kegg_maps_aparna'
#print(DATA_DIR)

# move to the working directory
os.chdir(DATA_DIR)

from shape import Line, Circle, Rectangle
from kegg_annotation import KeggAnnotation
from svg_content import SvgContent

class KEGGPathway:

    def __init__(self):
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
        self._root = None
        self._json_data = None
        self._org =None
        self._pathway_id =None
        self._title = None      
        self._shape_info = None
        self.image = None

    @property
    def json_data(self):
        if self._json_data is None:  # Check if json_data has been computed
            return "None"
        else:
            # returns the value of the _json_data
            return self._json_data

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

    def _convert_to_json(self, xml_path):
        try:
            #if os.path.exists(xml_path):
            # parse the XML file specified by xml_path
            # retrieve the root element of the parsed XML tree
            self._root = ET.parse(xml_path).getroot()
            # convert the attributes of the root element into key-value pairs
            root_info = dict(self._root.items())

            data = {
                root_info['number']: {
                    root_info['org']: {
                        **{k: v for k, v in root_info.items() if k != 'number' and k != 'org'},  # Exclude 'number' and 'org' from the root_info
                        "entries": [] 
                    }
                }
            }
            # iterate over all the entry elements found in the XML tree.
            entries = self._root.findall('entry')
            for entry in entries:
                entry_data = {
                    "id": entry.get('id'),
                    "name": [entry.get('name')],
                    "type": [entry.get('type')],
                    "graphics": {}
                }
                graphics = entry.find('graphics')
                #if graphics is not None: # in which case is it none ??
                entry_data["graphics"] = {
                    "type": graphics.get('type'),
                    "x_coordinate": graphics.get('x'),
                    "y_coordinate": graphics.get('y'),
                    "height": graphics.get('height'),
                    "width": graphics.get('width'),
                    "coords": graphics.get('coords')
                }
                # append the entry_data dictionary to the "entries" 
                data[root_info['number']][root_info['org']]["entries"].append(entry_data)
   
            # Convert the data to JSON format
            json_data = json.dumps(data, indent=4)
            return json_data
        # Handle the exception if the file does not exist
        except FileNotFoundError as e:
            print(f"The specified XML file does not exist: {e}")
            return 
    def _extract_pathway_info(self,json_data):
        """
        This private method extracts pathway information from the JSON data.
        It searches for the first occurrence of a nested dictionary with the key 'title',
        and returns the organization, pathway ID, and title if found.
        If no 'title' is found, it returns the organization, pathway ID, and None.
        """
        data = json_data
        pathway_id = next(iter(data.keys()))
        org = list(data[pathway_id].keys())[0]
        for value1 in data.values():
            for value2 in value1.values():
                if isinstance(value2, dict) and 'title' in value2:
                    title = value2['title']
                    title = re.sub('_+', '_', title.replace(':', '_'))
                    return org, pathway_id, title
        return org, pathway_id, None
    
     
    def _extract_png_info(self):
        """
            This method extracts information from a JSON file associated with a 
            PNG image. It reads the JSON file, extracts the height, width, and
            image information, and updates the corresponding attributes of the object.
            It returns a tuple containing the width and height of the image.
        """
        try:
            # Construct the path to the JSON file based on the pathway ID
            image_path ="./maps_png/map" + self._pathway_id + ".png.json"
            print(image_path)
            # Open the JSON file and load the data
            with open(image_path, 'r') as file:
                image_data = json.load(file)
            
            # Extract the height, width, and image information
            self._height = image_data['height']
            self._width = image_data['width']
            self.image = image_data['image']
            print(len(self.image))
            
            # Return the width and height as a tuple
            return self._width,self._height
        except FileNotFoundError:
            # Handle the case when the JSON file is not found
            raise FileNotFoundError("JSON file not found.")

        except KeyError:
            # Handle the case when the required information is missing from the JSON file
            raise KeyError("Missing required information in the JSON file.")
            
    def get_pathway_components_information(self, data):
        components = []
        
        for item in data:
            shape = item['graphics']['type']
            if shape == 'line':
                component = Line(item)
            elif shape == 'circle':
                component = Circle(item)
            elif shape == 'rectangle' or shape == 'roundrectangle':
                component = Rectangle(item)
            else:
                raise ValueError(f"Unknown shape: {shape}")
            description =  KeggAnnotation.get_annotation(item['type'],item['name'])
    
            shape_geometry = component.calc_geometry()
            
            component_basics= {'id':component.id, 'shape':component.shape }
            components.append(component_basics|{'shape_geometry':shape_geometry} | description )
    
        return components
    
    def create_svg_content(self,data):
        baseProfile = 'Full'
        # extracts the width and height information for the SVG
        width, height =self._extract_png_info()
        image_data = self.image
        print(data['id'])
        # Construct the SVG namespace and define the defs section
        svg_tag = 'kegg-svg-' + self._pathway_id
        namespace = f'''<svg id="{svg_tag}" title="{self._title}" width="{width}" height="{height}" version="1.1" baseProfile="{baseProfile}" 
        xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        <style>.shape {{cursor: pointer}}</style>'''
        
        defs = f'''<defs>
            <pattern id="{self._pathway_id}" 
            width="{width}" height="{height}" patternUnits="userSpaceOnUse"  
            style="pointer-events: none">
                <image 
                xlink:href="data:image/png;base64,{image_data}" width="{width}" height="{height}" />
            </pattern>
        </defs>
        <rect x="0" y="0" fill="url(#{self._pathway_id})" 
        width="{width}" height="{height}"  
        style="pointer-events: none"/>
        <defs id="shape-color-defs">
        </defs>
        '''
        
        
        svg=""
        for item in data:
            svg_content = SvgContent(item)
            svg += svg_content.create_svg_content()
        
        # construct the SVG content by concatenating the namespace, the svg_data, and the defs section.
        svg_content =  namespace +'\n'+'<g name="shapes">'+'\n' + svg + '\n'+ '</g>'+ '\n' +  defs +'\n'  +'</svg>'
        
        return svg_content
            
         
    def json_to_svg(self, map_id, baseProfile = "full"):
        #  call _xml_from_map_id method to retrieve the paths of the XML files 
        # corresponding to the given map_id.
        data ,  pathway , org = self._merge_json(map_id)

        if data:
            
            self._shape_info = self.get_pathway_components_information(data)
            # call the _create_svg_content method with the json_data as an argument 
            # to generate the SVG content.              
            svg_content = self.create_svg_content(self._shape_info)
            # Create directory for SVG outputs
            OUT_DIR= f'{DATA_DIR}/SVG_output'
            os.makedirs(OUT_DIR, exist_ok=True)

            
            file_path = os.path.join(OUT_DIR, f"{self._org}{self._pathway_id}.svg")
            
            with open(file_path, 'w') as file:
                file.write(svg_content)  
        else:
            print("The specified XML file does not exist. Please provide a valid XML file .")
  
 #################################################################################################           
   
    def _merge_json(self,map_id):
        """
            Merge JSON data from multiple sources into a single JSON object.
            
            Parameters:
            - map_id (str): A string indicating the map id for the pathway.
            
            Returns:
            - merged_data (list): A list of merged JSON objects.
            - pathway_id (str): The pathway ID.
            - org (str): The merged annotation indicating which which data resources were merged
            
            """
        # Initialize empty list for later    
        merged_json = []    
        merged_org = []
        # Initialize empty list called data
        data =[]
        
        #  call _xml_from_map_id method to retrieve the paths of the XML files 
        # corresponding to the given map_id.
        ko_path, ec_path, rn_path, org_path = self._xml_from_map_id(map_id)

        # Initialize empty list called data
        data =[]
        # ko_path exists and is a valid file, it loads the JSON data from the 
        # ko_path using the __convert_to_json method.
        if ko_path is not None and os.path.exists(ko_path):
            
            json_data  = json.loads(self._convert_to_json(ko_path))  # Load the JSON data
            org, pathway_id, title = self._extract_pathway_info(json_data)
            
            data_ko= (json_data, org, pathway_id, title )
            # append to  data
            data.append(data_ko)
            # If the ec_path exists and is a valid file, follow the same process 
            # before to extract the pathway information from the ec_path and append
            # it to the data list.           
            if ec_path is not None and os.path.exists(ec_path):
                
                json_data  = json.loads(self._convert_to_json(ec_path))  # Load the JSON data
                org, pathway_id, title = self._extract_pathway_info(json_data)
                
                data_ec= (json_data, org, pathway_id,title)                
                data.append(data_ec)
                
            # Repeat for rn_path
            if rn_path is not None and os.path.exists(rn_path):
                
                json_data = json.loads(self._convert_to_json(rn_path))  # Load the JSON data
                org, pathway_id, title = self._extract_pathway_info(json_data)
                
                data_rn= (json_data, org, pathway_id,title )
                data.append(data_rn)
            # Repeat for org_path
            if org_path is not None and os.path.exists(org_path):
                
                json_data  = json.loads(self._convert_to_json(org_path))  # Load the JSON data
                org, pathway_id, title = self._extract_pathway_info(json_data)
                
                data_org= (json_data, org, pathway_id,title)
                data.append(data_org)
                
            json_data = data
            # Iterate over the data from different sources
            for data in data:
                json_data = data[0]
                org = data[1]
                pathway_id = data[2]
                title=data[3]
                # Append the JSON data and organism to the respective lists
                merged_json.append(json_data[pathway_id][org]['entries'])
                merged_org.append(org)
            # Flatten the merged_json list
            json_data = [item for sublist in merged_json for item in sublist]
            # Set the pathway_id and org attributes
            self._pathway_id = pathway_id
            self._org = '+'.join(merged_org)
            self._title = title
    
            merged_data = {}
            # Merge the JSON data based on entry_id, shape, x_coordinate, y_coordinate and coords
            for entry in json_data:
                entry_id = entry['id']
                entry_type = entry['graphics']['type']
                x_coordinate = entry['graphics']['x_coordinate']
                y_coordinate = entry['graphics']['y_coordinate']
                coords = entry['graphics']['coords']

                if "map" in [entry['type'][0]]:

                    name = [entry['name']][0]
                    
                    entry['name'][0] = "map"+name[0][-5:]

                        
                if entry_id in merged_data:
                    merged_entry = merged_data[entry_id]
                    if (merged_entry['graphics']['type'] == entry_type and
                        merged_entry['graphics']['x_coordinate'] == x_coordinate and
                        merged_entry['graphics']['y_coordinate'] == y_coordinate and
                        merged_entry['graphics']['coords'] == coords):
                        
                        name = entry['name'][0]
                        entry_type = entry['type'][0]
                        if name not in merged_entry['name']:
                            merged_entry['name'].append(entry['name'][0])
                            merged_entry['type'].append(entry['type'][0])
                        
                else:
                    merged_data[entry_id] = {
                        'id': entry_id,
                        'type': [entry['type'][0]],
                        'name': [entry['name'][0]],                                          
                        'graphics': entry['graphics']
                    }
                    
            # Convert the merged_data dictionary to a list
            self._json_data = list(merged_data.values())
            
            return self._json_data, self._pathway_id, self._org
        else:
            print("The specified XML file does not exist")
            return data, None,None


    def _xml_from_map_id(self, map_id):
        """
            Generates file paths for different XML files based on the given map_id.
            
            Args:
                map_id (str): The map_id to generate file paths.
            Returns:
                tuple: A tuple containing the file paths for KO, EC, RN, and Org XML files respectively.
            Raises:
                AssertionError: If the map_number is not an integer.
        """
        # check if the string variable map_id contains a period ('.')
        # assign the substring of map_id from the beginning up to (but not including) 
        # the index of the period to the variable map_id.
        if "." in map_id:
            index = map_id.rindex(".")
            map_id = map_id[:index]
    
        # Find the index where the letters end and the numbers start
        index = 0
        for i, char in enumerate(map_id):
            if char.isdigit():
                index = i
                break
        map_prefix = map_id[:index] # get map prefix
        map_number = map_id[index:] # get map suffix
        
        try:
            assert isinstance(int(map_number), int), "map_number should be an integer"
        except ValueError:
            print("Invalid map_number format. Please provide a valid map_id. eg: 'ko00400' or '00400' or '400' .")
            return None, None, None, None
                
        if len(map_number) < 5:
            map_number = map_number.zfill(5)
        
        ko_map_id = "ko" + map_number
        ko_path =f'{DATA_DIR}/kgml_data/ko/{ko_map_id}.xml'
        ec_map_id = "ec"+map_number
        ec_path = f'{DATA_DIR}/kgml_data/ec/{ec_map_id}.xml'
        rn_map_id = "rn"+map_number
        rn_path = f'{DATA_DIR}/kgml_data/rn/{rn_map_id}.xml'
        
        expected_prefixes = ["ko", "rn","ec","map",""]
        if map_prefix not in expected_prefixes:
            org_map_id = map_prefix + map_number
            org_path = f'{DATA_DIR}/kgml_data/orgs/{org_map_id}.xml'
            return ko_path, ec_path, rn_path, org_path
        else:
            return ko_path, ec_path, rn_path, None
############################################################################################   
xml_file="04110.xml"
        
ap=KEGGPathway()
#ap.json_data
#ap.pathway_info
ap.json_to_svg(xml_file)

