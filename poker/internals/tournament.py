from __future__ import annotations

import math
from dataclasses import dataclass

from .engine import AI, Match, Seat
from .rules import Rules


TABLE_SIZE = 8  # The most players who can sit at one table


@dataclass
class Result:
    # Where a player finished. Players who went out say on which hand, and at which table.
    place: int
    name: str
    stack: int
    errors: int
    table: int | None = None
    hand: int | None = None


class Table:
    def __init__(self, number: int, match: Match):
        self.number = number  # Counting from 1
        self.match = match
        self.closed = False
        self.moved_to: list[int] = []  # The tables its players were sent to, once it has closed

    def players(self) -> list[Seat]:
        # The players still in at this table
        return [seat for seat in self.match.seats if seat.stack > 0]

    def hands_played(self) -> int:
        return len(self.match.hands)

    def in_play(self) -> bool:
        # Still open, with hands left to play. It may be down to one player, waiting for players to be moved to it or from it.
        return not self.closed and bool(self.players()) and self.hands_played() < self.match.rules.hands

    def can_deal(self) -> bool:
        return self.in_play() and not self.match.is_over()


class Tournament:
    # One or more tables of poker. Players are shared out between as few tables as they fit at, and as tables empty
    # the smallest is broken up and its players sent to the others. The tournament is over once one player has every chip,
    # or once no table can deal another hand, because each table has played the most hands which the rules allow.
    def __init__(self, *, ais: list[tuple[str, AI]], rules: Rules | None = None, seed: int | None = None, table_size: int = TABLE_SIZE):
        if len(ais) < 2:
            raise ValueError(f"Expected at least 2 AIs, but there were {len(ais)}")

        self.rules = rules if rules is not None else Rules()
        self.table_size = table_size
        count = math.ceil(len(ais) / table_size)
        self.tables: list[Table] = []

        for index in range(count):
            # Dealt out in turn like cards, so that the tables are as even as they can be. The first table gets the seed itself,
            # so a single table plays exactly the same hands as a Match would.
            table_seed = seed if seed is None or index == 0 else f"{seed}/{index}"
            self.tables.append(Table(index + 1, Match(ais=ais[index::count], rules=self.rules, seed=table_seed)))

        self.entrants = len(ais)
        self.out: list[Result] = []  # In the order players went out
        self.recorded: set[Seat] = set()

    # ---- Playing

    def play(self):
        # Plays the whole tournament without watching it, keeping the tables level by always dealing at the one which is furthest behind
        while not self.is_over():
            table = min((table for table in self.tables if table.can_deal()), key=lambda table: (table.hands_played(), table.number))
            self.play_hand(table)

    def play_hand(self, table: Table) -> dict:
        # Plays the next hand at a table, then moves players between tables if they need it. Returns the hand that was played.
        match = table.match
        match.play_hand(table.hands_played() + 1)
        hand = match.hands[-1]
        self.record_exits(table, hand)
        self.rebalance()
        return hand

    def is_over(self) -> bool:
        return len(self.players()) < 2 or not any(table.can_deal() for table in self.tables)

    def players(self) -> list[Seat]:
        return [seat for table in self.tables for seat in table.players()]

    def open_tables(self) -> list[Table]:
        return [table for table in self.tables if not table.closed]

    def hands_played(self) -> int:
        return sum(table.hands_played() for table in self.tables)

    # ---- Going out

    def record_exits(self, table: Table, hand: dict):
        # Everyone who went out in this hand takes the places just below the players still in. Of those, whoever started
        # the hand with more chips finishes higher, as is usual in a tournament.
        busted = [seat for seat in table.match.seats if seat.stack == 0 and seat not in self.recorded]

        if not busted:
            return

        started = dict(zip(hand["players"], hand["frames"][0]["stacks"]))
        busted.sort(key=lambda seat: started.get(seat.name, 0), reverse=True)
        remaining = len(self.players())

        for offset, seat in reversed(list(enumerate(busted))):  # The lowest place is listed first, as if they went out first
            self.recorded.add(seat)
            self.out.append(Result(place=remaining + 1 + offset, name=seat.name, stack=0, errors=seat.errors, table=table.number, hand=hand["number"]))

    def standings(self) -> list[Result]:
        # Players still in come first, most chips first, then everyone who went out, the last to go out first
        still_in = sorted(self.players(), key=lambda seat: seat.stack, reverse=True)
        results = [Result(place=place, name=seat.name, stack=seat.stack, errors=seat.errors) for place, seat in enumerate(still_in, start=1)]
        return results + sorted(self.out, key=lambda result: result.place)

    # ---- Moving players

    def rebalance(self):
        # Only tables with hands left take part. A table which has played all its hands keeps its players.
        tables = [table for table in self.tables if table.in_play()]

        if len(tables) < 2:
            return

        # Break up the smallest tables while the players would fit at fewer of them
        while len(tables) > 1 and len(tables) > math.ceil(sum(len(table.players()) for table in tables) / self.table_size):
            closing = min(tables, key=lambda table: (len(table.players()), -table.number))
            tables.remove(closing)

            for seat in list(closing.players()):
                target = min(tables, key=lambda table: (len(table.players()), table.number))
                self.move(seat, closing, target)

                if target.number not in closing.moved_to:
                    closing.moved_to.append(target.number)

            closing.closed = True

        # Then keep the tables within one player of each other, so nobody sits short-handed for long
        while True:
            biggest = max(tables, key=lambda table: (len(table.players()), -table.number))
            smallest = min(tables, key=lambda table: (len(table.players()), table.number))

            if len(biggest.players()) - len(smallest.players()) < 2:
                break

            self.move(self.next_big_blind(biggest), biggest, smallest)

    def next_big_blind(self, table: Table) -> Seat:
        # The player who would pay the big blind next at this table moves, which is the usual way to choose
        match = table.match
        order = [match.seats[(match.button + 1 + index) % len(match.seats)] for index in range(len(match.seats))]
        order = [seat for seat in order if seat.stack > 0]
        return order[min(2, len(order) - 1)]

    def move(self, seat: Seat, source: Table, target: Table):
        source.match.remove(seat)

        # Anyone who has gone out at the table being moved to gives up their seat first, so there is room
        for gone in [other for other in target.match.seats if other.stack == 0]:
            target.match.remove(gone)

        target.match.add(seat)
        source.match.notes.append(f"{seat.name} moves to table {target.number}")
        target.match.notes.append(f"{seat.name} joins from table {source.number}")
