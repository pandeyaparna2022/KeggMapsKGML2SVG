# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 10:40:05 2025

@author: aparn
"""

import unittest
from unittest.mock import patch
from pathlib import Path
from xml.etree.ElementTree import Element
from keggmapwizard.kegg_file import KgmlFile

class TestKgmlFile(unittest.TestCase):
    def setUp(self):
        # Initialize common test variables for reuse
        self.map_id = "eco00010"
        self.file_type = "ko"
        self.data_dir = "test_data"
        # Create an instance of KgmlFile for testing
        self.kgml = KgmlFile(map_id=self.map_id, file_type=self.file_type, data_directory=self.data_dir)

    def test_file_name_regular(self):
        # Verify correct file name for typical (non-orgs) file types
        self.assertEqual(self.kgml.file_name, "ko00010")

    def test_file_name_orgs(self):
        # Verify file name logic for 'orgs' type, which uses raw map_id
        kgml_org = KgmlFile("b00001", "orgs", self.data_dir)
        self.assertEqual(kgml_org.file_name, "b00001")

    def test_file_directory(self):
        # Validate that file directory is constructed correctly
        expected = Path(self.data_dir) / "kgml_data" / self.file_type
        self.assertEqual(self.kgml.file_directory, expected)

    def test_file_path_regular(self):
        # Validate expected full file path for regular (non-orgs) type
        expected = Path(self.data_dir) / "kgml_data" / self.file_type / "ko00010.xml"
        self.assertEqual(self.kgml.file_path, expected)

    def test_file_path_orgs(self):
        # Validate expected file path construction for 'orgs' type
        kgml_org = KgmlFile("b00001", "orgs", self.data_dir)
        expected = Path(self.data_dir) / "kgml_data" / "orgs" / "b00001.xml"
        self.assertEqual(kgml_org.file_path, expected)

    @patch("xml.etree.ElementTree.parse")
    def test_file_contents_loads_once(self, mock_parse):
        # Simulate an XML root with mock attributes
        root = Element("pathway", attrib={"org": "eco", "title": "Glycolysis", "number": "00010"})
        mock_parse.return_value.getroot.return_value = root

        # First access triggers parsing
        contents1 = self.kgml.file_contents
        # Second access should use cached version
        contents2 = self.kgml.file_contents
        # Confirm both accesses return the same object
        self.assertIs(contents1, contents2)
        # Ensure XML file was parsed only once
        mock_parse.assert_called_once()

    @patch("xml.etree.ElementTree.parse")
    def test_metadata_properties(self, mock_parse):
        # Mock pathway XML with org, title, and number attributes
        root = Element("pathway", attrib={"org": "eco", "title": "Glycolysis", "number": "00010"})
        mock_parse.return_value.getroot.return_value = root

        # Trigger parsing
        _ = self.kgml.file_contents

        # Validate individual metadata extraction
        self.assertEqual(self.kgml.organism, "eco")
        self.assertEqual(self.kgml.title, "Glycolysis")
        self.assertEqual(self.kgml.pathway_number, "00010")

    @patch("xml.etree.ElementTree.parse")
    def test_entries_property(self, mock_parse):
        # Create XML with multiple <entry> elements
        root = Element("pathway")
        entry1 = Element("entry", attrib={"id": "1"})
        entry2 = Element("entry", attrib={"id": "2"})
        root.extend([entry1, entry2])  # Add entries to root
        mock_parse.return_value.getroot.return_value = root

        # Verify that entries are parsed and retrieved correctly
        entries = self.kgml.entries
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].attrib["id"], "1")
        self.assertEqual(entries[1].attrib["id"], "2")

    @patch("xml.etree.ElementTree.parse", side_effect=FileNotFoundError("mocked missing file"))
    def test_read_file_missing(self, mock_parse):
        # Simulate missing file error
        contents = self.kgml.file_contents
        # Expect graceful fallback (returns None)
        self.assertIsNone(contents)

    def test_is_file_cached_behavior(self):
        # By default, the file shouldn't be cached
        self.assertFalse(self.kgml._KgmlFile__is_file_cached())

        # Simulate loaded state manually
        self.kgml._in_memory = True
        self.kgml._KgmlFile__file_contents = "mock"
        # Verify internal cache check returns contents
        self.assertEqual(self.kgml._KgmlFile__is_file_cached(), "mock")

###############################################################################

if __name__ == '__main__':
    unittest.main()