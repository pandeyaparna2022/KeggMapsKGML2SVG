import os
from keggmapwizard.kegg_pathway_map import download_kegg_resources


def cli():
    if 'KEGG_MAP_WIZARD_DATA' not in os.environ:
        os.environ['KEGG_MAP_WIZARD_DATA'] = input('Please enter the path for KEGG_MAP_WIZARD_DATA: ')

    import fire

    # keggmapwizard --map_ids "['00400', '00380']" --orgs "['gma', 'mus']"
    fire.Fire(download_kegg_resources)


if __name__ == '__main__':
    cli()
