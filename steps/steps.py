from update_localpdb import update_localpdb
from fetch_stcrdab_info import fetch_stcrdab_info
from fetch_sabdab_info import fetch_sabdab_info
from query_localpdb import query_localpdb
from process_localpdb_query_matches import process_localpdb_query_matches
from create_core_records import create_core_records
from fetch_chronology_data import fetch_chronology_data
from fetch_title_data import fetch_title_data
from fetch_experimental_data import fetch_experimental_data
from fetch_publication_data import fetch_publication_data
from find_alike_chains import find_alike_chains
from assign_species import assign_species
from assign_chain_types import assign_chain_types
from assign_complex_type import assign_complex_type
from assign_allele_number import assign_allele_number
from fetch_coordinates import fetch_coordinates

def stub_function():
    return None


steps = {
    '1':{
        'function':update_localpdb,
        'title_template':'the local copy of the pdb using localpdb.',
        'title_verb': ['Updating','Updates'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '2':{
        'function':fetch_stcrdab_info,
        'title_template':'the local copy of the data from STCRDab.',
        'title_verb': ['Updating','Updates'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '3':{
        'function':fetch_sabdab_info,
        'title_template':'the local copy of the data from SABDab.',
        'title_verb': ['Updating','Updates'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '4':{
        'function':query_localpdb,
        'title_template':'the local copy of the PDB data.',
        'title_verb': ['Querying','Queries'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '5':{
        'function':process_localpdb_query_matches,
        'title_template':'the output files of the query_localpdb step.',
        'title_verb': ['Processing','Processes'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': False
    },
    '6':{
        'function':create_core_records,
        'title_template':'core records for each structure.',
        'title_verb': ['Creating','Creates'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': False
    },
    '7':{
        'function':fetch_chronology_data,
        'title_template':'chronology records from PDBe for each structure.',
        'title_verb': ['Fetching','Fetches'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '8':{
        'function':fetch_title_data,
        'title_template':'title records from PDBe for each structure.',
        'title_verb': ['Fetching','Fetches'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '9':{
        'function':fetch_experimental_data,
        'title_template':'experimental records from PDBe for each structure.',
        'title_verb': ['Fetching','Fetches'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '10':{
        'function':fetch_publication_data,
        'title_template':'publication records from PDBe/PMCe for each structure.',
        'title_verb': ['Fetching','Fetches'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '11':{
        'function':find_alike_chains,
        'title_template':'alike chains from localpdb.',
        'title_verb': ['Mapping','Maps'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '12':{
        'function':assign_species,
        'title_template':'a species to the complex.',
        'title_verb': ['Assigning','Assigns'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '13':{
        'function':assign_chain_types,
        'title_template':'the alike chains to specific chain types.',
        'title_verb': ['Assigning','Assigns'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '14':{
        'function':assign_complex_type,
        'title_template':'the the complex type from the chain types.',
        'title_verb': ['Assigning','Assigns'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '15':{
        'function':assign_allele_number,
        'title_template':'allele numbers from the IPD collection.',
        'title_verb': ['Assigning','Assigns'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '16':{
        'function':fetch_coordinates,
        'title_template':'the coordinates from the PDBe.',
        'title_verb': ['Fetching','Fetches'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '17':{
        'function':stub_function,
        'title_template':'the coordinates from the PDBe.',
        'title_verb': ['Relettering','Reletters'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '18':{
        'function':stub_function,
        'title_template':'the structure against a canonical structure.',
        'title_verb': ['Aligning','Aligns'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '19':{
        'function':stub_function,
        'title_template':'the peptide in the structure.',
        'title_verb': ['Characterizing','Charecterizes'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '20':{
        'function':stub_function,
        'title_template':'the peptide neighbours.',
        'title_verb': ['Mapping','Maps'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '20':{
        'function':stub_function,
        'title_template':'the sidechain binding pockets.',
        'title_verb': ['Mapping','Maps'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '21':{
        'function':stub_function,
        'title_template':'the hetatoms.',
        'title_verb': ['Cleaning','Cleans'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '22':{
        'function':stub_function,
        'title_template':'the structure into components.',
        'title_verb': ['Splitting','Splits'],
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    }

}