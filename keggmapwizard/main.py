"""
KeggCLI Module

This module provides a command line interface (CLI) for interacting with the 
KeggMapWizard (KMW) application, which facilitates the retrieval and visualization 
of KEGG (Kyoto Encyclopedia of Genes and Genomes) pathway data.

The KeggCLI class includes methods to download KEGG resources and create SVG 
pathway maps based on specified map IDs and organisms. It allows users to 
interact with KMW application through command-line inputs, enabling flexible 
retrieval and visualization of biological pathways.

Classes:
    KeggCLI: A class that provides methods for downloading KEGG resources and 
    creating SVG pathway maps.

Functions:
    cli(): Entry point for the KeggCLI command line interface, allowing users 
    to execute commands related to KEGG resources directly from the command line.

Usage:
    To use this module, run the script directly. The Fire library will 
    automatically generate a command line interface based on the methods 
    available in the KeggCLI class, allowing users to invoke methods with 
    appropriate parameters.

Example:
    python main.py download_kegg_resources --map_ids 520 --orgs hsa --reload True
"""

import fire
from keggmapwizard.kegg_pathway_map import download_kegg_resources
from keggmapwizard.kegg_pathway_map import KeggPathwayMap


class KeggCLI:
    """
    Command Line Interface (CLI) for interacting with KMW application.
    
    The KeggCLI class provides methods to download KEGG resources and create 
    SVG pathway maps based on specified map IDs and organisms. It facilitates 
    user interaction through command-line inputs, allowing for flexible 
    retrieval and visualization of KEGG data.
    
    Methods:
        download_kegg_resources(map_ids, orgs=None, reload=False):
            Downloads KEGG resources for the specified map IDs and organisms.
            The resources can be reloaded if specified.
        
        create_svg_map(map_ids, orgs='', reload=False):
            Creates SVG pathway maps for the specified map IDs and organisms, 
            optionally reloading resources if specified.
    
    Usage:
        To use this class, instantiate it and call the desired methods with 
        appropriate parameters. The CLI can be run directly to interact with 
        KEGG resources via command line.
    """
    def download_kegg_resources(self, map_ids = None, orgs = None,reload: bool = False):
        """
        Downloads KEGG resources for the specified map IDs and organisms.
        
        This method retrieves KEGG resources based on the provided map IDs and 
        optional organism identifiers. It allows for the input of multiple map IDs 
        and organisms, which can be specified as a list or a comma-separated string. 
        The resources can be reloaded if the `reload` parameter is set to True.
        
        Parameters:
            map_ids (list or str): A list of KEGG map IDs or a comma-separated 
            string of map IDs to download. Each map ID corresponds to a specific 
            pathway in the KEGG database.
            
            orgs (list, tuple, or str, optional): A list of organism identifiers 
            (e.g., species codes) for which the resources should be downloaded. 
            If not provided, the method will default to None.
        
            reload (bool, optional): A flag indicating whether to reload the 
            resources. If set to True, the method will download the resources 
            again, even if they already exist.
        
        Returns:
            The result of the download operation, which include status messages 
            and data related to the downloaded resources.
        """
        if map_ids is not None:            
            if not isinstance(map_ids, list):
                map_ids = [s.strip() for s in str(map_ids).split(',')]
        if orgs is not None:
            if not isinstance(orgs, list):
                if isinstance(orgs, tuple):
                    orgs = list(orgs)
                else:
                    orgs=[orgs]
        return download_kegg_resources(map_ids, orgs,reload)


    def create_svg_map(self, map_ids, orgs='', reload=False):
        """
        Creates SVG pathway maps for the specified map IDs and organisms.
        
        This method generates SVG visualizations of KEGG pathway maps based on 
        the provided map IDs and optional organism identifiers. It allows for 
        the input of multiple map IDs and organisms, which can be specified as 
        a list or a comma-separated string. If the `reload` parameter is set to 
        True, the method will first download the necessary KEGG resources before 
        creating the SVG maps.
        
        Parameters:
            map_ids (list or str): A list of KEGG map IDs or a comma-separated 
            string of map IDs for which SVG maps should be created. Each map ID 
            corresponds to a specific pathway in the KEGG database.
            
            orgs (list, tuple, or str, optional): A list of organism identifiers 
            (e.g., species codes) to be included in the SVG maps. If not provided, 
            the method will default to an empty string.
        
            reload (bool, optional): A flag indicating whether to reload the 
            resources before creating the SVG maps. If set to True, the method 
            will download the resources again, even if they already exist.
        
        Returns:
            None: This method does not return any value. It directly creates 
            SVG files for the specified pathway maps.
        
        """
        # Check if the input is a list for map_ids
        if not isinstance(map_ids, list):
            map_ids = [s.strip() for s in str(map_ids).split(',')]
        # Check if orgs is a list
        if not isinstance(orgs, list):
            if isinstance(orgs, tuple):
                orgs = list(orgs)
            else:
                orgs=[orgs]

        if reload:
            self.download_kegg_resources(map_ids,orgs,reload)
            reload = False

        # Iterate over each map_id
        for map_id in map_ids:
            # Concatenate each org to the map_id and create SVG maps
            for org in orgs:
                combined_id = f"{org}{map_id}"  # Concatenate map_id and org

                pathway_map = KeggPathwayMap(map_id=combined_id, reload=reload)
                pathway_map.create_svg_map()

def cli():
    """
    Entry point for the KeggCLI command line interface.
    
    This function initializes the command line interface for the KeggCLI class 
    using the Fire library. It allows users to interact with KEGG resources 
    through command-line commands, enabling functionalities such as downloading 
    KEGG pathway resources and creating SVG pathway maps.
    
    Usage:
        To run the CLI, execute the script directly. The Fire library will 
        automatically generate a command line interface based on the methods 
        available in the KeggCLI class, allowing users to invoke methods 
        with appropriate parameters directly from the command line.
    
    Example:
        python main.py download_kegg_resources --map_ids "['00400', '00440']" --orgs "['gma', 'mus']"
        python main.py download_kegg_resources --map_ids 00400,00430 --orgs hsa,mus --reload True
        python main.py download_kegg_resources --map_ids 430 --orgs mmu --reload True
        python main.py create_svg_map --map_ids "['00400', '00440']" --orgs "['gma', 'mus']"
        python main.py create_svg_map --map_ids 00400,00430 --orgs hsa,mus --reload True
        python main.py create_svg_map --map_ids 430 --orgs mmu --reload True
    """
    fire.Fire(KeggCLI)

if __name__ == '__main__':
    cli()
