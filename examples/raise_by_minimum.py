from poker.action import Action
from poker.game_state import GameState


def myAI(state: GameState) -> Action:
    # Raises by the smallest amount allowed every time it can, and otherwise calls
    if state.min_raise is None:
        return Action.call()  # Raising isn't allowed, so this calls, or checks when there's nothing to call

    return Action.raise_by(state.min_raise)
