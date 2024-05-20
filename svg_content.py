# -*- coding: utf-8 -*-
"""
Created on Tue May 14 13:21:53 2024

@author: aparn
"""
from shape import Line, Circle, Rectangle
from xml.etree import ElementTree as ET

from kegg_annotation import KeggAnnotation
from urllib.parse import quote

# Define variables to be used later
fill_color = "transparent"        
stroke = "black"
stroke_width="1.5" 
fill="transparent"
baseProfile = 'Full'

        
def _get_pathway_components_information(data,organism):
    
    #  Initializes an empty list called components to store the pathway components.
    components = []
    
    #  Iterates over each item in the data list.
    for item in data:
        # Retrieves the value of the 'type' key nested within the 'graphics' key of the current item. 
        # This value represents the shape of the component.
        
        # Assess the tye of shape and create a shape object accordingly.
        shape = item['graphics']['type']
        if shape == 'line':
            component = Line(item)
        elif shape == 'circle':
            component = Circle(item)
        elif shape == 'rectangle' or shape == 'roundrectangle':
            component = Rectangle(item)
            
        else:
        # Raises a ValueError with a message indicating that the shape is unknown 
        # if it doesn't match any of the expected shapes.
            raise ValueError(f"Unknown shape: {shape}")
        
        # Create a KeggAnnotation object using the current item and the provided organism.
        kegg = KeggAnnotation(item,organism)
        # Retrieves the annotation for the current item's type and name using the 
        # KeggAnnotation object.
        description =  kegg.get_annotation(item['type'], item['name'])
        # Calculates the geometry of the component
        shape_geometry = component.calc_geometry()
        
        # Creates a dictionary called component_basics with the 'id' and 'shape' 
        # attributes of the component.        
        component_basics= {'id':component.id, 'shape':component.shape }
        #  Appends a dictionary to the components list. The dictionary contains 
        # the component_basics, shape_geometry, and description dictionaries merged 
        # together using the | operator.
        components.append(component_basics|{'shape_geometry':shape_geometry} | description )

    return components

def _create_namespace(pathway_id,width,height):
    # Create the SVG element with the specified id, width, height, version, 
    # baseprofile, and xmlns attributes
    svg_tag = 'kegg-svg-' +  pathway_id
    doc = ET.Element('svg',id=f"{svg_tag}", width=f"{width}", height=f"{height}", version='1.1', baseprofile='full', xmlns="http://www.w3.org/2000/svg")
    
    # Set the xmlns:xlink attribute
    doc.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    
    ## Create the style element and set its text content
    style = ET.Element('style')
    style.text = '.shape {cursor: pointer}'
    # Append the style element to the SVG element
    doc.append(style) 
    
    # Return the created SVG element    
    return doc



def create_svg_content(data, organism, pathway_id, width, height, image_data,color_function, *args):
    # Assign the value of fill_color to the variable fill
    fill = fill_color
    
    # Call the _get_pathway_components_information function with the data and 
    # organism parameters and assign the result back to the data variable
    data = _get_pathway_components_information(data, organism)

    # Call the _create_namespace function with the pathway_id, width, and height
    # parameters and assign the result to the doc variable
    doc = _create_namespace(pathway_id, width, height)
    # Create an XML element with the tag 'g' and attribute 'name' set to 'shapes' 
    # and assign it to the group variable
    group = ET.Element('g', {'name': 'shapes'})
    
    # Iterate over each item in the data list
    for item in data:
        # Iterate over each details in the 'data_annotation' list of the current item
        for details in item['data_annotation']:
            # Check if the 'description' key exists in the details dictionary
            if "description" in details:
                # If it exists, quote the value of the 'description' key and assign
                # it back to the same key
                details['description'] = quote(details['description'])
        # Get the value of the 'visualizatin_class' key from the current item and 
        # assign it to the visualization_class variable
        visualization_class = item['visualizatin_class']
        # Insert the string 'shape' at the beginning of the visualization_class list
        visualization_class.insert(0, 'shape')
        # # Join the elements of the visualization_class list with a space and 
        # assign the result back to the visualization_class variable    
        visualization_class = ' '.join(visualization_class)    
        
        # Create an XML subelement with the tag specified by the value of the 'shape' key 
        # from the current item, and set the 'shape_id', 'stroke', 'fill', and 'style' 
        # attributes using values from the item and other variables
        shape_event = ET.SubElement(group, f"{item['shape']}", shape_id=f"{item['id']}", 
                                    stroke=f"{stroke}", fill=f"{fill}", style="stroke-opacity: 1")
        # # Iterate over each key-value pair in the 'shape_geometry' dictionary of the current item
        for key, value in item['shape_geometry'].items():
            shape_event.set(f"{key}", f"{str(value)}")
        # Set the 'stroke-width' attribute of the shape_event element using the 
        # value of the stroke_width variable # Set the attribute of the shape_event 
        # element with the key-value pair   
        shape_event.set('stroke-width', f"{stroke_width}")

        # Set the 'class' attribute of the shape_event element using the value of 
        # the visualization_class variable
        shape_event.set('class',f"{visualization_class}")
        
        # add a desc element to the shape_event
        # Set the text content of the desc element to the value of the 'data_annotation' 
        # key from the current item
        desc = ET.SubElement(shape_event, 'desc')
        desc.text = f"{item['data_annotation']}"

        # add a title element to the shape_event
        # Set the text content of the title element to the value of the 'title' 
        # key from the current item
        title = ET.SubElement(shape_event, 'title')
        title.text = f"{item['title']}"
        
    
    # append the group element to the doc XML element
    doc.append(group)
    
    # Create an XML element with the tag 'pattern' and attributes 'id', 'width', 
    # 'height', 'patternUnits', and 'style' set to the corresponding values
    pattern = ET.Element('pattern', id=f"{pathway_id}", width="{self.width}", height="{self.height}", patternUnits="userSpaceOnUse", style="pointer-events: none")
    # create the image element within the pattern element
    image = ET.SubElement(pattern, 'image')
    # # Set the 'xlink:href' attribute of the image element using the value of 
    # the self.image_data variable
    image.set('xlink:href', "data:image/png;base64,{self.image_data}")
    # Set the 'width' and 'height' attribute of the image element using the value of the 
    # width and height variable
    image.set('width', "{width}")
    image.set('height', "{height}")
    
    # Create an XML element with the tag 'defs' and assign it to the defs variable
    defs = ET.Element('defs')
    # append the pattern element to the defs element
    pattern = ET.SubElement(defs, 'pattern')
    pattern.set('id', pathway_id)
    pattern.set('width', width)
    pattern.set('height', height)
    pattern.set('patternUnits', 'userSpaceOnUse')
    pattern.set('style', 'pointer-events: none')
    image = ET.SubElement(pattern, 'image')
    image.set('xlink:href', f'data:image/png;base64,{image_data}')
    image.set('width', width)
    image.set('height', height)
    doc.append(defs)

    # Create an XML element with the tag 'rect' and attributes 'x', 'y', 'fill',
    # 'width', 'height', and 'style' set to the corresponding values
    rect = ET.Element('rect', x="0", y="0", fill=f"url(#{pathway_id})", width=f"{width}", height=f"{height}", style="pointer-events: none")
    # Append the rect element to the doc XML element
    doc.append(rect)
    # Create an XML element with the tag 'defs' and attribute 'id' set to 'shape-color-defs' 
    # and assign it to the defs variable
    defs = ET.Element('defs', id="shape-color-defs")
    # Append the defs element to the doc XML element
    doc.append(defs)

    #  # Check if the color_function parameter is not None
    if color_function is not None:
        # # Call the color_function with the *args parameters and the data 
        # parameter set to the doc variable
        doc = color_function(*args,data=doc)
  
    # Return the doc and data variables as a tuple
    return doc, data





   