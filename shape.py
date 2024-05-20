# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 17:48:42 2024

@author: Aparna
"""
from abc import abstractmethod
from pathway_component import PathwayComponent

class Shape(PathwayComponent):
    def __init__(self, data):
        super().__init__(data)
        
    @abstractmethod
    def calc_geometry(self):
        pass

 
class Line(Shape):
    def calc_geometry(self):
        # Convert the geometry string to a list of integers
        coords = [int(i) for i in self.coords.split(',')]  # convert to int to catch errors
        # Assert no. of coordinates are even
        assert len(coords) % 2 == 0, f'number of polygon coordinates must be even! {coords} -> {coords}'
        # Group the coordinates into pairs to create points
        points = [(coords[l * 2], coords[l * 2 + 1]) for l in range(len(coords) // 2)]
        # Create a shape_path string in the format 'M x1,y1 L x2,y2 L x3,y3 ...'
        # eg: [(1, 2), (3, 4), (5, 6)] => 'M 1,2 L 3,4 L 5,6'.    
        d = 'M ' + ' L '.join(f'{x},{y}' for x, y in points)
        
        self.geometry = {
            #'id':self.id,
            #'shape': 'path',
            'd': d
            }
        self.shape ='path'
        return self.geometry 
       

class Circle(Shape):
    def calc_geometry(self):
        
        # Calculate the radius of the  and assign x and y coordinates to cs and cy
        self.geometry = {
            #'id':self.id,
            #'shape': 'path',
            # Calculate the radius
            'r': int(self.width) / 2,
            'cx': int(self.x_coordinate),
            'cy': int(self.y_coordinate)
        }
        self.shape =  'circle'
        return self.geometry

 
class Rectangle(Shape):
    def calc_geometry(self):
        
        # Modify the x and y coordinates for svg (KGML specific issue)
        if int(self.width) > 46 and int(self.height) >17:
            x_coordinate=int(self.x_coordinate)+0.7
            y_coordinate=int(self.y_coordinate)+0.7
        # Adjust the x and y coordinates based on the width and height
        x_coordinate = int(self.x_coordinate)-(int(self.width)/2)
        y_coordinate = int(self.y_coordinate)-(int(self.height)/2)
        # Set the rx and ry values
        if self.shape == 'roundrectangle':
            x_coordinate=x_coordinate+ 1 
            y_coordinate = y_coordinate + 1
            rx=10
            ry= 10
        else:
            rx=0
            ry=0
        self.shape = 'rect'  
        
        # Calculate the radius of the  and assign x and y coordinates to cs and cy
        self.geometry = {
            #'id':self.id,
            #'shape': 'rect',
            'x': x_coordinate,
            'y': y_coordinate,
            'height': self.height,
            'width': self.width,
            'rx' : rx,
            'ry' : ry
        }
        return self.geometry