#!/bin/python3

import json
import logging
import os
import sys
import time
import copy
import random
from logging.handlers import RotatingFileHandler

from alexis_src.client_player import ClientPlayer
from alexis_src.get_all_possible_plays import get_all_possible_plays
from alexis_src.immutable_play import immutable_play
from alexis_src.evaluate_game_state import predict_carlotta_move_inspector

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 12000
# HEADERSIZE = 10

"""
set up inspector logging
"""
# inspector_logger = logging.getLogger()
# inspector_logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# # file
# if os.path.exists("./logs/inspector.log"):
#     os.remove("./logs/inspector.log")
# file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# inspector_logger.addHandler(file_handler)
# # stream
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.WARNING)
# inspector_logger.addHandler(stream_handler)


def get_best_play(game_state, plays):
    best_play = None
    min_carlotta_move = None
    best_game_state = None

    for play in plays:
        new_game_state = immutable_play(game_state, play)
        (scream, no_scream) = predict_carlotta_move_inspector(new_game_state)
        new_min_carlotta_move = abs(scream - no_scream)

        if best_play == None or new_min_carlotta_move < min_carlotta_move:
            best_play = play
            min_carlotta_move = new_min_carlotta_move
            best_game_state = new_game_state

    return (best_play, min_carlotta_move, best_game_state)


def immutable_play_rec2(question):
    plays = get_all_possible_plays(question)

    best_play = None
    min_carlotta_move = None
    for play in plays:
        new_game_state = immutable_play(question["game state"], play)

        new_data = copy.deepcopy(question["data"])
        new_data.pop(play[0])
        new_question = {
            "question type": question["question type"],
            "data": new_data,
            "game state": new_game_state
        }

        plays2 = get_all_possible_plays(new_question)

        for play2 in plays2:
            new_game_state2 = immutable_play(new_game_state, play2)
            (scream, no_scream) = predict_carlotta_move_inspector(new_game_state2)
            new_min_carlotta_move = abs(scream - no_scream)

            if best_play == None or new_min_carlotta_move < min_carlotta_move:
                best_play = play + play2
                min_carlotta_move = new_min_carlotta_move

    return best_play


class SimpleMaxAI:
    def __init__(self):
        self.response_stack = []

    def get_next_play(self, question):
        if self.response_stack == []:
            if (question["game state"]["num_tour"] - 1) % 2 == 1:
                self.response_stack = immutable_play_rec2(question)
            else:
                plays = get_all_possible_plays(question)
                (best_play, _, _) = get_best_play(question["game state"], plays)

                self.response_stack = best_play

        if question["question type"] == "select character":
            return self.response_stack.pop(0)
        else:
            return question["data"].index(self.response_stack.pop(0))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        seed = float(sys.argv[1])
    else:
        seed = time.time()
    random.seed(seed)

    ai = SimpleMaxAI()
    p = ClientPlayer(DEFAULT_HOST, DEFAULT_PORT, ai)
    p.run()
