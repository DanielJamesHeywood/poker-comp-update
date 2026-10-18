from poker.action import Action
from poker.game_state import GameState

def myAI(state: GameState) -> Action:
    return Action.check() if state.my_player.chips_bet == max(player.chips_bet for player in state.players) else Action.fold()
