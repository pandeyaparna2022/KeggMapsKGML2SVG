from pathlib import Path
from xml.etree import ElementTree as ET


class KgmlFile:
    def __init__(self, map_id, file_type, data_directory, reload=False):

        self.file_type = file_type
        self.data_directory = data_directory
        self.__file_contents = None
        self._in_memory = False
        self.map_id = map_id
        self._reload = reload

    @property
    def file_name(self):
        if self.file_type == 'orgs':

            return self.map_id
        else:

            return self.file_type + f"{self.file_type}{self.map_id[-5:]}"

    @property
    def file_directory(self):
        return self.data_directory / Path("kgml_data") / Path(self.file_type)

    @property
    def file_path(self):

        if self.file_type == 'orgs':

            return self.file_directory / Path(f"{self.map_id}.xml")
        else:
            return self.file_directory / Path(f"{self.file_type}{self.map_id[-5:]}.xml")

    @property
    def file_contents(self):

        if not self._in_memory:
            self.__file_contents = self.__read_file()
            # to do : make it so such that kegg file instance is created only if the file exists
            self._in_memory = True
        return self.__file_contents

    @property
    def organism(self):
        if self.file_contents is not None:
            root_info = dict(self.file_contents.items())

            return root_info['org']
        else:
            return None

    @property
    def title(self):
        if self.file_contents is not None:
            root_info = dict(self.file_contents.items())

            return root_info['title']
        else:
            return None

    @property
    def pathway_number(self):
        if self.file_contents is not None:
            root_info = dict(self.file_contents.items())

            return root_info['number']
        else:
            return None

    @property
    def entries(self):
        if self.file_contents is not None:
            entries = self.file_contents.findall('entry')

            return entries
        else:
            return []

    def __is_file_cached(self):

        if self._in_memory:
            return self.__file_contents
        else:
            return self.__file_contents is not None

        # The is operator checks for object identity, so it returns True if the 
        # self.__file_contents is not None and False otherwise.
        return self.__file_contents is not None

    def __read_file(self):
        try:

            # parse the XML file specified by xml_path
            # retrieve the root element of the parsed XML tree
            root = ET.parse(self.file_path).getroot()
            # convert the attributes of the root element into key-value pairs
            return root

        except FileNotFoundError as error:
            print(f"File not found! {error}")

            return None

# Kgml_file = KgmlFile("ko00010","ko",DATA_DIR)
# Kgml_file.file_path
# Kgml_file.file_contents
