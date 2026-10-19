from poker.action import Action
from poker.game_state import GameState

def myAI(state: GameState) -> Action:
    card, other_card = state.my_player.hole_cards
    return Action.raise_by(state.my_player.chips_in_stack) if card.rank == other_card.rank else defaultAI(state)


def defaultAI(state: GameState) -> Action: # This ai runs if myAI raises an exception, returns an invalid action or takes too long
    return Action.check() if not state.my_player.chips_in_stack or state.my_player.chips_bet == max(player.chips_bet for player in state.players) else Action.fold()
