# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 12:30:39 2024

@author: aparn
"""

import unittest  # Import the unittest module for creating unit tests.
from unittest.mock import patch, mock_open  # Import patch and mock_open for mocking file operations.
import json  # Import the json module to handle JSON data.


from keggmapwizard.base_image import BaseImage  

class TestBaseImage(unittest.TestCase):
    """Test case class for the BaseImage class."""

    def test_initialization(self):
        """Test the initialization of the BaseImage class."""
        map_id = "test_map"  # Define a test map ID.
        image_data = "image_data_placeholder"  # Define placeholder image data.
        height = 100  # Define a test height for the image.
        width = 200  # Define a test width for the image.
        
        # Create an instance of BaseImage with the test data.
        base_image = BaseImage(map_id, image_data, height, width)
        
        # Assert that the map_id attribute is set correctly.
        self.assertEqual(base_image.map_id, map_id)
        # Assert that the image attribute is set correctly.
        self.assertEqual(base_image.image, image_data)
        # Assert that the image_height attribute is set correctly.
        self.assertEqual(base_image.image_height, height)
        # Assert that the image_width attribute is set correctly.
        self.assertEqual(base_image.image_width, width)

    @patch("builtins.open", new_callable=mock_open, read_data='{"height": 100, "width": 200, "image": "image_data_placeholder"}')
    def test_from_png(self, mock_file):
        """Test the from_png class method."""
        map_id = "test_map"  # Define a test map ID for the from_png method.
        image_path = "dummy_path.json"  # Define a dummy path for the image file.
        
        # Call the from_png method to create a BaseImage instance from the mocked file data.
        base_image = BaseImage.from_png(map_id, image_path)
        
        # Assert that the map_id attribute is set correctly.
        self.assertEqual(base_image.map_id, map_id)
        # Assert that the image_height attribute is set correctly (as a string).
        self.assertEqual(base_image.image_height, "100")  # Note: height is stored as str
        # Assert that the image_width attribute is set correctly (as a string).
        self.assertEqual(base_image.image_width, "200")   # Note: width is stored as str
        # Assert that the image attribute is set correctly.
        self.assertEqual(base_image.image, "image_data_placeholder")
        
        # Ensure that the file was opened with the correct path and mode.
        mock_file.assert_called_once_with(image_path, 'r')

# This block allows the test to be run directly from the command line.
if __name__ == "__main__":
    unittest.main()  # Run all the test cases defined in the TestBaseImage class.
