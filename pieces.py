from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from GUI import Status


class Player:
    def __init__(self, player_sign, direction):
        self.player_sign = player_sign
        self.direction = direction

    def __repr__(self):
        return f"<Player {self.player_sign}>"


class Piece(ABC):
    """ ABC class with a lot of propeties set to False so they can be used on specific subclasses"""
    img_directory: str = "./img/"
    img_path: str = img_directory + "{}{}.png"
    piece_name: str
    is_checkable: bool = False
    has_been_checked: bool = None
    has_moved: bool = False
    can_castle: bool = False
    en_passant: bool = None

    pos: List[int]

    def __init__(self, start_pos: List[int], owner: Player) -> None:
        self.start_pos = tuple(start_pos)
        self.pos = tuple(start_pos)
        self.owner = owner

        self.img_path = self.img_path.format(
            self.owner.player_sign, self.piece_name)

    @abstractmethod
    def possible_directions(self) -> List[List[Tuple[int, Status]]]:
        """Returns a list of possible moves, in lines (if possible)"""

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pos}>"
    

class Pawn(Piece):
    piece_name = "p"
    en_passant = False

    def possible_directions(self) -> List[Union[Status, List[int]]]:
        dir = []
        x, y = self.pos
        add_y = self.owner.direction

        if y == self.start_pos[1]:  # only targets empty spaces
            dir.append([Status.EMPTY, (x, y + add_y), (x, y + add_y * 2)])
        else:
            dir.append([Status.EMPTY, (x, y + add_y)])

        if y == self.start_pos[1] + 2 * add_y:
            self.en_passant = True
        else:
            self.en_passant = False

        for add_x in (-1, 1):   # only targets enemy spaces
            add_y = self.owner.direction

            new_x, new_y = x + add_x, y + add_y
            if 0 <= new_x <= 7 and 0 <= new_y <= 7:
                dir.append([Status.ENEMY, (new_x, new_y)])
                dir.append([Status.EN_PASSANT, (new_x, y)])

        return dir


class Rook(Piece):
    piece_name = "r"
    can_castle = True

    def possible_directions(self) -> List[List[int]]:
        dir = []
        x, y = self.pos

        for add_x, add_y in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            new_x, new_y = x + add_x, y + add_y
            current_dir = [Status.NORMAL]

            while 0 <= new_x <= 7 and 0 <= new_y <= 7:
                current_dir.append((new_x, new_y))

                new_x += add_x
                new_y += add_y

            dir.append(current_dir)
        return dir


class Bishop(Piece):
    piece_name = "b"

    def possible_directions(self) -> List[List[int]]:
        dir = []
        x, y = self.pos

        for add_x, add_y in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            new_x, new_y = x + add_x, y + add_y
            current_dir = [Status.NORMAL]

            while 0 <= new_x <= 7 and 0 <= new_y <= 7:
                current_dir.append((new_x, new_y))

                new_x += add_x
                new_y += add_y

            dir.append(current_dir)
        return dir


class Queen(Piece):
    piece_name = "q"

    def possible_directions(self) -> List[List[int]]:
        dummy_rook = Rook(self.pos, self.owner)
        dummy_bishop = Bishop(self.pos, self.owner)

        dir = dummy_rook.possible_directions() + dummy_bishop.possible_directions()
        return dir


class Knight(Piece):
    piece_name = "n"

    def possible_directions(self) -> List[List[int]]:
        dir = []
        x, y = self.pos

        for add_x, add_y in ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)):

            new_x, new_y = x + add_x, y + add_y
            if 0 <= new_x <= 7 and 0 <= new_y <= 7:
                dir.append([Status.NORMAL, (new_x, new_y)])

        return dir


class King(Piece):
    piece_name = "k"
    is_checkable = True

    def possible_directions(self) -> List[List[int]]:
        dir = []
        x, y = self.pos

        for add_x, add_y in ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1), (2, 0), (-2, 0)):

            new_x, new_y = x + add_x, y + add_y
            if 0 <= new_x <= 7 and 0 <= new_y <= 7:
                status = Status.NORMAL if abs(add_x) < 2 else Status.CASTLE
                dir.append([status, (new_x, new_y)])
            #print(dir, self.pos)

        return dir


# just for test, doesnt work anymore
if __name__ == "__main__":
    from GUI import GUI
    """Test for piece movements"""
    white_player = Player("w", -1)
    black_player = Player("b", 1)

    pos = (2, 5)
    player = black_player

    p = Pawn(pos, player)
    r = Rook(pos, player)
    b = Bishop(pos, player)
    q = Queen(pos, player)
    n = Knight(pos, player)
    k = King(pos, player)

    test_subject = q

    print(test_subject.possible_directions())

    gui = GUI()
    gui.draw_grid()
    gui.test(test_subject)

    while True:
        pass
