from update_localpdb import update_localpdb
from fetch_stcrdab_info import fetch_stcrdab_info
from fetch_sabdab_info import fetch_sabdab_info
from query_localpdb import query_localpdb
from process_localpdb_query_matches import process_localpdb_query_matches
from create_core_records import create_core_records
from fetch_chronology_data import fetch_chronology_data


steps = {
    '1':{
        'function':update_localpdb,
        'title_template':'Updating the local copy of the pdb using localpdb.',
        'list_item':'Updates the local copy of the pdb using localpdb.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '2':{
        'function':fetch_stcrdab_info,
        'title_template':'Updating the local copy of the data from STCRDab.',
        'list_item':'Updates the local copy of the data from STCRDab.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '3':{
        'function':fetch_sabdab_info,
        'title_template':'Updating the local copy of the data from SABDab.',
        'list_item':'Updates the local copy of the data from SABDab.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '4':{
        'function':query_localpdb,
        'title_template':'Querying the local copy of the PDB data.',
        'list_item':'Queries the local copy of the PDB data.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '5':{
        'function':process_localpdb_query_matches,
        'title_template':'Processing the output files of the query_localpdb step.',
        'list_item':'Processes the output files of the query_localpdb step.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '6':{
        'function':create_core_records,
        'title_template':'Creating core records for each structure.',
        'list_item':'Creates core records for each structure.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    },
    '7':{
        'function':fetch_chronology_data,
        'title_template':'Fetching chronology records from PDBe for each structure.',
        'list_item':'Fetches chronology records from PDBe for each structure.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None,
        'has_progress': True
    }

}