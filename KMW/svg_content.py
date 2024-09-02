# -*- coding: utf-8 -*-
"""
Created on Tue May 14 13:21:53 2024

@author: aparn
"""

from xml.etree import ElementTree as ET
from urllib.parse import quote
# pylint: disable=too-many-locals
# Define variables to be used later
FILL_COLOR = "transparent"
STROKE = "black"
STROKE_WIDTH="1.5"
FILL="transparent"
BASE_PROFILE = 'full'

def __create_namespace(base_image,title):
    # Create the SVG element with the specified id, width, height, version,
    # baseprofile, and xmlns attributes

    svg_tag = 'kegg-svg-' +  base_image.map_id[-5:]
    doc = ET.Element('svg',title=f"{title}",id=f"{svg_tag}", width=f"{base_image.image_width}",
                     height=f"{base_image.image_height}", version='1.1',
                     baseprofile=f"{BASE_PROFILE}",
                     xmlns="http://www.w3.org/2000/svg")

    # Set the xmlns:xlink attribute
    doc.set("xmlns:xlink", "http://www.w3.org/1999/xlink")

    ## Create the style element and set its text content
    style = ET.Element('style')
    style.text = '.shape {cursor: pointer}'
    # Append the style element to the SVG element
    doc.append(style)

    # Return the created SVG element
    return doc

def create_svg_content(pathway,base_image,color_function, *args):
    # Assign the value of fill_color to the variable fill

    pathway_components= pathway.pathway_components

    # Call the _create_namespace function with the pathway_id, width, and height
    # parameters and assign the result to the doc variable
    doc = __create_namespace(base_image,pathway.title)
    # Create an XML element with the tag 'g' and attribute 'name' set to 'shapes'
    # and assign it to the group variable
    group = ET.Element('g', {'name': 'shapes'})

    # Iterate over each item in the data list
    for item in pathway_components:
        # Iterate over each details in the 'data_annotation' list of the current item
        for details in item.pathway_annotation_data['data_annotation']:
            # Check if the 'description' key exists in the details dictionary
            if "description" in details:
                # If it exists, quote the value of the 'description' key and assign
                # it back to the same key
                details['description'] = quote(details['description'])
        # Get the value of the 'visualizatin_class' key from the current item and
        # assign it to the visualization_class variable
        visualization_class = item.pathway_annotation_data['visualizatin_class']
        # Insert the string 'shape' at the beginning of the visualization_class list
        visualization_class.insert(0, 'shape')
        # # Join the elements of the visualization_class list with a space and
        # assign the result back to the visualization_class variable
        visualization_class = ' '.join(visualization_class)

        # Create an XML subelement with the tag specified by the value of the 'shape' key
        # from the current item, and set the 'shape_id', 'stroke', 'fill', and 'style'
        # attributes using values from the item and other variables
        shape_event = ET.SubElement(group, f"{item.pathway_component_geometry_shape}",
                                    shape_id=f"{item.pathway_component_id}",
                                    stroke=f"{STROKE}", fill=f"{FILL}", style="stroke-opacity: 1")
        # # Iterate over each key-value pair in the 'shape_geometry' dictionary of the current item
        for key, value in item.pathway_component_geometry.items():
            shape_event.set(f"{key}", f"{str(value)}")
        # Set the 'stroke-width' attribute of the shape_event element using the
        # value of the stroke_width variable # Set the attribute of the shape_event
        # element with the key-value pair
        shape_event.set('stroke-width', f"{STROKE_WIDTH}")

        # Set the 'class' attribute of the shape_event element using the value of
        # the visualization_class variable
        shape_event.set('class',f"{visualization_class}")

        # add a desc element to the shape_event
        # Set the text content of the desc element to the value of the 'data_annotation'
        # key from the current item
        desc = ET.SubElement(shape_event, 'desc')
        desc.text = f"{item.pathway_annotation_data['data_annotation']}"

        # add a title element to the shape_event
        # Set the text content of the title element to the value of the 'title'
        # key from the current item
        title = ET.SubElement(shape_event, 'title')
        title.text = f"{item.pathway_annotation_data['title']}"


    # append the group element to the doc XML element
    doc.append(group)

    # Create an XML element with the tag 'defs' and assign it to the defs variable
    defs = ET.Element('defs')
    # Create an subelement with the tag 'pattern' and attributes 'id', 'width',
    # 'height', 'patternUnits', and 'style' set to the corresponding values
    # append the pattern element to the defs element
    pattern = ET.SubElement(defs, 'pattern')
    pattern.set('id', base_image.map_id[-5:])
    pattern.set('width', base_image.image_width)
    pattern.set('height', base_image.image_height)
    pattern.set('patternUnits', 'userSpaceOnUse')
    pattern.set('style', 'pointer-events: none')
    # create the image element within the pattern element
    image = ET.SubElement(pattern, 'image')
    # Set the 'xlink:href' attribute of the image element using the value of
    # the image_data variable
    image.set('xlink:href', f'data:image/png;base64,{base_image.image}')
    # Set the 'width' and 'height' attribute of the image element using the value of the
    # width and height variable
    image.set('width', base_image.image_width)
    image.set('height', base_image.image_height)

    # append the defs element to the doc XML element
    doc.append(defs)

    # Create an XML element with the tag 'rect' and attributes 'x', 'y', 'fill',
    # 'width', 'height', and 'style' set to the corresponding values
    rect = ET.Element('rect', x="0", y="0", fill=f"url(#{ base_image.map_id[-5:]})",
                      width=f"{ base_image.image_width}",
                      height=f"{base_image.image_height}", style="pointer-events: none")
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
    return doc
   