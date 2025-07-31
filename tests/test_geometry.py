# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 15:58:53 2025

@author: aparn
"""
import unittest
from keggmapwizard.geometry import Geometry, Line, Circle, Rectangle, geometry_factory 

class TestGeometry(unittest.TestCase):

    def test_geometry_base_attributes(self):
        # Tests that Geometry base class correctly stores shape type and coordinates
        coords = {'x': 10, 'y': 20}
        shape = 'circle'
        obj = Geometry(coords, shape)
        self.assertEqual(obj.geometry_coords, coords)
        self.assertEqual(obj.geometry_shape, shape)

    def test_line_geometry_details_valid(self):
        # Tests parsing a valid line input into a correct SVG path string
        data = {
            'graphics': {
                'coords': '10,20,30,40,50,60',
                'type': 'line'
            }
        }
        line_obj = Line.geometry_details(data)
        expected = 'M 10,20 L 30,40 L 50,60'
        self.assertEqual(line_obj.geometry_coords['d'], expected)
        self.assertEqual(line_obj.geometry_shape, 'path')

    def test_line_geometry_details_odd_coordinates_raises(self):
        # Tests that an odd number of coordinates in a line raises an error
        data = {
            'graphics': {
                'coords': '10,20,30',  # Invalid length
                'type': 'line'
            }
        }
        with self.assertRaises(AssertionError):
            Line.geometry_details(data)

    def test_circle_geometry_details(self):
        # Tests circle parsing: correct radius and center point
        data = {
            'graphics': {
                'x': '100',
                'y': '200',
                'width': '40',
                'type': 'circle'
            }
        }
        circle = Circle.geometry_details(data)
        self.assertEqual(circle.geometry_coords['cx'], 100)  # center x
        self.assertEqual(circle.geometry_coords['cy'], 200)  # center y
        self.assertEqual(circle.geometry_coords['r'], 20)    # radius
        self.assertEqual(circle.geometry_shape, 'circle')

    def test_rectangle_geometry_details_regular(self):
        # Tests regular rectangle coordinates and dimensions
        data = {
            'graphics': {
                'x': '100',
                'y': '100',
                'width': '40',
                'height': '20',
                'type': 'rectangle'
            }
        }
        rect = Rectangle.geometry_details(data)
        self.assertEqual(rect.geometry_coords['rx'], 0)  # corner radius x
        self.assertEqual(rect.geometry_coords['ry'], 0)  # corner radius y
        self.assertEqual(rect.geometry_shape, 'rect')

    def test_rectangle_geometry_details_round(self):
        # Tests round rectangle behavior including coordinate shift and corner rounding
        data = {
            'graphics': {
                'x': '100',
                'y': '100',
                'width': '80',
                'height': '30',
                'type': 'roundrectangle'
            }
        }
        rect = Rectangle.geometry_details(data)
        self.assertEqual(rect.geometry_coords['rx'], 10)  # rounded corner x
        self.assertEqual(rect.geometry_coords['ry'], 10)  # rounded corner y
        self.assertEqual(rect.geometry_shape, 'rect')
        self.assertTrue(rect.geometry_coords['x'] > 0)    # ensure valid x
        self.assertTrue(rect.geometry_coords['y'] > 0)    # ensure valid y

    def test_geometry_factory_line(self):
        # Tests the factory for line type returns a Line instance
        data = {'graphics': {'coords': '0,0,100,100', 'type': 'line'}}
        result = geometry_factory(data)
        self.assertIsInstance(result, Line)
        self.assertEqual(result.geometry_shape, 'path')

    def test_geometry_factory_circle(self):
        # Tests the factory for circle type returns a Circle instance
        data = {'graphics': {'x': '10', 'y': '20', 'width': '40', 'type': 'circle'}}
        result = geometry_factory(data)
        self.assertIsInstance(result, Circle)
        self.assertEqual(result.geometry_shape, 'circle')

    def test_geometry_factory_rectangle(self):
        # Tests the factory for rectangle type returns a Rectangle instance
        data = {'graphics': {'x': '10', 'y': '20', 'width': '40', 'height': '20', 'type': 'rectangle'}}
        result = geometry_factory(data)
        self.assertIsInstance(result, Rectangle)
        self.assertEqual(result.geometry_shape, 'rect')

    def test_geometry_factory_roundrectangle(self):
        # Tests the factory for roundrectangle type returns a Rectangle instance with rounded attributes
        data = {'graphics': {'x': '10', 'y': '20', 'width': '50', 'height': '20', 'type': 'roundrectangle'}}
        result = geometry_factory(data)
        self.assertIsInstance(result, Rectangle)
        self.assertEqual(result.geometry_shape, 'rect')

    def test_geometry_factory_unknown_type(self):
        # Tests that an unknown type returns None from the factory
        data = {'graphics': {'type': 'unknown'}}
        result = geometry_factory(data)
        self.assertIsNone(result)
   
###############################################################################

if __name__ == '__main__':
    unittest.main()