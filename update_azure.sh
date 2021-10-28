#!/bin/bash

rsync \
	--exclude='__pycache__' --exclude='.git' --exclude='*.png' --exclude='*.jpg' --exclude='*.pdf' --exclude='logs' --exclude='saved_games' \
	-av -e ssh ./ alexis@52.179.22.22:AI
