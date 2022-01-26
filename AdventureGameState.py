
from enum import Enum, auto

class AdventureGameState(Enum):
    STARTING = auto()
    STARTED = auto()
    PLAYING = auto()
    FINISHEDWON = auto()
    FINISHEDLOST = auto()
    QUITTING = auto()
    QUIT = auto()
