"""

Contains utils class that are used by the main

"""
import copy
import sys

from utils import  *


def card_fight(attacker, defender):
    if attacker is not None:
        damage_done = attacker.power
        if 'WEAKNESS' in attacker.effects:
            damage_done -= 1
            if damage_done < 0:
                damage_done = 0

        if defender is None:
            return damage_done
        else:
            if 'DEATH' in attacker.effects:
                defender.health = 0
            starting_health = defender.health
            defender.health -= damage_done
            if defender.health <= 0:
                defender = None
                return damage_done - starting_health
    return 0


class BoardState:
    """This class is a wrapper for the cardio board state
    """

    def __init__(self, board=None, deck=None, hand=None, enemy_cards=None, player_health=6, enemy_health=6):
        self.board = board
        self.hand = hand
        self.deck = deck
        self.hamsters_remaining = 10
        self.spirits = 3

        self.player_health = player_health

        self.enemy_cards = enemy_cards
        self.enemy_health = enemy_health

        self.has_drawn_card = False
        self.has_fought = False

        self.turn_stats = TurnStats()

    def set_player_cards(self, board, hand, deck, spirits, hamsters_remaining, has_drawn_card=False):
        self.board = board
        self.hand = hand
        self.deck = deck
        self.spirits = spirits
        self.hamsters_remaining = hamsters_remaining
        self.has_drawn_card = has_drawn_card

    def set_enemy_cards(self, enemy_cards):
        self.enemy_cards = enemy_cards

    def set_health(self, player_health=6, enemy_health=6):
        self.player_health = player_health
        self.enemy_health = enemy_health

    def draw_card(self):
        card = self.deck[0]
        self.deck.pop(0)
        self.hand.append(card)
        self.has_drawn_card = True

    def draw_hamster(self):
        self.hand.append(Card(name="Hamster", power=0, health=1, fire_cost=0))
        self.hamsters_remaining -= 1
        self.has_drawn_card = True

    def play_card(self, card_index, position, sacrifice=None, spirit_count=0):
        card_to_play = self.hand[card_index]
        self.hand.pop(card_index)

        if sacrifice is not None:
            for s in sacrifice:
                self.board[s] = None

        if spirit_count > 0:
            self.spirits -= spirit_count

        self.board[position] = card_to_play

    def fights(self):
        for i in range(4):
            self.fight(i, True)
    #         player cards

        for i in range(4):
            self.fight(i, False)
    #         enemy front line

        for i in range(4):
            if self.enemy_cards[i] is None and self.enemy_cards[i + 4] is not None:
                self.enemy_cards[i] = copy.deepcopy(self.enemy_cards[i + 4])
                self.enemy_cards[i + 4] = None
                self.fight(i, False)
    #         enemy back line

        self.has_fought = True

    def fight(self, index, player_is_attacker=False):
        if player_is_attacker:
            damage = card_fight(self.board[index], self.enemy_cards[index])
            self.turn_stats.damage_enemy(damage)
            self.enemy_health -= damage
            if damage > 0 and self.enemy_cards[index] is None:
                self.player_health += damage
                self.turn_stats.damage_player(-damage)
                if self.player_health > 5:
                    self.player_health = 5
        else:
            there_is_a_defender = False
            if self.board[index] is not None:
                there_is_a_defender = True
            damage = card_fight(self.enemy_cards[index], self.board[index])
            self.turn_stats.damage_player(damage)
            self.player_health -= damage
            if damage > 0 and self.board[index] is None:
                if there_is_a_defender:
                    self.spirits += 1
                self.enemy_health += damage
                self.turn_stats.damage_enemy(-damage)
                if self.enemy_health > 5:
                    self.enemy_health = 5



    def print(self):
        print("Board State")
        print(f"Enemy Health: {self.enemy_health}")
        print(f"Player Health: {self.player_health}")
        print("Enemy Cards")
        for card in self.enemy_cards:
            if card is not None:
                card.print()
        print("Player Cards")
        print("Board")
        for card in self.board:
            if card is not None:
                card.print()
        print("Hand")
        for card in self.hand:
            if card is not None:
                card.print()
        print(f"Draw Pile: {len(self.deck)}")
        print(f"Hamsters: {self.hamsters_remaining}")


class TurnStats:

    def __init__(self):
        self.total_damage_done_to_player = 0
        self.total_damage_done_to_enemy = 0

        self.max_power_on_player_side = 0
        self.max_power_on_enemy_side = 0
        self.num_player_cards_on_the_board = 0
        self.num_enemy_cards_on_the_board = 0
        self.num_player_cards_in_hand = 0
        self.num_player_cards_in_deck = 0

    def damage_player(self, amount):
        self.total_damage_done_to_player += amount

    def damage_enemy(self, amount):
        self.total_damage_done_to_enemy += amount

    def get_max_power_on_player_side(self, board=None, hand=None, deck=None):
        self.max_power_on_player_side = 0

        if board is not None:
            for card in board:
                if card is not None:
                    if 'WEAKNESS' in card.effects:
                        self.max_power_on_player_side += (card.power - 1)
                    else:
                        self.max_power_on_player_side += card.power

        if hand is not None:
            for card in hand:
                if card is not None:
                    if 'WEAKNESS' in card.effects:
                        self.max_power_on_player_side += (card.power - 1)
                    else:
                        self.max_power_on_player_side += card.power

        if deck is not None:
            for card in deck:
                if card is not None:
                    if 'WEAKNESS' in card.effects:
                        self.max_power_on_player_side += (card.power - 1)
                    else:
                        self.max_power_on_player_side += card.power

        return self.max_power_on_player_side

    def get_max_power_on_enemy_side(self, enemy_cards):
        self.max_power_on_enemy_side = 0

        if enemy_cards is not None:
            for card in enemy_cards:
                if card is not None:
                    if 'WEAKNESS' in card.effects:
                        self.max_power_on_enemy_side += (card.power - 1)
                    else:
                        self.max_power_on_enemy_side += card.power

        return self.max_power_on_enemy_side

    def get_difference_in_max_power_favoring_player(self, state):
        player_total = self.get_max_power_on_player_side(state.board)
        enemy_total = self.get_max_power_on_enemy_side(state.enemy_cards)
        return player_total - enemy_total

    def get_num_player_cards_on_board(self, board):
        self.num_player_cards_on_the_board = 0
        for card in board:
            if card is not None:
                self.num_player_cards_on_the_board += 1
        return self.num_player_cards_on_the_board

    def get_num_enemy_cards_on_board(self, enemy_cards):
        self.num_enemy_cards_on_the_board = 0
        for card in enemy_cards:
            if card is not None:
                self.num_enemy_cards_on_the_board += 1
        return self.num_enemy_cards_on_the_board

    def get_difference_in_cards_on_board_favoring_player(self, state):
        player_total = self.get_num_player_cards_on_board(state.board)
        enemy_total = self.get_num_enemy_cards_on_board(state.enemy_cards)
        return player_total - enemy_total

    def get_num_player_cards_in_hand(self, hand):
        self.num_player_cards_in_hand = 0
        for card in hand:
            if card is not None:
                self.num_player_cards_in_hand += 1
        return self.num_player_cards_in_hand

    def get_num_player_cards_in_deck(self, deck):
        self.num_player_cards_in_deck = 0
        for card in deck:
            if card is not None:
                self.num_player_cards_in_deck += 1
        return self.num_player_cards_in_deck


class PlayerCards:
    """
    This is a wrapper class to hold all the players cards
    """

    def __init__(self, board, hand, deck):
        self.board = board
        self.hand = hand
        self.deck = deck
        self.hamsters_remaining = 10

    def draw_card(self):
        card = self.deck[0]
        self.deck.pop(0)
        self.hand.append(card)

    def draw_hamster(self):
        self.hand.append(Card(name="Hamster", power=0, health=1, cost=0))
        self.hamsters_remaining -= 1

    def play_card(self, card_index, position, sacrifice=None):
        card_to_play = self.hand[card_index]
        self.hand.pop(card_index)

        if sacrifice is not None:
            for s in sacrifice:
                self.board[s] = None

        self.board[position] = card_to_play

    def print(self):
        print("Player Cards")
        print("Board")
        for card in self.board:
            if card is not None:
                card.print()
        print("Hand")
        for card in self.hand:
            if card is not None:
                card.print()
        print(f"Draw Pile: {len(self.deck)}")
        print(f"Hamsters: {self.hamsters_remaining}")


class Card:
    """
    This class will store data about cards that the AI cares about
    """

    def __init__(self, name="Example", power=1, health=1, fire_cost=1, spirit_cost=0, has_fire=0, has_spirit=0,
                 effects=None):
        if effects is None:
            effects = []
        self.name = name
        self.power = power
        self.health = health
        self.fire_cost = fire_cost
        self.spirit_cost = spirit_cost
        self.has_fire = has_fire
        self.has_spirit = has_spirit
        self.effects = effects

    def print(self):
        print(f"{self.name} power:{self.power} health:{self.health} fire_cost:{self.fire_cost}")


class Memoize:

    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        # Warning: You may wish to do a deepcopy here if returning objects
        return self.memo[args]

