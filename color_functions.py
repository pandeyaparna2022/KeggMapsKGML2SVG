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
    root = data
    defs = ET.Element('defs')
    for i in range(len(shape_id)):
        # Parse the SVG file
        gradient_id = 'gradient_'+shape_id[i]
        
    
        # Find the shape element with the given shape_id
        shape_element = root.find(".//*[@shape_id='{}']".format(shape_id[i]))
        if shape_element is None:
            print("Shape element with shape_id = '{}' not found.".format(shape_id[i]))
            return root
        
        offset=100/len(colors)
    
        # Create a linear gradient element
        
        gradient_element = ET.SubElement(defs, 'linearGradient', id=gradient_id, x1='0%', y1='0%', x2='100%', y2='0%')
        offset1 = offset-offset
        offset2 = offset
        for col in range(len(colors)):
    
            stop_element1 = ET.SubElement(gradient_element, 'stop')
            
            stop_element1.set( 'offset', str(offset1)+'%')
            stop_element1.set( 'stop-color', colors[col])
            stop_element2 = ET.SubElement(gradient_element, 'stop')
            stop_element2.set( 'offset', str(offset2)+'%')
            stop_element2.set( 'stop-color', colors[col])
            
            offset1=offset2
            offset2 = offset2+offset
        # Print the value of the fill attributea
        shape_element.set('fill', 'url(#{})'.format(gradient_id))
        shape_element.set('stroke', 'url(#{})'.format(gradient_id))
    root.append(defs)
        
        #print("Value of fill attribute for shape_id='{}': {}".format(shape_id, shape_element.get('fill')))

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

def custom_annotations(query:list,*args,data):  
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
        
    
#ap.create_svg(add_linear_gradient_to_svg3,['34','35','36','90'])