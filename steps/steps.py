from test_step import test_step

steps = {
    '1':{
        'function':test_step,
        'title_template':'Creating the folder structure in the output directory',
        'list_item':'Creating the folder structure in the output directory',
        'is_multi': False,
        'multi_param': None,
        'multi_options': None
    },
    '2':{
        'function':test_step,
        'title_template':'Creating the folder structure in the output directory',
        'list_item':'Creating the folder structure in the output directory',
        'is_multi': True,
        'multi_param': 'pdb_code',
        'multi_options': ['1hhh','1hhi','1hhj','1hhk']
    }
}