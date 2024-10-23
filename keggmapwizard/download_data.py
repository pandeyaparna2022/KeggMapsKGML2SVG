import os
import base64
from io import BytesIO
import re
import time
import json
import urllib.request
import urllib.error
from PIL import Image
from .utils import KEGG_MAP_WIZARD_DATA as DATA_DIR


# todo: INCORPORATE PARALLEL PROCESSING
def download_data(url: str, arg: str, path: str, verbose: bool = True):
    """
    Handle the downloading of data based on a URL and an argument.

    Args:
        url (str): The web address for the argument/query used to download the data.
        arg (str): Argument/query to be downloaded.
        path (str): Path to save the downloaded file.
        verbose (bool): A boolean flag indicating whether to display verbose output.

    Returns:
        None
    """

    def save_file(content, file_name, mode='w'):
        """Helper function to save content to a file."""
        with open(f'{path}/{file_name}', mode) as file:
            file.write(content)
        if verbose:
            print(f"Saved {file_name}")

    def log_bad_request():
        """Helper function to log bad requests."""
        save_file(arg + '\n', 'bad_requests.txt', mode='a')
        if verbose:
            print(f"Data non-existent for query: {arg}. Status code: {error_code}")

    try:
        # Make the request
        with urllib.request.urlopen(url) as response:
            data = response.read()

            if verbose:
                print(f"Downloading {arg}...")

            # Define URL patterns for kgml and PNG file types
            pattern1 = r'^http://rest\.kegg\.jp/get/[^/]+/kgml$'
            pattern2 = r'https://www\.genome\.jp/kegg/pathway/map/map\d+\.png'

            # Determine file type and extension based on URL pattern
            if re.match(pattern1, url):
                file_name = f'{arg}.xml'
                save_file(data.decode('utf-8'), file_name)
            elif re.match(pattern2, url):
                file_name = f'map{arg}.png'
                save_file(data, file_name, mode='wb')
                # Uncomment if encode_png is needed
                # encode_png(f'{path}/{file_name}')
            else:
                file_name = f'{arg}.txt'
                save_file(data.decode('utf-8'), file_name)

    except urllib.error.HTTPError as error:
        # Handle HTTP error codes (e.g., 400, 404)
        error_code = error.code
        if error_code in (400, 404):
            log_bad_request()
        else:
            if verbose:
                print(f"An error occurred for query: {arg}. Status code: {error_code}")
    except urllib.error.URLError as error:
        # Handle other URL errors
        if verbose:
            print(f"Failed to reach server for query: {arg}. Reason: {error.reason}")


def download_rest_data(
        args_list: list,
        reload: bool = False,
        bad_requests_file: str = "bad_requests.txt",
        verbose: bool = True
) -> None:
    """
    Args:
         args_list: List of arguments for that indicate which files to download
         n_parallel: Number of parallel downloads
         reload: if True: overwrite existing files, if False: only download non-existing files
         bad_requests_file: path to file that conains list of non-existent files
         verbose: if True: print summary
    """
    # create a directory for the rest data and changes the working directory to it.
    path = f'{DATA_DIR}/rest_data/'
    os.makedirs(f'{path}', exist_ok=True)

    # Check if any of the arguments in the args_list are
    # 1) in bad_requests and
    # 2) already present only if reload == True

    args_list = check_bad_requests(args_list, path, bad_requests_file, verbose)

    if not reload:
        args_list = [args for args in args_list if not os.path.isfile(f'{path}/{args}.txt')]

    if len(args_list) == 0:
        if verbose:
            print("No new files to download.")
        return
    if verbose:
        print(f'These files will be downloaded: {args_list}')
    for arg in args_list:
        url = f'https://rest.kegg.jp/list/{arg}'
        download_data(url, arg, path, verbose)
    return


def extract_all_map_ids():
    """
    Args:
         None
    Returns:
        List of map ids from "pathway.txt" file in the rest_data         
    """
    # Check if the file "pathway.txt" exists in the directory
    # os.chdir(f'{DATA_DIR}/rest_data')
    # Check if the "pathway.txt" exists in the current directory.
    path = f'{DATA_DIR}/rest_data'

    if not os.path.exists(path):
        # Create the directory
        os.makedirs(path)
    if os.path.isfile(f'{path}/pathway.txt'):
        print("pathway.txt file exists. Extracting map ids from this file ...")
    # If the file does not exist, initiate the download of the 'pathway' file
    # using the download_data() function
    else:
        print("File does not exist. Downloading...")
        url = "https://rest.kegg.jp/list/pathway"
        download_data(url, 'pathway', path, verbose=True)  # Call the download function to download the file
        # read the content of the file into the variable 'pathway'.
    with open(f'{path}/pathway.txt', 'r') as file:
        pathway = file.read()

    # re.findall() function to extract all the map IDs from the 'pathway'
    # content based on the specified regular expression pattern r'\bmap\d{5}\b'.
    # flags=re.IGNORECASE parameter ensures that the search is case-insensitive.
    map_ids = re.findall(r'\bmap\d{5}\b', pathway, flags=re.IGNORECASE)

    # remove map from the names
    remove_map_prefix = lambda x: x[3:]

    # Apply the transformation to each element in the list using map()
    map_ids = list(map(remove_map_prefix, map_ids))

    # return the extracted map IDs as a list
    return map_ids


def encode_png(png_path: str) -> None:
    """
    Takes a PNG image file as input and converts it to the 'RGBA' mode.
    Converts pixels with white full opacity (255, 255, 255, 255) to transparent 
    (255, 255, 255, 0).
    Creates a JSON object containing the width, height, and the base64 encoded 
    string of the modified image and writes it to a file with the same name as 
    the original PNG file but with a '.json' extension.
    Args:
         PNG image file
    
    Returns:
        None       
    """
    # Check if the file path exists
    if os.path.isfile(png_path):
        # Open the PNG image file
        img = Image.open(png_path)
        # Convert the image to the 'RGBA' mode
        img = img.convert('RGBA')
        # Load the pixel data of the image
        pixdata = img.load()
        # Get the width and height of the image
        width, height = img.size

        # Iterate through each pixel of the image
        for y_coord in range(height):
            for x_coord in range(width):
                r, b, g, a = pixdata[x_coord, y_coord]
                assert r == b == g, f'{(r,g,b,a)=}'
                assert a == 255, f'{(r,g,b,a)=}'
                pixdata[x_coord, y_coord] = (0, 0, 0, 255 - r)  # All pixels are black with variable transparency

        # Create a buffer to save the modified image as a PNG
        buffer = BytesIO()
        # Save the modified image to the buffer in PNG format
        img.save(buffer, 'PNG')
        # Close the image file
        img.close()
        
        # encoded_image=base64.b64encode(buffer.getvalue()).decode()
        # Create a JSON object containing the width, height, and the base64 encoded
        # string of the modified image.
        with open(png_path + '.json', 'w') as file:
            json.dump(dict(
                width=width,
                height=height,
                image=base64.b64encode(buffer.getvalue()).decode()), file)


def download_base_png_maps(map_ids: [str], reload: bool = False,
                           bad_requests_file: str = "bad_requests.txt",
                           verbose: bool = True, encode: bool = True) -> None:
    """
    Downloads PNG maps, saves them, modifies them and Create a JSON object 
    containing the width, height, and the base64 encoded string of the modified
    image.
    
    Args:
        map_ids: list of ids of the images to be downloaded
        reload: A boolean flag indicating whether to download a map thats already 
        present in the directory. If True: overwrite existing files, 
        if False: only download non-existing files.
        verbose: A boolean flag indicating whether to display verbose output 
        for ongoing operation     

    """

    map_ids = check_input(map_ids)

    # Record the start time
    start_time = time.time()  # Record the start time
    # Create a directory to store the PNGa maps if it doesn't exist
    path = f'{DATA_DIR}/maps_png/'
    os.makedirs(f'{path}', exist_ok=True)
    # Check if any of the arguments in the map_ids are
    # 1) in bad_requests and
    # 2) already present only if reload == True

    map_ids = check_bad_requests(map_ids, path, bad_requests_file, verbose)
    map_numbers = list(set(map(lambda x: x[-5:], map_ids)))

    if not reload:
        map_ids = [map_id for map_id in map_ids if not os.path.isfile(f'{path}/{"map" + map_id[-5:]}.png')]
        map_numbers = list(set(map(lambda x: x[-5:], map_ids)))

    if len(map_ids) == 0:
        if verbose:
            print("No New PNG map/s to download.")
    else:
        if verbose:
            print(f'PNG file/s will be downloaded for maps: {map_numbers}')

        for map_id in map_ids:
            map_number = map_id[-5:]  # Get the last five characters

            if verbose:
                # Display the progress of the download
                print(f'map {map_ids.index(map_id) + 1} of {len(map_ids)}')
            # download all the maps in the filtered maps_id list
            url = f'https://www.genome.jp/kegg/pathway/map/map{map_number}.png'
            # Call the download_data function to download the data
            download_data(url, map_number, path, verbose)
            if encode:
                # Call the encode_png function to modify the saved image
                encode_png(f'{path}/{"map" + map_id[-5:] + ".png"}')
    # Record the end time

    end_time = time.time()
    # Calculate the total time taken
    total_time = end_time - start_time  # Calculate the total time taken
    if verbose:
        # Display the total time taken for the download process
        print(f"Total time taken to finish task: {total_time} seconds")


def download_kgml(map_ids: [str], reload: bool = False, bad_requests_file: str =
"bad_requests.txt", verbose: bool = True, file_type='all') -> None:
    """
        Downloads KGML files for given map IDs.
        
        Args:
            map_ids (list of str): List of map IDs to download KGML files for.
            reload (bool, optional): Flag indicating whether to reload previously downloaded files. Defaults to False.
            bad_requests_file (str, optional): File path to store IDs of maps that failed to download. Defaults to "bad_requests.txt".
            verbose (bool, optional): Flag indicating whether to print progress messages. Defaults to True.
        
        Returns:
            None
            
        This function downloads KGML (KEGG Markup Language) files for the given map IDs. KGML files are XML representations
        of KEGG pathway maps. The function allows for reloading previously downloaded files if the 'reload' flag is set to True.
        If a map fails to download, its ID is stored in the 'bad_requests_file' for reference.
        
        Example usage:
        download_kgml(["map00010", "map00020"], reload=True, bad_requests_file="failed_maps.txt", verbose=True)
        """
    # start_time = time.time()  # Record the start time

    start_time = time.time()  # Record the start time
    map_ids = check_input(map_ids)
    if len(map_ids) == 0:
        print("Nothing to download.")
        return

    path = f'{DATA_DIR}/kgml_data'
    os.makedirs(f'{path}', exist_ok=True)
    os.makedirs(f'{path}/ko', exist_ok=True)
    os.makedirs(f'{path}/ec', exist_ok=True)
    os.makedirs(f'{path}/rn', exist_ok=True)
    os.makedirs(f'{path}/orgs', exist_ok=True)

    # Check if any of the arguments in the map_ids are
    # 1) in bad_requests and
    # 2) already present only if reload == True

    ko_map_ids = []
    ec_map_ids = []
    rn_map_ids = []
    org_map_ids = []
    # Iterate through each element of the map_ids list
    for map_id in map_ids:

        map_number = map_id[-5:]  # Get the last five characters
        map_prefix = map_id[:-5]  # Get the rest of the string

        ko_map_id = "ko" + map_number
        ko_map_ids.append(ko_map_id)

        ec_map_id = "ec" + map_number
        ec_map_ids.append(ec_map_id)

        rn_map_id = "rn" + map_number
        rn_map_ids.append(rn_map_id)

        if map_prefix != "map" and map_prefix != "":
            org_map_id = map_prefix + map_number
            org_map_ids.append(org_map_id)

    ko_map_ids = check_bad_requests(ko_map_ids, f'{path}/ko', bad_requests_file, verbose)
    ec_map_ids = check_bad_requests(ec_map_ids, f'{path}/ec', bad_requests_file, verbose)
    rn_map_ids = check_bad_requests(rn_map_ids, f'{path}/rn', bad_requests_file, verbose)
    org_map_ids = check_bad_requests(org_map_ids, f'{path}/orgs', bad_requests_file, verbose)

    if not reload:
        ko_map_ids = [map_id for map_id in ko_map_ids if not os.path.isfile(f'{path}/ko/{map_id}.xml')]
        ec_map_ids = [map_id for map_id in ec_map_ids if not os.path.isfile(f'{path}/ec/{map_id}.xml')]
        rn_map_ids = [map_id for map_id in rn_map_ids if not os.path.isfile(f'{path}/rn/{map_id}.xml')]
        org_map_ids = [map_id for map_id in org_map_ids if not os.path.isfile(f'{path}/orgs/{map_id}.xml')]

    files_to_download = ko_map_ids + ec_map_ids + rn_map_ids + org_map_ids
    print(f"Missing kgml files: {files_to_download}")

    for i in range(len(ko_map_ids)):
        if verbose:
            print(f'ko file {i + 1} of {len(ko_map_ids)}')

        ko_url = f"http://rest.kegg.jp/get/{ko_map_ids[i]}/kgml"
        download_data(ko_url, ko_map_ids[i], f'{path}/ko')

    for i in range(len(ec_map_ids)):
        if verbose:
            print(f'ec file {i + 1} of {len(ec_map_ids)}')

        ec_url = f"http://rest.kegg.jp/get/{ec_map_ids[i]}/kgml"
        download_data(ec_url, ec_map_ids[i], f'{path}/ec')

    for i in range(len(rn_map_ids)):
        if verbose:
            print(f'rn file {i + 1} of {len(rn_map_ids)}')

        rn_url = f"http://rest.kegg.jp/get/{rn_map_ids[i]}/kgml"
        download_data(rn_url, rn_map_ids[i], f'{path}/rn')

    for i in range(len(org_map_ids)):
        if verbose:
            print(f'organism file {i + 1} of {len(org_map_ids)}')

        org_url = f"http://rest.kegg.jp/get/{org_map_ids[i]}/kgml"
        download_data(org_url, org_map_ids[i], f'{path}/orgs')

    end_time = time.time()
    # Calculate the total time taken
    total_time = end_time - start_time  # Calculate the total time taken
    if verbose:
        # Display the total time taken for the download process
        print(f"Total time taken to finish task: {total_time} seconds")


def check_bad_requests(args_list: list, path: str, bad_requests_file: str, verbose: bool) -> list:
    """
    Checks if the arguments/files to be downloaded are in the bad_requests.txt
    Args:
         args_list: List of arguments that indicate which files to download
         bad_requests_file: Path to file that contains a list of non-existent files
    Returns:
         List of arguments to be downloaded
    """
    if len(args_list) == 0:
        return []
    # Initialize an empty list bad_requests to hold all the bad queries.
    bad_requests = []

    # Check if the bad_requests_file exists and is a file.
    if bad_requests_file and os.path.isfile(f'{path}/{bad_requests_file}'):
        with open(f'{path}/{bad_requests_file}', 'r') as file:
            bad_requests = file.read().splitlines()
        # print(f"Checking the {args_list} in {bad_requests_file}.")

    ################ This is more for printing if verbose == True #############
    # For printing
    if verbose and bad_requests:

        # Find the args  that are already noted as bad_requests
        filtered_args = [args for args in args_list if args in bad_requests]
        # Print the args that are noted as bad_requests
        for args in filtered_args:
            print(f'{args} was previously identified as a bad request and will \
therefore not be downloaded.')

    # Filter the args_list to include only files that are not in the list
    # of bad requests.
    args_list = [args for args in args_list if args not in bad_requests]

    return args_list


def check_input(map_ids: list):
    # Check if input is a list
    if not isinstance(map_ids, list):
        print("map_ids is not a list. Please provide a list of map IDs.")
        return []
    ##### Check if elements of map_ids fit the required format ############

    # Create an empty list to add only the map_ids that fit the criteria
    map_id_list = []
    map_ids = list(map(str, map_ids))
    for map_id in map_ids:
        # check if the string variable map_id contains a period ('.'). in case the map id was
        # provided with a extension
        # assign the substring of map_id from the beginning up to (but not including)
        # the index of the period to the variable map_id.
        if "." in map_id:
            index = map_id.rindex(".")
            map_id = map_id[:index]
        # convert map_id to string

        map_id = str(map_id)

        # check if the map id is only digits
        if map_id.isdigit():
            # check if the length of the map number is less than 5, if so
            # pad it with leading zeros and appened it to filtered list
            if len(map_id) <= 5:
                map_id = str(map_id).zfill(5)
                map_id_list.append(map_id)
            # else print a warning stating the format is not correct
            else:
                print(f"{map_id} is Not a valid map_id. Maximum length allowd for a map number is 5.")
        # Check if map_id is just characters and if so print a warning msg.
        elif map_id.isalpha():

            print(f"{map_id} is Not a valid map_id. Map id cannot just be characters.")
        # check if map_id fits the criteria
        # characters followed by number and the length of number is less than no more than 5
        else:
            for i in range(len(map_id)):

                if map_id[i].isdigit():

                    if map_id[i:].isdigit():
                        map_number = map_id[i:]
                        prefix = map_id[:i]

                        if len(map_number) <= 5:

                            map_number = str(map_number).zfill(5)
                            if prefix != 'map':
                                map_id = prefix + map_number
                            else:
                                map_id = map_number
                            map_id_list.append(map_id)
                        else:
                            print(f"{map_id} is Not a valid map_id. Maximum length allowd for a map number is 5 .")
                        break
                    else:
                        print(f"{map_id} is Not a valid map_id.")
                        break
    return map_id_list
