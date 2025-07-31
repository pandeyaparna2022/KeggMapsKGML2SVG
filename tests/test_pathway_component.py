# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 16:04:54 2025

@author: aparn
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from keggmapwizard.pathway_component import PathwayComponent  

class TestPathwayComponent(unittest.TestCase):

    def setUp(self):
        # Prepare a common entry used across multiple tests
        self.entry = {
            'id': 'pc1',
            'name': ['map12345'],
            'type': ['map'],
            'graphics': {
                'type': 'circle',
                'x': '100',
                'y': '150',
                'width': '20'
            }
        }

    def test_initialization_sets_geometry(self):
        # Checks that initialization correctly sets up geometry shape and coordinates
        component = PathwayComponent(self.entry)
        self.assertEqual(component.pathway_component_id, 'pc1')
        self.assertEqual(component.pathway_component_geometry_shape, 'circle')
        self.assertIn('cx', component.pathway_component_geometry)

    def test_retrieve_pathway_annotation_for_map_type(self):
        # Verifies annotation retrieval modifies map name properly for 'map' types
        component = PathwayComponent(self.entry)
        component.retrive_pathway_annotation_data()
        self.assertEqual(component.pathway_annotation_data[0]['name'], 'map12345')
        self.assertEqual(component.pathway_annotation_data[0]['type'], 'map')

    def test_retrieve_pathway_annotation_for_non_map(self):
        # Ensures names are preserved when entry type is not 'map'
        entry = self.entry.copy()
        entry['type'] = ['gene']
        component = PathwayComponent(entry)
        component.retrive_pathway_annotation_data()
        self.assertEqual(component.pathway_annotation_data[0]['name'], 'map12345')
        self.assertEqual(component.pathway_annotation_data[0]['type'], 'gene')

    def test_is_equivalent_returns_none_if_id_missing(self):
        # If entry ID isn't in existing components, should return None
        component = PathwayComponent(self.entry)
        existing = {}
        result = component.is_equivalent(existing, 'testfile')
        self.assertIsNone(result)

    def test_is_equivalent_geometry_matches(self):
        # If geometry matches, should return the component
        component = PathwayComponent(self.entry)
        existing = {
            'pc1': MagicMock(pathway_component_geometry=component.pathway_component_geometry)
        }
        result = component.is_equivalent(existing, 'file')
        self.assertEqual(result['pc1'], existing['pc1'])

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('keggmapwizard.config.config.working_dir', Path("/tmp"))
    def test_is_equivalent_geometry_diff_writes_file(self, mock_open, mock_exists, mock_mkdir):
        # If geometry differs, file should be created and content written
        component = PathwayComponent(self.entry)
        mock_geom = component.pathway_component_geometry.copy()
        mock_geom['cx'] += 1  # Change geometry

        existing = {
            'pc1': MagicMock(pathway_component_geometry=mock_geom)
        }
        result = component.is_equivalent(existing, 'example')
        mock_open.assert_called_once()  # ensure file opened
        mock_mkdir.assert_called_once_with('Inconsistent_KGML')
        self.assertEqual(result['pc1'], existing['pc1'])

    def test_merge_pathway_components_adds_annotation(self):
        # Tests that annotation gets appended if not present
        component = PathwayComponent(self.entry)
        component.retrive_pathway_annotation_data()

        existing = {
            'pc1': MagicMock(pathway_annotation_data=[])
        }
        result = component.merge_pathway_components(existing)
        self.assertEqual(len(result['pc1'].pathway_annotation_data), 1)

    def test_merge_pathway_components_skips_duplicate_annotation(self):
        # If annotation is already present, should not add a duplicate
        component = PathwayComponent(self.entry)
        component.retrive_pathway_annotation_data()

        existing = {
            'pc1': MagicMock(pathway_annotation_data=[
                {'name': 'map12345', 'type': 'map'}
            ])
        }
        result = component.merge_pathway_components(existing)
        self.assertEqual(len(result['pc1'].pathway_annotation_data), 1)

###############################################################################

if __name__ == '__main__':
    unittest.main()