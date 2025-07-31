# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 12:40:14 2025

@author: aparn
"""

import os
import re
import sys
from io import BytesIO, StringIO
from PIL import Image
import json
import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import urllib.error
from pathlib import Path
from keggmapwizard.download_data import download_data, download_rest_data, extract_all_map_ids, encode_png, check_input, check_bad_requests, download_base_png_maps
from keggmapwizard.config import config
import tempfile
import base64
DATA_DIR = config.working_dir



class TestDownloadData(unittest.TestCase):
    
    @patch('pathlib.Path.mkdir')  # Prevent actual directory creation
    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_kgml_file(self, mock_file, mock_urlopen, mock_mkdir):
        # Mock the response from urlopen
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'<xml>data</xml>'
        
        url = 'http://rest.kegg.jp/get/sample/kgml'
        arg = 'sample'
        path = 'test_directory'
        
        download_data(url, arg, path, verbose=False)

        # Check if the file was saved correctly
        mock_file.assert_called_once_with(Path (path) / 'sample.xml', 'w')
        mock_file().write.assert_called_once_with('<xml>data</xml>')

    @patch('pathlib.Path.mkdir')  # Prevent actual directory creation
    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_png_file(self, mock_file, mock_urlopen, mock_mkdir):
        # Mock the response from urlopen
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        
        url = 'https://www.genome.jp/kegg/pathway/map/map1.png'
        arg = '1'
        path = 'test_directory'
        
        download_data(url, arg, path, verbose=False)

        # Check if the PNG file was saved correctly
        mock_file.assert_called_once_with(Path (path) / 'map1.png', 'wb')
        mock_file().write.assert_called_once_with(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
        
    @patch('pathlib.Path.mkdir')  # Prevent actual directory creation
    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_rest_file(self, mock_file, mock_urlopen, mock_mkdir):
        # Mock the response from urlopen
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'This is a test.'
        
        url = 'http://example.com/data'
        arg = 'test'
        path = 'test_directory'
        
        download_data(url, arg, path, verbose=False)

        # Check if the text file was saved correctly
        mock_file.assert_called_once_with(Path(path) / 'test.txt', 'w')
        mock_file().write.assert_called_once_with('This is a test.')

    @patch('pathlib.Path.touch')  # Prevent FileNotFoundError
    @patch('pathlib.Path.mkdir')  # Prevent actual directory creation
    @patch('urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_http_error_handling(self, mock_open_func, mock_urlopen, mock_mkdir, mock_touch):
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
        
        # Invoke the function
        download_data(url, arg, path, verbose=False)
    
        # Check that bad request logging was triggered
        mock_open_func.assert_any_call(Path(path) / 'bad_requests.txt', 'a')
        mock_open_func().write.assert_any_call('test\n')
        
###############################################################################

    @patch("keggmapwizard.download_data.download_data")
    @patch("os.makedirs")
    @patch("os.path.isfile")
    @patch('builtins.print')
    @patch("keggmapwizard.download_data.check_bad_requests")
    def test_download_skips_bad_requests_when_reload_false(
        self,
        mock_check_bad_requests,
        mock_print,
        mock_isfile,
        mock_makedirs,
        mock_download_data
    ):
        # Setup
        mock_check_bad_requests.return_value = ['arg1', 'arg2']  # bad requests
        mock_isfile.side_effect = lambda path: False  # all files treated as new

        
        download_rest_data(['arg1', 'arg2', 'arg3'], reload=False, verbose=True)

        expected_path =  Path(DATA_DIR) / "rest_data"

        # Only arg1 and arg2 should be downloaded
        mock_download_data.assert_has_calls([
            call('https://rest.kegg.jp/list/arg1', 'arg1', expected_path, True),
            call('https://rest.kegg.jp/list/arg2', 'arg2', expected_path, True)
        ], any_order=True)
        
        # Assertions
        self.assertEqual(mock_download_data.call_count, 2)  # Ensure download_data was called twice
        
        mock_print.assert_any_call("These files will be downloaded: ['arg1', 'arg2']")
        



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

class TestPNGFunctions(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.png_path = self.test_dir / "test_img.png"
        self.json_path = self.png_path.with_suffix(".json")

        # Create mock config and dependency functions
        self.mock_config = MagicMock()
        self.mock_config.working_dir = str(self.test_dir)

        self.mock_image = Image.new("RGBA", (2, 2), (255, 255, 255, 255))
        self.mock_image.save(self.png_path)

    def tearDown(self):
        for file in self.test_dir.glob("*"):
            file.unlink()
        self.test_dir.rmdir()
        
    @patch("keggmapwizard.download_data.Image.open")
    @patch("keggmapwizard.download_data.BytesIO")
    @patch("keggmapwizard.download_data.base64.b64encode", return_value=b"mock_base64_encoded_data")
    @patch("keggmapwizard.download_data.open", new_callable=mock_open)
    @patch("keggmapwizard.download_data.os.path.isfile", return_value=True)
    def test_encode_png_mocks(self, mock_isfile, mock_open_file, mock_b64encode, mock_bytes_io, mock_image_open):
        # Setup mock image
        mock_img = MagicMock(spec=Image.Image)
        converted_img = MagicMock(spec=Image.Image)
        converted_img.size = (1, 1)
        
        # Mock pixel access
        mock_pixdata = MagicMock()
        mock_pixdata.__getitem__.return_value = (255, 255, 255, 255)
        mock_pixdata.__setitem__ = MagicMock()
    
        converted_img.load.return_value = mock_pixdata
        converted_img.save = MagicMock()
        converted_img.close = MagicMock()
        mock_img.convert.return_value = converted_img
        mock_image_open.return_value = mock_img
    
        # Mock BytesIO buffer
        mock_buffer = BytesIO()
        mock_bytes_io.return_value = mock_buffer
    
        # Execute
        encode_png(Path("test_image.png"))
    
        # Assert image operations
        mock_image_open.assert_called_once_with(Path("test_image.png"))
        mock_img.convert.assert_called_once_with("RGBA")
        converted_img.save.assert_called_once_with(mock_buffer, "PNG")
        converted_img.close.assert_called_once()
        mock_pixdata.__setitem__.assert_called_with((0, 0), (255, 255, 255, 0))
    
        # Combine written output for JSON parsing
        handle = mock_open_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        written_json = json.loads(written_data)
    
        # Check JSON structure
        self.assertEqual(written_json["width"], 1)
        self.assertEqual(written_json["height"], 1)
        self.assertEqual(written_json["image"], "mock_base64_encoded_data")

    @patch("os.path.isfile", return_value=True)
    def test_encode_png_creates_json(self, mock_isfile):
        encode_png(self.png_path)
        self.assertTrue(self.json_path.exists())

        with open(self.json_path) as f:
            data = json.load(f)
        self.assertEqual(data["width"], 2)
        self.assertEqual(data["height"], 2)
        self.assertIn("image", data)

        decoded = base64.b64decode(data["image"])
        img = Image.open(BytesIO(decoded)).convert("RGBA")
        self.assertEqual(img.getpixel((0, 0)), (255, 255, 255, 0))

    @patch("os.path.isfile", return_value=False)
    def test_encode_png_skips_if_missing(self, mock_isfile):
        encode_png(Path("nonexistent.png"))
        self.assertFalse(self.json_path.exists())

    @patch("keggmapwizard.download_data.check_input", return_value=["ko12345", "ko67890"])
    @patch("keggmapwizard.download_data.check_bad_requests", return_value=["ko12345"])
    @patch("keggmapwizard.config", new_callable=lambda: MagicMock(working_dir=str(Path(tempfile.mkdtemp()))))
    @patch("keggmapwizard.download_data.download_data")
    @patch("keggmapwizard.download_data.encode_png")
    def test_download_base_png_maps_flow(self, mock_encode, mock_download, mock_config, mock_bad, mock_input):
        test_ids = ["ko12345", "ko67890"]
        download_base_png_maps(test_ids, reload=False, verbose=False)

        mock_download.assert_called_once()
        mock_encode.assert_called_once()
        

    @patch("builtins.print")
    @patch("keggmapwizard.download_data.check_input", return_value=[])
    @patch("keggmapwizard.config", new_callable=lambda: MagicMock(working_dir=str(Path(tempfile.mkdtemp()))))
    def test_download_base_png_maps_no_new_maps(self, mock_config, mock_input, mock_print):
        download_base_png_maps([], verbose=True)
        mock_print.assert_any_call("No New PNG map/s to download.")
###############################################################################

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
        self.assertEqual(result, list(set(['00001', '00002', '00003'])))

    def test_invalid_map_id_too_long(self):
        result = check_input(['123456'])
        self.assertEqual(result, [])
        self.assertIn("123456 is Not a valid map_id. Maximum length allowed for a map number is 5.", self.held_output.getvalue())

    def test_invalid_map_id_characters_only(self): # works
        result = check_input(['abcde'])
        self.assertEqual(result, [])
        self.assertIn("abcde is Not a valid map_id. Map id cannot just be characters.", self.held_output.getvalue())

    def test_invalid_map_id_mixed_characters(self):
        result = check_input(['map123456'])
        self.assertEqual(result, [])
        self.assertIn("map123456 is Not a valid map_id. Maximum length allowed for a map number is 5.", self.held_output.getvalue())

    def test_non_list_input(self):
        result = check_input('12345')
        self.assertEqual(result, [])
        self.assertIn("map_ids is not a list. Please provide a list of map IDs.", self.held_output.getvalue())

    def test_empty_list(self): 
        result = check_input([])
        self.assertEqual(result, [])
        #self.assertIn("No map id provided", self.held_output.getvalue())

    def test_string_with_extension(self):                                                                                               # changed 
        # Test map IDs with extensions
        result = check_input(["123.txt", "map123.xml", "00123.svg"])
        self.assertEqual(result, list(set(["00123" ])))

    def test_string_after_digit(self):                                                                                               # changed 
        # Test map IDs with extensions
        result = check_input(["123map","480ko"])
        self.assertEqual(result, [])
    
    def test_empty_string(self):
        # Test empty string as input
        result = check_input("")
        self.assertEqual(result, [])
    
    def test_uniqueness_of_return(self):
        # Test unique map ids
        result = check_input(["123", "00123"])
        self.assertEqual(result, ["00123"])
    
    def test_map_prefix_stripping(self):
        result = check_input(["map123"])
        self.assertEqual(result, ["00123"])
        
    def test_digit_only_id_padding(self):
        result = check_input(["123"])
        self.assertEqual(result, ["00123"])
        
    def test_special_none_case(self):
        result = check_input(["None"])
        self.assertEqual(result, [])
        self.assertIn("No map id provided", self.held_output.getvalue())
        
    def test_alpha_numeric_valid_prefix(self):
        result = check_input(["ko12"])
        self.assertEqual(result, ["ko00012"])

###############################################################################

class TestCheckBadRequests(unittest.TestCase):
    
    def setUp(self):
        # Setup a temporary directory if needed
        self.path = Path("test_path")
        self.bad_file = "bad_requests.txt"

    @patch("os.path.isfile", return_value=False)
    def test_no_bad_requests_file(self, mock_isfile):
        # Test check missing file
        args = ["map00010", "map00020"]
        result = check_bad_requests(args, self.path, self.bad_file, verbose=False, reload=False)
        self.assertEqual(result, args)

    @patch("os.path.isfile")
    def test_check_bad_requests(self, mock_isfile):
        # Filters known bad requests	
        # Mock os.path.isfile to return True (simulate existence of bad_requests_file)
        mock_isfile.return_value = True

        # Simulate the content of the bad_requests_file using mock_open
        mock_file_content = "map12345\nmap45678\n"
        with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
            # Define input arguments
            args_list = ["map12345", "map23456"]
            path = Path("/mock/path")
            bad_requests_file = "bad_requests.txt"
            verbose = False
            reload = False

            # Call the function
            result = check_bad_requests(args_list, path, self.bad_file, reload = reload, verbose = verbose)

            # Check the filtered result
            expected_result = ["map23456"]  # Only file3.txt is not in bad_requests_file
            self.assertEqual(result, expected_result)

            # Verify the bad_requests_file was opened with the correct path
            mock_file.assert_called_once_with(Path(path) / bad_requests_file, "r")
        
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="map00010\nmap00030")
    def test_filter_bad_requests_without_reload_verbose_off(self, mock_file, mock_isfile):
        args = ["map00010", "map00020", "map00030"]
        result = check_bad_requests(args, self.path, self.bad_file, verbose=False, reload=False)
        # map00010 and map00030 should be filtered out
        self.assertEqual(result, ["map00020"])
        
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="map00010\nmap00030")
    def test_filter_bad_requests_with_reload_verbose_on(self, mock_file, mock_isfile):
        # Keeps bad entries if reload=True, prints retry message
        args = ["map00010", "map00020", "map00030"]
        with patch("sys.stdout", new=StringIO()) as fake_out:
            result = check_bad_requests(args, self.path, self.bad_file, verbose=True, reload=True)
            self.assertEqual(result, args)  # No filtering if reload=True
            output = fake_out.getvalue()
            self.assertIn("map00010 was previously identified as a bad request. Attempting to download again.", output)
            self.assertIn("map00030 was previously identified as a bad request. Attempting to download again.", output)

    def test_empty_args_list(self):
        result = check_bad_requests([], self.path, self.bad_file, verbose=False, reload=False)
        self.assertEqual(result, [])


###############################################################################

class TestExtractAllMapIds(unittest.TestCase):

    def setUp(self):
        self.rest_path = Path(DATA_DIR) / "rest_data"
        self.file_path = self.rest_path / "pathway.txt"

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="map00001\nmap00002\nmap00003\n")
    @patch('keggmapwizard.download_data.download_data')
    def test_file_exists(self, mock_download, mock_open_file, mock_isfile, mock_exists):
        result = extract_all_map_ids()
        mock_open_file.assert_called_once_with(self.file_path, 'r')
        self.assertEqual(result, ['00001', '00002', '00003'])
        mock_download.assert_not_called()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=False)
    @patch('builtins.open', new_callable=mock_open, read_data="map00001\nmap00002\nmap00003\n")
    @patch('keggmapwizard.download_data.download_data')
    def test_file_missing_triggers_download(self, mock_download, mock_open_file, mock_isfile, mock_exists):
        result = extract_all_map_ids()
        mock_open_file.assert_called_once_with(self.file_path, 'r')
        mock_download.assert_called_once_with(
            "https://rest.kegg.jp/list/pathway", 'pathway', self.rest_path, verbose=True
        )
        self.assertEqual(result, ['00001', '00002', '00003'])

    @patch('os.path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('os.path.isfile', return_value=False)
    @patch('builtins.open', new_callable=mock_open, read_data="path:map00001\npath:map00002")
    @patch('keggmapwizard.download_data.download_data')
    def test_creates_directory_and_downloads(self, mock_download, mock_open_file, mock_isfile, mock_makedirs, mock_exists):
        result = extract_all_map_ids()
        mock_makedirs.assert_called_once_with(self.rest_path)
        mock_download.assert_called_once()
        self.assertEqual(result, ['00001', '00002'])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="some random text without map IDs")
    def test_no_ids_in_file(self, mock_open_file, mock_isfile, mock_exists):
        result = extract_all_map_ids()
        self.assertEqual(result, [])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="map00001\nmap00002\ninvalid\nmapXYZ")
    def test_partial_valid_entries(self, mock_open_file, mock_isfile, mock_exists):
        result = extract_all_map_ids()
        self.assertEqual(result, ['00001', '00002'])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="path:MAP00099\npath:map99999")
    def test_case_insensitive_extraction(self, mock_open_file, mock_isfile, mock_exists):
        result = extract_all_map_ids()
        self.assertEqual(result, ['00099', '99999'])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="path:map00010\npath:map12345\npath:map54321")
    def test_prefixed_lines_are_parsed(self, mock_open_file, mock_isfile, mock_exists):
        result = extract_all_map_ids()
        self.assertEqual(result, ['00010', '12345', '54321'])
###############################################################################

if __name__ == '__main__':
    unittest.main()