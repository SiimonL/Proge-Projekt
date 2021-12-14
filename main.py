
import pygame, os, sys, time, random
from numpy import transpose
from pygame import mouse

pygame.init()


SIZE = (600, 600)
screen = pygame.display.set_mode(SIZE)


FPS = 60
GRID_START = (150, 200)
CELL_SIZE = 40
CELL_GAP = 2
CELL_WIDTH = 3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# Hovering Color
GRAY = (150, 150, 150, 0.5)
# Marker Color
DARK_GRAY = (80, 80, 80)
# Grid Background
LIGHT_GRAY = (222, 222, 222)

mouse_pos = (0, 0)
cross_img = pygame.image.load(os.path.join('assets/images/' 'cross.png'))
number_font = pygame.font.Font(os.path.join('assets/fonts', 'Arvo-Bold.ttf'), 26)

levels = {}
for i, file in enumerate(os.scandir('./assets/levels/')):
    with open(file) as f:
        levels[i] = [list(map(int, line.strip().split(' '))) for line in f.readlines()]

def text(msg, color, x, y, origin='topleft'):
    text_surface = number_font.render(msg, True, color)
    text_rect = text_surface.get_rect()
    if origin == 'topleft':
        text_rect.topleft = (x, y)
    elif origin == 'topright':
        text_rect.topright = (x, y)
    elif origin == 'center':
        text_rect.center = (x, y)

    screen.blit(text_surface, text_rect)

class Grid:
    def __init__(self, matrix: list, start_pos: tuple) -> None:
        self.matrix = matrix
        self.start_pos = start_pos
        self.origin_x = start_pos[0]
        self.origin_y = start_pos[1]
        self.row_len = len(matrix[0])
        self.col_len = len(matrix)
        self.cross_positions = set()  # (x, y)
        self.marker_positions = set() # (x, y)
        self.correct_positions = self.get_correct_positions() # (x, y)
        self.side_numbers = self.get_side_numbers() # From top to bottom
        self.top_numbers = self.get_top_numbers()  # From left to right

    def get_side_numbers(self):
        display_numbers = []
        for row in self.matrix:
            counter = 0
            row_numbers = []
            for i in row:
                if i == 0:
                    if counter != 0:
                        row_numbers.append(str(counter))
                    counter = 0
                else:
                    counter += 1
            if counter != 0:
                row_numbers.append(str(counter))
            
            display_numbers.append(row_numbers)
        return display_numbers
    
    def get_top_numbers(self):
        transposed_matrix = transpose(self.matrix)
        display_numbers = []
        for row in transposed_matrix:
            counter = 0
            row_numbers = []
            for i in row:
                if i == 0:
                    if counter != 0:
                        row_numbers.append(str(counter))
                    counter = 0
                else:
                    counter += 1
            if counter != 0:
                row_numbers.append(str(counter))
            
            display_numbers.append(row_numbers)
        return display_numbers
    
    def get_correct_positions(self):
        solution = set()
        y = self.origin_y
        for i, row in enumerate(self.matrix):
            x = self.origin_x
            for j, el in enumerate(row):
                if el == 1:
                    solution.add((x+(CELL_SIZE*j), y+(CELL_SIZE*i)))
                x += CELL_GAP
            y += CELL_GAP
        return solution
    
    def draw_grid(self, mouse_pos: tuple):
        y = self.origin_y
        for i, row in enumerate(self.matrix):
            x = self.origin_x
            for j, el in enumerate(row):
                pygame.draw.rect(screen, WHITE, pygame.Rect(x+(CELL_SIZE*j),y+(CELL_SIZE*i), CELL_SIZE, CELL_SIZE), border_radius=4)
                x += CELL_GAP
            y += CELL_GAP
        
        if self.is_hovering_over(mouse_pos):
            self.draw_hover_highlight(mouse_pos)
        
        for cross in self.cross_positions:
            screen.blit(cross_img, cross)
    
        for marker in self.marker_positions:
            pygame.draw.rect(screen, DARK_GRAY, pygame.Rect(marker, (CELL_SIZE, CELL_SIZE)), border_radius=4)
        
        y = self.origin_y
        for i, row in enumerate(self.matrix):
            x = self.origin_x
            for j, el in enumerate(row):
                pygame.draw.rect(screen, BLACK, pygame.Rect(x+(CELL_SIZE*j),y+(CELL_SIZE*i), CELL_SIZE, CELL_SIZE), width=CELL_WIDTH, border_radius=4)
                x += CELL_GAP
            y += CELL_GAP
    
    def draw_bounding_box(self, startx: int, starty: int):
        dx = (self.origin_x + (CELL_SIZE*self.row_len + CELL_GAP*self.row_len-1)) - startx
        dy = (self.origin_y + (CELL_SIZE*self.col_len + CELL_GAP*self.col_len-1)) - starty
        pygame.draw.rect(screen, LIGHT_GRAY, pygame.Rect(startx, starty, dx+5, dy+5), border_radius=5)
        pygame.draw.rect(screen, BLACK, pygame.Rect(startx, starty, dx+5, dy+5), width=3, border_radius=5)

        pygame.draw.line(screen, BLACK, (startx, self.origin_y-5), (startx+dx, self.origin_y-5), width=3)
        pygame.draw.line(screen, BLACK, (self.origin_x-5, starty), (self.origin_x-5, starty+dy), width=3)

    def draw_hover_highlight(self, mouse_pos: tuple):
        coordinates = self.get_cell(mouse_pos)
        if coordinates is None:
            return
        else:
            pygame.draw.rect(screen, GRAY, pygame.Rect(coordinates, (CELL_SIZE, CELL_SIZE)), border_radius=4)

    def get_cell(self, coordinates: tuple):
        y = self.origin_y
        for i, row in enumerate(self.matrix):
            x = self.origin_x
            for j, el in enumerate(row):
                if x+(CELL_SIZE*j) <= coordinates[0] <= x+(CELL_SIZE*j)+CELL_SIZE and \
                    y+(CELL_SIZE*i) <= coordinates[1] <= y+(CELL_SIZE*i)+CELL_SIZE:
                    return (x+(CELL_SIZE*j), y+(CELL_SIZE*i))
                x += CELL_GAP
            y += CELL_GAP
        return None

    def is_hovering_over(self, mouse_pos: tuple):
        return self.origin_x < mouse_pos[0] < self.origin_x+(CELL_SIZE*self.row_len)+(CELL_GAP*(self.col_len-1)) and \
            self.origin_y < mouse_pos[1] < self.origin_y+(CELL_SIZE*self.row_len)+(CELL_GAP*(self.col_len-1))
    

    # Updates the list of crosses based on the given mouse position (Called whenever the left mouse button is pressed)
    def update_crosses(self, mouse_pos: tuple, draging=False):
        coordinates = self.get_cell(mouse_pos)
        if coordinates is None:
            return
        else:
            if coordinates in self.marker_positions:
                return
            elif coordinates in self.cross_positions and not draging:
                self.cross_positions.remove(coordinates)
            else:
                self.cross_positions.add(coordinates)
    
    # Updates the list of markers based on the given mouse position (Called whenever the right mouse button is pressed)
    def update_markers(self, mouse_pos: tuple, draging=False):
        coordinates = self.get_cell(mouse_pos)
        if coordinates is None:
            return
        else:
            if coordinates in self.cross_positions:
                return
            elif coordinates in self.marker_positions and not draging:
                self.marker_positions.remove(coordinates)
            else:
                self.marker_positions.add(coordinates)

    def check_win(self):
        return self.marker_positions == self.correct_positions

    def render_indicators(self):
        for i, row in enumerate(self.side_numbers):
            text('   '.join(row), BLACK, self.origin_x-15, self.origin_y+4+(CELL_GAP+CELL_SIZE)*i, 'topright')
        
        for i, row in enumerate(self.top_numbers):
            rev_row = list(reversed(row))
            for j, el in enumerate(rev_row):
                text(el, BLACK, self.origin_x+CELL_SIZE/2+(CELL_GAP+CELL_SIZE)*i, self.origin_y-21-37*j,'center')



while True:
    random_level = levels[random.randint(0,len(levels)-1)]
    #grid = Grid(random_level, GRID_START)
    grid = Grid(levels[4], GRID_START)
    while True:
        
        #Checking for events
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    if grid.is_hovering_over(mouse_pos):
                        grid.update_markers(mouse_pos)
                if event.button == 3: # Right Click
                    if grid.is_hovering_over(mouse_pos):
                        grid.update_crosses(mouse_pos)
            
            grid_cell = grid.get_cell(mouse_pos)
            if grid_cell not in grid.marker_positions and grid_cell not in grid.cross_positions:
                if pygame.mouse.get_pressed()[0]:
                    if grid.is_hovering_over(mouse_pos):
                        grid.update_markers(mouse_pos, draging=True)
                elif pygame.mouse.get_pressed()[2]:
                    if grid.is_hovering_over(mouse_pos):
                        grid.update_crosses(mouse_pos, draging=True)
        
        
        #Updating variables and drawing objects
        
        grid.draw_bounding_box(40, 50)
        grid.draw_grid(mouse_pos)
        grid.render_indicators()

        if grid.check_win():
            break
        
        #Updating the screen
        pygame.display.flip()
        screen.fill(WHITE)
        
        #Add delay
        time.sleep(round(1/FPS, 3))


sys.exit()