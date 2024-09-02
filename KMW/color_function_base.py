# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:08:02 2024

@author: aparn
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 20 13:33:34 2024

@author: aparn
"""
from xml.etree import ElementTree as ET
import random

def color_all(*args, data):
    # Parse the element_tree object
    
    root = data
    elements = root.find('.//g')
    if args:
        color = args[0]
    else:
        color = 'blue'
    # Set the fill of each element to the specified color
    for element in elements:
        element.set('fill', color)
        element.set('stroke', color)
        element.set('stroke-width', '3')
        element.set('fill', color)
        element.set('fill-opacity', '0.15')
    
    return root

def color_org(org,*args, data):
    # Parse the element_tree object
    root = data
    elements = root.find('.//g')
    # Determine the color to use; default to 'blue' if not provided
    color = args[0] if args else 'blue'
    
    # Set the stroke of each element to the specified color

    for shapes in elements:
        # Extract the title element from shapes
        title_element = shapes.find('title')
      
        # Extract the title text if the title element           
        title_text = eval(title_element.text)
        
        # process the organism prefix to match the format in SVG
        query = org + ":"
        
        if any(query in item for item in title_text):
            
            shapes.set('stroke', color)
            shapes.set('stroke-width', '3')
            shapes.set('fill', color)
            shapes.set('fill-opacity', '0.15')
    
    return root

def color_custom_annotations(query:dict,*args,data):  
    '''Color only shapes with indicated annotation blue'''
    colors = []
    # Use the provided data as the root of the XML tree
    root = data
    
    # Determine the color to use; default to 'blue' if not provided
    color = args[0] if args else 'blue'
    
    # Find the group of elements in the SVG
    elements = root.find('.//g')
    # Set the fill of each element to the specified color
   
    # Return early if the query is empty
    if not query:
        return root
    # if the length of query is less than 5 execute the following commands
    if len(query) < 5:
        
        for shapes in elements:
            
            # Extract the title element from shapes
            title_element = shapes.find('title')
          
            # Extract the title text if the title element           
            title_text = eval(title_element.text)
        
            # Define an empty list for colors to store colors if there are more than one query
            colors = []
           
            # Iterate over each key-value pair in the query
            for key, values in query.items():
                # Check if any value in the list of values of the query dictionary
                # matches the title text
                           
                if any(value in item for item in title_text for value in values):
                    colors.append(color)  # Add the specified color
                else:
                    colors.append('white') # Default to white
                    
                # Update title text based on matches
                for value in values:
                    if any(value in item for item in title_text):
                        # Create a new list to replace items
                        updated_title_text = []
                        # Update title text with the key
                        for item in title_text:                            
                            if (value in item):   
                                updated_title_text.append(f"{key}:{item}")                        
                                shapes.set('fill-opacity', '0.5') # Set opacity
                                
                                # if the length of queries is 1 then the shape will be filled with
                                # specified color otherwise a gradient will be added later
                                if len(query) == 1:
                                    shapes.set('fill', color)
                            else:
                                updated_title_text.append(item)  # Keep the original 
                                # item if conditions are not met
                            # Replace the title_text with updated_title_text
                            title_element.text = str(updated_title_text)
            # Executed when length of queries is more than 1
            # Check if any color is not white
            if colors and any(c != 'white' for c in colors):
                # Create a new definitions element 
                defs = ET.Element('defs')
                defs = set_gradient(shapes.get('shape_id'), shapes, defs, colors)  # Set gradient
                root.append(defs)  # Append definitions to root
             
    return root

###################################################################################


def check_string_in_list(string_list, search_string):
    for item in string_list:
        #print(item)
        if search_string in item:
            return True
    return False



######################################################################################


def add_linear_gradient_to_svg(shape_id:list, predefined_colors:list=[ 'blue'], data=None):
    # assign the data parameter to the root variable. 
    root = data
    
    elements = root.find('.//g')
    
    # Create a <defs> element
    defs = ET.Element('defs')
    
    # Set the fill of each element to the specified color
    if not any(isinstance(i, list) for i in shape_id):
        
        no_of_groups =  len([shape_id])
        
    else:
        no_of_groups = sum(isinstance(i, list) for i in shape_id)
        
    print(no_of_groups) 
    if no_of_groups ==0:
        return root 
    
    elif no_of_groups ==1:
        groups = [[shape_id]]
    else:
        groups =shape_id
    #print(groups)
    for shapes in elements:
        for element in shapes:
            
            if element.tag == 'title':
                title_text = eval(element.text)

                colors = []
                annos = []
                for sublist in groups:
                    
                    anno, color = check_anno(title_text, sublist)
                    print(anno)
                    print(color)
                    annos.append(anno)
                    colors.append(color)
                    
                for i in range(len(colors)):
                    color_index = i % len(predefined_colors)
                    if colors[i] == 'blue' :
                        colors[i] = predefined_colors[color_index]                                          
                
                if any(color != 'white' for color in colors):
                    
                    
                    anno_list = list(filter(None, annos))
                    anno = '_'.join(set(anno_list))
              
                    anno = anno.replace(' ', '_').replace('(', '_').replace(')', '_')
                    
                    
                    if no_of_groups > 10:
                        white_count = colors.count('white')
                        white_percentage = (white_count / len(colors)) * 100
                        non_white_percentage = 100-white_percentage
                    
                        if non_white_percentage == 0:
                            colors = ['white']
                        elif non_white_percentage <= 25:
                            colors = ['pink']
                        elif non_white_percentage <= 50:
                            colors = ['yellow']
                        elif non_white_percentage <= 75:
                            colors = ['orange']
                        else:
                            colors = ['green']
                        print(non_white_percentage)
                    
                    
                
                    defs = set_gradient(anno,shapes,defs,colors)

    root.append(defs)      
        

    return root                  
    
    
    
def set_gradient(anno:str,shape_element, defs,  colors:list=['yellow', 'red', 'blue', 'green']):   

    gradient_id = 'gradient_'+anno
    
    # Calculate the offset for each color
    #offset=100/len(colors)
    offset=100/len(colors)
    
    
    # Create a <linearGradient> element with the generated gradient_id and
    # x1, y1, x2, y2 attributes            
    gradient_element = ET.SubElement(defs, 'linearGradient', id=gradient_id, x1='0%', y1='0%', x2='100%', y2='0%')
    offset1 = offset-offset
    offset2 = offset
    # Create a <stop> elements with the offset and stop-color attributes 
    # for all the colors
    for col in range(len(colors)):
        

        stop_element1 = ET.SubElement(gradient_element, 'stop')
        
        stop_element1.set( 'offset', str(offset1)+'%')
        stop_element1.set( 'stop-color', colors[col])
        stop_element2 = ET.SubElement(gradient_element, 'stop')
        stop_element2.set( 'offset', str(offset2)+'%')
        stop_element2.set( 'stop-color', colors[col])
        
        # Update the offset values for the next color stop
        offset1=offset2
        offset2 = offset2+offset
    # Set the 'fill' and 'stroke' attributes of the shape_element to 
    # reference the gradient_id

    shape_element.set('fill', 'url(#{})'.format(gradient_id))
    shape_element.set('stroke', 'url(#{})'.format(gradient_id))   

    return defs     

def check_anno(map_anno, anno_list):
    
    #print(anno_list)
    for key,value in anno_list[0].items():
        for anno in value:
            if anno in ' '.join(map_anno):
                return anno, "blue"
    return "","white"


# example annnotations for use case
string = '''K01736
K01696
K01695
K06001
K01695
K01696
K06001
K01609
K00766
K01657
K04092
K04517
K00800
K00014
K03785
K00817
K00817'''

my_list = string.split("\n")
new_lists = []
for _ in range(10):
    new_list = random.choices(my_list, k=2)
    new_lists.append(new_list)

#print(new_lists)