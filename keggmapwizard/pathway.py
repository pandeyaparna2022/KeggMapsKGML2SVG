from pathlib import Path
from keggmapwizard.config import config
from keggmapwizard.kegg_file import KgmlFile
from keggmapwizard.pathway_component import PathwayComponent
#from keggmapwizard.geometry_annotation import GeometryAnnotation
from keggmapwizard.annotation_settings import ANNOTATION_SETTINGS


class Pathway:
    def __init__(self, map_id: str, file_types: list):
        
        self.map_id = map_id
        self.__kegg_files = []
        self.__org_files = []
        self._file_types = file_types

    @property
    def kegg_files(self): # works
        if not self.__kegg_files:
            self.__kegg_files = self.__create_kegg_files()
        return self.__kegg_files

    @property
    def org_files(self): # works
        if not self.__org_files:
            self.__org_files = self.__create_org_files()
        return self.__org_files

    @property
    def pathway_components(self):
        return self.__create_pathway_components()

    @property
    def title(self):
        title = set()
        files = self.kegg_files + self.org_files
        for file in files:
            
            title.add(file.title)

        return '/'.join(title)

    @property
    def pathway_number(self):
        pathway_number = set()
        files = self.kegg_files + self.org_files
        for file in files:
            pathway_number.add(file.pathway_number)
        return '/'.join(pathway_number)

    @property
    def org(self):
        org = []
        files = self.kegg_files + self.org_files
        for file in files:
            if file.organism is not None:
                org.append(file.organism)
        org = "_".join(org)
        return org

    def __create_kegg_files(self):
        kegg_files = []
        kegg_file_types = [element for element in self._file_types if element != 'orgs']
        for file_type in kegg_file_types:
            kegg_files.append(KgmlFile(self.map_id[-5:], file_type, config.working_dir))
        return kegg_files

    def __create_org_files(self):
        org_files = []
        if 'orgs' in self._file_types:
            prefix = self.map_id[:-6]
            suffix = self.map_id[-5:]
            
            
            separated_org_list = prefix.split(':')
            for org in separated_org_list:
                org_files.append(KgmlFile(org+suffix, 'orgs', config.working_dir))
        return org_files

    def __create_pathway_components(self):
        
        files = self.kegg_files + self.org_files
        if len(self.org_files) == 0:
            organisms = [None]
        else:
            org = []
            
            for file in self.org_files:
                if file.organism is not None:
                    org.append(file.organism)
            organisms = org
            
        merged_data = {}

        for file in files:
            for entry in file.entries:
                graphics = entry.find('graphics')
                entry_data = {
                    "id": entry.get('id'),
                    "name": [entry.get('name')],
                    "type": [entry.get('type')],
                    "graphics": {
                        "type": graphics.get('type'),
                        "x": graphics.get('x'),
                        "y": graphics.get('y'),
                        "height": graphics.get('height'),
                        "width": graphics.get('width'),
                        "coords": graphics.get('coords')
                    }
                }

                pathway_component = PathwayComponent(entry_data)

                pathway_component.retrive_pathway_annotation_data()

                equivalent_pathway_component = pathway_component.is_equivalent(merged_data, file.file_name)
                if equivalent_pathway_component is not None:
                    updated_pathway_component = pathway_component.merge_pathway_components(equivalent_pathway_component)
                    merged_data.update(updated_pathway_component)

                else:
                    merged_data.update({pathway_component.pathway_component_id: pathway_component})

        pathway_components = []
        

        annotations = self.__provide_annotations(organisms)
       
        for key, value in merged_data.items():
            annotation_object = GeometryAnnotation(organisms)
           
            geometry_annotation = annotation_object.get_annotation(value.pathway_annotation_data, annotations)
            value.pathway_annotation_data = geometry_annotation
            pathway_components.append(value)

        return pathway_components

    def __provide_annotations(self, organisms:[]):

        annotations = {}

        for key, value in ANNOTATION_SETTINGS.items():
            data_dict = {}
        
            rest_file = value['rest_file']
            if rest_file == 'org':
                rest_file = organisms
        
            # Normalize rest_file to be a list (even if it's a string)
            if isinstance(rest_file, str):
                rest_file = [rest_file]
            substraction = 0
            for rf in rest_file:
                if rf != '':

                    file_path = Path(config.working_dir) / 'rest_data' / f"{rf}.txt"
                    try:
                        with open(file_path, 'r') as file:
                            for line in file:
                                data = line.strip().split('\t')
                                if len(data) < 2:
                                    key_anno = data[0]
                                    value_anno = ""
                                else:
                                    if key == 'Gene':
                                        key_anno = data[0]
                                        value_anno = data[3]
                                    else:
                                        key_anno = data[0]
                                        value_anno = data[1]
        
                                data_dict[key_anno] = value_anno
        
                    except FileNotFoundError:
                        print(f"File not found: {file_path}")
                        data_dict[key] = ''

                if key == 'Gene' :
                    exec(f"{organisms[substraction]} = {data_dict}")
                    print(organisms[substraction])
                    substraction = substraction + 1
                else:
                    exec(f"{key} = {data_dict}")
                annotations.update({key: data_dict})

        return annotations