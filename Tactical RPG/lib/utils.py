import pygame
from pygame.locals import *
from locals import *

def key_presses(keys, next_x, next_y, COLS, ROWS):
	"""Moves the x and y coordinates when using the keyboard"""
	change_made = False
	if keys[K_UP] and keys[K_LEFT]:
		change_made = True
		if next_y != 0 and next_x != 0:
			next_x -= 1
			next_y -= 1
		if next_y == 0 and next_x != 0:
			next_x -=1
		if next_y != 0 and next_x == 0:
			next_y -= 1
	elif keys[K_UP] and keys[K_RIGHT]:
		change_made = True
		if next_y != 0 and next_x != COLS - 1:
			next_x += 1
			next_y -= 1
		if next_y == 0 and next_x != COLS -1:
			next_x += 1
		if next_y != 0 and next_x == COLS - 1:
			next_y -= 1
	elif keys[K_DOWN] and keys[K_LEFT]:
		change_made = True
		if next_y != ROWS - 1 and next_x != 0:
			next_x -= 1
			next_y += 1
		if next_y == ROWS - 1 and next_x != 0:
			next_x -= 1
		if next_y != ROWS - 1 and next_x == 0:
			next_y += 1
	elif keys[K_DOWN] and keys[K_RIGHT]:
		change_made = True
		if next_y != ROWS - 1 and next_x != COLS - 1:
			next_x += 1
			next_y += 1
		if next_y == ROWS - 1 and next_x != COLS - 1:
			next_x += 1					
		if next_y != ROWS - 1 and next_x == COLS - 1:
			next_y += 1
	elif keys[K_UP]:
		if next_y != 0:
			next_y -= 1
			change_made = True
	elif keys[K_DOWN]:
		if next_y != ROWS - 1:
			next_y += 1
			change_made = True
	elif keys[K_LEFT]:
		if next_x != 0:
			next_x -= 1
			change_made = True
	elif keys[K_RIGHT]:
		if next_x != COLS - 1:
			next_x += 1
			change_made = True
	return next_x, next_y, change_made

def pixel_to_block(x, y):
	return x/(WINDOWWIDTH/COLS), y/(WINDOWHEIGHT/ROWS)

def block_to_pixels(x,y):
	return x * WINDOWWIDTH, y * WINDOWHEIGHT