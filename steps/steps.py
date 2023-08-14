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
    }
}