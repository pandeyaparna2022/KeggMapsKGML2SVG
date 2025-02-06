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
        # override the default working directory with its value. If not, keep the default
        self.working_dir = os.environ.get('KEGG_MAP_WIZARD_DATA',self.working_dir)

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
# Print the default working directory that has been set during initialization.
print("Default working directory is set to:", config.working_dir)
# Prompt the user to enter a desired path for the working directory, allowing it to be optional.
USER_PATH= input('Please enter the desired path for KEGG_MAP_WIZARD_DATA (optional): ')
# If the user input is empty, set USER_PATH to None.
if USER_PATH == '':
    USER_PATH = None
# If the user provided a path, update the working directory to the absolute path
# of the provided input.
if USER_PATH is not None:
    config.set_working_dir(os.path.abspath(USER_PATH))
# Print the current working directory after any updates made by the user.
print("Working directory has been set to:", config.working_dir)
# Check if the working directory exists; if it doesn't, create the directory.
if not os.path.isdir(config.working_dir):
    os.mkdir(config.working_dir)
# If the environment variable 'KEGG_MAP_WIZARD_DATA' is not set, assign the
# current working directory to it.
if 'KEGG_MAP_WIZARD_DATA' not in os.environ:
    os.environ['KEGG_MAP_WIZARD_DATA'] = config.working_dir
# Assign the working directory to a constant variable for further use in the application.
KEGG_MAP_WIZARD_DATA = config.working_dir
