from keggmapwizard.annotation_settings import ANNOTATION_SETTINGS

compound_reaction_mapping = {
    "gl": "G",
    "dr": "D",
    "cpd": "C",
    "DG": "DG",
    "rn": "R",
    "rc": "RC",
}

# Define mappings for other query types
query_type_mapping = {
    'enzyme': 'EC',
    'ortholog': 'K',
    'brite': 'BR',
    'group': 'GR',
    'other': 'O',
    'gene': 'Gene',
}


class GeometryAnnotation():
    def __init__(self, organism):
        self.org = organism

    def __repr__(self):
        return f'<KeggAnnotation: {self.anno_type} - {self.name}>'

    def _get_description(self, anno_type, anno_name):
        """
        Use rest data to get the description of an annotation query.

        Args:
            anno_type (str): The first queryName of the annotation.
            anno_name (str): Type of annotation.

        Returns:
            str: The description for the given annotation or an empty string if not found.
        """

        if anno_name in anno_type:

            result = anno_type[anno_name]
            result = result.replace("'", "")
            result = result.replace("<->", "(1->4)")
            result = result.replace("<=>", "(1->4)")

            return result
        else:
            return ""

    def get_annotation(self, queries: [dict], annotations):
        """
        Create annotation and get the description of the annotation.

        :param query1: list describing the query type e.g. map, gene, enzyme, compound, etc.
        :param query2: query to be annotated e.g.cpd:C000500 (actual name of the compound in the map)
        :return: description. If none is found, an empty string is returned and a warning is printed.
        """
        # Create empty dictionary and empty lists for later
        dictionary = {}
        data_annotations = []
        html_classes = []
        title_descriptions = []

        existing_queries = ['compound', 'map', 'enzyme', 'ortholog', 'reaction', 'gene', 'group', 'brite', 'other']

        # Assert that the query type is legitimate
        for query in queries:
            assert query['type'] in existing_queries

        for query in queries:
            query_type = query['type'].lower()
            query_name = query['name']

            # split string in query_name into multiple substrings based on whitespace characters.

            query_names = query_name.split()

            for part in query_names:
                parts = part.split(":", 1)
                if len(parts) < 2:
                    anno_name = parts[0]
                else:
                    anno_name = parts[1]

                if query_type in ('compound', 'reaction'):
                    anno_type = compound_reaction_mapping[parts[0]]
                elif query_type == 'map':
                    anno_type = 'MAP'
                    anno_name = 'map' + anno_name[-5:]
                else:
                    anno_type = query_type_mapping[query_type]

                html_class = ANNOTATION_SETTINGS[anno_type]['html_class']
                html_classes.append(html_class)
                if anno_type == 'EC':
                    name = "EC:" + anno_name
                elif anno_type == 'Gene':
                    name = f"{self.org}:" + anno_name
                    anno_name = f"{self.org}:" + anno_name
                else:
                    name = anno_name

                if anno_name in annotations[anno_type]:

                    result = annotations[anno_type][anno_name]
                    result = result.replace("'", "")
                    result = result.replace("<->", "(1->4)")
                    result = result.replace("<=>", "(1->4)")
                else:
                    result = ''

                description = result

                if anno_type == 'EC' or anno_type == "RC" or anno_type == "R":
                    title_info = name
                elif anno_type == 'MAP' or anno_type == 'BR':
                    title_info = name + ":" + description
                else:
                    title_info = name + " (" + description.split(';')[0].strip() + ")"

                title_descriptions.append(title_info)

                data_annotations.append(dict(type=anno_type, name=name, description=description
                                             ))

        dictionary.update(dict(title=title_descriptions, visualizatin_class=list(set(html_classes)),
                               data_annotation=data_annotations
                               ))
        self.data_annotation = dictionary

        return self.data_annotation
