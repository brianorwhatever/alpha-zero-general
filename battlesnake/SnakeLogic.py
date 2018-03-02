'''
Author: Eric P. Nichols
Date: Feb 8, 2008.
Board class.
Board data:
  1=white, -1=black, 0=empty
  first dim is column , 2nd is row:
     pieces[1][7] is the square in column 2,
     at the opposite end of the board in row 8.
Squares are stored and manipulated as (x,y) tuples.
x is the column, y is the row.
'''
from random import randint

FOOD = 99
WHITE = 1
BLACK = -1
HEALTH = 15

def _random_free_space(pieces, n):
    while True:
        x = randint(0, n-1)
        y = randint(0, n-1)
        if pieces[x][y] == 0:
            return x, y

def copy(board):
    return [row[:] for row in board]

def remove_food(board):
    return [x if x != FOOD else 0 for x in board]

class Board():

    # list of all 4 directions on the board, as (x,y) offsets
    __directions = [(1,0),(0,-1),(-1,0),(0,1)]

    def __init__(self, n):
        "Set up initial board configuration."

        self.n = n
        self.white_health = HEALTH
        self.black_health = HEALTH
        # Create the empty board array.
        self.pieces = [None]*self.n
        for i in range(self.n):
            self.pieces[i] = [0]*self.n

        # Set up the initial 3 pieces.
        player_1_x, player_1_y = _random_free_space(self.pieces, self.n)
        self.pieces[player_1_x][player_1_y] = 1
        player_2_x, player_2_y = _random_free_space(self.pieces, self.n)
        self.pieces[player_2_x][player_2_y] = -1
        food_x, food_y = _random_free_space(self.pieces, self.n)
        self.pieces[food_x][food_y] = FOOD

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        white_count = 0
        black_count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] != FOOD and self[x][y] > 0:
                    white_count += 1
                elif self[x][y] != FOOD and self[x][y] < 0:
                    black_count += 1
        if color == WHITE:
            return white_count - black_count
        else:
            return black_count - white_count

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white head, -1 for black head
        """
        moves = []  # stores the legal moves.

        # Get all the squares with pieces of the given color.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == color:
                    newmoves = self.get_moves_for_square((x, y))
                    moves.append(newmoves)
        return list(moves)

    def has_legal_moves(self, color):
        return len(self.get_legal_moves(color)) > 0

    def get_moves_for_square(self, square):
        """Returns all the legal moves that use the given square as a base.
        That is, if the given square is (3,4) and it contains a black piece,
        and (3,5) and (3,6) contain white pieces, and (3,7) is empty, one
        of the returned moves is (3,7) because everything from there to (3,4)
        is flipped.
        """
        (x_origin,y_origin) = square

        # determine the color of the piece.
        color = self[x_origin][y_origin]

        # skip empty source squares.
        if color != 1 and color != -1:
            return None

        # search all possible directions.
        moves = []
        for direction in self.__directions:
            x = x_origin + direction[0]
            y = y_origin + direction[1]
            if self.n > x >= 0 and self.n > y >= 0 and (self[x][y] == 0 or self[x][y] == FOOD):
                moves.append(direction)

        # return the generated move list
        return moves

    def execute_move(self, move, color):
        """Perform the given move on the board.
        color gives the color pf the piece to play (1=white,-1=black)
        """
        move_x = move[0]
        move_y = move[1]
        origin_x, origin_y = self._find_head(color)
        x = move_x + origin_x
        y = move_y + origin_y

        if color == WHITE:
            self.white_health -= 1
            if self.white_health == 0:
                self._remove_snake(color)
                return

        elif color == BLACK:
            self.black_health -= 1
            if self.black_health == 0:
                self._remove_snake(color)
                return

        if self[x][y] == FOOD:
            if color == WHITE:
                self.white_health = HEALTH
            elif color == BLACK:
                self.black_health = HEALTH
            self._move_snake(color, (origin_x, origin_y), move, True)
            new_food_x, new_food_y = _random_free_space(self.pieces, self.n)
            self.pieces[new_food_x][new_food_y] = 1
        elif self[x][y] != 0:
            # BUG - snake can't step where it's tail previously was
            self._remove_snake(color)
        else:
            self._move_snake(color, (origin_x, origin_y), move, False)

    def _remove_snake(self, color):
        if color == WHITE:
            self.pieces = [[0 if x != FOOD and x > 0 else x for x in y] for y in self.pieces]
        elif color == BLACK:
            self.pieces = [[0 if x != FOOD and x < 0 else x for x in y] for y in self.pieces]

    def _move_snake(self, color, head, move, add_to_tail=False):
        temp_board = copy(self.pieces)
        tail_x, tail_y = self._find_tail(color)
        body_len = abs(temp_board[tail_x][tail_y])
        # remove tail
        if not add_to_tail:
            temp_board[tail_x][tail_y] = 0
        # increment body pieces
        for x in range(body_len):
            temp_board[temp_board == x] = x + 1 * color
        # add new head
        temp_board[head[0]+move[0]][head[1]+move[1]] = color
        self.pieces = temp_board

    def _find_tail(self, color):
        largest_white_x = None
        largest_white_y = None
        largest_black_x = None
        largest_black_y = None
        for x in self.n:
            for y in self.n:
                if self[x][y] > 0 and self[x][y] > self[largest_white_x][largest_white_y]:
                    largest_white_x = x
                    largest_white_y = y
                elif self[x][y] < 0 and self[x][y] < self[largest_black_x][largest_black_y]:
                    largest_black_x = x
                    largest_black_y = y
        if color == WHITE:
            return largest_white_x, largest_white_y
        elif color == BLACK:
            return largest_black_x, largest_black_y

    def _find_head(self, color):
        for x in self.n:
            for y in self.n:
                if self[x][y] == color:
                    return x, y
