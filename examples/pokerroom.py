from poker.action import Action
from poker.card import Rank
from poker.game_state import GameState


# PokerRoom.com's nine tiers of starting hands, worked out from how much each hand won in real games played there, as
# Wikipedia's "Texas hold 'em starting hands" lists them, strongest first. A hand ending in "s" has both cards of the same suit, and one without it has two different suits.
TIERS = [
    {"AA", "KK", "QQ", "JJ", "AKs"},
    {"AQs", "TT", "AK", "AJs", "KQs", "99"},
    {"ATs", "AQ", "KJs", "88", "KTs", "QJs"},
    {"A9s", "AJ", "QTs", "KQ", "77", "JTs"},
    {"A8s", "K9s", "AT", "A5s", "A7s"},
    {"KJ", "66", "T9s", "A4s", "Q9s"},
    {"J9s", "QJ", "A6s", "55", "A3s", "K8s", "KT"},
    {"98s", "T8s", "K7s", "A2s"},
    {"87s", "QT", "Q8s", "44", "A9", "J8s", "76s", "JT"},
]

LETTERS = dict(zip(Rank, "23456789TJQKA"))  # Rank lists the ranks from lowest to highest


def hand(state: GameState) -> str:
    # Our two cards written like the tiers, such as "AKs", "AK" or "QQ"
    high, low = sorted(state.my_player.hole_cards, key=lambda card: list(Rank).index(card.rank), reverse=True)
    suited = high.suit is low.suit and high.rank is not low.rank
    return LETTERS[high.rank] + LETTERS[low.rank] + ("s" if suited else "")


def myAI(state: GameState) -> Action:
    # Goes all in with a hand in the top five of PokerRoom.com's nine tiers, and otherwise checks or folds
    if any(hand(state) in tier for tier in TIERS[:5]):
        return Action.raise_by(10 ** 9)  # More than anyone has, which puts us all in

    to_call = max(player.chips_bet for player in state.players) - state.my_player.chips_bet
    return Action.check() if to_call == 0 else Action.fold()
