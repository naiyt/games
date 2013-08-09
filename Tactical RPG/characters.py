import sys
import pygame
from lib.utils import *
from lib.locals import *
from pygame.locals import *


class Character:
	def __init__(self, image, name, str, speed, hp, defense, move_range, box, weapon=None):
		self.image = pygame.image.load(image)
		self.name = name
		self.str = str
		self.speed = speed
		self.hp = hp
		self.defense = defense
		self.move_range = move_range

		self.box = box # The actual grid object this character is in
		self.pixel_position = (self.box.upper_x, self.box.upper_y)

		self.boxes_in_range = None
		self.weapon = weapon
		self.boxes_in_weapon_range = None

	def move(self, new_box):
		"""
		-Sets the range to none, so we can recalculate the range when needed.
		-Sets the previous boxes character to none
		-Sets the characters box to the new box
		-Sets the new boxes character to self
		-Sets the new pixel pixel pos
		-Does not redraw - that's up to the game loop

		"""
		
		self.boxes_in_range = None
		self.box.character = None
		self.box = new_box
		self.box.character = self
		self.pixel_position = (self.box.upper_x, self.box.upper_y)


	def draw(self, displaysurf):
		displaysurf.blit(self.image, self.pixel_position)