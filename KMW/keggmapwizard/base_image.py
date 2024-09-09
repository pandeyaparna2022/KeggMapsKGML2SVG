# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 11:41:52 2024

@author: aparn
"""
import json
# pylint: disable=too-few-public-methods
class BaseImage:
    """
    A class representing a base png pathway image .

   Attributes:
       map_id : str
           The ID of the pathway map.
       image: The image data.
       image_height: The height of the image.
       image_width: The width of the image.
    """
    def __init__(self, map_id:str,image,height,width):
        """
        Initializes a new instance of the class.
    
        Args:
        - map_id (str): The ID of the pathway map.
        - image: The image of the pathway map.
        - height: The height of the image.
        - width: The width of the image.
       """
        self.map_id = map_id
        self.image = image
        self.image_height = height
        self.image_width = width

    @classmethod
    def from_png(cls, map_id,image_path):
        """
        Create a BaseImage object from a json file.

        Args:
            cls: The class itself.
            map_id (str): The ID of the pathway map.
            image_path (str): The path to the json file.

        Returns:
            BaseImage: An instance of the BaseImage class.

        """
        # Open the JSON file and load the data
        with open(image_path, 'r') as file:
            image_data = json.load(file)

        height = str(image_data['height'])
        width = str(image_data['width'])
        image= image_data['image']

        return cls(map_id, image,height,width)
    