from examples.defaultAI import defaultAI

from poker.action import Action
from poker.game_state import GameState


def myAI(state: GameState) -> Action:
    return defaultAI(state) # This ai runs if myAI raises an exception, returns an invalid action or takes too long
