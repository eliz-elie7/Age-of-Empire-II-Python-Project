from .General import General
from .BrainDead import BrainDead
from .Daft import Daft
from .Napoleon import Napoleon
from .SunTzu import SunTzu

GENERALS = {
    "braindead": BrainDead,
    "daft": Daft,
    "napoleon": Napoleon,
    "suntzu": SunTzu,
}

def get_general(name):
    try:
        return GENERALS[name.lower()]
    except KeyError:
        raise ValueError(f"Général IA inconnu : {name}")