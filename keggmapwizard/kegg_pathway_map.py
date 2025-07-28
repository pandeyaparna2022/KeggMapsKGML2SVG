"""
This module provides functionality for creating KEGG pathway maps in svg format.
It includes classes and methods for downloading pathway data, processing it, 
and saving the pathway map in svg format.
"""
import os
from xml.etree import ElementTree as ET
from pathlib import Path
from keggmapwizard.config import config
from keggmapwizard.download_data import (download_rest_data, download_base_png_maps,
                                         download_kgml, check_input, extract_all_map_ids,
                                         check_map_prefix)
from keggmapwizard.pathway import Pathway
from keggmapwizard.base_image import BaseImage
from keggmapwizard.svg_content import create_svg_content
from keggmapwizard.color_function_base import color_org


class KeggPathwayMap:
    """
    Class to create a KeggPathwayMap object.
    
    This class is responsible for initializing a KEGG pathway map object,
    retrieving necessary resources, and managing the associated data, including
    pathway information, organism details, and image data.
    
    Attributes:
        map_id (str): The identifier for the KEGG map.
        reload (bool): A flag indicating whether to reload resources.
        _pathway (object): The pathway data associated with the map (initialized to None).
        _image_data (object): The image data for the pathway (initialized to None).
        _organism (object): The organism associated with the pathway (initialized to None).
            
    Methods:
        __init__(map_id, reload=False): Initializes a KeggPathwayMap instance with
                                        the specified map_id and reload flag.
        map_id: Returns the map ID of the pathway. If the map ID is not in the correct
                format, it returns an empty string.
        organism: Retrieves the organism associated with the pathway based on the map ID.
        pathway: Creates and returns the pathway data if it has not been initialized yet.
        base_image: Retrieves the base image data for the pathway if it has not been initialized.
        create_svg_map(color_function=None, *args, path=None, output_name=None):
            Generates an SVG representation of the pathway map with optional color customization.

    Private Methods:
        __file_exists(): Checks if the necessary files for the pathway exist and
                         downloads them if needed.
        __file_types(): Determines the types of files available for the pathway
                        based on the map ID.
        __create_pathway(): Creates a pathway object based on the available file types.
        __base_image(): Retrieves the base image for the pathway from the specified path.
    """
   
    def __init__(self, map_id=None, reload=False):
        print(f"Initializing an instance of {self.__class__.__name__}")
        print("Retreiving/downloading required resources.")
        self._map_id = check_input([map_id])
        self._pathway = None
        self._title = None
        self._image_data = None
        self._organism = None
        self._reload = reload
        self.__file_exists()

    @property
    def map_id(self):
        """
        If the map ID is not in coorect format it returns and empty string,
        else it returns the map ID.

        Returns:
        -------
        str: the map id of the pathway.

        """
        if len(self._map_id) == 0:
            map_id = ''
        else:
            map_id = self._map_id[0]
        return map_id

    @property
    def organism(self):
        """
        Retrieves the organism associated with the KEGG pathway map based on the map ID.
    
        This property checks if the organism has already been set. If it has not,
        it attempts to determine the organism from the map ID. The map ID is expected
        to follow a specific format, where the organism name is derived from the 
        characters preceding the last five characters of the map ID. If the map ID 
        indicates a known type ('ko', 'ec', 'rn'), or if the corresponding KGML 
        file does not exist, the organism will be set to None.
    
        If the organism is successfully determined, it is cached for future access.
    
        Returns:
        -------
        str or None: The organism name derived from the map ID, or None if the 
                     organism cannot be determined or does not exist.
        """
        if self._organism is not None:
            return self._organism  # Return cached result
        
        prefix = self.map_id[:-5]
        suffix = self.map_id[-5:]
        
        org_prefixes = check_map_prefix(prefix)
        
        filtered_prefixes = [item for item in org_prefixes if item not in 
                             {'ko', 'ec', 'rn', 'map', 'Map', ''}]
        
        if len(filtered_prefixes) ==0:
            self._organism = None
            return None
        
        organisms_list = []
        
        for org in filtered_prefixes:
            map_id = f"{org}{suffix}"
            file_path = Path(config.working_dir) / "kgml_data" / "orgs" / f"{map_id}.xml"
        
            if file_path.exists():
                organisms_list.append(org)
            else:
                print(f"{org} KGML file does not exist for {suffix}")
        
        if organisms_list:
            organism_str = ":".join(organisms_list)
            self._map_id = [f"{organism_str}:{suffix}"]
            self._organism = organism_str
        else:
            self._organism = None
        
        return self._organism          


    @property
    def pathway(self):
        """
        Retrieves the pathway data associated with the KEGG map.
    
        This property checks if the pathway data has already been created. If it has not,
        the method calls the private method `__create_pathway()` to initialize the pathway
        data. Once created, the pathway data is cached for future access.
    
        Returns:
        -------
        object: The pathway data associated with the KEGG map. If the pathway has not 
                been created yet, it will be initialized upon the first access.
        """
        if self._pathway is None:
            self._pathway = self.__create_pathway()

        return self._pathway

    @property
    def title(self):
        """
        Retrieves the title of the pathway.
    
        This property checks if the internal `_title` attribute is None. If it is, 
        the title is fetched from the `pathway` object and stored in `_title` for 
        future access. This ensures that the title is only retrieved once and 
        cached for efficiency.
    
        Returns:
        -------
        str: The title of the pathway. If the title has not been set, it will 
             be fetched from the `pathway` object.
        """
        if self._title is None:
            self._title = self.pathway.title

        return self._title

    @property
    def base_image(self):
        """
        Retrieves the base image data associated with the KEGG pathway.
        
        This property checks if the base image data has already been initialized. If it has not,
        the method calls the private method `__base_image()` to create and retrieve the base image
        data. Once initialized, the base image data is cached for future access.
        
        Returns:
        -------
        object: The base image data for the KEGG pathway. If the base image has not 
                been created yet, it will be initialized upon the first access.
        """
        if self._image_data is None:
            self._image_data = self.__base_image()
        return self._image_data

    def __file_exists(self):
        """
        Checks for the existence of necessary files related to the KEGG pathway.
        
        This private method verifies if the KEGG map ID is not empty. If valid, it calls
        another function to download the base PNG map and KGML files associated with the
        map ID. Additionally, if an organism is associated with the pathway, it checks for the 
        existence of the corresponding organism specific KGML file. If the file exists,
        it downloads the REST data associated with the organism.
        
        This method is responsible for ensuring that all required resources are available 
        for the KEGG pathway map to function correctly.
        
        Returns:
        -------
        None
        """
        args_list = ['pathway', 'br', 'md', 'ko', 'gn', 'compound', 'glycan', 'rn', 'rc',
                     'enzyme', 'ne', 'variant', 'ds', 'drug', 'dgroup']
        if self.map_id != '':
            download_rest_data(args_list, self._reload)
            download_kgml([self.map_id], self._reload)
            download_base_png_maps([self.map_id], self._reload)

            if self.organism is not None:
                separated_org_list = self.organism.split(':')
                for org in separated_org_list:
                    map_id = org + self.map_id[-5:]
                    kgml_file_path = Path(config.working_dir) / "kgml_data" / 'orgs' / f"{map_id}.xml"
                    if os.path.exists(kgml_file_path):
                        rest_file = org
                        download_rest_data([rest_file], self._reload)

    def __file_types(self):
        """
        Checks for the existence of specific file types related to the KEGG pathway.
        
        This private method verifies the presence of predefined file types in the 
        `kgml_data` directory. It checks for the existence of files with extensions 
        'ko', 'ec', and 'rn', appending any found file types to a list. Additionally, 
        if an organism is associated with the pathway, it checks for the existence 
        of a corresponding KGML file.
        
        The method returns a list of existing file types that were found.
        
        Returns:
        -------
        list: A list of strings representing the existing file types. Possible 
              values include 'ko', 'ec', 'rn', and 'orgs' if the respective files 
              exist. The list may be empty if none of the files are found.
        """
        existing_file_types = []
        base_file_types = ['ko', 'ec', 'rn']

        for file_type in base_file_types:
            file_path = Path(config.working_dir) / "kgml_data" / file_type / f"{file_type}{self.map_id[-5:]}.xml"
            if os.path.exists(file_path):
                existing_file_types.append(file_type)

        if self.organism is not None:
            
            separated_org_list = self.organism.split(':')
            for org in separated_org_list:
                map_id = org + self.map_id[-5:]
                kgml_file_path = Path(config.working_dir) / "kgml_data" / 'orgs' / f"{map_id}.xml"

                if os.path.exists(kgml_file_path):
                    existing_file_types.append('orgs')

        return list(set(existing_file_types))

    def __create_pathway(self):
        """
        Creates a Pathway object based on available file types.
    
        This private method checks for the existence of specific file types related 
        to the KEGG pathway using the `__file_types` method. If any file types are 
        found, it attempts to create a `Pathway` object. The creation of the 
        `Pathway` object depends on whether the 'orgs' file type is present:
        - If 'orgs' is found, the `Pathway` is initialized with the full `map_id`.
        - If 'orgs' is not found, the `Pathway` is initialized using the last five 
          characters of the `map_id`.
    
        If no file types are found, or if the pathway cannot be created, a message 
        is printed indicating that no pathway can be created.
    
        Returns:
        -------
        Pathway or None: Returns the created `Pathway` object if successful; 
                         otherwise, returns None.
        """
        pathway = None
        file_types = self.__file_types()
        if len(file_types) != 0:
            # pathway = Pathway(self.map_id)
            
            if 'orgs' in file_types:
                pathway = Pathway(self.map_id, file_types)
            else:
                pathway = Pathway(self.map_id[-5:], file_types)
        if pathway is None:
            print('No pathway to create')
        return pathway

    def __base_image(self):
        """
        Retrieves the base image for the specified map ID.
    
        This private method constructs the file path for a PNG image in JSON format 
        based on the last five characters of the `map_id`. It checks if the image 
        file exists at the constructed path. If the file is found, it creates and 
        returns a `BaseImage` object using the `from_png` method, passing the 
        `map_id` and the image path.
    
        If the image file does not exist, the method returns None.
    
        Returns:
            BaseImage or None: Returns a `BaseImage` object if the image file is 
            found and successfully created; otherwise, returns None.
        """
        base_image = None
        image_path = Path(config.working_dir) / "maps_png" / f"map{self.map_id[-5:]}.json"

        if os.path.exists(image_path):
            base_image = BaseImage.from_png(self.map_id, image_path)

        return base_image

    def create_svg_map(self, color_function=None,*args, path=None, output_name=None):
        """
        Creates an SVG representation of the KEGG pathway map and saves it to a specified location.
        
        This method generates an SVG map based on the current pathway and base image. If either 
        the base image or pathway is not available, it prints a message and returns None. 
        The SVG content is created using the `create_svg_content` function, which takes the 
        pathway, base image, and optional color function as parameters.
        
        The method allows for customization of the output directory and file name:
        - If `path` is provided, the SVG will be saved in that directory. If the directory 
          does not exist, it defaults to a predefined output directory.
        - If `output_name` is provided, the SVG file will be named accordingly; otherwise, 
          it will use a default naming convention based on the organism and map ID.
        
        Parameters:
        color_function (callable, optional): A function to determine the color scheme 
                                            for the SVG elements. Defaults to None.
        *args: Additional positional arguments to be passed to the `create_svg_content` function.
         path (str, optional): The directory path where the SVG file will be saved. 
                               If None, defaults to the predefined output directory.
        output_name (str, optional): The name of the output SVG file. If None, a unique default 
                                     name will be generated based on the organism and map ID.
        
        Returns:
        -------
        object: The SVG pathway object created. Returns None if the pathway or base image 
                is not available.
        """
        
        if self.base_image is None or self.pathway is None:
            print('No pathway to create')
            svg_pathway_object = None
        else:
            svg_pathway_object = create_svg_content(self.pathway, self.base_image,
                                                    color_function, *args)
            # Create directory for SVG outputs
            
            if path is None:
                out_dir = Path(config.working_dir) / "SVG_output"
            else:
                if os.path.exists(Path(path)):
                    out_dir = Path(path) / "SVG_output"
                else:
                    out_dir = Path(config.working_dir) / "SVG_output"
                    print(
                        "The given path for the output does not exist. Therefore,"
                        " the files will be stored in the default output directory:")
                    print(out_dir)
            os.makedirs(out_dir, exist_ok=True)
            if output_name is None:
                file_path = out_dir / f"{self.pathway.org}{self.map_id[-5:]}.svg"
            else:
                file_path = out_dir / f"{output_name}.svg"
            with open(file_path, 'wb') as file:
                file.write(b'\n')
                file.write(b'\n')
                file.write(ET.tostring(svg_pathway_object))
            print(f'wrote {file_path}')

        return svg_pathway_object


def download_kegg_resources(map_ids: [str] = None, orgs: [str] = None, reload: bool = False):
    """
    Downloads various KEGG resources based on provided map IDs and organisms.

    Args:
        map_ids (list of str, optional): List of map identifiers. Defaults to 
                                         extracting all map IDs if None.
        orgs (list of str, optional): List of organisms. If provided, resources will also
                                      be downloaded for each organism combined with map IDs.
        reload (bool, optional): If True, forces re-download of all resources even if 
                                 they are already present locally. Defaults to False.
    """
    args_list = ['pathway', 'br', 'md', 'ko', 'gn', 'compound', 'glycan', 'rn', 'rc',
                 'enzyme', 'ne', 'variant', 'ds', 'drug', 'dgroup']
    # If nap_ids is not provided i.e. is None. use all available map ids in KEGG database.
    if map_ids is None:
        map_ids = extract_all_map_ids()
    # If organism prefix/es are provided concatenate the provided prefixes to all the map_ids
    if orgs is None:
        processed_map_ids = map_ids
    else:

        # Initialize an empty list to store the results
        processed_map_ids = []
        for org in orgs:
            # Append all the orgs to the args list
            args_list.append(org)
            for map_id in map_ids:
                processed_map_ids.append(org + map_id)

    # download the KEGG resources i.e., PNG maps, KGML files and REST data
    download_base_png_maps(map_ids, reload=reload)
    download_kgml(processed_map_ids, reload=reload)
    download_rest_data(args_list, reload=reload)
