# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 14:14:41 2024

@author: Aparna
"""

from abc import ABC

class PathwayComponent(ABC):
    def __init__(self, data):
        self.x_coordinate = (data['graphics']['x_coordinate'])
        self.y_coordinate = (data['graphics']['y_coordinate'])
        self.coords = data['graphics']['coords']
        self.height = (data['graphics']['height'])
        self.width = (data['graphics']['width'] )
        self.id = data['id']
        self.shape = data['graphics']['type'] 
        self.geometry = None
        self.data = data
        self.data_annotation = None
        
        
   

       

