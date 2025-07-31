# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 16:13:01 2025

@author: aparn
"""

import unittest
from unittest.mock import MagicMock
import xml.etree.ElementTree as ET
from keggmapwizard.svg_content import create_svg_content, _create_namespace, define_legend

class TestSVGCreation(unittest.TestCase):

    def setUp(self):
        # Mock base_image with required attributes
        self.base_image = MagicMock()
        self.base_image.map_id = "map00010"
        self.base_image.image_width = "200"
        self.base_image.image_height = "100"
        self.base_image.image = "encoded_image_data"

        # Mock pathway component with geometry and annotation data
        self.mock_component = MagicMock()
        self.mock_component.pathway_component_id = "e1"
        self.mock_component.pathway_component_geometry = {'cx': 50, 'cy': 60, 'r': 10}
        self.mock_component.pathway_component_geometry_shape = "circle"
        self.mock_component.pathway_annotation_data = {
            'title': "Mock Title",
            'visualizatin_class': ["enzyme"],
            'data_annotation': [{
                "description": "catalyzes conversion",
                "type": "EC",
                "name": "EC:1.1.1.1"
            }]
        }

        # Mock pathway with a title and component list
        self.mock_pathway = MagicMock()
        self.mock_pathway.title = "Mock Pathway"
        self.mock_pathway.pathway_components = [self.mock_component]

    def test_create_namespace_structure(self):
        # Verify that __create_namespace returns a valid SVG root with correct attributes
        doc = _create_namespace(self.base_image, self.mock_pathway.title)

        self.assertEqual(doc.tag, "svg")
        self.assertEqual(doc.attrib["width"], "200")
        self.assertEqual(doc.attrib["height"], "100")
        self.assertIn("xmlns:xlink", doc.attrib)

        # Confirm style tag is present
        style_found = any(child.tag == "style" and child.text.strip() == '.shape {cursor: pointer}' for child in doc)
        self.assertTrue(style_found)

    def test_create_svg_content_builds_shape_elements(self):
        # Test that create_svg_content adds geometry and annotation to SVG
        doc = create_svg_content(self.mock_pathway, self.base_image, None)

        # Look for one circle element inside the <g name='shapes'>
        shapes_group = next((el for el in doc if el.tag == 'g' and el.attrib.get('name') == 'shapes'), None)
        self.assertIsNotNone(shapes_group)

        # Check shape creation
        shape = next((el for el in shapes_group if el.attrib.get("shape_id") == "e1"), None)
        self.assertEqual(shape.tag, "circle")
        self.assertEqual(shape.attrib["class"], "shape enzyme")
        self.assertIn("stroke", shape.attrib)
        self.assertIn("fill", shape.attrib)

    def test_create_svg_content_adds_description_and_title(self):
        # Check that <desc> and <title> are embedded correctly under shape
        doc = create_svg_content(self.mock_pathway, self.base_image, None)
        shape = next(el for el in doc.iter("circle") if el.attrib.get("shape_id") == "e1")
        title = shape.find("title")
        desc = shape.find("desc")

        self.assertIsNotNone(title)
        self.assertIsNotNone(desc)
        self.assertEqual(title.text, "Mock Title")
        self.assertIn("EC:1.1.1.1", desc.text)

    def test_create_svg_content_defines_pattern_image(self):
        # Ensure background image pattern is embedded with correct attributes
        doc = create_svg_content(self.mock_pathway, self.base_image, None)

        pattern = next((el for el in doc.iter("pattern")), None)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.attrib["id"], "00010")
        self.assertEqual(pattern.attrib["width"], "200")
        self.assertEqual(pattern.attrib["height"], "100")

        image = pattern.find("image")
        self.assertIsNotNone(image)
        self.assertEqual(image.attrib["xlink:href"], "data:image/png;base64,encoded_image_data")

    def test_create_svg_content_handles_color_function(self):
        # Simulate custom color function returning an updated doc and color legend
        def mock_color_function(*args, data):
            return data, ["#ff0000", "#00ff00"]

        doc = create_svg_content(self.mock_pathway, self.base_image, mock_color_function)
        defs_tag = next((el for el in doc if el.tag == "defs" and el.attrib.get("id") == "shape-color-defs"), None)
        self.assertIsNotNone(defs_tag)

    def test_create_svg_content_appends_rect_overlay(self):
        # Confirm that rect is appended with a background fill URL referencing the pattern
        doc = create_svg_content(self.mock_pathway, self.base_image, None)
        rect = next((el for el in doc.iter("rect")), None)
        self.assertIsNotNone(rect)
        self.assertEqual(rect.attrib["fill"], "url(#00010)")
        self.assertEqual(rect.attrib["width"], "200")
        self.assertEqual(rect.attrib["height"], "100")

###############################################################################

class TestDefineLegend(unittest.TestCase):

    def setUp(self):
        self.base_image = MagicMock()
        self.base_image.image_width = "200"
        self.base_image.image_height = "100"

        # Mock doc as an XML root element
        self.doc = ET.Element("svg")

    def test_legend_with_white_only(self):
        # Legend should only show 'Absent' label
        updated_doc = define_legend(['white'], self.base_image, self.doc, MagicMock(__name__="color_custom_annotations"))
        
        # Verify 'Absent' text is present
        absent_texts = [el.text for el in updated_doc if el.tag == 'text']
        self.assertIn("Absent", absent_texts)
        self.assertEqual(len(absent_texts), 1)  # Only "Absent" should be present

    def test_legend_with_single_present_color(self):
        # Should append one additional rect + text for "Present"
        updated_doc = define_legend(['red'], self.base_image, self.doc, MagicMock(__name__="color_custom_annotations"))

        texts = [el.text for el in updated_doc if el.tag == 'text']
        self.assertIn("Absent", texts)
        self.assertIn("Present", texts)
        self.assertEqual(len([el for el in updated_doc if el.tag == 'rect']), 2)

    def test_legend_with_multiple_colors_custom_annotations(self):
        # Should add text labels as "org/genome: <counter>"
        color_func = MagicMock()
        color_func.__name__ = "color_custom_annotations"
        updated_doc = define_legend(['red', 'blue', 'white', 'green'], self.base_image, self.doc, color_func)

        labels = [el.text for el in updated_doc if el.tag == 'text']
        expected_labels = ["Absent", "org/genome: 1", "org/genome: 2", "org/genome: 3"]
        for label in expected_labels:
            self.assertIn(label, labels)

    def test_legend_with_multiple_colors_linear_gradient_groups(self):
        # Should add labels formatted as "%_org_in_group: <=<counter>"
        color_func = MagicMock()
        color_func.__name__ = "add_linear_gradient_groups"
        updated_doc = define_legend(['yellow', 'blue', 'white'], self.base_image, self.doc, color_func)

        labels = [el.text for el in updated_doc if el.tag == 'text']
        expected_labels = ["Absent", "%_org_in_group: <=25", "%_org_in_group: <=50"]
        for label in expected_labels:
            self.assertIn(label, labels)

###############################################################################

if __name__ == '__main__':
    unittest.main()