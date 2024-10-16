# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:36:21 2024

@author: aparn
"""

import unittest
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET
from keggmapwizard.color_function_base import color_all, color_org, color_custom_annotations, set_gradient  


class TestColorFunctions(unittest.TestCase):

    def setUp(self):
        # Create a mock XML structure for testing
        self.root = ET.Element('svg', {
            'title': "Maturity onset diabetes of the young",
            'id': "kegg-svg-04950",
            'width': "891",
            'height': "970",
            'version': "1.1",
            'baseprofile': "full",
            'xmlns': "http://www.w3.org/2000/svg",
            'xmlns:xlink': "http://www.w3.org/1999/xlink"
        })
        
        # Add style element
        style = ET.SubElement(self.root, 'style')
        style.text = ".shape {cursor: pointer}"

        # Create a group element with name "shapes"
        self.group = ET.SubElement(self.root, 'g', {'name': 'shapes'})

        # Create first rectangle with title and description
        rect1 = ET.SubElement(self.group, 'rect', {
            'shape_id': "7",
            'stroke': "black",
            'fill': "transparent",
            'style': "stroke-opacity: 1",
            'x': "336.0",
            'y': "390.5",
            'height': "17",
            'width': "46",
            'rx': "0",
            'ry': "0",
            'stroke-width': "1.5",
            'class': "shape gene enzyme"
        })
        desc1 = ET.SubElement(rect1, 'desc')
        desc1.text = "[{'type': 'K', 'name': 'K08034', 'description': 'TCF2%2C%20HNF1B%3B%20transcription%20factor%202%2C%20hepatocyte%20nuclear%20factor%201-beta'}, {'type': 'Gene', 'name': 'mmu:21410', 'description': 'Hnf1b%2C%20HNF-1-beta%2C%20HNF-1B%2C%20HNF-1Beta%2C%20Hnf1beta%2C%20LFB3%2C%20Tcf-2%2C%20Tcf2%2C%20vHNF1%3B%20HNF1%20homeobox%20B'}]"
        title1 = ET.SubElement(rect1, 'title')
        title1.text = "['K08034 (TCF2, HNF1B)', 'mmu:21410 (Hnf1b, HNF-1-beta, HNF-1B, HNF-1Beta, Hnf1beta, LFB3, Tcf-2, Tcf2, vHNF1)']"

        # Create second rectangle with title and description
        rect2 = ET.SubElement(self.group, 'rect', {
            'shape_id': "8",
            'stroke': "black",
            'fill': "transparent",
            'style': "stroke-opacity: 1",
            'x': "461.0",
            'y': "344.5",
            'height': "17",
            'width': "46",
            'rx': "0",
            'ry': "0",
            'stroke-width': "1.5",
            'class': "shape gene enzyme"
        })
        desc2 = ET.SubElement(rect2, 'desc')
        desc2.text = "[{'type': 'K', 'name': 'K06054', 'description': 'HES1%3B%20hairy%20and%20enhancer%20of%20split%201'}, {'type': 'Gene', 'name': 'mmu:15205', 'description': 'Hes1%2C%20Hry%2C%20bHLHb39%3B%20hes%20family%20bHLH%20transcription%20factor%201'}]"
        title2 = ET.SubElement(rect2, 'title')
        title2.text = "['K06054 (HES1)', 'mmu:15205 (Hes1, Hry, bHLHb39)']"

        # Store the root for use in tests
        self.data = self.root

 

    def test_color_all_default_color(self):
        # Test color_all with default color
        root, _ = color_all(data=self.data)

        # Check that the fill and stroke attributes were set
        for element in root.find('.//g'):
            self.assertEqual(element.get('fill'), 'blue')
            self.assertEqual(element.get('stroke'), 'blue')
            self.assertEqual(element.get('stroke-width'), '3')
            self.assertEqual(element.get('fill-opacity'), '0.15')

    def test_color_all_custom_color(self):
        # Test color_all with a custom color
        root, _ = color_all('red', data=self.data)

        # Check that the fill and stroke attributes were set to the custom color
        for element in root.find('.//g'):
            self.assertEqual(element.get('fill'), 'red')
            self.assertEqual(element.get('stroke'), 'red')
            self.assertEqual(element.get('stroke-width'), '3')
            self.assertEqual(element.get('fill-opacity'), '0.15')

    def test_color_org_default_color(self):
        # Test color_org with default color
        root, colors = color_org('shape1', data=self.data)

        # Check that the stroke attributes were set
        for element in root.find('.//g'):
            if element.find('title').text == 'shape1':
                self.assertEqual(element.get('stroke'), 'blue')
                self.assertEqual(element.get('fill'), 'blue')
                self.assertEqual(element.get('stroke-width'), '3')
                self.assertEqual(element.get('fill-opacity'), '0.15')

    def test_color_org_custom_color(self):
        # Test color_org with a custom color
        root, colors = color_org('shape1', 'green', data=self.data)

        # Check that the stroke attributes were set to the custom color
        for element in root.find('.//g'):
            if element.find('title').text == 'shape1':
                self.assertEqual(element.get('stroke'), 'green')
                self.assertEqual(element.get('fill'), 'green')
                self.assertEqual(element.get('stroke-width'), '3')
                self.assertEqual(element.get('fill-opacity'), '0.15')
                
    def test_set_gradient(self):
        """Test set_gradient function."""
        shape_element = ET.SubElement(self.group, 'shape', shape_id='shape1')
        defs = ET.SubElement(self.root, 'defs')
        colors = ['red', 'blue']
        result_defs = set_gradient('shape1', shape_element, defs, colors)
        
        # Check if gradient is created correctly
        self.assertEqual(len(result_defs), 1)  # Should have one defs element
        gradient = result_defs.find('linearGradient')
        self.assertIsNotNone(gradient)
        self.assertEqual(gradient.get('id'), 'gradient_shape1')
        self.assertEqual(shape_element.get('fill'), 'url(#gradient_shape1)')
        self.assertEqual(shape_element.get('stroke'), 'url(#gradient_shape1)')
        
 
if __name__ == "__main__":
    unittest.main()
