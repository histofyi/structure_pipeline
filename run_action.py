from actions import align_action, available_actions
from actions import load_config

from rich import print
from rich.console import Console
console = Console()



config = load_config()

this_action = 'align_to_canonical'

action = available_actions[this_action]['action']
action_title = available_actions[this_action]['title']

console.print("")
console.rule(f"[bold white]Running {action_title}")

action(config, 'class_i', '6nf7-assembly1.cif')