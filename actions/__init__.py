from .aligner import align_action

from .shared.pipeline import load_config

available_actions = {
    'align_to_canonical':{
        'action':align_action,
        'title':'Align to Canonical Structure'
    }
}



action_ordering = ['align_to_canonical']