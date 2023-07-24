from test_step import test_step
from update_localpdb import update_localpdb

steps = {
    '1':{
        'function':update_localpdb,
        'title_template':'Updating the local copy of the pdb using localpbd.',
        'list_item':'Updating the local copy of the pdb using localpbd.',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None
    }
}