# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 21:36:54 2025

@author: aparn
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from keggmapwizard.pathway import Pathway


class TestPathway(unittest.TestCase):

    @patch('keggmapwizard.pathway.config')
    @patch('keggmapwizard.pathway.KgmlFile')
    def test_kegg_files_loading(self, MockKgmlFile, mock_config):
        mock_config.working_dir = '/test_dir'
        mock_instance = MagicMock()
        MockKgmlFile.return_value = mock_instance

        pathway = Pathway('hsa00010', ['type1', 'type2'])
        files = pathway.kegg_files

        self.assertEqual(len(files), 2)
        MockKgmlFile.assert_any_call('00010', 'type1', '/test_dir')
        MockKgmlFile.assert_any_call('00010', 'type2', '/test_dir')

    @patch('keggmapwizard.pathway.config')
    @patch('keggmapwizard.pathway.KgmlFile')
    def test_org_files_loading(self, MockKgmlFile, mock_config):
        mock_config.working_dir = '/test_dir'
        
        # Create unique mock instances for each expected call
        mock_instance_eco = MagicMock()
        mock_instance_hsa = MagicMock()
        MockKgmlFile.side_effect = [mock_instance_eco, mock_instance_hsa]
        
        # Make sure the map_id is passed correctly
        pathway = Pathway('eco:hsa:00010', ['orgs'])
        files = pathway.org_files
        
        # Validate file count
        self.assertEqual(len(files), 2)
    
        # Verify exact calls to KgmlFile
        expected_calls = [
            unittest.mock.call('eco00010', 'orgs', '/test_dir'),
            unittest.mock.call('hsa00010', 'orgs', '/test_dir')
        ]
        self.assertEqual(MockKgmlFile.call_args_list, expected_calls)


    @patch('keggmapwizard.pathway.PathwayComponent')
    @patch('keggmapwizard.pathway.KgmlFile')
    @patch('keggmapwizard.pathway.config')
    @patch('keggmapwizard.pathway.GeometryAnnotation')
    def test_pathway_components_merge(
        self, MockGeomAnn, MockConfig, MockKgmlFile, MockPathwayComponent
    ):
        # Setup mocks
        MockConfig.working_dir = '/mock_dir'

        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda k: {
            'id': '1', 'name': 'GeneX', 'type': 'gene'
        }[k]
        mock_entry.find.return_value.get.side_effect = lambda k: '10'

        mock_file = MagicMock()
        mock_file.entries = [mock_entry]
        mock_file.organism = 'eco'
        mock_file.file_name = 'file1'

        MockKgmlFile.return_value = mock_file

        mock_pc = MagicMock()
        mock_pc.is_equivalent.return_value = None
        mock_pc.pathway_component_id = 'pc1'
        mock_pc.retrive_pathway_annotation_data.return_value = None
        mock_pc.merge_pathway_components.return_value = {'pc1': mock_pc}
        MockPathwayComponent.return_value = mock_pc

        mock_ga = MagicMock()
        mock_ga.get_annotation.return_value = {'x': '10', 'annotated': True}
        MockGeomAnn.return_value = mock_ga

        pathway = Pathway('eco00010', ['orgs'])
        result = pathway.pathway_components

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].pathway_annotation_data['annotated'])

    @patch('builtins.open', new_callable=mock_open, read_data="GENE0001\tDesc\tX\tAnnotatedValue\n")
    @patch('pathlib.Path.exists', return_value=True)
    @patch('keggmapwizard.pathway.config')
    @patch('keggmapwizard.pathway.ANNOTATION_SETTINGS', {
        'Gene': {'rest_file': 'eco'},
        'Compound': {'rest_file': 'compound'}
    })
    def test_provide_annotations(self, mock_config, mock_exists, mock_open_file):
        mock_config.working_dir = '/mock_dir'
        pathway = Pathway('eco00010', ['orgs'])
        annotations = pathway._Pathway__provide_annotations(['eco'])

        self.assertIn('Gene', annotations)
        self.assertIn('Compound', annotations)
        self.assertIn('GENE0001', annotations['Gene'])
        self.assertEqual(annotations['Gene']['GENE0001'], 'AnnotatedValue')

    @patch('keggmapwizard.pathway.KgmlFile')
    @patch('keggmapwizard.pathway.config')
    def test_title_and_pathway_number(self, mock_config, MockKgmlFile):
        mock_config.working_dir = '/dir'
        mock_file1 = MagicMock(title='Metabolism', pathway_number='001', organism='eco')
        mock_file2 = MagicMock(title='Energy', pathway_number='002', organism='hsa')
        MockKgmlFile.side_effect = [mock_file1, mock_file2]

        pathway = Pathway('eco:hsa00010', ['orgs'])
        _ = pathway.org_files  # trigger loading

        title = pathway.title
        self.assertIn('Metabolism', title)
        self.assertIn('Energy', title)

        number = pathway.pathway_number
        self.assertIn('001', number)
        self.assertIn('002', number)

        orgs = pathway.org
        self.assertEqual(orgs, 'eco_hsa')

###############################################################################

if __name__ == '__main__':
    unittest.main()

