from poker.action import Action
from poker.game_state import GameState


def myAI(state: GameState) -> Action:
    # Raises by the size of the pot every time it can, and otherwise calls
    if state.min_raise is None:
        return Action.call()  # Raising isn't allowed, so this calls, or checks when there's nothing to call

    to_call = max(player.chips_bet for player in state.players) - state.my_player.chips_bet
    pot_after_calling = state.chips_in_pot + to_call
    return Action.raise_by(max(pot_after_calling, state.min_raise))  # More than we have puts us all in
