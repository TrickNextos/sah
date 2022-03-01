from typing import List, Tuple, Dict

from pieces import Piece, Player, Pawn, Rook, Knight, Bishop, Queen, King
from GUI import GUI, Status

white_player = Player("w", -1)
black_player = Player("b", 1)

start_board = {
    Rook((0, 0), black_player), Knight((1, 0), black_player), Bishop(
        (2, 0), black_player), Queen((3, 0), black_player),
    King((4, 0), black_player), Bishop((5, 0), black_player), Knight(
        (6, 0), black_player), Rook((7, 0), black_player),

    Pawn((0, 1), black_player), Pawn((1, 1), black_player), Pawn(
        (2, 1), black_player), Pawn((3, 1), black_player),
    Pawn((4, 1), black_player), Pawn((5, 1), black_player), Pawn(
        (6, 1), black_player), Pawn((7, 1), black_player),


    Pawn((0, 6), white_player), Pawn((1, 6), white_player), Pawn(
        (2, 6), white_player), Pawn((3, 6), white_player),
    Pawn((4, 6), white_player), Pawn((5, 6), white_player), Pawn(
        (6, 6), white_player), Pawn((7, 6), white_player),

    Rook((0, 7), white_player), Knight((1, 7), white_player),   Bishop(
        (2, 7), white_player), Queen((3, 7), white_player),
    King((4, 7), white_player), Bishop((5, 7), white_player),   Knight(
        (6, 7), white_player), Rook((7, 7), white_player)
}


def pawn_upgrade(piece, pos):
    if isinstance(piece, Pawn):
        direction = piece.owner.direction
        if pos[1] == 7 and direction == 1 or pos[1] == 0 and direction == -1:
            piece = Queen(pos, piece.owner)
    return piece


class Board:

    letters_table = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7
    }

    def __init__(self, starter_board: dict = start_board):
        self.pieces: dict = {}
        for piece in starter_board:
            self.pieces[piece.pos] = piece
        self.gui: GUI = GUI()

    def draw_board(self):
        self.gui.draw_grid()

    def draw_pieces(self):
        for piece in self.pieces.values():

            self.gui.draw_piece(piece.pos, piece.img_path)
        self.gui.update()

    def draw_moves(self, moves: List[Tuple[int, str]]):
        self.gui.draw_can_move(moves)

    def __getitem__(self, pos) -> Piece:
        pos = tuple(pos)
        x, y = pos
        if isinstance(x, str):
            pos = [self.letters_table[x], 8 - int(y)]
        try:
            piece = self.pieces[pos]
        except KeyError:
            return Status.NO_PIECE_PRESENT, None
        return Status.PIECE_PRESENT, piece

    def highlight(self, piece: Piece):
        self.gui.draw_piece(piece.pos, piece.img_path,
                            background=Status.HIGHLIGHT)


class Simulation:
    castle_rook = dict()
    _checkmate = True
    en_passant = dict()

    def __init__(self, tester_board, cur_player):
        self.start_board = dict(tester_board)
        self.tester_board = dict(tester_board)
        self.cur_player = cur_player

    def run(self):
        """Main func that returns a dict of all possible moves"""
        all_moves = {}
        #print("Check:", self.check())
        for old_pos, my_piece in self.start_board.items():
            if my_piece.owner == self.cur_player:

                correct_moves = {}
                available_moves = self.check_directions(my_piece)
                for new_pos, status in available_moves.items():
                    self.move(my_piece, new_pos)

                    if self.check() is False:
                        correct_moves[new_pos] = status
                        self._checkmate = False
                    my_piece.pos = old_pos

                    self.tester_board = dict(self.start_board)
                all_moves[my_piece] = correct_moves
        # print(all_moves)
        #print("a", all_moves)
        self.moves = all_moves
        return all_moves

    def currently_checked(self):
        return self.check(board_name="start_board")

    def checkmate(self) -> bool:
        print(self._checkmate)
        return self._checkmate

    def move(self, cur_piece: Piece, new_pos):
        """ Moves a piece but is used only for test (it's reverted back)"""
        del self.tester_board[cur_piece.pos]
        cur_piece = pawn_upgrade(cur_piece, new_pos)
        cur_piece.pos = new_pos
        self.tester_board[cur_piece.pos] = cur_piece

    def locate_king(self, return_object=False):
        """ Gets pos of current's player king """
        for my_piece in self.tester_board.values():
            if my_piece.owner == self.cur_player and my_piece.is_checkable:
                return my_piece.pos

    def check(self, board_name="tester_board"):
        king_pos = self.locate_king()
        for pos, enemy in getattr(self, board_name).items():
            if enemy.owner != self.cur_player:
                moves = self.check_directions(enemy, enemy_only=True)
                for pos in moves.items():
                    if pos[0] == king_pos:
                        return True
        return False

    def can_en_passant(self, piece: Piece, new_pos):
        if not new_pos in self.tester_board:
            return 
        x, y = new_pos
        moving_pos = (x, y + piece.owner.direction)
        if moving_pos in self.tester_board:
            return

        other_piece: Piece = self.tester_board[new_pos]
        if not other_piece.en_passant is True:
            return
        self.en_passant[new_pos] = moving_pos
        #print("works", piece, new_pos)
        return True

    def special_directions(self, piece, pos, special_status):
        if pos in self.tester_board:                # checks if mentioned position is occupied by any piece
            status = Status.ENEMY
        else:
            status = Status.EMPTY

        if special_status == Status.ENEMY:
            if status == Status.EMPTY:              # attack only enemies
                return True

        elif special_status == Status.EMPTY:        # e.g.: attack only
            if status != Status.EMPTY:
                return True

        elif special_status == Status.CASTLE:       # it can't castle
            castle_status = self.can_castle(piece, pos)
            if not castle_status:
                return True

        elif special_status == Status.EN_PASSANT:
            return not self.can_en_passant(piece, pos)

        return False                                # all is good

    def can_castle(self, piece: Piece, pos):
        if not isinstance(piece, King):
            return
        if piece.owner != self.cur_player:
            return
        if piece.has_moved or piece.has_been_checked:
            return

        king_x, king_y = piece.pos
        rook_x = 0 if king_x > pos[0] else 7
        if (rook_x, king_y) not in self.tester_board:
            return
        rook = self.tester_board[rook_x, king_y]
        if not isinstance(rook, Rook):
            return
        if rook.has_moved:
            return

        direction = -1 if king_x > pos[0] else 1
        for x in range(king_x + direction, rook_x, direction):
            if (x, king_y) in self.tester_board:
                return False
        self.castle_rook[pos] = (rook, (king_x + direction, king_y))
        return True

    def check_directions(self, cur_piece: Piece, enemy_only: bool = False):
        all_directions = cur_piece.possible_directions()
        moves = {}
        for direction in all_directions:
            for pos in direction[1:]:
                try:
                    occupaying_piece = self.tester_board[pos]
                except KeyError:                                # no piece there: Status.EMPTY
                    if not(enemy_only):
                        moves[pos] = Status.EMPTY
                        if direction[0] in (Status.EN_PASSANT, Status.CASTLE):
                            moves[pos] = direction[0]
                else:                                           # piece is there and its not the same owner: Status.ENEMY
                    if occupaying_piece.owner != cur_piece.owner:
                        moves[pos] = Status.ENEMY
                        if direction[0] in (Status.EN_PASSANT, Status.CASTLE):
                            moves[pos] = direction[0]
                    break

            if direction[0] != Status.NORMAL and moves != {}:
                if self.special_directions(cur_piece, pos, direction[0]) and pos in moves:
                    del moves[pos]

        return moves


class Game:
    _i = 0
    last_piece_moved = None
    is_checked = set()

    def __init__(self, owners: List[Player], board: Board = Board()):
        self.board = board
        self.owners = list(owners)
        self.change_player()

    def change_player(self):
        self.cur_player = self.owners[self._i % 2]
        self.opponent_player = self.owners[(self._i + 1) % 2]
        self._i += 1
    """
    def check_directions(self, cur_piece:Piece, check=True, deadly_piece=None) -> List[Tuple[int, Status]]:
        all_directions = cur_piece.possible_directions()
        available_moves = dict()
        for direction in all_directions:
            for pos in direction[1:]:                               # gets all directions
                status, occupaying_piece = self.board[pos]
                if status is Status.NO_PIECE_PRESENT:
                    available_moves[pos] = Status.EMPTY
                    continue
                elif occupaying_piece.owner == cur_piece.owner:
                    break
                else:
                    available_moves[pos] = Status.ENEMY
                    break


            if available_moves != {}:
                if not direction[0] == Status.NORMAL:                   # removes some if needed (pawn)
                    special_status = direction[0]
                    for pos in direction[1:]:
                        status, occupaying_piece = self.board[pos]
                        if special_status == Status.ENEMY:
                            if status == Status.NO_PIECE_PRESENT:
                                del available_moves[pos]
                                continue
                        
        
        return available_moves
"""
    """
    def check_dir_for_check(self, cur_piece, available_moves: Dict, deadly_piece = None):
        after_check = available_moves
        for pos, status in dict(available_moves).items():
            if status == Status.ENEMY:
                if deadly_piece != None and pos == deadly_piece.pos:
                    piece = self.board[pos]
                    self.extra_higlight = piece
                    continue
                

            if self.calculate_check(cur_piece, pos):
                for piece in self.is_checked:
                    if piece.owner == self.cur_player:
                        del after_check[pos]
                        continue
        return after_check"""

    def calculate(self, piece: Piece):
        self.board.draw_board()
        self.board.draw_moves(self.only_moves[piece])
        self.board.highlight(piece)
        self.board.draw_pieces()

    def move(self, piece: Piece, new_pos: Tuple[int, int]) -> None:
        self.board.draw_board()  # draws

        moves = self.only_moves[piece]
        if new_pos in moves.keys():
            status = moves[new_pos]
            print(status)
        else:                                                                   # if the pos is not correct
            incorrect_piece_status, clicked_piece = self.board[new_pos]
            if incorrect_piece_status == Status.PIECE_PRESENT and piece.owner == clicked_piece.owner:
                return Status.RECHOOSE
            return Status.INCORRECT_SPOT

        # chose correct square
        del self.board.pieces[piece.pos]
        # upgrade to Queen if neccesary
        piece = pawn_upgrade(piece, new_pos)
        if status is Status.CASTLE:
            self.move(*self.castle_rook[new_pos])
        
        if status is Status.EN_PASSANT:
            print("en_passant", self.en_passant[new_pos])
            moving_pos = self.en_passant[new_pos]
            piece.pos = moving_pos
            self.board.pieces[moving_pos] = piece
            del self.board.pieces[new_pos]

        else:
            piece.pos = new_pos
            self.board.pieces[new_pos] = piece

        piece.has_moved = True

        self.board.draw_pieces()
        return Status.MOVED             # everything is ok
        """
        self.board.draw_board()
        #moves = self.check_directions(piece, deadly_piece=self.last_piece_moved)
        
        try:
            #print("only", self.only_moves)
            print(piece, new_pos)
            print(self.only_moves[piece])
            status = self.only_moves[new_pos]
            print("OK")
            #status = moves[new_pos]
        except KeyError:
            incorrect_piece_status, clicked_piece = self.board[new_pos]
            print("incorrect:", incorrect_piece_status, clicked_piece)
            if incorrect_piece_status == Status.PIECE_PRESENT and piece.owner == clicked_piece.owner:
                return Status.RECHOOSE
            return Status.INCORRECT_SPOT
        if status == Status.ENEMY:
            self.board.pieces.pop(self.board[new_pos][1])

        
        piece.pos = new_pos
        self.board.pieces[piece] = new_pos

        self.last_piece_moved = piece
        #print("Check:", self.calculate_check(deadly_piece=self.last_piece_moved))
        #print("King:", self.is_checked)
        
        self.board.draw_pieces()
        return Status.MOVED"""
    """def calculate_check(self, can_move_piece=None, new_pos=None, deadly_piece=None):
        self.is_checked = set()
        all_king_pos = set()
        old_pos = None
        if not can_move_piece is None:
                old_pos = can_move_piece.pos
                can_move_piece.pos = new_pos
                self.board.pieces[new_pos] = can_move_piece
                #print("New piece pos", can_move_piece, can_move_piece.pos)
        for piece in self.board.pieces.values():
            
            if piece.is_checkable:
                all_king_pos.add(piece.pos)

            moves = self.check_directions(piece, check=False)
            for pos, status in moves.items():
                if status == Status.ENEMY:
                    _, enemy_piece = self.board[pos]
                    if enemy_piece.is_checkable:
                        #print("Enemy",enemy_piece)
                        self.is_checked.add(enemy_piece)
                        

        if not old_pos is None:
            can_move_piece.pos = old_pos
            self.board.pieces[old_pos] = can_move_piece


        #print("Kings", all_king_pos)
        for piece in self.is_checked:
            return True
        return False
        """
    """def checkmate(self):
        #Useless
        checkmate = False
        if self.calculate_check():
            checkmate = True
        for piece in self.board.pieces:
            moves = self.check_directions(piece, deadly_piece=self.last_piece_moved)
            if piece.owner == self.cur_player:
                if moves != dict():
                    checkmate = False
        return checkmate
"""

    def simulate(self):
        """Simulates every game move to determine if it causes check"""
        sim = Simulation(dict(self.board.pieces), self.cur_player)
        if sim.currently_checked():
            self.board.pieces[sim.locate_king()].has_been_checked = True
        self.only_moves = sim.run()
        self.castle_rook: dict = sim.castle_rook
        self.checkmate = sim.checkmate()
        self.en_passant = sim.en_passant

    def main(self):
        self.board.draw_board()
        self.board.draw_pieces()
        running = True
        need_new_pos = True

        self.simulate()

        while running != Status.QUIT:
            if need_new_pos:                                # chooses new piece
                running, pos = self.board.gui.get_click()
                print("1", pos)

            status, chosen_piece = self.board[pos]
            if status == Status.PIECE_PRESENT and chosen_piece.owner != self.cur_player:  # checks if it's the correct player
                print(2, "wrong player")
                continue

            if status == Status.PIECE_PRESENT:   # Checks if there is a piece
                print(3, "piece present")
                self.calculate(chosen_piece)
                print("Check:", self.checkmate)
                while True:
                    # Where do you want the piece to move
                    running, pos = self.board.gui.get_click()
                    is_moved = self.move(chosen_piece, pos)
                    if is_moved == Status.MOVED:
                        need_new_pos = True
                        self.change_player()
                        self.simulate()
                        if self.checkmate:
                            running = Status.QUIT
                        break
                    elif is_moved == Status.RECHOOSE:
                        need_new_pos = False
                        break


if __name__ == "__main__":
    g = Game([white_player, black_player])

    g.main()
