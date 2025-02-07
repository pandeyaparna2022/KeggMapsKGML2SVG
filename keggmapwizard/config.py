# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:54:19 2025

@author: aparn
"""

import os
import tempfile

class Config:
    """
    A class to manage configuration settings for the KEGG Map Wizard.
    
    This class is responsible for setting and managing the working directory 
    used by the KEGG Map Wizard application. It initializes the working 
    directory to a default location within the system's temporary directory. 
    Additionally, it allows for the working directory to be overridden by an 
    environment variable, providing flexibility in configuration.
    
    Attributes:
        working_dir (str): The path to the working directory used by the
                           application. This can be set to a default value or
                           overridden by an environment variable.
    Methods:
        set_working_dir(new_path): Updates the working directory to the 
                                   specified new path.
    """
    def __init__(self):
        # Initialize the Config class instance.

        # Set a default working directory by joining the system's temporary directory
        # with the subdirectory "KEGG_MAP_WIZARD_DATA".
        self.working_dir = os.path.join(tempfile.gettempdir(), "KEGG_MAP_WIZARD_DATA")
        
        # Check if an environment variable 'KEGG_MAP_WIZARD_DATA' is set; if it is,
        # assess if it is a valid path.and if so override the default working
        # directory with its value. If not, keep the default
        if 'KEGG_MAP_WIZARD_DATA' in os.environ:
            KEGG_MAP_WIZARD_DATA = os.environ['KEGG_MAP_WIZARD_DATA']
            if not os.path.isdir(KEGG_MAP_WIZARD_DATA):
                try:
                    os.makedirs(KEGG_MAP_WIZARD_DATA, exist_ok=True)
                    print(os.path.abspath(KEGG_MAP_WIZARD_DATA))
                except FileNotFoundError as e:
                    # if the env variable does not have a valid path then print 
                    # an error and remove it
                    print(f"Error: {e}. Please check if the base path exists.")
                    del os.environ['KEGG_MAP_WIZARD_DATA']
                    
        self.working_dir = os.path.abspath(os.environ.get('KEGG_MAP_WIZARD_DATA',self.working_dir))

    def set_working_dir(self, new_path):
        """
        Update the working directory to the specified path.
        
        This method allows the user to programmatically change the working directory 
        of the Config instance. The new path provided as an argument will replace 
        the current working directory.
        
        Parameters:
            new_path (str): The new path to set as the working directory. This should 
            be a valid directory path as a string.
        """
        # Update the working directory to the new path provided as an argument.
        self.working_dir = new_path

# Create a singleton instance of the Config class, allowing global access to the configuration.
config = Config()

if 'KEGG_MAP_WIZARD_DATA' in os.environ:
    print("Default working directory is set to:", config.working_dir)
    
else:
    # Prompt the user to enter a desired path for the working directory, allowing it to be optional.
    KEGG_MAP_WIZARD_DATA= input('Please enter the desired path for KEGG_MAP_WIZARD_DATA '
                     'or press Enter to create a new folder in the current directory : ')

    # If the user input is empty, create a data directory in current path.
    if KEGG_MAP_WIZARD_DATA == '':
        KEGG_MAP_WIZARD_DATA = './KEGG_MAP_WIZARD_DATA'
        
    # Try to create the directory if the path is not valid set the data directory
    # the default one
    try:
        os.makedirs(KEGG_MAP_WIZARD_DATA, exist_ok=True)
        os.environ['KEGG_MAP_WIZARD_DATA'] = os.path.abspath(KEGG_MAP_WIZARD_DATA)
        config.set_working_dir(os.path.abspath(KEGG_MAP_WIZARD_DATA))
        # Print the current working directory after any updates made by the user.
        print("Working directory has been set to:", config.working_dir)
    except FileNotFoundError as e:
          print(f"Error: {e}. Please check if the base path exists.")
          print("The default working directory has been set to", config.working_dir)
           
KEGG_MAP_WIZARD_DATA = config.working_dir
