import pygame
import pygame.locals
import math
from random import randint
import pylab


class Board(object):
	"""
	The game board is responsible for drawing the window.
	"""
	
	def __init__(self, width, height):
		"""
		Game board builder. Prepares the game window.
		
		:param width: width in pixels
		:param height: height w pikselach
		"""
		self.width = width
		self.height = height
		self.surface = pygame.display.set_mode((width, height), 0, 32)
		pygame.display.set_caption('Game of life')
		
	def draw(self, *args):
		"""
		Draws the game window.
		
		:param args: list of objects to draw
		"""
		background = (0, 0, 0)
		self.surface.fill(background)
		for drawable in args:
			drawable.draw_on(self.surface)
			
		pygame.display.update()
		
	def getWidth(self):
		return int(self.width)
		
	def getHeight(self):
		return int(self.height)
		
		
class GameOfLife(object):
	"""
	Combines all elements into a whole.
	"""
	
	def __init__(self, width, height, cells, side, cell_size = 10):
		"""
		Preparation of game settings.
		
		:param width: board width measured by the number of cells
		:param height: board height measured by the number of cells
		:param cell_size: side of the cell in pixels
		:param cells: number of cells at the beginning of the game
		:param side: side of the square with cells at the beginning of the game
		"""
		pygame.init()
		self.board = Board(width * cell_size, height * cell_size)
		self.fps_clock = pygame.time.Clock()
		self.population = Population(width, height, cells, side, cell_size)

		
	def run(self):
		"""
		Main game loop
		"""
		cells = []
		while not self.handle_events():
			self.board.draw(
				self.population,
			)
			if getattr(self, "started", None):
				cells.append(self.population.number_of_life_cells())
				self.population.cycle_generation()
				if (self.population_constant(cells) or self.max_live_cells()):
					self.population_analysis(cells)
					break
			self.fps_clock.tick(20)
			
	def handle_events(self):
		for event in pygame.event.get():
			
			if event.type == pygame.locals.QUIT:
				pygame.quit()
				return True
			from pygame.locals import MOUSEMOTION, MOUSEBUTTONDOWN
			if(event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN):
				self.population.handle_mouse()
			from pygame.locals import KEYDOWN, K_RETURN
			if(event.type == KEYDOWN or event.type == K_RETURN):
				self.started = True
	
	def max_live_cells(self):
		number_of_cells = self.population.number_of_life_cells();
		if(number_of_cells < 10):
			return True		
			
	def population_constant(self, cells):
		cycles = len(cells)
		if cycles>5:
			if(cells[cycles-1] == cells[cycles-2] == cells[cycles-3] == cells[cycles-4]):
				return True
				
	def population_analysis(self, population):
		cycles = len(population)
		print("Initial state of the population: ", population[0])
		print("Number of cycles: ", cycles)
		if len(population)<2:
			print("The population failed to grow.")
		else:
			print("The largest number of cells was: ", max(population[1:]))
			print("The population stopped at ", population[cycles-1], " cells.")
			print("It took place in cycle no.: ", population.index(max(population[1:])))
			pylab.plot(population)
			pylab.title("Graph of the number of cells as a function of time")
			pylab.xlabel("Cycles")
			pylab.ylabel("Number of cells")
			pylab.grid(True)
			pylab.show()
		
DEAD = 0
ALIVE = 1


class Population(object):
	
	def __init__(self, width, height, cells, side, cell_size=10):
		self.box_size = cell_size
		self.width = width
		self.height = height
		self.cells = cells
		self.side = side
		self.generation = self.start_generation(cells, side)
		
	def reset_generation(self):
		return [[DEAD for y in range(self.height)] for x in range(self.width)]
		
	def start_generation(self, cells, side):
		generation = self.reset_generation()
		if(cells <= 0 or side <= 0):
			return generation
		else:
			i=0
			while i < cells:
				cooX = []
				cooY = []
				x=randint(int(self.width/2 - side/2), int(self.width/2 + side/2))
				y=randint(int(self.height/2 - side/2), int(self.height/2 + side/2))
				if (cooX.count(x) and cooY.count(y)):
					continue
				else:
					cooX.append(x)
					cooY.append(y)
					generation[int(x)][int(y)] = ALIVE
					i+=1
			return generation
			
	def handle_mouse(self):
		buttons = pygame.mouse.get_pressed()
		if not any(buttons):
			return
		
		alive = True if buttons[0] else False
		
		x, y = pygame.mouse.get_pos()
		
		x /= self.box_size
		y /= self.box_size
		
		self.generation[int(x)][int(y)] = ALIVE if alive else DEAD
		
	def draw_on(self, surface):
		for x, y in self.alive_cells():
			size = (self.box_size, self.box_size)
			position = (x * self.box_size, y * self.box_size)
			color = (255, 255, 255)
			thickness = 1
			pygame.draw.rect(surface, color, pygame.locals.Rect(position, size), thickness)
			
	def alive_cells(self):
		for x in range(len(self.generation)):
			column = self.generation[x]
			for y in range(len(column)):
				if column[y] == ALIVE:
					yield x, y
					
	def number_of_life_cells(self):
		life = 0
		for x in range(len(self.generation)):
			column = self.generation[x]
			for y in range(len(column)):
				if column[y] == ALIVE:
					life+=1
		return life
					
	def neighbours(self, x, y):
		for nx in range(x-1, x+2):
			for ny in range(y-1, y+2):
				if (nx == x and ny == y):
					continue
				if nx >= self.width:
					nx = 0
				elif nx < 0:
					nx = self.width-1
				if ny >= self.height:
					ny = 0
				elif ny < 0:
					ny = self.height-1
					
				yield self.generation[nx][ny]
				
	def cycle_generation(self):
		
		next_gen = self.reset_generation()
		for x in range(len(self.generation)):
			column = self.generation[x]
			for y in range(len(column)):
				count = sum(self.neighbours(x, y))
				if count == 3:
					next_gen[x][y] = ALIVE
				elif count == 2:
					next_gen[x][y] = column[y]
				else:
					next_gen[x][y] = DEAD
					
		self.generation = next_gen
		


if __name__ == '__main__':
	print("\n\n\n Welcome to the Game of Life.\nThe board on which the game will be played is 80x40 units long.\nThe total area is 3200 (units of length) ^ 2. \nPlease enter the density of the initial population and the area on which life will begin.\n")
	density = int(input("Enter the cell density. Number of cells in a field of 100 (units of length) ^ 2.\nThe maximum density is 200.\n"))
	while (density > 200 or density < 0):
		density = int(input("Error! Density cannot be greater than 200 or smaller than 0. Please enter number again.\n"))
	area = int(input("Enter the field in which the cells are located. The field will be a square where 1 unit is the side of one cell.\n"))
	while (area > 1000 or area < 0):
		area = int(input("Error! Area cannot be greater than 1000 or smaller than 0. Please enter number again.\n"))
	cells = (density*area)/100
	side = int(math.sqrt(area))
	game = GameOfLife(80, 40, cells, side)
	game.run()
