from poker.action import Action
from poker.game_state import GameState

def myAI(state: GameState) -> Action:
    return Action.raise_by(1) if state.my_player.chips_in_stack else Action.check()
