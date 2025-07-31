from pathlib import Path
from keggmapwizard.config import config
from keggmapwizard.kegg_file import KgmlFile
from keggmapwizard.pathway_component import PathwayComponent
from keggmapwizard.geometry_annotation import GeometryAnnotation
from keggmapwizard.annotation_settings import ANNOTATION_SETTINGS


class Pathway:
    def __init__(self, map_id: str, file_types: list):
        # Store map ID and file types
        self.map_id = map_id
        self._file_types = file_types
        # Lazy-load containers
        self._kegg_files = None
        self._org_files = None

    @property
    def kegg_files(self):
        # Load KEGG files only once
        if self._kegg_files is None:
            suffix = self.map_id[-5:]
            types = [ft for ft in self._file_types if ft != 'orgs']
            self._kegg_files = [KgmlFile(suffix, ft, config.working_dir) for ft in types]
        return self._kegg_files

    @property
    def org_files(self):
        # Load organism-specific files if 'orgs' is requested
        if self._org_files is None:
            self._org_files = []
            if 'orgs' in self._file_types:
                prefix = self.map_id[:-6]
                suffix = self.map_id[-5:]
                self._org_files = [
                    KgmlFile(f"{org}{suffix}", 'orgs', config.working_dir)
                    for org in prefix.split(':') if org
                ]
            
        return self._org_files

    @property
    def pathway_components(self):
        # Load pathway components separately if needed (placeholder call)
        return self.__create_pathway_components()

    @property
    def title(self):
        # Collect unique titles from all files and join them
        titles = {f.title for f in self.kegg_files + self.org_files}
        return '/'.join(titles)

    @property
    def pathway_number(self):
        # Collect unique pathway numbers from all files and join them
        pathway_numbers = {f.pathway_number for f in self.kegg_files + self.org_files}
        return '/'.join(pathway_numbers)

    @property
    def org(self):
        # Collect non-empty organism tags and join with underscores
        orgs = [f.organism for f in self.kegg_files + self.org_files if f.organism]
        return '_'.join(orgs)

    def __create_pathway_components(self):
        # Combine all KEGG and organism files into one list
        files = self.kegg_files + self.org_files
        # Determine the list of organisms based on org_files
        organisms = []
        if len(self.org_files) == 0:
            organisms = [None]
        else:
            # Extract valid organism identifiers
            for file in self.org_files:
                if file.organism is not None:
                    organisms.append(file.organism)
        # Initialize a dictionary to store merged pathway components    
        merged_data = {}
        # Iterate through each file and its entries
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
                # Create a PathwayComponent object using entry data
                pathway_component = PathwayComponent(entry_data)
                # Retrieve additional annotation data for this component
                pathway_component.retrive_pathway_annotation_data()
                # Check if an equivalent component already exists in merged_data
                equivalent_pathway_component = pathway_component.is_equivalent(merged_data, file.file_name)
                # If a match is found, merge them and update the dictionary
                if equivalent_pathway_component is not None:
                    updated_pathway_component = pathway_component.merge_pathway_components(equivalent_pathway_component)
                    merged_data.update(updated_pathway_component)

                else:
                    # Otherwise, insert as a new unique component
                    merged_data.update({pathway_component.pathway_component_id: pathway_component})
        # Initialize final list to hold fully annotated pathway components
        pathway_components = []
        
        # Generate annotations for the organism(s)
        annotations = self.__provide_annotations(organisms)
        # Annotate each component using GeometryAnnotation logic
        for key, value in merged_data.items():
            annotation_object = GeometryAnnotation()
            geometry_annotation = annotation_object.get_annotation(value.pathway_annotation_data, annotations)
            # Update the component's annotation
            value.pathway_annotation_data = geometry_annotation
            # Add to the final result list
            pathway_components.append(value)
        # Return the completed list of annotated pathway components
        return pathway_components

    def __provide_annotations(self, organisms:[]):
        # Dictionary to hold all annotation results
        annotations = {}
        # Iterate through each annotation type and its config settings
        for key, value in ANNOTATION_SETTINGS.items():
            # Temporary dictionary to store annotations for this specific key
            data_dict = {}
            # Get the REST file specifier from the annotation settings
            rest_file = value['rest_file']
            # If it's set to 'org', use the input organisms list instead
            if rest_file == 'org':
                rest_file = organisms
            # Ensure rest_file is a list even if a single string is provided
            if isinstance(rest_file, str):
                rest_file = [rest_file]

            # Iterate through each rest file (i.e., organism or data source)
            # Skip empty strings
            for rf in filter(None, rest_file): 

                # Construct full path to the annotation file
                file_path = Path(config.working_dir) / 'rest_data' / f"{rf}.txt"
                try:
                    # Open the file for reading
                    with open(file_path, 'r') as file:
                        # Read line by line
                        for line in file:
                            # Split line into fields
                            data = line.strip().split('\t')
                            key_anno = data[0]
                            # If data has less than 2 fields, default values
                            if len(data) < 2:
                                value_anno = ""
                            else:
                                # Choose value based on the annotation type
                                if key == 'Gene':
                                    value_anno = data[3]
                                else:
                                    value_anno = data[1]
                            # Save to current annotation dictionary
                            data_dict[key_anno] = value_anno
                # Handle missing file exceptions
                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                    # Insert empty default if file is missing
                    data_dict[key] = ''
                 # Update main annotations dictionary with the current annotation data
                annotations.update({key: data_dict})

        # Return full annotations dictionary
        return annotations