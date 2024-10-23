# -*- coding: utf-8 -*-

import os
import re
import sys
from io import BytesIO, StringIO
from PIL import Image
import json
import unittest
from unittest.mock import patch, mock_open, MagicMock
import urllib.error
from keggmapwizard.download_data import download_data, download_rest_data, extract_all_map_ids, encode_png, check_input
from keggmapwizard.utils import KEGG_MAP_WIZARD_DATA as DATA_DIR  # Import DATA_DIR

class TestDownloadData(unittest.TestCase):

    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_kgml_file(self, mock_file, mock_urlopen):
        # Mock the response from urlopen
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'<xml>data</xml>'
        
        url = 'http://rest.kegg.jp/get/sample/kgml'
        arg = 'sample'
        path = 'test_directory'
        
        download_data(url, arg, path, verbose=False)

        # Check if the file was saved correctly
        mock_file.assert_called_once_with('test_directory/sample.xml', 'w')
        mock_file().write.assert_called_once_with('<xml>data</xml>')

    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_png_file(self, mock_file, mock_urlopen):
        # Mock the response from urlopen
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        
        url = 'https://www.genome.jp/kegg/pathway/map/map1.png'
        arg = '1'
        path = 'test_directory'
        
        download_data(url, arg, path, verbose=False)

        # Check if the PNG file was saved correctly
        mock_file.assert_called_once_with('test_directory/map1.png', 'wb')
        mock_file().write.assert_called_once_with(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')

    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_text_file(self, mock_file, mock_urlopen):
        # Mock the response from urlopen
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'This is a test.'
        
        url = 'http://example.com/data'
        arg = 'test'
        path = 'test_directory'
        
        download_data(url, arg, path, verbose=False)

        # Check if the text file was saved correctly
        mock_file.assert_called_once_with('test_directory/test.txt', 'w')
        mock_file().write.assert_called_once_with('This is a test.')

    @patch('urllib.request.urlopen')
    def test_http_error_handling(self, mock_urlopen):
        # Mock an HTTP error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url='http://example.com',
            code=404,
            msg='Not Found',
            hdrs=None,
            fp=None
        )
        
        url = 'http://example.com/data'
        arg = 'test'
        path = 'test_directory'
        
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            download_data(url, arg, path, verbose=False)
            # Check if the bad request was logged
            mock_file.assert_any_call('test_directory/bad_requests.txt', 'a')
            mock_file().write.assert_any_call('test\n')

###############################################################################


    @patch('os.makedirs')
    @patch('os.path.isfile')
    @patch('builtins.print')
    @patch('keggmapwizard.download_data.download_data')  
    @patch('keggmapwizard.download_data.check_bad_requests')
    def test_download_new_files(self, mock_check_bad_requests, mock_download_data, mock_print, mock_isfile, mock_makedirs):
        # Setup
        mock_isfile.side_effect = lambda x: False  # Simulate that no files exist
        mock_check_bad_requests.return_value = ['file1', 'file2']
        args_list = ['file1', 'file2', 'file3']

        # Call the function
        download_rest_data(args_list, reload=False, verbose=True)

        # Assertions
        mock_makedirs.assert_called_once()  # Check if directory creation was called
        mock_check_bad_requests.assert_called_once_with(args_list, f'{DATA_DIR}/rest_data/', 'bad_requests.txt', True)
        mock_download_data.assert_any_call('https://rest.kegg.jp/list/file1', 'file1', f'{DATA_DIR}/rest_data/', True)
        mock_download_data.assert_any_call('https://rest.kegg.jp/list/file2', 'file2', f'{DATA_DIR}/rest_data/', True)
        self.assertEqual(mock_download_data.call_count, 2)  # Ensure download_data was called twice

    @patch('os.makedirs')
    @patch('os.path.isfile')
    @patch('builtins.print')
    @patch('keggmapwizard.download_data.check_bad_requests')
    def test_no_files_to_download(self, mock_check_bad_requests, mock_print, mock_isfile, mock_makedirs):
        # Setup
        mock_isfile.side_effect = lambda x: True  # Simulate that all files exist
        mock_check_bad_requests.return_value = []
        args_list = ['file1', 'file2']

        # Call the function
        download_rest_data(args_list, reload=False, verbose=True)

        # Assertions
        mock_print.assert_called_once_with("No new files to download.")  # Check if no files message was printed

    @patch('os.makedirs')
    @patch('os.path.isfile')
    @patch('builtins.print')
    @patch('keggmapwizard.download_data.download_data')
    @patch('keggmapwizard.download_data.check_bad_requests')
    def test_reload_option(self, mock_check_bad_requests, mock_download_data, mock_print, mock_isfile, mock_makedirs):
        # Setup
        mock_isfile.side_effect = lambda x: True  # Simulate that files already exist
        mock_check_bad_requests.return_value = ['file1', 'file2']
        args_list = ['file1', 'file2']

        # Call the function with reload=True
        download_rest_data(args_list, reload=True, verbose=True)

        # Assertions
        self.assertEqual(mock_download_data.call_count, 2)  # Ensure download_data was called twice even if files exist

###############################################################################


    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data='map00001\nmap00002\nmap00003\n')
    @patch('keggmapwizard.download_data.download_data')  
    def test_extract_map_ids_file_exists(self, mock_download_data, mock_open, mock_makedirs, mock_isfile, mock_exists):
        # Setup
        mock_exists.side_effect = lambda x: True  # Simulate that the directory exists
        mock_isfile.return_value = True  # Simulate that the pathway.txt file exists

        # Call the function
        result = extract_all_map_ids()

        # Assertions
        mock_open.assert_called_once_with(f'{DATA_DIR}/rest_data/pathway.txt', 'r')  # Check if the file was opened
        self.assertEqual(result, ['00001', '00002', '00003'])  # Check if the extracted map IDs are correct
        mock_download_data.assert_not_called()  # Ensure download_data was not called

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data='map00001\nmap00002\nmap00003\n')
    @patch('keggmapwizard.download_data.download_data')  # Replace 'your_module' with the actual module name
    def test_extract_map_ids_file_does_not_exist(self, mock_download_data, mock_open, mock_makedirs, mock_isfile, mock_exists):
        # Setup
        mock_exists.side_effect = lambda x: True  # Simulate that the directory exists
        mock_isfile.return_value = False  # Simulate that the pathway.txt file does not exist

        # Call the function
        result = extract_all_map_ids()

        # Assertions
        mock_open.assert_called_once_with(f'{DATA_DIR}/rest_data/pathway.txt', 'r')  # Check if the file was opened
        self.assertEqual(result, ['00001', '00002', '00003'])  # Check if the extracted map IDs are correct
        mock_download_data.assert_called_once_with("https://rest.kegg.jp/list/pathway", 'pathway', f'{DATA_DIR}/rest_data', verbose=True)  # Ensure download_data was called
###############################################################################

    @patch('keggmapwizard.download_data.Image.open')
    @patch('keggmapwizard.download_data.BytesIO')
    @patch('keggmapwizard.download_data.base64.b64encode')
    @patch('keggmapwizard.download_data.open', new_callable=mock_open)
    @patch('keggmapwizard.download_data.os.path.isfile')
    def test_encode_png(self, mock_isfile, mock_open_file, mock_b64encode, mock_bytes_io, mock_image_open):
        # Setup
        mock_isfile.return_value = True  # Simulate that the file exists
        
        # Create a mock image object
        mock_image = MagicMock(spec=Image.Image)
        # Set the return value of Image.open to the mock image
        mock_image_open.return_value = mock_image
        
        # Simulate the behavior of convert method
        converted_image = MagicMock(spec=Image.Image)
        mock_image.convert.return_value = converted_image
        
        # Simulate the size of the image
        converted_image.size = (4, 4)  # Example size (width, height)
        
        # Simulate the load method to return a mock pixel access object
        mock_pixdata = MagicMock()
        
        # Set up the mock pixel access object to return RGBA values
        mock_pixdata.__getitem__.side_effect = lambda x: (255, 255,255, 255)  # Example RGBA values
        
        converted_image.load.return_value = mock_pixdata

        # Mock the BytesIO object
        mock_buffer = BytesIO()
        mock_bytes_io.return_value = mock_buffer
        
        # Mock base64 encoding
        mock_b64encode.return_value = b'mock_base64_encoded_data'

        # Call the function
        encode_png('test_image.png')

        # Check if the image was opened
        mock_image_open.assert_called_once_with('test_image.png')

        # Check if the image was converted to 'RGBA'
        mock_image.convert.assert_called_once_with('RGBA')

        # Check if the image was saved to the buffer
        converted_image.save.assert_called_once_with(mock_buffer, 'PNG')

        # Check if the JSON file was written correctly
        mock_open_file.assert_called_once_with('test_image.png.json', 'w')
###############################################################################
class TestCheckInput(unittest.TestCase):

    def setUp(self):
        # Redirect stdout to capture print statements
        self.held_output = StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        # Reset redirect.
        sys.stdout = sys.__stdout__

    def test_valid_map_ids(self):
        result = check_input(['1', '2', '3'])
        self.assertEqual(result, ['00001', '00002', '00003'])

    def test_invalid_map_id_too_long(self):
        result = check_input(['123456'])
        self.assertEqual(result, [])
        self.assertIn("123456 is Not a valid map_id. Maximum length allowd for a map number is 5.", self.held_output.getvalue())

    def test_invalid_map_id_characters_only(self):
        result = check_input(['abcde'])
        self.assertEqual(result, [])
        self.assertIn("abcde is Not a valid map_id. Map id cannot just be characters.", self.held_output.getvalue())

    def test_invalid_map_id_mixed_characters(self):
        result = check_input(['map123456'])
        self.assertEqual(result, [])
        self.assertIn("map123456 is Not a valid map_id. Maximum length allowd for a map number is 5 .", self.held_output.getvalue())

    def test_non_list_input(self):
        result = check_input('not_a_list')
        self.assertEqual(result, [])
        self.assertIn("map_ids is not a list. Please provide a list of map IDs.", self.held_output.getvalue())

    def test_empty_list(self):
        result = check_input([])
        self.assertEqual(result, [])
###############################################################################

if __name__ == '__main__':
    unittest.main()
