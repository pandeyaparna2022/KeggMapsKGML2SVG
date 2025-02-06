from keggmapwizard.kegg_pathway_map import download_kegg_resources
from keggmapwizard.kegg_pathway_map import KeggPathwayMap
import fire

class KeggCLI:
    def download_kegg_resources(self, map_ids, orgs = None,reload: bool = False):
        if not isinstance(map_ids, list):
            map_ids = [map_ids]
        if not isinstance(orgs, list):
            orgs = [orgs]
        return download_kegg_resources(map_ids, orgs,reload)

    def create_svg_map(self, map_ids,orgs):
        # Check if the input is a list
        if isinstance(map_ids, list):
            # Create an instance of KeggPathwayMap and call create_svg_map
            for map_id in map_ids:
                pathway_map = KeggPathwayMap(map_id=map_id)
                pathway_map.create_svg_map()
        else:
            pathway_map = KeggPathwayMap(map_id=map_ids)
            pathway_map.create_svg_map()
        

def cli():
    fire.Fire(KeggCLI)

    


if __name__ == '__main__':
    cli()
    
   