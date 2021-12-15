
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
ORANGE = (224, 127, 22)
HOVER_COLOR = (150, 150, 150, 0.5)
MARKER_COLOR = (80, 80, 80)
GRID_BACKGROUND = (222, 222, 222)

mouse_pos = (0, 0)
# Piltide sisse laadimine
cross_img = pygame.image.load(os.path.join('assets/images/' 'cross.png'))
example_img = pygame.image.load(os.path.join('assets/images', 'example.png'))
example2_img = pygame.image.load(os.path.join('assets/images', 'example2.png'))
marker_ex = pygame.image.load(os.path.join('assets/images', 'marker_ex.png'))
cross_ex = pygame.image.load(os.path.join('assets/images', 'cross_ex.png'))

# Fontide sisse laadimine
number_font = pygame.font.Font(os.path.join('assets/fonts', 'Arvo-Bold.ttf'), 26)
tutorial_font = pygame.font.Font(os.path.join('assets/fonts', 'BakbakOne-Regular.ttf'), 24)
text_font = pygame.font.Font(os.path.join('assets/fonts', 'BakbakOne-Regular.ttf'), 26)
big_font = pygame.font.Font(os.path.join('assets/fonts', 'BakbakOne-Regular.ttf'), 70)

# levelite failist sõnastikku lugemine
levels = {}
for i, file in enumerate(os.scandir('./assets/levels/')):
    with open(file) as f:
        levels[i] = [list(map(int, line.strip().split(' '))) for line in f.readlines()]
level_order = random.sample(range(len(levels)), len(levels))

# Lihtne funktsioon ekraanile teksti kuvamiseks
def text(msg: str, color: tuple, x: int, y: int, font: pygame.font.Font, origin='topleft', background=None):
    text_surface = font.render(msg, True, color, background)
    text_rect = text_surface.get_rect()
    if origin == 'topleft':
        text_rect.topleft = (x, y)
    elif origin == 'topright':
        text_rect.topright = (x, y)
    elif origin == 'bottomleft':
        text_rect.bottomleft = (x, y)
    elif origin == 'bottomright':
        text_rect.bottomright = (x, y)
    elif origin == 'center':
        text_rect.center = (x, y)

    screen.blit(text_surface, text_rect)


# Esimenüü
def main_menu():
    while True:
        screen.fill(WHITE)
        text('NONOGRAM', ORANGE, 300, 300, big_font, origin='center')
        text('Vajuta Enter et mängu alustada', BLACK, 300, 360, text_font, origin='center')
        text('Vajuta J et näha juhiseid.', BLACK, 300, 420, text_font, origin='center')
        text('Vajuta Q et mäng kinni panna', BLACK, 300, 390, text_font, origin='center')

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_q:
                    sys.exit()
                elif event.key == pygame.K_j:
                    instructions()
        
        time.sleep(round(10/FPS, 3))


# Pausimenüü
def esc_menu():
    text('Q - Lõpeta mängimine.      ESC - Mängi edasi', BLACK, 10, 5, text_font)
    text('PAUS!', ORANGE, 300, 300, big_font, origin='center')
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_q:
                    sys.exit()

        time.sleep(round(10/FPS, 3))

# Juhend
def instructions():
    screen.fill(WHITE)
    text('Mängu eesmärk on täita terve ruudustik korrektselt.', BLACK, 10, 10, tutorial_font)
    text('Rea ja veeru juures olevad numbrid näitavad', BLACK, 10, 60, tutorial_font)
    text('mitu järjestikku ruutu on antud reas või veerus', BLACK, 10, 85, tutorial_font)

    screen.blit(example_img, (60, 180))
    text('Näiteks see tähendab, et reas on 3 järjestikku ja', BLACK, 10, 230, tutorial_font)
    text('2 järjestikku ruutu ja nende vahel võib olla ükskõik', BLACK, 10, 255, tutorial_font)
    text('kui suur vahe.', BLACK, 10, 280, tutorial_font)

    text('Näiteks see on 1 täitmise võimalus', BLACK, 10, 360, tutorial_font)
    screen.blit(example2_img, (60, 400))

    screen.blit(marker_ex, (215, 485)) 
    text('Vasak hiireklikk -', BLACK, 10, 490, tutorial_font)

    screen.blit(cross_ex, (215, 535))
    text('Parem hiireklikk -', BLACK, 10, 540, tutorial_font)
    
    text('ESC - tagasi', BLACK, 590, 590, tutorial_font, origin='bottomright')
    
    pygame.display.flip()
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        time.sleep(round(5/FPS, 3))

# Võidu ekraan
def win_sequence():
    text('Hästi!', ORANGE, 300, 300, big_font, origin='center')
    pygame.display.flip()
    time.sleep(1)

class Grid:
    def __init__(self, matrix: list, start_pos: tuple):
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

    # Käib üle antud 2D järjendi, loendades kokku, mitu korda esineb number "1"
    # Need numbrid kuvatakse mängu välja vasakul pool
    # Kui leitakse number "0", siis lisatakse praegune järjestikuste 1-te arv (counter) listi, ja alustatakse counter uuesti 0-st
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
    
    # Käib üle antud 2D järjendi, loendades kokku, mitu korda järjest esineb number "1"
    # Need numbrid kuvatakse mängu välja ülesse
    # Kui leitakse number "0", siis lisatakse praegune järjestikuste 1-te arv (counter) listi, ja alustatakse counter uuesti 0-st 
    def get_top_numbers(self):
        #Kuna need numbrid peavad lugema veergudest, siis on kergem maatriks transponeerida, et taaskasutada funktsiooni get_side_numbers()
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
    
    # Leiab antud maatriksis igale numbrile 1 vastava koordinaatide paari, et pärast võrrelda mängija sisestatud permutatsiooniga
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
        
        # Joonistab valge ruudu ruudustiku ruutide kohtadele
        y = self.origin_y
        for i, row in enumerate(self.matrix):
            x = self.origin_x
            for j, el in enumerate(row):
                pygame.draw.rect(screen, WHITE, pygame.Rect(x+(CELL_SIZE*j),y+(CELL_SIZE*i), CELL_SIZE, CELL_SIZE), border_radius=4)
                x += CELL_GAP
            y += CELL_GAP
        
        # Joonistab halli ruudu ruudu peale mille kohal hiir praeguselt on
        if self.is_hovering_over(mouse_pos):
            self.draw_hover_highlight(mouse_pos)
        
        # Joonistab kõik salvestatud ristid ekraanile
        for cross in self.cross_positions:
            screen.blit(cross_img, cross)
    
        # Joonistab kõik salvestatud markerid ekraanile
        for marker in self.marker_positions:
            pygame.draw.rect(screen, MARKER_COLOR, pygame.Rect(marker, (CELL_SIZE, CELL_SIZE)), border_radius=4)
        
        # Joonistab iga kasti ümber musta joone
        y = self.origin_y
        for i, row in enumerate(self.matrix):
            x = self.origin_x
            for j, el in enumerate(row):
                pygame.draw.rect(screen, BLACK, pygame.Rect(x+(CELL_SIZE*j),y+(CELL_SIZE*i), CELL_SIZE, CELL_SIZE), width=CELL_WIDTH, border_radius=4)
                x += CELL_GAP
            y += CELL_GAP
    
    # Joonistab änguvälja ümber oleva kasti
    def draw_bounding_box(self, startx: int, starty: int):
        dx = (self.origin_x + (CELL_SIZE*self.row_len + CELL_GAP*self.row_len-1)) - startx
        dy = (self.origin_y + (CELL_SIZE*self.col_len + CELL_GAP*self.col_len-1)) - starty
        pygame.draw.rect(screen, GRID_BACKGROUND, pygame.Rect(startx, starty, dx+5, dy+5), border_radius=5)
        pygame.draw.rect(screen, BLACK, pygame.Rect(startx, starty, dx+5, dy+5), width=3, border_radius=5)

        pygame.draw.line(screen, BLACK, (startx, self.origin_y-5), (startx+dx, self.origin_y-5), width=3)
        pygame.draw.line(screen, BLACK, (self.origin_x-5, starty), (self.origin_x-5, starty+dy), width=3)

    # Täidab ruubu, mille kohal on hiir, halli värviga
    def draw_hover_highlight(self, mouse_pos: tuple):
        coordinates = self.get_cell(mouse_pos)
        if coordinates is None:
            return
        else:
            pygame.draw.rect(screen, HOVER_COLOR, pygame.Rect(coordinates, (CELL_SIZE, CELL_SIZE)), border_radius=4)

    def draw_score(self, score: int):
        text('Skoor:', BLACK, self.origin_x-100, self.origin_y-140, text_font)
        text(str(score), BLACK, self.origin_x-70, self.origin_y-110, text_font)

    # Leiab antud hiire koordinaatidele vastava ruudu üleva vasaku nurga koordinaadid. Kui ruutu ei leidu, siis tagastab None
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

    # Leiab kas hiir on umbes mänguvälja sees. Arvasin et see on effektiivsem kuid tegelt ei tea kas see on.
    def is_hovering_over(self, mouse_pos: tuple):
        return self.origin_x < mouse_pos[0] < self.origin_x+(CELL_SIZE*self.row_len)+(CELL_GAP*(self.col_len-1)) and \
            self.origin_y < mouse_pos[1] < self.origin_y+(CELL_SIZE*self.row_len)+(CELL_GAP*(self.col_len-1)) 

    # Uuendab markerite listi antud hiire positisiooni alusel (kutsutud kui vasak hiire nupp on alla vajutatud)
    def update_crosses(self, mouse_pos: tuple):
        coordinates = self.get_cell(mouse_pos)
        if coordinates is None:
            return
        else:
            if coordinates in self.marker_positions:
                return
            elif coordinates in self.cross_positions:
                self.cross_positions.remove(coordinates)
            else:
                self.cross_positions.add(coordinates)
    
    # Uuendab markerite listi antud hiire positisiooni alusel (kutsutud kui parem hiire nupp on alla vajutatud)
    def update_markers(self, mouse_pos: tuple):
        coordinates = self.get_cell(mouse_pos)
        if coordinates is None:
            return
        else:
            if coordinates in self.cross_positions:
                return
            elif coordinates in self.marker_positions:
                self.marker_positions.remove(coordinates)
            else:
                self.marker_positions.add(coordinates)

    # Kontrollib, kas mängija sistestatud permutatsioon on õige.
    def check_win(self):
        return self.marker_positions == self.correct_positions

    def render_indicators(self):
        for i, row in enumerate(self.side_numbers):
            text('   '.join(row), BLACK, self.origin_x-15, self.origin_y+4+(CELL_GAP+CELL_SIZE)*i, number_font, origin='topright')
        
        for i, row in enumerate(self.top_numbers):
            rev_row = list(reversed(row))
            for j, el in enumerate(rev_row):
                text(el, BLACK, self.origin_x+CELL_SIZE/2+(CELL_GAP+CELL_SIZE)*i, self.origin_y-21-37*j,number_font, origin='center')

completed = 0
main_menu()
while True:
    if completed >= len(levels):
        screen.fill(WHITE)
        text('MÄNG LÄBI!', ORANGE, 300, 300, big_font, origin='center')
        text(f'Lõpetasite kõik {completed} levelit!', BLACK, 300, 350, text_font, origin='center')
        pygame.display.flip()
        time.sleep(5)
        sys.exit()

    grid = Grid(levels[level_order[completed]], GRID_START)
    #grid = Grid(levels[5], GRID_START)
    while True:
        
        # Eventide kuulamine
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1: # Left Click
                    if grid.is_hovering_over(mouse_pos):
                        # Lisab ruudu ülemise vasaku nurga koordinaadid mille kohal hiir
                        # praeguselt on, markerite listi (need joonistatakse real 321 meetodiga draw_grid)
                        grid.update_markers(mouse_pos)
                elif event.button == 3: # Right Click
                    if grid.is_hovering_over(mouse_pos):
                        # Lisab ruudu ülemise vasaku nurga koordinaadid mille kohal hiir
                        # praeguselt on, ristide listi (need joonistatakse real 321 meetodiga draw_grid)
                        grid.update_crosses(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    esc_menu()



        # Muutujate uuendamine ja ekraani uuendamine
        screen.fill(WHITE)

        grid.draw_bounding_box(GRID_START[0]-110, GRID_START[1]-150)
        mouse_pos = pygame.mouse.get_pos()
        grid.draw_grid(mouse_pos)
        grid.render_indicators()
        grid.draw_score(completed)
        text('ESC - Paus', BLACK, 10, 590, text_font, origin='bottomleft')
        
        #Updating the screen
        pygame.display.flip()

        if grid.check_win():
            win_sequence()
            completed += 1
            break
        
        #Add delay
        time.sleep(1/FPS)

sys.exit()
