from poker.action import Action
from poker.game_state import GameState


def myAI(state: GameState) -> Action:
    # Goes all in every time it's allowed to raise, and otherwise calls
    if state.min_raise is None:
        return Action.call()  # Raising isn't allowed, so this calls, which may put us all in anyway

    return Action.raise_by(state.my_player.chips_in_stack)  # More than we have left after calling, which puts us all in
