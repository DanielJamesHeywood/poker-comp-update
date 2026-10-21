from collections import defaultdict

from poker.action import Action
from poker.card import Rank
from poker.game_state import GameState


# Phil Hellmuth's tiers of starting hands, from his book Play Poker Like the Pros, as Wikipedia's "Texas hold 'em starting
# hands" lists them. A hand ending in "s" has both cards of the same suit, and one without it has two different suits.
TIERS = {
    1: {"AA", "KK", "AKs", "QQ", "AK"},
    2: {"JJ", "TT", "99"},
    3: {"88", "77", "AQs", "AQ"},
    4: {"66", "55", "44", "33", "22", "AJs", "ATs", "A9s", "A8s"},
    5: {"A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KQs", "KQ"},
    6: {"QJs", "JTs", "T9s", "98s", "87s", "76s", "65s"},
}
LETTERS = dict(zip(Rank, "23456789TJQKA"))  # Rank lists the ranks from lowest to highest


def tier(state: GameState) -> int | None:
    # Which tier our two cards are in, or None if they're in none of them
    high, low = sorted(state.my_player.hole_cards, key=lambda card: list(Rank).index(card.rank), reverse=True)
    hand = LETTERS[high.rank] + LETTERS[low.rank] + ("s" if high.suit is low.suit and high.rank is not low.rank else "")
    return next((number for number, hands in TIERS.items() if hand in hands), None)


# What we've seen each other player do, by their id. We only see the table when it's our turn, so these count how many
# times we've looked at each player, and how many of those times they had folded.
looks: dict[int, int] = defaultdict(int)
folded: dict[int, int] = defaultdict(int)
LEAST_LOOKS = 10  # Before this many looks at a player, we don't know them well enough to say what they usually do


def take_notes(state: GameState):
    others = [player for player in state.players if player is not state.my_player]

    for player in others:
        looks[player.id] += 1
        folded[player.id] += player.has_folded


def share(counts: dict[int, int], player) -> float:
    # The share of our looks at the player which counted, or 0 if we haven't looked at them enough times yet
    return counts[player.id] / looks[player.id] if looks[player.id] >= LEAST_LOOKS else 0.0


def others_usually_fold(state: GameState) -> bool:
    # Whether everyone else still in the hand had folded in at least four fifths of our looks at them
    left = [player for player in state.players if player is not state.my_player and not player.has_folded]
    return all(share(folded, player) >= 4 / 5 for player in left)


def go_all_in() -> Action:
    return Action.raise_by(10 ** 9)  # More than anyone has, which puts us all in


def check_or_fold(state: GameState) -> Action:
    to_call = max(player.chips_bet for player in state.players) - state.my_player.chips_bet
    return Action.check() if to_call == 0 else Action.fold()


def myAI(state: GameState) -> Action:
    # Goes all in with a hand in tiers 1 to 5, or with any hand when everyone else still in the hand had folded in at least four fifths of our looks at them, and otherwise checks or folds
    take_notes(state)

    if tier(state) in (1, 2, 3, 4, 5) or others_usually_fold(state):
        return go_all_in()

    return check_or_fold(state)
