import sys
import pygame
import time
import math
from characters import Character
from weapon import Weapon
from pygame.locals import *
from lib.utils import *
from lib.locals import *


def main():
	"""Basic global setup and initiation"""
	assert (WINDOWWIDTH / COLS) % 2 == 0, 'Incorrect number of columns'
	assert (WINDOWHEIGHT / ROWS) % 2 == 0, 'Incorrect number of rows'

	global FPSCLOCK, DISPLAYSURF

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption("This is a thing")
	BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

	while True:
		runGame()


def runGame():
	"""Main game code/loop goes here"""

	# A background that can be transculescent
	background = DISPLAYSURF.convert_alpha()
	background_img = pygame.image.load("background.png")

	click = pygame.mixer.Sound('click.wav')

	mouse_x = 0
	mouse_y = 0

	width = WINDOWWIDTH / COLS
	gridboxes = [[0 for x in xrange(ROWS)] for x in xrange(COLS)]
	for col in range(COLS):
		for row in range(ROWS):
			upper_x = col * width
			upper_y = row * width
			new_grid = Grid(upper_x, upper_y, width, width)
			gridboxes[col][row] = new_grid

	weapons = []
	longsword = Weapon("Longsword", 10, 10, 10, 1)
	weapons.append(longsword)

	# Setting up basic characters
	characters = [] # TODO: Create a "create character" method1
	img1 = 'tree.png'
	img2 = 'rock.png'
	x = y = 3
	lantus = create_character(characters, img1, "Lantus", 10,10,10,10,TESTRANGE,x,y, gridboxes, longsword)
	novolog = create_character(characters, img1, "Novolog", 10,10,10,10,TESTRANGE-1, x+1, y-1, gridboxes, longsword)
	petrus = create_character(characters, img2, "Petrus", 10,10,10,10,TESTRANGE, x-1, y+1, gridboxes, longsword)
	frampt = create_character(characters, img2, "Frampt", 10,10,10,10,TESTRANGE, x+2, y-1, gridboxes, longsword)

	change_made = False
	button_down = False
	first_button = False

	previous_box = gridboxes[0][0] # Used to keep track of the last char clicked
	start_time = time.clock()
	next_time = 0

	current_character = None
	character_highlighted = False

	while True:
		background.blit(background_img, (0,0))
		#background.fill(BGCOLOR)
		DISPLAYSURF.blit(background, (0,0))


		# Draw all current gridboxes and their coresponding characters
		for col in range(COLS):
			for row in range(ROWS):
				gridboxes[col][row].draw()
				if gridboxes[col][row].character != None:
					gridboxes[col][row].character.draw(DISPLAYSURF)

		next_x = previous_box.box_pos[0]
		next_y = previous_box.box_pos[1]

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				change_made = True
				mouse_x, mouse_y = event.pos
				next_x = mouse_x / (WINDOWWIDTH/COLS)
				next_y = mouse_y / (WINDOWHEIGHT/ROWS)
				mouse_over_char = click_characters(next_x, next_y, characters, gridboxes)
				if mouse_over_char and current_character is None:
					clear_range_highlights(gridboxes)
					highlight_range(mouse_over_char)
				elif current_character is None:
					clear_range_highlights(gridboxes)
			elif event.type == KEYDOWN:
				button_down = True
				first_button = True
				next_time = time.clock()
			elif event.type == KEYUP:
				button_down = False
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if current_character is not None and character_highlighted:
						if move_in_range(current_character, next_x, next_y, gridboxes):
							move_character(next_x, next_y, current_character, gridboxes)
						else:
							current_character = None
						clear_range_highlights(gridboxes)
						character_highlighted = False
					else:
						current_character = click_characters(next_x, next_y, characters, gridboxes)
						if current_character:
							character_highlighted = True
						else:
							clear_range_highlights(gridboxes)


		if (button_down and time.clock() - next_time > CLICKDELAY) or first_button:
			first_button = False
			pygame.event.pump()
			keys = pygame.key.get_pressed()
			next_x, next_y, change_made = key_presses(keys, next_x, next_y, COLS, ROWS)
	

		if change_made:
			previous_box.color = GRIDDEFAULT # Set back to default
			gridboxes[next_x][next_y].color = GRIDHIGHLIGHT
			previous_box = gridboxes[next_x][next_y]
			change_made = False

		pygame.display.update()
		FPSCLOCK.tick(FPS)


def create_character(characters_array, char_img, char_name, str, speed, hp, defense, move_range, x, y, gridboxes, weapon):
	if gridboxes[x][y].character == None:
		box = gridboxes[x][y]
		if box:
			new_char = Character(char_img, char_name, str, speed, hp, defense, move_range, box, weapon)
			gridboxes[x][y].character = new_char
			characters_array.append(new_char)
			return new_char
	print "Couldn't add character"
	return None

def move_in_range(character, x, y, gridboxes):
	"""Checks to see if a move is in a character's range"""
	box = gridboxes[x][y]
	if box in character.boxes_in_range:
		return True
	else:
		return False

def move_character(x, y, character, gridboxes):
	"""Gets the new box, and moves that character with the object's move method"""
	new_box = gridboxes[x][y]
	character.move(new_box)

def highlight_range(character):
	if character.boxes_in_range is not None:
		for box in character.boxes_in_range:
			box.highlighted = True
	if character.boxes_in_weapon_range is not None:
		for box in character.boxes_in_weapon_range:
			box.highlighted = True
			box.highlighted_color = GRIDWEAPONHIGHLIGHT

def clear_range_highlights(gridboxes):
	"""Clears all highlighted boxes, after moving off of a character"""
	for col in range(COLS):
		for row in range(ROWS):
			gridboxes[col][row].visited = False
			gridboxes[col][row].end_of_range = False
			gridboxes[col][row].highlighted = False
			gridboxes[col][row].highlighted_color = GRIDDEFAULT
	
def click_characters(x, y, characters, gridboxes):
	curr_box = gridboxes[x][y]
	if curr_box.character != None:
		character = curr_box.character
		if character.boxes_in_range == None:
			character.boxes_in_range = get_blocks_in_range(curr_box, gridboxes, character.move_range)
			character.boxes_in_weapon_range = get_weapon_range(gridboxes, character)
			highlight_range(character)
		#if character.boxes_in_range is not None:
		#	for curr_box in character.boxes_in_range:
		#		curr_box.highlighted = True
		return character
	return None


def get_blocks_in_range(curr_box, gridboxes, char_range, all_boxes=None):
	""" Recursive function to get the boxes in a character's range"""

	# Should be set to the current box on the first run
	if all_boxes == None:
		all_boxes = [curr_box]

	# Base case: we've reached the edge of the character's range
	if char_range <= 0:
		curr_box.end_of_range = True
		return [curr_box]

	curr_boxes = []

	x = curr_box.box_pos[0]
	y = curr_box.box_pos[1]

	# Gets each box adjacent to current box (unless it's out of range of the map)
	if x + 1 <= COLS - 1:
		this_box = gridboxes[x+1][y]
		if this_box.visited == False:
			this_box.visited = True
			curr_boxes.append(this_box)

	if x -1 >= 0:
		this_box = gridboxes[x-1][y]
		if this_box.visited == False:
			this_box.visited = True
			curr_boxes.append(this_box)

	if y + 1 <= ROWS - 1:
		this_box = gridboxes[x][y+1]
		if this_box.visited == False:
			this_box.visited = True
			curr_boxes.append(this_box)

	if y - 1 >= 0:
		this_box = gridboxes[x][y-1]
		if this_box.visited == False:
			this_box.visited = True
			curr_boxes.append(this_box)


	# Add each adjacent box to our list of boxes, and then recursively call
	# get_blocks_in_range on each box in that list.
	this_list = []
	for this_box in curr_boxes:
		if this_box.character == None: # Don't overlap characters
			this_list.append(this_box)
			this_list += get_blocks_in_range(this_box, gridboxes, char_range-1, curr_boxes)
	return this_list

def get_weapon_range(gridboxes, character):
	if character.weapon:
		boxes_in_range = character.boxes_in_range
		weapon_range = []
		for box in boxes_in_range:
			if box.end_of_range:
				new_boxes = get_blocks_in_range(box, gridboxes, character.weapon.range)
				weapon_range += new_boxes
		return weapon_range



class Grid:
	def __init__(self, upper_x, upper_y, width, height, status=None, color=GRIDDEFAULT, line_width=GRIDWIDTH):
		self.upper_x = upper_x
		self.upper_y = upper_y
		self.width = width
		self.height = height
		self.status = status
		self.color = color
		self.line_width = line_width
		self.highlighted = False
		self.highlighted_color = RANGECOLOR
		self.highlighted_linewidth = HIGHLIGHTEDWIDTH

		self.character = None

		x, y = pixel_to_block(self.upper_x, self.upper_y)
		self.box_pos = (x,y)

		self.visited = False
		self.end_of_range = False


	def draw(self):
		if self.highlighted:
			pygame.draw.rect(DISPLAYSURF, self.highlighted_color, (self.upper_x, self.upper_y, self.width, self.height), self.highlighted_linewidth)
		else:
			pygame.draw.rect(DISPLAYSURF, self.color, (self.upper_x, self.upper_y, self.width, self.height), self.line_width)

	def current_pos(self):
		return (self.upper_x, self.upper_y)


if __name__ == "__main__":
	main()