"""Package generals - Intelligences artificielles"""

from .General import General
from .BrainDead import BrainDead
from .Daft import Daft

GENERALS = {
    "braindead": BrainDead,
    "daft": Daft,
}

def get_general(name):
    try:
        return GENERALS[name.lower()]()
    except KeyError:
        raise ValueError(f"Général inconnu : {name}")
