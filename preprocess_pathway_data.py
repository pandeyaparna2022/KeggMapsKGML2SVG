# -*- coding: utf-8 -*-
"""
Created on Tue May 14 18:30:50 2024

@author: aparna
"""
from download_data import check_input
from xml.etree import ElementTree as ET
import json
import re
import os

DATA_DIR = os.environ['KEGG_MAP_WIZARD_DATA']
def extract_png_info(pathway_id):
    """
    Extracts information from a PNG file based on the given 
    pathway ID.

    Parameters
    ----------
    pathway_id : str
        The ID of the pathway associated with the PNG file.

    Handels
    ------
    FileNotFoundError
        If the specified file is not found.
    KeyError
        If the height, width or image key(s) is/are missing 
        in the json file.

    Returns
    -------
    height : int
        Height of the base png image.
    width : int
        Width of the base png image.
    image : str
        base64 encoded image.

    """

    try:
        # Construct the path to the JSON file based on the pathway ID
        image_path ="./maps_png/map" + pathway_id + ".png.json"
        
        # Open the JSON file and load the data
        with open(image_path, 'r') as file:
            image_data = json.load(file)
        
        # Extract the height, width, and image information
        height = str(image_data['height'])
        width = str(image_data['width'])
        image= image_data['image']
                
        # Return the width and height as a tuple
        return height, width, image
    except FileNotFoundError:
        # Handle the case when the JSON file is not found
        print(f"JSON file not found in {DATA_DIR}/{image_path} folder.")
        return None, None, None
        
    except KeyError:
        # Handle the case when the required information is missing from the JSON file
        print("Required information missing in the JSON file.")
        return None, None, None
###############################################################################
def xml_path_from_map_id(map_id):
    
    """
    Generates file paths to different KGML files if they exist
    based on the given map_id. If file paths does not exist it attempts to download
    them and the associated png.

    Parameters
    ----------
    map_id :str
        The map_id for which to generate the file path.
        
    Returns
    -------
    str
        Path to ko KGML file.
    str
        Path to ec KGML file.
    str
        Path to rn KGML file.
    str
        Path to organism specific KFML file or NONE, depending on prefix of map_id.

    """

   
    # add map_id to a list and use a predefined function to 
    # assess if format of the map_id is correct
    
    list_map_id = [map_id]
    
    map_id_list = check_input(list_map_id)
    if len(map_id_list)==0:
        return None, None, None, None

    # Separate map prefix and map number
    map_id=map_id_list[0]
    map_prefix = map_id[:-5] # get map prefix
    map_number = map_id[-5:] # get map suffix

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
############################################################


        
def extract_pathway_info(json_data):
    """
    This method extracts pathway information from the KGML files
    that have been converted to JSON format.

    Parameters
    ----------
    json_data : dict
    A dictionary representing the JSON data. The dictionary should have the following keys:
    - 'org': The organism information.
    - 'pathway_id': The pathway ID.
    It may also have:
    - 'title': The type of data.

    Returns
    -------
    
    org : str
        The ko/ec/rn information or organism information, 
        depending on the input.
    pathway_id : str
        The pathway ID/pathway number of the pathway.
    title : str
        The title of the pathway.

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
        

def convert_to_json(xml_path):
    """
    Extracts relevant information from the KGML file specified by
    the xml_path.
    
    Handels
    ------
    FileNotFoundError
        If the specified file is not found.
        
    Parameters
    ----------
    xml_path : string
        Path to the KGML file.

    Returns
    -------
    json_data : dictionary
        Relevant information  from specified KGML files in 
        JSON format.

    """
    try:
        # parse the XML file specified by xml_path
        # retrieve the root element of the parsed XML tree
        root = ET.parse(xml_path).getroot()
        # convert the attributes of the root element into key-value pairs
        root_info = dict(root.items())

        data = {
            root_info['number']: {
                root_info['org']: {
                    **{k: v for k, v in root_info.items() if k != 'number' and k != 'org'},  # Exclude 'number' and 'org' from the root_info
                    "entries": [] 
                }
            }
        }
        # iterate over all the entry elements found in the XML tree.
        entries = root.findall('entry')
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
    except FileNotFoundError as error:
        print(f"The specified XML file does not exist: {error}")
        return None
    
    
def merge_json(ko_path, ec_path, rn_path, org_path):
    """
        Merge data from multiple KGML files into a single JSON object.

    Parameters
    ----------
    ko_path : str
        Path to ko KGML file.
    ec_path : str
        Path to ec KGML file.
    rn_path : str
        Path to rn KGML file.
    org_path : str
        Path to organism specific KGML file.

    Returns
    -------
    data : list
        A list of all the entries for a pathway map after merging the specified 
        files
    pathway_id : str
        A string specifying the pathway number/id.
    org : str
        A string specifying which files were merged.

    """
    # Initialize empty list for later    
    organism = None
    merged_json = []    
    merged_org = []
    data =[]

    # ko_path exists and is a valid file, it loads the JSON data from the 
    # ko_path using the __convert_to_json method.
    if ko_path is not None and os.path.exists(ko_path):        
        json_data  = json.loads(convert_to_json(ko_path))  # Load the JSON data
        org, pathway_id, title = extract_pathway_info(json_data)
        data.append((json_data,'ko'))
        # If the ec_path exists and is a valid file, follow the same process 
        # before to extract the pathway information from the ec_path and append
        # it to the data list.           
        if ec_path is not None and os.path.exists(ec_path):            
            json_data  = json.loads(convert_to_json(ec_path))  # Load the JSON data
            data.append((json_data,'ec'))
            
        # Repeat for rn_path
        if rn_path is not None and os.path.exists(rn_path):            
            json_data = json.loads(convert_to_json(rn_path))  # Load the JSON data
            data.append((json_data,'rn'))
    # if org_path exists and is a valid file, load the JSON data from the 
    # org_path using the convert_to_json function.    
    if org_path is not None and os.path.exists(org_path):            
        json_data  = json.loads(convert_to_json(org_path))  # Load the JSON data
        organism, pathway_id, title = extract_pathway_info(json_data)
        data.append((json_data,organism))

    if len(data)!= 0:
        # Iterate over the data from different sources
        for data_point in data:
            data = data_point[0]
            org = data_point[1]
            # Append the JSON data and organism to the respective lists
            merged_json.append(data_point[0][pathway_id][org]['entries'])
            merged_org.append(org)
        # Flatten the merged_json list
        merged_json_data = [item for sublist in merged_json for item in sublist]
        # Set the pathway_id and org attributes
        org = '+'.join(merged_org)

        merged_data = {}
        # Merge the JSON data based on entry_id, shape, x_coordinate, y_coordinate and coords
        for entry in merged_json_data:
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
        # Convert the merged_data dictionary to a list of dictionaries
        json_data = list(merged_data.values())        
        return json_data, org, pathway_id, title, organism
    else:
        print("The specified XML file does not exist")
        return data, None,None,None, None

 