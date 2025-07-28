from keggmapwizard.annotation_settings import ANNOTATION_SETTINGS
# Map specific compound/reaction prefixes to shorthand codes
compound_reaction_mapping = {
    "gl": "G",
    "dr": "D",
    "cpd": "C",
    "DG": "DG",
    "rn": "R",
    "rc": "RC",
}

# Map other query types to their corresponding annotation codes
query_type_mapping = {
    'enzyme': 'EC',
    'ortholog': 'K',
    'brite': 'BR',
    'group': 'GR',
    'other': 'O',
    'gene': 'Gene',
}

# GeometryAnnotation class for providing annotations to queries
class GeometryAnnotation():
    def __init__(self, organisms):
        self.org = organisms # Store the organism info
        self.anno_type = 'N/A'
        self.name = 'N/A'

    def __repr__(self):
        # Custom representation when printing an instance
        return f'<KeggAnnotation: {self.anno_type} - {self.name}>'

    def _get_description(self, anno_type, anno_name, annotations):
        """
        Use rest data to get the description of an annotation query.

        Args:
            anno_type (str): The first queryName of the annotation.
            anno_name (str): Type of annotation.

        Returns:
            str: The description for the given annotation or an empty string if not found.
        """

        if anno_name in annotations[anno_type]:
            # Remove/replace problematic characters for svg
            result = annotations[anno_type][anno_name]
            result = result.replace("'", "")
            result = result.replace("<->", "(1->4)")
            result = result.replace("<=>", "(1->4)")

            return result
        else:
            return ""
        

    def get_annotation(self, queries: [dict], annotations: {}):
        """
        Process queries and retrieve formatted annotation for elements of queries
        
        Args:
            queries ([dict]): list of dictionaries. Each dictionary contatins queries to be annotated.
            annotations (dict): Reference Annotation dictionary.
        
        Returns:
            Structured dictionary with annotation descriptions and metadata. If none is found, an empty string is returned.
        """
        # Create empty dictionary and empty lists for later
        dictionary = {}           # Final result container
        data_annotations = []     # List of processed annotation entries
        html_classes = []         # Stores HTML classes used for visualization
        title_descriptions = []   # Titles or tooltips for the annotation elements

        existing_queries = ['compound', 'map', 'enzyme', 'ortholog', 'reaction', 'gene', 'group', 'brite', 'other']
        
        #Assert that the query type is legitimate
        for query in queries:
            
            assert query['type'] in existing_queries

        for query in queries:
            query_type = query['type'].lower() # Normalize the type to lowercase
            query_name = query['name']         # Extract the annotation name

            # split string in query_name into multiple substrings based on whitespace characters.
            query_names = query_name.split()

            for part in query_names:
                parts = part.split(":", 1)     # Split into prefix and actual name
                if len(parts) < 2:
                    anno_name = parts[0]
                else:
                    anno_name = parts[1]
                # Determine annotation type based on prefix or query type
                if query_type in ('compound', 'reaction'):
                    anno_type = compound_reaction_mapping[parts[0]]
                elif query_type == 'map':
                    anno_type = 'MAP'
                    anno_name = 'map' + anno_name[-5:]  # Format map name appropriately
                else:
                    anno_type = query_type_mapping[query_type]
                    
                # set the class attribute anno_type
                self.anno_type = anno_type
                
                # Get HTML class styling from settings
                html_class = ANNOTATION_SETTINGS[anno_type]['html_class']
                html_classes.append(html_class)
                
                # Format the annotation name differently for specific types
                if anno_type == 'EC':
                    name = "EC:" + anno_name
                elif anno_type == 'Gene':
                    name = parts[0]+":" + anno_name
                    anno_name = name 
                else:
                    name = anno_name
                self.name = name
                
                # Look up description in reference annotation dictionary                
                description = self._get_description(anno_type, anno_name, annotations)
                
                # Format the title (tooltip) depending on annotation type
                if anno_type == 'EC' or anno_type == "RC" or anno_type == "R":
                    title_info = name
                elif anno_type == 'MAP' or anno_type == 'BR':
                    title_info = name + ":" + description
                else:
                    title_info = name + " (" + description.split(';')[0].strip() + ")"

                title_descriptions.append(title_info)

                # Store full annotation record in data_annotations
                data_annotations.append(dict(type=anno_type, name=name, description=description
                                             ))
        # Assemble Final dictionary
        dictionary.update(dict(title=title_descriptions,
                               visualizatin_class=list(set(html_classes)),
                               data_annotation=data_annotations
                               ))
        self.data_annotation = dictionary

        return self.data_annotation
