from update_localpdb import update_localpdb
from fetch_stcrdab_info import fetch_stcrdab_info
from fetch_sabdab_info import fetch_sabdab_info

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
    }

}