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
def add_linear_gradient_to_svg(shape_id:list, colors:list=['yellow', 'red', 'blue', 'green'],data=data):
    # assign the data parameter to the root variable. 
    root = data
    # Create a <defs> element
    defs = ET.Element('defs')
    # iterate over the indices of the shape_id list.
    for i in range(len(shape_id)):
        
        # Generate a unique gradient ID for each shape_id
        gradient_id = 'gradient_'+shape_id[i]

        # Find the shape element with the given shape_id
        shape_element = root.find(".//*[@shape_id='{}']".format(shape_id[i]))
        # check if the shape element was found. 
        if shape_element is None:
            print("Shape element with shape_id = '{}' not found.".format(shape_id[i]))
            
        else:
            # Calculate the offset for each color
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
    # Append the <defs> element to the root element
    root.append(defs)      
        

    return root



def color_all(*args, data=None):
    # Parse the element_tree object
    root = data
    elements = root.find('.//g')
    if args:
        color = args[0]
    else:
        color = 'red'
    # Set the fill of each element to the specified color
    for element in elements:
        element.set('fill', color)
    
    return root

def color_custom_annotations(query:list,*args,data):  
    '''Color only shapes with indicated annotation red'''
    # Parse the element_tree object
    root = data
    
    if args:
        color = args[0]
    else:
        color = 'pink'
    
    elements = root.find('.//g')
    
   
    # Set the fill of each element to the specified color

    for shapes in elements:
        for element in shapes:
            title_text = []
            if element.tag == 'title':
                title_text = eval(element.text)
    
            for anno in query:
                if anno in title_text:
                    shapes.set('fill', color)

    return root
        
