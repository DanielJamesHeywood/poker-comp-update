from poker.action import Action
from poker.game_state import GameState


def myAI(state: GameState) -> Action:
    # Raises by half of the chips it has left after calling, or by the smallest raise if that's more, every time it can
    if state.min_raise is None:
        return Action.call()  # Raising isn't allowed, so this calls, or checks when there's nothing to call

    to_call = max(player.chips_bet for player in state.players) - state.my_player.chips_bet
    left_after_calling = state.my_player.chips_in_stack - to_call
    return Action.raise_by(max(left_after_calling // 2, state.min_raise))
