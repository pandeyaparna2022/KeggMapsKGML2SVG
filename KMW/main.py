# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 14:40:51 2024

@author: Aparna
"""

import os

import random
import multiprocessing
import logging
#from download_data import download_rest_data, download_base_png_maps, download_kgml

# Define DATA_DIR
#KEGG_MAP_WIZARD_DATA = 'C:\\Users\\aparn\\Desktop\\masters_thesis\\KeggMapsKGML2SVG'
KEGG_MAP_WIZARD_DATA = 'C:\\Users\\aparn\\Desktop\\KeggMapsKGML2SVG\\KMW'

# Add the path to the environment
# For now. Need to change it so the user can dynamically set this
os.environ['KEGG_MAP_WIZARD_DATA'] = f'{KEGG_MAP_WIZARD_DATA}'


# Set the envronment variable 
# For now need to change it so user can dynamically set this 
os.environ['KEGG_MAP_WIZARD_PARALLEL'] = '6'

# retrieves the value of the environment variable KEGG_MAP_WIZARD_PARALLEL and
# assigns it to the variable N_PARALLEL_DOWNLOADS. If the environment variable 
# is not set, it defaults to the value '6'.

N_PARALLEL_DOWNLOADS = os.environ.get('KEGG_MAP_WIZARD_PARALLEL', '6')

# assert N_PARALLEL_DOWNLOADS is a decimal value using the isdecimal() method. 
# If the assertion fails, it will raise an AssertionError with a the specified
# error message.
assert N_PARALLEL_DOWNLOADS.isdecimal(), f'The environment variable KEGG_MAP_WIZARD_PARALLEL must be decimal. ' \
                                         f'KEGG_MAP_WIZARD_PARALLEL={N_PARALLEL_DOWNLOADS}'

# converts the value of N_PARALLEL_DOWNLOADS to an integer                                        
N_PARALLEL_DOWNLOADS = int(N_PARALLEL_DOWNLOADS)

# assert the environment variable KEGG_MAP_WIZARD_DATA is present in the os.environ 
# dictionary. If the variable is not found, it raises an AssertionError with a 
# the specified error message.

assert 'KEGG_MAP_WIZARD_DATA' in os.environ, \
    'Please set the environment variable KEGG_MAP_WIZARD_DATA to the directory where KEGG data will be stored'

# retrieves and assign the value of the environment variable to DATA_DIR
DATA_DIR = os.environ['KEGG_MAP_WIZARD_DATA']
os.chdir(f'{DATA_DIR}')

# assert the directory specified by DATA_DIR exists. If the directory does not 
# exist, it raises an AssertionError with the specified error message.
assert os.path.isdir(DATA_DIR), f'Directory not found: KEGG_MAP_WIZARD_DATA={DATA_DIR}'
#from download_data import download_rest_data, extract_all_map_ids,download_base_png_maps,download_kgml
# logs warning message providing details about the setup by including the values 
# of KEGG_MAP_WIZARD_DATA and N_PARALLEL_DOWNLOADS for reference and 
# troubleshooting purposes.
logging.warning(f'Setup: KEGG_MAP_WIZARD_DATA={DATA_DIR}; KEGG_MAP_WIZARD_PARALLEL={N_PARALLEL_DOWNLOADS}')


from kegg_pathway_map import KeggPathwayMap
from color_function_base import color_all, color_custom_annotations, color_org
from color_functions_color_groups import add_linear_gradient_groups