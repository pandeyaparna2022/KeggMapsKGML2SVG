# KeggMapWizard

> **Warning**
> Using this tool may require a [KEGG subscription](https://www.kegg.jp/kegg/legal.html)!

This script downloads KEGG REST data, KEGG configs and KEGG PNGs and converts them into SVG maps which can be processed dynamically using modern
browsers.

I included a simple JavaScript library that enables coloring the maps. It requires

- jQuery
- [chroma.js](https://gka.github.io/chroma.js/) to calculate color gradients
- [html2canvas](https://html2canvas.hertzen.com/) to render the SVGs as PNGs

## Python

### Creating the SVGs

Set the environment variable `KEGG_MAP_WIZARD_DATA` to where you want data to be downloaded to.

```bash
export KEGG_MAP_WIZARD_DATA='/path/to/desired/download/location'
```

or in Python:

```python
import os

os.environ['KEGG_MAP_WIZARD_DATA'] = '/path/to/desired/download/location'
```

In a Python 3.9 console, type:

```python
from kegg_map_wizard import KeggMapWizard, KeggMap, KeggShape, KeggAnnotation, ColorMaker

KeggMapWizard.download_kegg_resources()  # this will download all available KEGG maps and other required resources
KeggMapWizard.download_kegg_resources(map_ids=['00400'], org=['gma','mus'], reload=True) # this will only download this KEGG resources for the specified organims and maps


# Create KeggMap object
svg_map = KeggPathwayMap("00400")

# Create SVG
svg_map.create_svg_map()


```
By default, the rendered SVGs will be saved in a directory called 'SVG_output' within the KEGG_MAP_WIZARD_DATA directory. Output SVG will follow the following naming format:

names of available kgml files separated by '_' followed by the pathway map number.

For example:
when map number is '00001', depending on which reference KGML files are available from KEGG the output name wille be one of the following:

- ko00001.svg  - if only ko KGML reference file is available
- ko_ec00001.svg - if only ko and ec KGML reference files are available
- ko_rn00001.svg - if only ko and rn KGML reference files are available
- ko_ec_rn00001.svg - if ko, ec and rn KGML reference file are available

If organism prefix is provided with the map number this is also included in the output name.

For example:
when map number is 'hsa00001',depending on which reference KGML files are available from KEGG the output name wille be one of the following:

- ko_hsa00001.svg  - if only ko KGML reference file and organism-specific KGML files are available.
- ko_ec_hsa00001.svg - if only ko and ec KGML reference files and organism-specific KGML files are available.
- ko_rn_hsa00001.svg - if only ko and rn KGML reference files and organism-specific KGML files are available.
- ko_ec_rn_hsa00001.svg - if ko, ec and rn KGML reference file and organism-specific KGML files are  available.

Both the output directory and output name can be specified by the user as follows"
```python
# Create KeggMap object
svg_map = KeggPathwayMap("00400")
# Create SVG
svg_map.create_svg_map(path = 'path/to/desired/directory',output_name = 'desired_name')
```

By default, all shapes are transparent. Below are some examples on how to apply colors in python:

```python
# Create SVG
svg_map.create_svg_map(path = 'path/to/desired/directory',output_name = 'desired_name')
```
By default, all shapes are transparent. Below are some example functions for coloring that are included in color_function_base.py script:

```python
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
        element.set('fill-opacity', '0.5')
    
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

```

In the color_function_base.py script, additional functions for coloring are available. The functions presented above are shown to provide users with an intuitive understanding of how to navigate the hierarchical structure of SVG files and to create custom coloring functions tailored to their specific needs.

The above mentioned functions can be called as follows:

```python
# Create KeggMap object
svg_map = KeggPathwayMap("00400")
# Create SVG
svg_map.create_svg_map(color_function, additional_arguments, path = 'path/to/desired/directory',output_name = 'desired_name')
```
Usecase examples are as follows:

```python
# Create KeggMap object
svg_map = KeggPathwayMap("00400")
# Create SVG
svg_map.create_svg_map(color_all, 'green', path = 'path/to/desired/directory',output_name = 'desired_name')
```

> **Warning**
> In the coloring functions provided in color_function_base.py script 
