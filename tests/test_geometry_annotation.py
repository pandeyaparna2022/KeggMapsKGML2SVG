# -*- coding: utf-8 -*-
"""
Created on Wed Jul 01 10:21:46 2025

@author: aparn
"""

import unittest
from keggmapwizard.annotation_settings import ANNOTATION_SETTINGS
from keggmapwizard.geometry_annotation import GeometryAnnotation  

class TestGeometryAnnotation(unittest.TestCase):

    def setUp(self):
        # Set up a fresh instance for each test
        self.annotator = GeometryAnnotation()

        # Mock annotation data that mimics external resources
        self.mock_annotations = {
            'C': {'C001': "Glucose; a sweet compound"},
            'EC': {'1.1.1.1': "Alcohol dehydrogenase"},
            'Gene': {'gene123': "Hypothetical gene"},
            'MAP': {'map00010': "Glycolysis / Gluconeogenesis"},
            'R': {'R001': "Reaction step 1"},
            'BR': {'br123': "Some Brite hierarchy"},
        }

    def test_repr_output(self):
        # Test the __repr__ method for initial/default values
        repr_str = repr(self.annotator)
        self.assertEqual(repr_str, "<KeggAnnotation: N/A - N/A>")

    def test_get_description_found(self):
        # Ensure _get_description returns expected text for valid input
        desc = self.annotator._get_description("C", "C001", self.mock_annotations)
        self.assertIn("Glucose", desc)

    def test_get_description_not_found(self):
        # Return empty string if key not found in annotations
        desc = self.annotator._get_description("C", "XYZ", self.mock_annotations)
        self.assertEqual(desc, "")

    def test_get_annotation_compound(self):
        # Validate correct processing of 'compound' query type
        queries = [{'type': 'compound', 'name': 'cpd:C001'}]
        result = self.annotator.get_annotation(queries, self.mock_annotations)

        self.assertIn('title', result)
        self.assertIn('visualizatin_class', result)
        self.assertIn('data_annotation', result)

        # Check correct assignment of type and name
        self.assertEqual(result['data_annotation'][0]['type'], 'C')
        self.assertEqual(result['data_annotation'][0]['name'], 'C001')

    def test_get_annotation_ec(self):
        # Check enzyme query handling and EC name formatting
        queries = [{'type': 'enzyme', 'name': '1.1.1.1'}]
        result = self.annotator.get_annotation(queries, self.mock_annotations)

        self.assertEqual(result['data_annotation'][0]['type'], 'EC')
        self.assertEqual(result['data_annotation'][0]['name'], 'EC:1.1.1.1')

    def test_get_annotation_map(self):
        # Verify map ID formatting and annotation lookup
        queries = [{'type': 'map', 'name': '00010'}]
        result = self.annotator.get_annotation(queries, self.mock_annotations)

        self.assertEqual(result['data_annotation'][0]['type'], 'MAP')
        self.assertEqual(result['data_annotation'][0]['name'], 'map00010')

    def test_get_annotation_gene(self):
        # Handle gene queries with prefixed naming convention
        queries = [{'type': 'gene', 'name': 'gene:gene123'}]
        result = self.annotator.get_annotation(queries, self.mock_annotations)

        self.assertEqual(result['data_annotation'][0]['type'], 'Gene')
        self.assertEqual(result['data_annotation'][0]['name'], 'gene:gene123')

    def test_invalid_query_type_assertion(self):
        # Confirm assertion failure on unknown query types
        queries = [{'type': 'notatype', 'name': 'value'}]
        with self.assertRaises(AssertionError):
            self.annotator.get_annotation(queries, self.mock_annotations)

    def test_multiple_query_names(self):
        # Test multiple annotations in one query string
        queries = [{'type': 'brite', 'name': 'br:br123 br:br999'}]
        result = self.annotator.get_annotation(queries, self.mock_annotations)

        # Validate that two entries were generated
        self.assertEqual(len(result['data_annotation']), 2)
        self.assertIn('BR', [d['type'] for d in result['data_annotation']])
        
###############################################################################

class TestAnnotationSettings(unittest.TestCase):

    def setUp(self):
        # List of all expected annotation codes
        self.expected_keys = [
            'K', 'EC', 'R', 'RC', 'C', 'G', 'D', 'DG',
            'BR', 'MAP', 'GR', 'O', 'Gene'
        ]

        # List of expected keys inside each annotation config
        self.sub_keys = ['html_class', 'type', 'rest_file', 'descr_prefix']

    def test_keys_existence(self):
        # Confirm all expected annotation keys exist
        for key in self.expected_keys:
            self.assertIn(key, ANNOTATION_SETTINGS, f"Missing key: {key}")

    def test_subkeys_structure(self):
        # Each annotation entry must contain required subkeys
        for code, config in ANNOTATION_SETTINGS.items():
            for subkey in self.sub_keys:
                self.assertIn(subkey, config, f"{code} missing subkey: {subkey}")

    def test_html_classes_are_strings(self):
        # Validate 'html_class' field is a string
        for config in ANNOTATION_SETTINGS.values():
            self.assertIsInstance(config['html_class'], str)

    def test_types_are_strings(self):
        # Validate 'type' field is a string
        for config in ANNOTATION_SETTINGS.values():
            self.assertIsInstance(config['type'], str)

    def test_rest_files_are_strings(self):
        # Validate 'rest_file' field is a string (including empty)
        for config in ANNOTATION_SETTINGS.values():
            self.assertIsInstance(config['rest_file'], str)

    def test_descr_prefix_is_string(self):
        # Validate 'descr_prefix' field is a string (including empty)
        for config in ANNOTATION_SETTINGS.values():
            self.assertIsInstance(config['descr_prefix'], str)

    def test_expected_html_class_duplicates(self):
        allowed_duplicates = {'enzyme', 'compound', 'undefined'}
        html_classes = [config['html_class'] for config in ANNOTATION_SETTINGS.values()]
        duplicates = [cls for cls in html_classes if html_classes.count(cls) > 1 and cls not in allowed_duplicates]
        self.assertEqual(duplicates, [], f"Unexpected duplicate html_class values found: {duplicates}")


    def test_prefix_consistency_for_non_empty_entries(self):
        # If rest_file is non-empty, prefix should also be defined (can be empty for MAP, BR)
        for key, config in ANNOTATION_SETTINGS.items():
            if config['rest_file']:  # Only check those that point to an actual resource
                self.assertIn('descr_prefix', config)
                self.assertIsInstance(config['descr_prefix'], str)

        
###############################################################################

if __name__ == '__main__':
    unittest.main()

