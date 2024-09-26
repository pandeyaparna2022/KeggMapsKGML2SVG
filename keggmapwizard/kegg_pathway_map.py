import os
from xml.etree import ElementTree as ET
from pathlib import Path
from .utils import KEGG_MAP_WIZARD_DATA as DATA_DIR
from .download_data import download_rest_data, download_base_png_maps, download_kgml, check_input, extract_all_map_ids
from .pathway import Pathway
from .base_image import BaseImage
from .svg_content import create_svg_content


class KeggPathwayMap:
    """
    Class to create a KeggPathwayMap object
            
    """
    def __init__(self, map_id, reload=False):
        print(f"Initializing an instance of {self.__class__.__name__}")
        print("Retreiving/downloading required resources.")
        self._map_id = check_input([map_id])
        self._pathway = None
        self._image_data = None
        self._organism = None
        self._reload = reload
        self.__file_exists()

    # To do : add title
    @property
    def map_id(self):
        """
        If the map ID is not in coorect format it returns and empty string,
        else it returns the map ID.

        Returns
        -------
        str
            the map id of the pathway.

        """
        if len(self._map_id) == 0:
            map_id = ''
        else:
            map_id = self._map_id[0]
        return map_id

    @property
    def organism(self):
        if self._organism is None:
            if self.map_id[:-5] not in ['ko', 'ec', 'rn', '']:
                file_path = DATA_DIR / Path("kgml_data") / Path('orgs') / Path(f"{self.map_id}.xml")
                if os.path.exists(file_path):
                    organism = self.map_id[:-5]
                else:
                    print(f"{self.map_id[:-5]} file does not exist for {self.map_id[-5:]}")
                    organism = None
            else:
                organism = None
        else:
            organism = self._organism
        self._organism = organism
        return self._organism

    @property
    def pathway(self):

        if self._pathway is None:
            self._pathway = self.__create_pathway()

        return self._pathway

    @property
    def base_image(self):
        if self._image_data is None:
            self._image_data = self.__base_image()
        return self._image_data

    def __file_exists(self):
        if self.map_id != '':
            download_kgml([self.map_id], self._reload)
            download_base_png_maps([self.map_id], self._reload)

            if self.organism is not None:
                kgml_file_path = DATA_DIR / Path("kgml_data") / Path('orgs') / Path(f"{self.map_id}.xml")
                if os.path.exists(kgml_file_path):
                    rest_file = self.organism
                    download_rest_data([rest_file], self._reload)

    def __file_types(self):
        existing_file_types = []
        base_file_types = ['ko', 'ec', 'rn']

        for file_type in base_file_types:
            file_path = DATA_DIR / Path("kgml_data") / Path(file_type) / Path(f"{file_type}{self.map_id[-5:]}.xml")
            if os.path.exists(file_path):
                existing_file_types.append(file_type)

        if self.organism is not None:
            kgml_file_path = DATA_DIR / Path("kgml_data") / Path('orgs') / Path(f"{self.map_id}.xml")
            if os.path.exists(kgml_file_path):
                existing_file_types.append('orgs')
        return existing_file_types

    def __create_pathway(self):
        pathway = None
        file_types = self.__file_types()
        if len(file_types) != 0:
            # pathway = Pathway(self.map_id)
            # if self.organism is not None:
            if 'orgs' in file_types:
                pathway = Pathway(self.map_id, file_types)
            else:
                pathway = Pathway(self.map_id[-5:], file_types)
        if pathway is None:
            print('No pathway to create')
        return pathway

    def __base_image(self):
        base_image = None
        image_path = DATA_DIR / Path("maps_png") / Path(f"map{self.map_id[-5:]}.png.json")
        if os.path.exists(image_path):
            base_image = BaseImage.from_png(self.map_id, image_path)
        return base_image

    def create_svg_map(self, color_function=None, *args, path=None, output_name=None):
        if self.base_image is None or self.pathway is None:
            print('No pathway to create')
            svg_pathway_object = None
        else:

            svg_pathway_object = create_svg_content(self.pathway, self.base_image, color_function, *args)
            # Create directory for SVG outputs
            if path is None:
                out_dir = DATA_DIR / Path("SVG_output")
            else:
                if os.path.exists(Path(path)):
                    out_dir = Path(path) / Path("SVG_output")
                else:
                    out_dir = Path(DATA_DIR) / Path("SVG_output")
                    print(
                        "The given path for the output does not exist. Therefore, the files will be stored in the default output directory:")
                    print(out_dir)
            os.makedirs(out_dir, exist_ok=True)
            if output_name is None:
                file_path = out_dir / Path(f"{self.pathway.org}{self.map_id[-5:]}.svg")
            else:
                file_path = out_dir / Path(f"{output_name}.svg")
            with open(file_path, 'wb') as file:
                file.write(b'\n')
                file.write(b'\n')
                file.write(ET.tostring(svg_pathway_object))
            print(f'wrote {file_path}')

        return svg_pathway_object


def download_kegg_resources(map_ids: [str] = None, orgs: [str] = None, reload=False):
    """
    Downloads various KEGG resources based on provided map IDs and organisms.

    Args:
        map_ids (list of str, optional): List of map identifiers. Defaults to extracting all map IDs if None.
        orgs (list of str, optional): List of organisms. If provided, resources will also be downloaded for
                                      each organism combined with map IDs.
        reload (bool, optional): If True, forces re-download of all resources even if they are already present locally.
                                 Defaults to False.
    """
    args_list = ['pathway', 'br', 'md', 'ko', 'gn', 'compound', 'glycan', 'rn', 'rc', 'enzyme', 'ne', 'variant',
                 'ds', 'drug', 'dgroup']

    if map_ids is None:
        map_ids = extract_all_map_ids()

    if orgs is None:
        processed_map_ids = map_ids
    else:

        # Initialize an empty list to store the results
        processed_map_ids = []
        for org in orgs:
            args_list.append(org)
            for map_id in map_ids:
                processed_map_ids.append(org + map_id)

    download_base_png_maps(processed_map_ids, reload=reload)
    download_kgml(processed_map_ids, reload=reload)
    download_rest_data(args_list, reload=reload)
