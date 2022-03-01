import pygame
from enum import Enum
from typing import List, Tuple, Dict

class Status(Enum):
    # used fo colors
    EMPTY = "empty"
    ENEMY = "enemy"
    HIGHLIGHT = "highlight"
    
    KING = "king"

    # Used in event loop
    QUIT = "quit"
    CLICKED = "clicked"

    # used to check if piece is present
    PIECE_PRESENT = "piece"
    NO_PIECE_PRESENT = "no_piece"

    MOVED = "moved"
    INCORRECT_SPOT = "incorrect_spot"
    RECHOOSE = "rechoose"

    # moving directions
    NORMAL = "normal"
    CASTLE = "castle"
    #ENEMY = "enemy"
    #EMPTY = "empty"


class Color():

    def __init__(self, empty, highlight, can_move):
        self.empty = empty
        self.highlight = highlight
        self.can_move = can_move


class GUI:
    SQUARE_SIZE = 75
    WIN_HEIGHT = 8 * SQUARE_SIZE
    WIN_WIDTH = 8 * SQUARE_SIZE

    WHITE = Color(
        empty = (238, 238, 210),
        highlight = (246, 246, 104),
        can_move = (214, 214, 189)
    )
    BLACK = Color(
        empty = (118, 150, 86),
        highlight = (187, 202, 42),
        can_move = (106, 135, 77)
    )

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))

    def draw_square(self, x, y, color_attr: Status =Status.EMPTY) -> None:
        square = pygame.Rect(
                    x * self.SQUARE_SIZE, y * self.SQUARE_SIZE,
                    self.SQUARE_SIZE, self.SQUARE_SIZE
                     )
        color = getattr(self.get_color(x, y), color_attr.value)
        pygame.draw.rect(self.screen, color, square)

    def draw_grid(self):
        """ Draws the grid """
        for y in range(0, self.WIN_HEIGHT // self.SQUARE_SIZE):
            for x in range(0, self.WIN_WIDTH // self.SQUARE_SIZE):
                self.draw_square(x, y)

    def draw_piece(self, pos: Tuple[int, int], piece_path: str, background=Status.EMPTY):
        x, y = pos
        nonsized_img = pygame.image.load(piece_path)
        img = pygame.transform.scale(nonsized_img, (self.SQUARE_SIZE, self.SQUARE_SIZE))

        if background == Status.HIGHLIGHT:
            self.draw_square(x, y, background)

        self.screen.blit(img, (x*self.SQUARE_SIZE, y*self.SQUARE_SIZE))


    def update(self):
        pygame.display.update()


    def get_color(self, x, y):
        """ Gets the color of inputed square"""
        if (x + y) % 2 == 0:
            return self.WHITE
        else:
            return self.BLACK


    def test(self, piece):
        """ Used in pieces.py test, displays the piece and it's moves"""
        x, y = piece.pos

        img = pygame.transform.scale(pygame.image.load(piece.img_path), (self.SQUARE_SIZE, self.SQUARE_SIZE))
        
        self.draw_can_move(piece.possible_directions())
        self.screen.blit(img, (x*self.SQUARE_SIZE, y*self.SQUARE_SIZE), )
        pygame.display.update()

    def draw_can_move(self, possible_moves: Dict):
        """ Draws circles on squares that are in the list"""
        for (x, y), status in possible_moves.items():
            if status == Status.ENEMY:
               self.draw_square(x, y, Status.HIGHLIGHT)
            else:
                 pygame.draw.circle(
                    self.screen, self.get_color(x, y).can_move,
                    (x*self.SQUARE_SIZE + self.SQUARE_SIZE * .5 , y*self.SQUARE_SIZE + self.SQUARE_SIZE * .5),
                    self.SQUARE_SIZE * .2
                    )

    def get_click(self):
        action = False
        while not action:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return Status.QUIT, event
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    x //= self.SQUARE_SIZE
                    y //= self.SQUARE_SIZE

                    clicking = True
                    while clicking:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONUP:
                                new_x, new_y = event.pos
                                new_x //= self.SQUARE_SIZE
                                new_y //= self.SQUARE_SIZE
                                clicking = False
                    if x == new_x and y == new_y:
                        return Status.CLICKED, (x, y)



if __name__ == "__main__":
    g = GUI()
    run = True
    while run:
        for event in pygame.event.get():
            print(event.type)
            if event.type == pygame.QUIT:
                run = False

