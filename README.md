# KeggMapsKGML2SVG

This script downloads KEGG REST data, KEGG kgml files and KEGG PNGs and converts them into SVG maps which can be processed dynamically using modern browsers.

# Creating the SVGs

Set the environment variable KEGG_MAP_WIZARD_DATA to where you want data to be downloaded to.

export KEGG_MAP_WIZARD_DATA='/path/to/desired/download/location'

or provide the path for in main.py file

KEGG_MAP_WIZARD_DATA = 'desired/path'

Downloading majority of the required files locally prior to creating the svgs is recommended as it will save time later.
For this uncomment the last two lines (this will take about half an hour or so) or test with just a few files as shown in main.py.

After the download you can create the svg by using the folloing code.

### create a keggPathwayMap object
map_{map_id} = KeggPathwayMap('map_id') # example map_has00400 = KeggPathwayMap('hsa00400') 
### Then create SVG from the keggPathwayMap object
map_has00400.create_svg_map() 

the output will be stored in a folder called SVG_outputs within the provided path for KEGG_MAP_WIZARD_DATA

One can further use various color functions to color specific elements within the pathway maps 

Please explore the color_function_base.py and color_functions+linear_gradient.py files for further detail


# Note:
This is a work in progress and this is being continuously updated in order to make existing tasks more efficient and to add new functionalities.


