#!/bin/python3

import sys
import time
import logging
import os
import random
from logging.handlers import RotatingFileHandler

from alexis_src.client_player import ClientPlayer
from alexis_src.utils import get_char_from_color
from alexis_src.get_all_possible_plays import get_all_possible_plays
from alexis_src.immutable_play import immutable_play
from alexis_src.evaluate_game_state import predict_carlotta_move

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
# fantom_logger = logging.getLogger()
# fantom_logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# # file
# if os.path.exists("./logs/fantom.log"):
#     os.remove("./logs/fantom.log")
# file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# fantom_logger.addHandler(file_handler)
# # stream
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.WARNING)
# fantom_logger.addHandler(stream_handler)


class SimpleMaxAI:
    def __init__(self):
        self.response_stack = []

    def get_next_play(self, question):
        if self.response_stack == []:
            plays = get_all_possible_plays(question)

            fantom_position = get_char_from_color(question["game state"], question["game state"]["fantom"])["position"]
            best_play = None
            max_carlotta_move = None
            for play in plays:
                new_game_state = immutable_play(question["game state"], play)
                new_max_carlotta_move = predict_carlotta_move(new_game_state, fantom_position)

                if best_play == None or new_max_carlotta_move > max_carlotta_move:
                    best_play = play
                    max_carlotta_move = new_max_carlotta_move

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
