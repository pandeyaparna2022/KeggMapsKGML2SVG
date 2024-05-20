# -*- coding: utf-8 -*-
"""
Created on Tue May 14 13:21:53 2024

@author: aparn
"""
from shape import Line, Circle, Rectangle
from xml.etree import ElementTree as ET

from kegg_annotation import KeggAnnotation
from urllib.parse import quote

fill_color = "transparent"        
stroke = "black"
stroke_width="1.5" 
fill="transparent"
baseProfile = 'Full'

        
def _get_pathway_components_information(data,organism):
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
        
        kegg = KeggAnnotation(item,organism)
        description =  kegg.get_annotation(item['type'], item['name'])
        #description =  KeggAnnotation.get_annotation(item['type'], item['name'])

        shape_geometry = component.calc_geometry()
        
        component_basics= {'id':component.id, 'shape':component.shape }
        components.append(component_basics|{'shape_geometry':shape_geometry} | description )

    return components

def _create_namespace(pathway_id,width,height):
    svg_tag = 'kegg-svg-' +  pathway_id
    doc = ET.Element('svg',id=f"{svg_tag}", width=f"{width}", height=f"{height}", version='1.1', baseprofile='full', xmlns="http://www.w3.org/2000/svg")
    doc.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    style = ET.Element('style')
    style.text = '.shape {cursor: pointer}'
    doc.append(style) 
    
    return doc

 # Assign a default value to fill

def create_svg_content(data, organism, pathway_id, width, height, image_data,color_function, *args):
    fill = fill_color
    
    data = _get_pathway_components_information(data, organism)
    print(*args)
    
    
   
    
    #variables = args  # ['EC:3.4.13.4', 'R03935', 'RC00090']
    doc = _create_namespace(pathway_id, width, height)
    
    group = ET.Element('g', {'name': 'shapes'})
  
    for item in data:
        for details in item['data_annotation']:
            if "description" in details:
                details['description'] = quote(details['description'])
        
        visualization_class = item['visualizatin_class']
        visualization_class.insert(0, 'shape')
        visualization_class = ' '.join(visualization_class)    
        
        #if color_function is not None:

            #fill = color_function(*args,data=item)

        
        shape_event = ET.SubElement(group, f"{item['shape']}", shape_id=f"{item['id']}", 
                                    stroke=f"{stroke}", fill=f"{fill}", style="stroke-opacity: 1")
        for key, value in item['shape_geometry'].items():
            shape_event.set(f"{key}", f"{str(value)}")
        shape_event.set('stroke-width', f"{stroke_width}")
        shape_event.set('class',f"{visualization_class}")
        
        # add a desc element to the shape_event
        desc = ET.SubElement(shape_event, 'desc')
        desc.text = f"{item['data_annotation']}"

        # add a title element to the shape_event
        title = ET.SubElement(shape_event, 'title')
        title.text = f"{item['title']}"
        
    
    # append the group element to the SVG XML element
    doc.append(group)
    
    # create the pattern element
    pattern = ET.Element('pattern', id=f"{pathway_id}", width="{self.width}", height="{self.height}", patternUnits="userSpaceOnUse", style="pointer-events: none")
    # create the image element within the pattern element
    image = ET.SubElement(pattern, 'image')
    image.set('xlink:href', "data:image/png;base64,{self.image_data}")
    image.set('width', "{self.width}")
    image.set('height', "{self.height}")
    # append the pattern element to the defs element
    defs = ET.Element('defs')
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

    # create rect element
    rect = ET.Element('rect', x="0", y="0", fill=f"url(#{pathway_id})", width=f"{width}", height=f"{height}", style="pointer-events: none")
    doc.append(rect)
    defs = ET.Element('defs', id="shape-color-defs")
    doc.append(defs)
                      
    defs = ET.SubElement(doc, 'defs')
    #docs1 = ET.tostring(doc)
    if color_function is not None:

        doc = color_function(*args,data=doc)
    
    
    return doc, data

def color_all(*args,data):
    '''Color all shapes the color specified by *args or red'''
    #print(item)

    if args:
        return  args[0] 
    else:
        return 'red'
        
    
def custom_annotations(query:list,*args,data):  
    '''Color only shapes with indicated annotation red'''
   
    res = data.get('title')
    #print(res)
    for element in query:
        if element in res:
            if args :
                return args[0]
            else:
                return 'red'            
        else:
            return 'transparent'
            

def custom_color_function(shape):
    '''Color all shapes with 4 sequential colors (yellow, red, blue, green)'''
    shape.definition = ColorMaker.svg_gradient(
        colors=['yellow', 'red', 'blue', 'green'],
        id=shape['id'],
        x1='0%',
        x2='100%'
    )
    return f'url(#{shape["id"]})'

# create a group element with the name 'shapes'






   