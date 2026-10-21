from collections import defaultdict

from poker.action import Action
from poker.game_state import GameState


# What we've seen each other player do, by their id. We only see the table when it's our turn, so these count how many
# times we've looked at each player, and how many of those times they had raised, which is having the biggest bet
# at the table when it's more than the big blind.
looks: dict[int, int] = defaultdict(int)
raised: dict[int, int] = defaultdict(int)
LEAST_LOOKS = 10  # Before this many looks at a player, we don't know them well enough to say what they usually do


def take_notes(state: GameState):
    others = [player for player in state.players if player is not state.my_player]
    biggest = max(state.players, key=lambda player: player.chips_bet)

    for player in others:
        looks[player.id] += 1

    if biggest is not state.my_player and biggest.chips_bet > state.big_blind:
        raised[biggest.id] += 1


def share(counts: dict[int, int], player) -> float:
    # The share of our looks at the player which counted, or 0 if we haven't looked at them enough times yet
    return counts[player.id] / looks[player.id] if looks[player.id] >= LEAST_LOOKS else 0.0


def bet_is_from_frequent_raiser(state: GameState) -> bool:
    # Whether there's a raise to call, made by a player who had raised in at least a fifth of our looks at them
    biggest = max(state.players, key=lambda player: player.chips_bet)
    return biggest is not state.my_player and biggest.chips_bet > state.big_blind and share(raised, biggest) >= 1 / 5


def go_all_in() -> Action:
    return Action.raise_by(10 ** 9)  # More than anyone has, which puts us all in


def check_or_fold(state: GameState) -> Action:
    to_call = max(player.chips_bet for player in state.players) - state.my_player.chips_bet
    return Action.check() if to_call == 0 else Action.fold()


def myAI(state: GameState) -> Action:
    # Goes all in against a raise from a player who had raised in at least a fifth of our looks at them, and otherwise checks or folds
    take_notes(state)

    if bet_is_from_frequent_raiser(state):
        return go_all_in()

    return check_or_fold(state)
