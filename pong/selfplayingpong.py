import sys
import time
import pygame
from pygame.locals import *
from random import choice


FPS = 500
WINDOWWIDTH = 800
WINDOWHEIGHT = 480
PADDLEWIDTH = 20
PADDLEHEIGHT = 100
BALLSIZE = 12
BALLSPEED = 10
AIPADDLESPEED = 60
BALLCOLLISIONFUDGE = 2
PAUSETIME = 5000
PADDLEFUDGEAMT = (PADDLEHEIGHT / 2) - 10
COORDINATE_REFRESH_SPEED = .01

WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)


BALLCOLOR = RED
BGCOLOR = WHITE
PADDLECOLOR = BLACK

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

Directions = Enum(["RIGHT", "LEFT", "UP", "DOWN"])
LEFT = Directions.LEFT
RIGHT = Directions.RIGHT
UP = Directions.UP
DOWN = Directions.DOWN

ANGLES = [1, 5, 0, 10]

def main():
	global FPSCLOCK, DISPLAYSURF
	pygame.init()

	start_time = time.clock()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

	mouse_x = 0
	mouse_y = 0
	pygame.display.set_caption('Pong!')
	DISPLAYSURF.fill(BGCOLOR)

	player_1 = Paddle(0,0, 'left')
	player_2 = Paddle(WINDOWWIDTH - PADDLEWIDTH, 0, 'right')

	font_obj = pygame.font.Font('freesansbold.ttf', 32)
	text_surface_obj = font_obj.render('P1: 0, P2: 0', True, BLACK)
	text_rect_obj = text_surface_obj.get_rect()
	text_rect_obj.center = (200, 150)

	x_directions = [LEFT, RIGHT]
	y_directions = [UP, DOWN]
	x_direction = choice(x_directions)
	y_direction = choice(y_directions)
	
	ball = Ball(BALLSIZE,(WINDOWWIDTH / 2, WINDOWHEIGHT / 2), x_direction, y_direction)

	first_point = True
	ball_point1 = [0,0]
	ball_point2 = [0,0]

	next_time = 0

	please_wait = False

	while True:
		DISPLAYSURF.fill(BGCOLOR)
		DISPLAYSURF.blit(text_surface_obj, text_rect_obj)

		player_1.draw(0, player_1.upper_y)
		player_2.draw(WINDOWWIDTH - PADDLEWIDTH, player_2.upper_y)

		if please_wait and time.clock() - next_time < 2:
			pygame.display.update()
			FPSCLOCK.tick(FPS)
			continue
		else:
			please_wait = False

		check_collision(ball, player_1.current_pos(), player_2.current_pos())

		score, player_1_scored, hit_wall = ball.new_pos()

		if hit_wall:
			first_point = True
		
		elapsed_time = time.clock()

		if first_point:
			next_time = time.clock()
			ball_point1 = ball.current_pos()
			first_point = False

		if first_point == False and elapsed_time - next_time > COORDINATE_REFRESH_SPEED:
			ball_point2 = ball.current_pos()
			first_point = True


		player_1.ai_movement(ball_point1, ball_point2)
		player_2.ai_movement(ball_point1, ball_point2)



		if score:
			if player_1_scored:
				player_1.increase_score(1)
				#print "Player 1 scored!"
			else:
				player_2.increase_score(1)
				#print "Player 2 scored!"
			score_str = "P1: %s, P2: %s" % (player_1.score, player_2.score)

			first_point = True
			trajectory_calculated = False

			text_surface_obj = font_obj.render(score_str, True, BLACK)
			text_rect_obj = text_surface_obj.get_rect()
			text_rect_obj.center = (200, 150)

			ball.set_center((WINDOWWIDTH / 2, WINDOWHEIGHT / 2))
			ball.set_direction(choice(x_directions), choice(y_directions))
			please_wait = True
			next_time = time.clock()

		

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				if mouse_y >= WINDOWHEIGHT - PADDLEHEIGHT:
					mouse_y = WINDOWHEIGHT - PADDLEHEIGHT

		pygame.display.update()
		FPSCLOCK.tick(FPS)


def check_collision(ball, player_1_pos, player_2_pos):
	ball_pos = ball.current_pos()
	if ball_pos[0] == 0 + PADDLEWIDTH + BALLSIZE - BALLCOLLISIONFUDGE:
		if ball_pos[1] >= player_1_pos and ball_pos[1] <= player_1_pos + PADDLEHEIGHT:
			ball.angle = choice(ANGLES)
			#print "Player 1 hit the ball!"
			ball.x_direction = RIGHT

	if ball_pos[0] == WINDOWWIDTH - PADDLEWIDTH - BALLSIZE + BALLCOLLISIONFUDGE:
		if ball_pos[1] >= player_2_pos and ball_pos[1] <= player_2_pos + PADDLEHEIGHT:
			ball.angle = choice(ANGLES)
			#print "Player 2 hit the ball!"
			ball.x_direction = LEFT


class Paddle:
	def __init__(self, upper_x, upper_y, side, COLOR=PADDLECOLOR, PADDLEWIDTH=PADDLEWIDTH, PADDLEHEIGHT=PADDLEHEIGHT):
		self.upper_x = upper_x
		self.upper_y = upper_y
		self.color = COLOR
		self.width = PADDLEWIDTH
		self.height = PADDLEHEIGHT
		self.score = 0
		self.ai_pos = 0 # Y coordinate that the paddle should be moving towards
		self.trajectory_calculated = False
		self.side = side


	def ai_movement(self, point1, point2):
		self.ai_pos = self._projected_wall_collision(point1, point2) - PADDLEHEIGHT / 2
		if self.ai_pos < 0:
			self.ai_pos = 0
		elif self.ai_pos > WINDOWHEIGHT:
			self.ai_pos = WINDOWHEIGHT - PADDLEHEIGHT

		upper_bound = self.ai_pos + PADDLEFUDGEAMT
		lower_bound = self.ai_pos - PADDLEFUDGEAMT		

		if self.upper_y == self.ai_pos:
			return

		elif self.upper_y < upper_bound and self.upper_y > lower_bound:
			return

		elif self.ai_pos > self.upper_y:
			self.upper_y = self.upper_y + AIPADDLESPEED
			#print 'Moving paddle down'
			return self.upper_x, self.upper_y
		elif self.ai_pos < self.upper_y:
			#print 'Moving paddle up'
			self.upper_y = self.upper_y - AIPADDLESPEED
			return self.upper_x, self.upper_y


	def _set_floats(self, coords):
		floating_point = [0.0,0.0]
		for index in range(len(coords)):
			floating_point[
			index] = float(coords[index])
		return floating_point

	def _projected_wall_collision(self, test_point1, test_point2):
		if self.side == 'left':
			test_point1 = self._set_floats(test_point1)
			test_point2 = self._set_floats(test_point2)
			try:
				slope = (test_point1[1] - test_point2[1]) / (test_point1[0] - test_point2[0])
			except ZeroDivisionError:
				slope = 0
			y_int = test_point1[1] - (slope * test_point1[0])
			#print 'P1: %s P2: %s Y_int: %s' % (test_point1, test_point2, abs(y_int))
			return abs(y_int)
		elif self.side == 'right':
			test_point1 = self._set_floats(test_point1)
			test_point2 = self._set_floats(test_point2)
			try:
				slope = (test_point1[1] - test_point2[1]) / (test_point1[0] - test_point2[0])
			except ZeroDivisionError:
				slope = 0
			y_int = test_point1[1] - (slope * test_point1[0])
			right_int = abs((slope * WINDOWWIDTH) + y_int)
			#print 'P1: %s P2: %s Right int:: %s' % (test_point1, test_point2, right_int)
			return right_int


	def draw(self, upper_x, upper_y):
		self.upper_x = upper_x
		self.upper_y = upper_y
		pygame.draw.rect(DISPLAYSURF, self.color, (self.upper_x, self.upper_y, self.width, self.height))

	def current_pos(self):
		return self.upper_y

	def increase_score(self, score):
		self.score += score

class Ball:
	def __init__(self, radius, center_point, x_direction, y_direction, color=BALLCOLOR, speed=BALLSPEED):
		self.radius = radius
		self.color = color
		self.speed = speed
		self.x_direction = x_direction
		self.y_direciton = y_direction
		self.center_point = center_point
		self.angle = 5 # The angle the ball is moving at (the val of Y)
		

	def draw(self, wait=False):
		pygame.draw.circle(DISPLAYSURF, self.color, self.center_point, self.radius)

	def set_center(self, new_center):
		self.center_point = new_center

	def set_direction(self, x_direction, y_direction):
		self.x_direction = x_direction
		self.y_direction = y_direction

	def new_pos(self, new_center_point=None):
		"""
		Calculate the new position of the ball. Runs once per loop in the 
		main loop.
		"""

		score = False
		player_1_score = False
		hit_wall = False

		if self.center_point[0] >= WINDOWWIDTH:
			score = True
			self.angle = choice(ANGLES)
			player_1_score = True
		if self.center_point[0] <= 0:
			score = True
			self.angle = choice(ANGLES)
			player_1_score = False

		if self.center_point[1] <= 0:
			self.y_direction = DOWN
			self.angle = choice(ANGLES)
			hit_wall = True
		if self.center_point[1] >= WINDOWHEIGHT:
			self.y_direction = UP
			self.angle = -1 * choice(ANGLES)
			hit_wall = True

		if self.x_direction == RIGHT:
			self.center_point = (self.center_point[0] + self.speed, self.center_point[1] + self.angle)

		else:
			self.center_point = (self.center_point[0] - self.speed, self.center_point[1] + self.angle)

		self.draw()
		return score, player_1_score, hit_wall

	def current_pos(self):
		return self.center_point


if __name__ == '__main__':
	main()