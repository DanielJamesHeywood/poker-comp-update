from collections import defaultdict

from poker.action import Action
from poker.game_state import GameState

from sklansky_and_malmuth import myAI as sklansky_and_malmuth  # The bot in sklansky_and_malmuth.py, next to this one


# What we've seen each other player do, by their id. We only see the table when it's our turn, so these count how many
# times we've looked at each player, and how many of those times they had raised without going all in, which is having
# the biggest bet at the table when it's more than the big blind, with chips still left.
looks: dict[int, int] = defaultdict(int)
raised: dict[int, int] = defaultdict(int)
LEAST_LOOKS = 10  # Before this many looks at a player, we don't know them well enough to say what they usually do


def take_notes(state: GameState):
    biggest = max(state.players, key=lambda player: player.chips_bet)

    for player in state.players:
        if player is not state.my_player:
            looks[player.id] += 1

    if biggest is not state.my_player and biggest.chips_bet > state.big_blind and biggest.chips_in_stack > 0:
        raised[biggest.id] += 1


def bet_is_from_frequent_raiser(state: GameState) -> bool:
    # Whether there's a raise to call, made without going all in by a player who had raised in at least a fifth of at least
    # 10 looks at them. Raising small often means a weak hand, which folds when we go all in.
    biggest = max(state.players, key=lambda player: player.chips_bet)

    if biggest is state.my_player or biggest.chips_bet <= state.big_blind or biggest.chips_in_stack == 0 or looks[biggest.id] < LEAST_LOOKS:
        return False

    return raised[biggest.id] >= looks[biggest.id] / 5


def myAI(state: GameState) -> Action:
    # Plays as sklansky_and_malmuth, and also goes all in against a raise from a player we've often seen raising without going all in
    take_notes(state)

    if bet_is_from_frequent_raiser(state):
        return Action.raise_by(10 ** 9)  # More than anyone has, which puts us all in

    return sklansky_and_malmuth(state)
