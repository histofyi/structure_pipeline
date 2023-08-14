from typing import Dict, List, Tuple

from helpers.files import read_json, write_json, write_step_tmp_output
from helpers.text import slugify

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work

from providers import PDBeProvider, PMCeProvider

from fuzzywuzzy import fuzz


def convert_pdbe_authors(author: Dict) -> Dict:
    """
    This function converts the author information from the PDBe API into the format used by the BibJSON standard.

    Args:
        author (Dict): The author information from the PDBe API.
    
    Returns:
        Dict: The author information in the format used by the BibJSON standard.
    """
    converted_author = {
        "lastname": author['last_name'],
        "name": author['full_name'],
        "initials": author["initials"]
    }
    return converted_author


def pdbe_to_bibjson(pdb_code, pdbe_publication_info:Dict) -> Tuple[Dict,Dict]:
    """
    This function converts the publication information from the PDBe API into the format used by the BibJSON standard.

    Args:
        pdb_code (str): The PDB code associated with the publication.
        pdbe_publication_info (Dict): The publication information from the PDBe API.

    Returns:
        Tuple[Dict,Dict]: The publication information in the format used by the BibJSON standard and the publication information from PubMed Central Europe.
    """
    # Convert the base publication information from the PDBe API into the format used by the BibJSON standard.
    bibjson = {
        'title':pdbe_publication_info['title'],
        'author':[convert_pdbe_authors(author) for author in  pdbe_publication_info['author_list']],
        'type':'article',
        'url':'',
        'identifier':[]
    }
    # If there is no information about the journal, then the publication is not yet published.
    if pdbe_publication_info['journal_info']['pdb_abbreviation'] == 'To be published':
        bibjson['journal'] = {
            'name':'', 
            'iso_abbreviation':'To be published'
        }
    else:    
        # If there is information about the journal, then the publication is published and we can capture information about the journal and citation.
        bibjson['year'] = pdbe_publication_info['journal_info']['year'],
        bibjson['journal'] = {
            'name':'', 
            'iso_abbreviation':pdbe_publication_info['journal_info']['ISO_abbreviation']
        }
        bibjson['volume'] = pdbe_publication_info['journal_info']['volume'],
        bibjson['issue'] = pdbe_publication_info['journal_info']['issue'],
        bibjson['pages'] = pdbe_publication_info['journal_info']['pages'],

    # Add the identifiers for the publication. First the doi, then the pubmed id.
    if pdbe_publication_info['doi']:
        bibjson['identifier'].append({'type':'doi', 'id':pdbe_publication_info['doi']})
    if pdbe_publication_info['pubmed_id']:
        bibjson['identifier'].append({'type':'pubmed', 'id':pdbe_publication_info['pubmed_id']})

    # If there is a doi, then we can fetch the publication information from PubMed Central Europe, this has additional information about whether the publication is open access and if it is in PubMed Central.
    if pdbe_publication_info['doi']:
        pmce_info = fetch_pmce_data(pdbe_publication_info['doi'])
    else:
        pmce_info = None
    return bibjson, pmce_info


def fetch_pmce_data(doi:str) -> Dict:
    """
    This function fetches the publication information from PubMed Central Europe.

    Args:
        doi (str): The doi of the publication.

    Returns:
        Dict: The publication information from PubMed Central Europe.
    """
    info = None

    # Fetch the publication information from PubMed Central Europe.
    pmce_publication_info, success, errors = PMCeProvider().fetch(doi)
    # If the publication information was fetched successfully, then we can extract the information we need.
    if pmce_publication_info:
        # Initialise the dictionary to store the information we need.
        info = {}

        # Define some helper functions to map the key names from the PubMed Central Europe API to the key names used by our data format.
        yes_no = lambda x : True if x=='y' else False
        exists = lambda x,y : x[y] if y in x else None
        
        # Map the information from the PubMed Central Europe API to the key names used by our data format.
        fields = [('open_access','isOpenAccess'),('in_pmc','inPMC'),('in_pmce','inEPMC'),('abstract','abstractText'),('fulltext_urls','fullTextUrlList')]
        for field in fields:
            info[field[0]] = exists(pmce_publication_info, field[1])
    # Return the information
    return info


def fetch_publication_data_action(**action_args) -> Tuple[bool, Dict, List]:
    """
    This function fetches the publication information from the PDBe API and PubMed Central Europe and formats it appropriately.
    
    Keyword Args:
        pdb_code (str): The PDB code associated with the publication.
    
    Returns:
        Tuple[bool, Dict, List]: A tuple containing a boolean indicating whether the action was successful, the publication information and a list of errors.
    """
    # Fetch the PDB code from the action arguments.
    pdb_code = action_args['pdb_code']

    # Fetch the publication information from the PDBe API.
    data, success, errors = PDBeProvider(pdb_code).fetch_publications()

    pdbe_abstract = None

    if success:
        # If the publication information was fetched successfully, then we can extract the abstract.
        pdbe_abstract = data['abstract']['unassigned']

        # Initialise the dictionary to store the information we need.
        publication_info = {
            'open_access':None,
            'in_pmc':None,
            'in_pmce':None,
            'abstract':pdbe_abstract,
            'bibjson':None
        }

        # Convert the publication information from the PDBe API into the format used by the BibJSON standard.
        bibjson, pmce_info = pdbe_to_bibjson(pdb_code, data)

        publication_info['bibjson'] = bibjson

        # If there is a doi, then we can fetch the publication information from PubMed Central Europe, this has additional information about whether the publication is open access and if it is in PubMed Central.
        if pmce_info:
            # If the publication information was fetched successfully, then we can extract the abstract.
            pmce_abstract = pmce_info['abstract']

            # Comparing the abstracts from the PDBe API and PubMed Central Europe, if they are similar then we can use the information from PubMed Central Europe.
            ratio = fuzz.ratio(pmce_abstract, pdbe_abstract) / 100            
            if ratio > 0.9:
                for key in ['open_access','in_pmc','in_pmce','fulltext_urls']:
                    publication_info[key] = pmce_info[key]
    # Then return the publication information, or errors if there were any.
        return (True, publication_info, None)
    else:
        return (False, None, ['unable_to_fetch_publication_data'])



def fetch_publication_data(**kwargs):
    """
    This function simply calls the do_work function with the fetch_publication_data_action function and the appropriate input and output facets.

    Returns:    
        Dict: The action output for the work done.
    """
    # Set the output facet to publication.
    output_facet = 'publication'

    # Fetch the new work from the file.
    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    # Call the do_work function with the fetch_publication_data_action function and the appropriate input and output facets.
    action_output = do_work(new_work, fetch_publication_data_action, output_facet, input_facet=None, kwargs=kwargs)

    # Return the action output to the pipeline for logging.
    return action_output