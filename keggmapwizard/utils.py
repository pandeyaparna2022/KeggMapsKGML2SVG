import os

KEGG_MAP_WIZARD_DATA = os.environ.get('KEGG_MAP_WIZARD_DATA', '/tmp/keggmapwizard')
if not os.path.isdir(KEGG_MAP_WIZARD_DATA):
    os.mkdir(KEGG_MAP_WIZARD_DATA)
