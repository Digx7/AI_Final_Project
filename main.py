import copy

from search import *
from data import *
from itertools import combinations
import ast

class Cardio(Problem):
    def __init__(self, initial, goal=None, goal_threshold=None):
        super().__init__(initial, goal)
        self.goal_threshold = goal_threshold

    def actions(self, state):
        available_actions = []

        if not state.has_drawn_card:
            if len(state.deck) > 0:
                available_actions.append('DRAW_CARD')
            if state.hamsters_remaining > 0:
                available_actions.append('DRAW_HAMSTER')

            # print(available_actions)
            return available_actions

        if not state.has_fought:
            available_actions.append('FIGHT')

        sacrificableCards = []
        emptyBoardSlots = []
        max_sacrificable = 0

        for j in range(4):
            if state.board[j] is None:
                emptyBoardSlots.append(j)
            if state.board[j] is not None:
                if state.board[j].has_fire == 0:
                    sacrificableCards.append(j)
                    max_sacrificable += 1

        for i in range(len(state.hand)):
            if state.hand[i].fire_cost == 0 and state.hand[i].spirit_cost == 0:
                for j in emptyBoardSlots:
                    available_actions.append(f'PLAYCARD_{i}_AT_{j}')
            if 0 < state.hand[i].fire_cost <= max_sacrificable and state.hand[i].spirit_cost == 0:
                sacrific_combos = list(combinations(sacrificableCards, state.hand[i].fire_cost))
                for j in emptyBoardSlots:
                    for k in sacrific_combos:
                        available_actions.append(f'PLAYCARD_{i}_AT_{j}_SACRICE_{k}')
                for k in sacrific_combos:
                    for j in k:
                        available_actions.append(f'PLAYCARD_{i}_AT_{j}_SACRICE_{k}')
            if 0 < state.hand[i].spirit_cost <= state.spirits and state.hand[i].fire_cost == 0:
                k = state.hand[i].spirit_cost
                for j in emptyBoardSlots:
                    available_actions.append(f'PLAYCARD_{i}_AT_{j}_SPIRIT_{k}')

        # print("With this state")
        # state.print()
        # print("You get these possible actions")
        # print(available_actions)
        return available_actions

    def result(self, state, action):
        if action == 'FIGHT':
            new_state = copy.deepcopy(state)
            new_state.fights()
            return new_state

        elif action == 'DRAW_HAMSTER':
            new_state = copy.deepcopy(state)
            new_state.draw_hamster()
            return new_state

        elif action == 'DRAW_CARD':
            new_state = copy.deepcopy(state)
            new_state.draw_card()
            return new_state

        else:
            inputs = action.split('_')
            if inputs[0] == "PLAYCARD":
                if len(inputs) > 5:
                    if inputs[4] == "SACRICE":
                        new_state = copy.deepcopy(state)
                        # print(inputs[5])
                        tuple_from_string = ast.literal_eval(inputs[5])
                        sacrifice_list = list(tuple_from_string)
                        new_state.play_card(int(inputs[1]), int(inputs[3]), sacrifice=sacrifice_list)
                        return new_state
                    if inputs[4] == "SPIRIT":
                        new_state = copy.deepcopy(state)
                        new_state.play_card(int(inputs[1]), int(inputs[3]), spirit_count=int(inputs[5]))
                        return new_state
                else:
                    new_state = copy.deepcopy(state)
                    new_state.play_card(int(inputs[1]), int(inputs[3]))
                    return new_state
            else:
                print("WARNING Non PLAYCARD complex action was detected")

    def heiristic_test(self, state):
        damage_to_enemy = state.turn_stats.total_damage_done_to_enemy
        power_advantage = state.turn_stats.get_difference_in_max_power_favoring_player(state)
        damage_taken = state.turn_stats.total_damage_done_to_player

        player_is_dead = 0
        enemy_is_dead = 0
        is_stalemate = 0

        if state.enemy_health == self.initial.enemy_health and state.player_health == self.initial.player_health:
            if state.turn_stats.get_num_player_cards_on_board(state.board) == self.initial.turn_stats.get_num_player_cards_on_board(self.initial.board):
                is_stalemate = 100

        if state.player_health <= 0:
            player_is_dead = 999

        if state.enemy_health <= 0:
            enemy_is_dead = 100

        return (2 * damage_to_enemy) + power_advantage - (1.5 * damage_taken) + enemy_is_dead - player_is_dead - is_stalemate

    def goal_test(self, state):

        if self.heiristic_test(state) > self.goal_threshold:
            return True
        else:
            return False

        # if self.goal_type == 0:
        #     if state.turn_stats.total_damage_done_to_enemy >= 5:
        #         return True
        #     return False
        # elif self.goal_type == 1:
        #     if state.turn_stats.total_damage_done_to_enemy >= 4:
        #         return True
        #     return False
        # elif self.goal_type == 2:
        #     if state.turn_stats.total_damage_done_to_enemy >= 3:
        #         return True
        #     return False
        # elif self.goal_type == 3:
        #     if state.turn_stats.total_damage_done_to_enemy >= 2:
        #         return True
        #     return False
        # elif self.goal_type == 4:
        #     if state.turn_stats.total_damage_done_to_enemy >= 1:
        #         return True
        #     return False
        # elif self.goal_type == 5:
        #     if state.turn_stats.get_difference_in_max_power_favoring_player(state) >= 4:
        #         return True
        #     return False
        # elif self.goal_type == 6:
        #     if state.turn_stats.get_difference_in_max_power_favoring_player(state) >= 3:
        #         return True
        #     return False
        # elif self.goal_type == 7:
        #     if state.turn_stats.get_difference_in_max_power_favoring_player(state) >= 2:
        #         return True
        #     return False
        # elif self.goal_type == 8:
        #     if state.turn_stats.get_difference_in_max_power_favoring_player(state) >= 1:
        #         return True
        #     return False
        # elif self.goal_type == 9:
        #     if state.turn_stats.get_difference_in_max_power_favoring_player(state) == 0:
        #         return True
        #     return False
        # elif self.goal_type == 10:
        #     if state.turn_stats.get_difference_in_max_power_favoring_player(state) == -1:
        #         return True
        #     return False
        # elif self.goal_type == 11:
        #     if state.turn_stats.total_damage_done_to_player <= 0:
        #         return True
        #     return False
        # elif self.goal_type == 12:
        #     if state.turn_stats.total_damage_done_to_player <= 1:
        #         return True
        #     return False
        # elif self.goal_type == 13:
        #     if state.turn_stats.total_damage_done_to_player <= 2:
        #         return True
        #     return False
        # elif self.goal_type == 14:
        #     if state.turn_stats.total_damage_done_to_player <= 3:
        #         return True
        #     return False
        # elif self.goal_type == 15:
        #     if state.turn_stats.total_damage_done_to_player <= 4:
        #         return True
        #     return False
        # elif self.goal_type == 16:
        #     if state.turn_stats.total_damage_done_to_player <= 5:
        #         return True
        #     return False


if __name__ == '__main__':
    boardState = BoardState()

#   Set enemy cards
    enemy_cards = [None, None, None,  None,
                   Card(name="Slothbear", power=0, health=2), None, None, None]
    boardState.set_enemy_cards(enemy_cards)

#   Set player cards
    player_cards_board = [None,  None, None, None]

    player_cards_hand = [Card(name="TwinCats", power=1, health=2, fire_cost=2, has_spirit=1),Card(name="Bunnyhop", power=1, health=1, fire_cost=1, has_fire=1),Card(name="Sunfish", power=0, health=1, fire_cost=1),]

    player_cards_deck = [
                         Card(name="Weasel", power=1, health=1, fire_cost=1),

                         Card(name="Shadow Rat", power=1, health=2, fire_cost=1),
                         Card(name="Smokepuff", power=0, health=2, fire_cost=1),

                         ]

    dead_cards = []

    spirits = 9
    hamsters_remaining = 10
    has_drawn = False

    boardState.set_player_cards(player_cards_board, player_cards_hand, player_cards_deck, spirits, hamsters_remaining, has_drawn)

#   Set health
    boardState.set_health(player_health=5, enemy_health=5)

#   Setup problem

    print("Running result")

    result = None

    # total_player_card_power = boardState.turn_stats.get_max_power_on_player_side(boardState.board, boardState.hand,
    #                                                                              boardState.deck)
    #
    # max_possible_damage_to_enemy = 5 - total_player_card_power
    #
    # i = max_possible_damage_to_enemy
    # if i < 0:
    #     i = 0

    i = 10

    while result is None:
        print(f'Searching for goal with a threshold greater than or equal to:  {i}\n\n')
        result = my_best_first_graph_search(Cardio(boardState, goal_threshold=i), True)
        if result is None:
            print("None")
        i -= 2
        if i < -10:
            break

    print(f'\nSteps to get to goal of threshold {i + 2}')
    for n in result.path():
        print(n.action)

    # if result is not None:
    #     result.state.print()
    #     print(result.action)
    #     result.parent

