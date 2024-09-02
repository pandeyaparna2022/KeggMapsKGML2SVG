# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 15:46:24 2024

@author: aparn
"""

from xml.etree import ElementTree as ET

def add_linear_gradient_to_svg(shape_id_g1:list, predefined_colors:list=['yellow', 'red', 'blue', 'green','pink'],data=None):
    # assign the data parameter to the root variable. 
    root = data
    
    elements = root.find('.//g')
    
    # Create a <defs> element
    defs = ET.Element('defs')
    
    # Set the fill of each element to the specified color
    # Check if there are sublists within the list
    # if NOT so no of groups =  1, convert the list into a nested list
    if not any(isinstance(i, list) for i in shape_id_g1):
        print(any(isinstance(i, list) for i in shape_id_g1))
        no_of_groups =  len([shape_id_g1])
        
    else:
        no_of_groups = sum(isinstance(i, list) for i in shape_id_g1)
        
        
    if no_of_groups ==0:
        return root 
    
    elif no_of_groups ==1:
        groups = [shape_id_g1]
    else:
        groups =shape_id_g1
    
    for shapes in elements:
        for element in shapes:
            title_text = []
            if element.tag == 'title':
                title_text = eval(element.text)

                colors = []
                annos = []
                for sublist in groups:
                    
                    anno, color = check_anno(title_text, sublist)

                    annos.append(anno)
                    colors.append(color)
                    
                for i in range(len(colors)):
                    color_index = i % len(predefined_colors)
                    if colors[i] == 'blue' :
                        colors[i] = predefined_colors[color_index]   

                if any(color != 'white' for color in colors):
                    print(colors)
                    
                    anno_list = list(filter(None, annos))
                    anno = '_'.join(set(anno_list))
              
                    anno = anno.replace(' ', '_').replace('(', '_').replace(')', '_')
                    
                    
                    if no_of_groups > 10:
                        white_count = colors.count('white')
                        white_percentage = (white_count / len(colors)) * 100
                        non_white_percentage = 100-white_percentage
                        
                        if non_white_percentage == 0:
                            colors = ['white']
                        if non_white_percentage <= 25:
                            colors = ['pink']
                        elif non_white_percentage <= 50:
                            colors = ['yellow']
                        elif non_white_percentage <= 75:
                            colors = ['orange']
                        else:
                            colors = ['green']

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
    for anno in anno_list:
        if anno in ' '.join(map_anno):
            return anno, "blue"
    return "","white"


#################################################################################
def add_linear_gradient_groups(shape_id_g1:list,shape_id_g2:list, predefined_colors:list=['yellow', 'red', 'blue', 'green','pink'],data=None):
    # assign the data parameter to the root variable. 
    root = data
    
    elements = root.find('.//g')
    
    # Create a <defs> element
    defs = ET.Element('defs')
    
    # Set the fill of each element to the specified color
    
    no_of_orgs1,group1 = assess_no_of_orgs(shape_id_g1)
    no_of_orgs2,group2 = assess_no_of_orgs(shape_id_g2)
        
    if no_of_orgs1 ==0 or no_of_orgs2==0:
        return root 

    for shapes in elements:
        for element in shapes:
            title_text = []
            if element.tag == 'title':
                title_text = eval(element.text)

                anno1,colors1 = process_groups(group1, title_text)    
                anno1,colors2 = process_groups(group2, title_text)    
                colors = colors1 +colors2
                
                if any(color != 'white' for color in colors):
                    print(colors)
                    defs = set_gradient(anno1,shapes,defs,colors)

    root.append(defs)      
        

    return root                  

def assess_no_of_orgs(shape_id:list):
    if not any(isinstance(i, list) for i in shape_id):
        
        no_of_groups =  len([shape_id])
        
    else:
        no_of_groups = sum(isinstance(i, list) for i in shape_id)
    if no_of_groups == 0:
        groups = []
    elif no_of_groups ==1:
        groups = [shape_id]
    else:
        groups =shape_id
    
    return no_of_groups,groups



def process_groups(groups, title_text):
    colors = []
    annos = []
    predefined_colors = ['red', 'green', 'yellow', 'orange']  # Example predefined colors

    for sublist in groups:
        anno, color = check_anno(title_text, sublist)
        annos.append(anno)
        colors.append(color)

    for i in range(len(colors)):
        color_index = i % len(predefined_colors)
        if colors[i] == 'blue':
            colors[i] = predefined_colors[color_index]
            
    anno_list = list(filter(None, annos))
    anno = '_'.join(set(anno_list))
  
    anno = anno.replace(' ', '_').replace('(', '_').replace(')', '_')
            
    #if any(color != 'white' for color in colors):
        
        
    anno_list = list(filter(None, annos))
    anno = '_'.join(set(anno_list))
  
    anno = anno.replace(' ', '_').replace('(', '_').replace(')', '_')
    
    
    #if len(groups) > 5:
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
            
    #print(colors)
    #else:
        #colors = ['white']
        
            
    return anno, colors




