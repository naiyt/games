import sys
import random
import pygame
import time
import math
import copy
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 480
PADDLEHEIGHT = 15
PADDLEWIDTH = 90
XBALLSPEED = 0
YBALLSPEED = 5
BALLSPEED = 10
BALLSIZE = 12
BALLCOLLISIONFUDGE =  10
NEW_BALL_WAIT = 2
MAXBOUNCEANGLE = 75
BRICKHEIGHT = 15
BRICKWIDTH = 95
BRICKMARGIN = 4

SMALLPADDLEWIDTH = 30
BIGPADDLEWIDTH = 150



WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)
BRIGHTBLUE =    (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN =         (  0, 204,   0)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)

ALLCOLORS = [RED, BLACK, BRIGHTBLUE, DARKTURQUOISE, GREEN, NAVYBLUE, RED]


BGCOLOR = WHITE
PADDLECOLOR = RED
BALLCOLOR = DARKTURQUOISE

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



def main():
	global FPSCLOCK, DISPLAYSURF
	pygame.init()

	bricks = create_bricks()

	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	FPSCLOCK = pygame.time.Clock()

	mouse_x = 0
	mouse_y = 0
	y_coordinate = WINDOWHEIGHT - PADDLEHEIGHT
	pygame.display.set_caption('Stupid Breakout Clone')

	player = Paddle(mouse_y, y_coordinate)

	x_directions = [LEFT, RIGHT]
	y_directions = [UP, DOWN]

	starting_y = (WINDOWHEIGHT/2) + 80
	ball = Ball(BALLSIZE, (WINDOWWIDTH/2, starting_y), LEFT, DOWN)

	next_time = 0
	please_wait = False
	start_time = time.clock()

	font_obj = pygame.font.Font('freesansbold.ttf', 32)
	text_surface_obj = font_obj.render('You Won!', True, BLACK)
	text_rect_obj = text_surface_obj.get_rect()
	text_rect_obj.center = (200, 150)

	while True:

		DISPLAYSURF.fill(BGCOLOR)
		player.set_pos(mouse_x)
		player.draw()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				if mouse_x >= WINDOWWIDTH - PADDLEWIDTH:
					mouse_x = WINDOWWIDTH - PADDLEWIDTH


		if len(bricks) == 0:
			DISPLAYSURF.blit(text_surface_obj, text_rect_obj)
			pygame.display.update()
			FPSCLOCK.tick(FPS)
			continue

		for brick in bricks:
			brick.draw()

		if please_wait and time.clock() - next_time < NEW_BALL_WAIT:
			pygame.display.update()
			FPSCLOCK.tick(FPS)
			continue
		else:
			please_wait = False

		bricks = check_collision(ball, player, bricks)
		lost_ball = ball.new_pos()
		#print ball.current_pos()
		
		if lost_ball:
			ball.set_pos((WINDOWWIDTH/2, starting_y))
			ball.set_velocity((XBALLSPEED, YBALLSPEED))
			please_wait = True
			next_time = time.clock()

		pygame.display.update()
		FPSCLOCK.tick(FPS)


def create_bricks():
	bricks = []
	rows_of_bricks = (WINDOWHEIGHT / 2) / BRICKHEIGHT
	columns_of_bricks = WINDOWWIDTH / BRICKWIDTH
	upper_x = 0
	upper_y = 0

	assert rows_of_bricks * BRICKHEIGHT <= (WINDOWHEIGHT / 2), 'Too many rows of bricks'
	assert columns_of_bricks * BRICKWIDTH <= WINDOWWIDTH, 'Too many columns of bricks'
	for row in range(rows_of_bricks):
		for col in range(columns_of_bricks):
			color = random.choice(ALLCOLORS)
			if row == 0:
				upper_y = BRICKMARGIN
			else:
				upper_y = (BRICKMARGIN * row) + (BRICKHEIGHT * row)
			if col == 0:
				upper_x = 0
			else:
				upper_x = (BRICKMARGIN * col) + (BRICKWIDTH * col)
			new_brick = Brick(upper_x, upper_y, color)
			bricks.append(new_brick)
	return bricks





def check_collision(ball, paddle, bricks):
	player_pos = paddle.current_pos()
	ball_pos = ball.current_pos()
	if ball_pos[1] >= WINDOWHEIGHT - PADDLEHEIGHT - BALLCOLLISIONFUDGE:
		if ball_pos[0] >= player_pos and ball_pos[0] <= player_pos + PADDLEWIDTH:
			ball.y_direction = UP
			# Equations for setting new angle of ball, from: 
			# http://gamedev.stackexchange.com/questions/4253/how-do-you-calculate-where-a-ball-should-go-when-it-bounces-off-the-bar
			relativeIntersectY = (player_pos+(PADDLEWIDTH/2)) - ball.current_pos()[1] 
			normalizedRelativeIntersectionY = (relativeIntersectY/(PADDLEWIDTH/2))
			bounceAngle = normalizedRelativeIntersectionY * MAXBOUNCEANGLE
			ballVx = int(abs(BALLSPEED*math.cos(bounceAngle)))
			ballVy = int(abs(BALLSPEED*math.sin(bounceAngle)))
			ball.set_velocity([ballVx, ballVy])
			#print "Bounce Angle: %s ballVx: %s ballVy: %s" % (bounceAngle, ballVx, ballVy)


	new_bricks = copy.deepcopy(bricks)
	for x in range(len(bricks)):
		if bottom_hit(bricks[x], ball_pos):
			ball.y_direction = DOWN
			set_status(new_bricks[x], ball, paddle)
			del new_bricks[x]
		elif top_hit(bricks[x], ball_pos):
			ball.y_direction = UP
			set_status(new_bricks[x], ball, paddle)
			del new_bricks[x]
		elif side_hit(bricks[x], ball_pos):
			set_status(new_bricks[x], ball, paddle)
			if ball.x_direction == RIGHT:
				ball.x_direction = LEFT
			else:
				ball.x_direction = RIGHT
			del new_bricks[x]

	return new_bricks


def set_status(brick, ball, paddle):
	pass
	#if brick.color == RED:
	#	paddle.set_width(BIGPADDLEWIDTH)
	#elif ball.color == BLACK:
	#	paddle.set_width(SMALLPADDLEWIDTH)
	#elif ball.color == GREEN:
	#	paddle.set_width(PADDLEWIDTH)


def bottom_hit(brick, ball_pos):
	if ball_pos[1] <= brick.upper_y + BRICKHEIGHT and ball_pos[1] >= brick.upper_y + BRICKHEIGHT/2:
		if ball_pos[0] >= brick.upper_x and ball_pos[0] <= brick.upper_x + BRICKWIDTH:
			return True
	return False

def top_hit(brick, ball_pos):
	if ball_pos[1] >= brick.upper_y and ball_pos[1] <= brick.upper_y + BRICKHEIGHT:
		if ball_pos[0] >= brick.upper_x and ball_pos[0] <= brick.upper_x + BRICKWIDTH:
			return True
	return False

def side_hit(brick, ball_pos):
	if ball_pos[1] >= brick.upper_y and ball_pos[1] <= brick.upper_y + BRICKHEIGHT:
		if ball_pos[0] >= brick.upper_x + 10 and ball_pos[0] <= brick.upper_x - 10:
			return True
	return False
	



class Brick:
	def __init__(self, upper_x, upper_y, color, height=BRICKHEIGHT, width=BRICKWIDTH):
		self.upper_x = upper_x
		self.upper_y = upper_y
		self.color = color
		self.height = height
		self.width = width

	def draw(self):
		pygame.draw.rect(DISPLAYSURF, self.color, (self.upper_x, self.upper_y, self.width, self.height))


class Paddle:
	def __init__(self, upper_x, upper_y, COLOR=PADDLECOLOR, PADDLEWIDTH=PADDLEWIDTH, PADDLEHEIGHT=PADDLEHEIGHT):
		self.upper_x = upper_x
		self.upper_y = upper_y
		self.color = COLOR
		self.width = PADDLEWIDTH
		self.height = PADDLEHEIGHT

	def set_width(self, width):
		self.width = width

	def current_pos(self):
		return self.upper_x

	def set_pos(self, upper_x, upper_y=None):
		self.upper_x = upper_x
		if upper_y is not None:
			self.upper_y = upper_y

	def draw(self):
		pygame.draw.rect(DISPLAYSURF, self.color, (self.upper_x, self.upper_y, self.width, self.height))



class Ball:
	def __init__(self, radius, center_point, x_direction, y_direction, color=BALLCOLOR, xvelocity=XBALLSPEED, yvelocity=YBALLSPEED):
		self.radius = radius
		self.center_point = center_point
		self.x_direction = x_direction
		self.y_direction = y_direction
		self.color = color
		self.x_velocity = xvelocity
		self.y_velocity = yvelocity

	def set_velocity(self, xyvelocity):
		self.x_velocity = xyvelocity[0]
		self.y_velocity = xyvelocity[1]

	def current_pos(self):
		return self.center_point

	def set_pos(self, center_point):
		self.center_point = center_point

	def draw(self):
		pygame.draw.circle(DISPLAYSURF, self.color, self.center_point, self.radius)

	def new_pos(self):
		lost_ball = False

		new_x = 0
		new_y = 0

		if self.center_point[0] >= WINDOWWIDTH: # Hit the right wall
			self.x_direction = LEFT
		if self.center_point[0] <= 0: # Hit the right wall
			self.x_direction = RIGHT
		if self.center_point[1] <= 0:  # Hit the ceiling
			self.y_direction = DOWN
		if self.center_point[1] >= WINDOWHEIGHT:
			lost_ball = True

		if lost_ball:
			#print 'Lost a ball!'
			return True

		else:
			if self.x_direction == LEFT:
				new_x = self.center_point[0] - self.x_velocity
			elif self.x_direction == RIGHT:
				new_x = self.center_point[0] + self.x_velocity
			if self.y_direction == DOWN:
				new_y = self.center_point[1] + self.y_velocity
			elif self.y_direction == UP:
				new_y = self.center_point[1] - self.y_velocity


			self.set_pos((new_x, new_y))
			self.draw()
			return False


if __name__ == '__main__':
	main()
