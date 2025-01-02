from argparse import ArgumentError
from collections import deque
from dataclasses import dataclass
from random import shuffle, randint


def subtract(a: int, b: int) -> int:
    if a > b:
        return a - b
    else:
        return b - a


@dataclass
class Player:

    def __init__(self, name: str, tkns: int, _starting_hand: dict[str:int] = None,
                 _is_ai: bool = False, _do_talk: bool = True) -> None:
        self.name = name
        self.tokens = tkns
        self.discard = None
        self.hand_type: str = ''
        if _starting_hand is None:
            self.hand: dict = {
                'sand': None,
                'blood': None
            }
        else:
            self.hand = _starting_hand
        self.difference: int = 0
        self.round_bet: int = 0
        self.hand_rating: int = 4
        self.is_ai = _is_ai
        self.do_talk = _do_talk

    def _get_hand_rating(self) -> None:
        if 0 in self.hand.values():
            if self.hand['sand'] == self.hand['blood']:
                self.hand_rating = 0
            else:
                 self.hand_rating = 1
        elif 1 in self.hand.values():
            if self.hand['sand'] == self.hand['blood']:
                self.hand_rating = 2
            else:
                self.hand_rating = 4
        elif self.hand['sand'] == self.hand['blood']:
            self.hand_rating = 3
        else:
            self.hand_rating = 4

    def _get_hand_type(self) -> None:
        match self.hand_rating:
            case 0:
                self.hand_type = 'Pure Sylop Sabacc' # 0 | 0 diff = 0
            case 1:
                self.hand_type = 'Sylop Sabacc' # 0 or x | 0 or x but not 0 | 0 or x | x diff = x
            case 2:
                self.hand_type = 'Prime Sabacc' # 1 or x | 1 or x but not x | x diff = x - 1
            case 3:
                self.hand_type = 'Sabacc' # x | x but not any above diff = 0
            case 4:
                self.hand_type = f'{self.difference} Bet' # x | y diff = x - y

    def _replace_wild(self) -> None:
        for i, card in enumerate([self.hand['sand'], self.hand['blood']]):
            if card == 7:
                if i == 0:
                    self.hand['sand'] = randint(1, 6)
                else:
                    self.hand['blood'] = randint(1, 6)

    def eval_hand(self):
        self.difference = subtract(self.hand['sand'], self.hand['blood'])
        self._replace_wild()
        self._get_hand_rating()
        self._get_hand_type()

    def do_round(self, game_data: list[int]) -> list[int]:
        self.difference = subtract(self.hand['sand'], self.hand['blood'])
        if self.do_talk is True:
            print(f'|  {self.name} Readout\n|'
                  f'\n|  Difference of {self.hand['sand']} and {self.hand['blood']} is {self.difference}')
        if self.difference == 0:
            if self.do_talk is True:
                print('|  PERFECT HAND DETECTED\n|  PASSING')
                input('|\n| PETC')
            return [0]
        best_pick, highest_discard, hand = None, -1, [self.hand['blood'], self.hand['sand']]
        for i, card in enumerate(game_data):
            if subtract(card, hand[i]) < self.difference:
                if self.do_talk is True:
                    print(f'|  Ideal Pick from Discard Detected\n'
                          f'|  {best_pick} leads to a Difference of {subtract(card, hand[i])} < {self.difference}')
                best_pick = i
            if highest_discard > card:
                highest_discard = card
        if self.do_talk is True:
            print(f'|  Highest Discard Value is {highest_discard}')
            if best_pick is None and self.difference != 0 and highest_discard > 4:
                print('|  Highest Discard too low to consider Gambling')
        if best_pick is None and self.difference != 0 and highest_discard < 4:
            if self.hand['sand'] > self.hand['blood']:
                if self.do_talk is True:
                    print('| Worst Hand is Sand')
                worst_card = 0
            else:
                if self.do_talk is True:
                    print('| Worst Hand is Blood')
                worst_card = 1
            if -1 < randint(0, 1000) < 500:
                if self.do_talk is True:
                    print('| Best Choice is to draw from the Random deck on my Worst Hand')
                    input('\nPETC')
                return [1, worst_card]
            else:
                if self.do_talk is True:
                    print('| Best Choice is to Stand')
                    input('\nPETC')
                return [0]
        else:
            if self.do_talk is True:
                print(f'| Best Choice is to pick from the {best_pick} Discard Pile')
                input('\nPETC')
            return [2, best_pick]

    def confirm_choice(self, deck_id: str) -> int:
        # Evaluates which of the two cards creates the smallest difference between them
        if deck_id == 'sand':
            held_deck_id = 'blood'
        elif deck_id == 'blood':
            held_deck_id = 'sand'
        else:
            raise ArgumentError
        potential_difference = subtract(self.hand[held_deck_id], self.discard)
        if self.difference <= potential_difference:
            if self.do_talk is True:
                print(f'\n|  Best Choice is to keep my original hand\n|  {self.difference} <= {potential_difference}')
            return 2
        else:
            if self.do_talk is True:
                print(f'\n|  Best Choice is to swap to the drawn card\n|  {self.difference} > {potential_difference}')
            return 1


class Sabacc(Player):


    def __init__(self, tokens: int, players: int, _do_single_player: bool = False) -> None:
        self.tokens = tokens
        if _do_single_player is False:
            self.player_list = [Player(f'Test {i+1}', self.tokens) for i in range(players)]
        else:
            self.player_list = [Player('Person', self.tokens)]
            for i in range(players-1):
                self.player_list.append(Player(f'AI {i+1}', self.tokens, _is_ai=True))
        self.deck_size: int = 62
        self.deck: dict = {
            'sand': self._make_deck(),
            'blood': self._make_deck()
        }
        self.discard_pile: dict = {
            'sand': deque(),
            'blood': deque()
        }
        self.round_data: dict = {
            'number': 0,
            'same_rating': False,
            'same_hand': False
        }
        self.shift_tokens: list = []

    def do_flop(self) -> None:
        sand = self.deck['sand'].popleft()
        blood = self.deck['blood'].popleft()
        self.discard_pile['sand'].appendleft(sand)
        self.discard_pile['blood'].appendleft(blood)

    def init_round(self) -> None:
        for player in self.player_list:
            player.hand['sand'] = self.deck['sand'][0]
            player.hand['blood'] = self.deck['blood'][0]
            self.do_flop()

    def _make_deck(self, _deck_size: int = None) -> deque:
        if _deck_size is None:
            _deck_size = self.deck_size//2
        deck, val, section = [], 0, _deck_size//7
        for i in range(_deck_size):
            deck.append(val)
            if (i % section) == 0 and i != 0:
                val += 1
        while len(deck) != _deck_size:
            if len(deck) < _deck_size:
                deck.append(7)
            if len(deck) > _deck_size:
                deck.pop()
        shuffle(deck)
        return deque(deck)

    def do_discard(self, plr: Player, _deck: str = 'sand', _from_discard: bool = True) -> None:
        if _from_discard is True:
            card = plr.discard
        else:
            card = plr.hand[_deck]
            plr.hand[_deck] = plr.discard
        plr.discard = None
        self.discard_pile[_deck].appendleft(card)

    def eval_hands(self) -> Player or None:
        best_hand_rating, lowest_diff = 5, 999
        best_hand, data_list = None, []
        for player in self.player_list:
            player.eval_hand()
            data_list.append([player.hand_type, player.difference, player])
            if player.hand_rating < best_hand_rating:
                best_hand_rating = player.hand_rating
                lowest_diff = player.difference
                best_hand = player
                continue
            if player.hand_rating == best_hand_rating and player.hand_rating != 0 and player.hand_rating != 3:
                if player.difference < best_hand.difference:
                    best_hand_rating = player.hand_rating
                    lowest_diff = player.difference
                    best_hand = player
                    continue
        all_same_hand, all_same_diff = True, True
        for data in data_list:
            if data[0] != best_hand.hand_type:
                all_same_hand = False
            if data[1] != best_hand.difference:
                all_same_diff = False
            if all_same_hand is False and all_same_diff is False:
                break
        self.round_data['same_hand'] = all_same_hand
        self.round_data['same_rating'] = all_same_diff
        if all_same_hand is True and all_same_diff is True:
            return None
        elif all_same_hand is True and all_same_diff is False:
            for data in data_list:
                if data[1] < lowest_diff:
                    lowest_diff = data[1]
                    best_hand = data[2]
            return best_hand
        else:
            return best_hand

    def wipe_round_data(self) -> None:
        self.round_data['number'] = 0
        self.round_data['same_hand'] = False
        self.round_data['same_rating'] = False
