from itertools import product
import numpy as np
import networkx as nx

def canonical(board):
    """
    Given a board (a flat tuple of 9 elements), this function returns
    its canonical form: the lexicographically smallest tuple among all
    rotations and reflections.
    """
    arr = np.array(board).reshape(3, 3)
    forms = []
    # There are 4 rotations (0, 90, 180, 270 degrees)
    for i in range(4):
        rotated = np.rot90(arr, i)
        # Add both the rotated board and its horizontal reflection.
        forms.append(tuple(rotated.flatten()))
        # Reflection: flip left-to-right (horizontal reflection)
        flipped = np.fliplr(rotated)
        forms.append(tuple(flipped.flatten()))
    # Return the minimum form (by tuple comparison) as the canonical representative.
    return min(forms)

def check_winner(board):
    """
    Check if a tic tac toe game has been won.

    Args:
        board (tuple): A tuple of 9 integers representing the game board.
                       0 = empty, 1 = circle, 2 = cross.
                       The board positions are indexed as follows:
                         0 | 1 | 2
                        ---+---+---
                         3 | 4 | 5
                        ---+---+---
                         6 | 7 | 8

    Returns:
        int: 1 if player 1 (circle) wins, 2 if player 2 (cross) wins, or 0 if no winner.
    """
    # Define all winning combinations: rows, columns, and diagonals.
    winning_combinations = [
        (0, 1, 2),  # Top row
        (3, 4, 5),  # Middle row
        (6, 7, 8),  # Bottom row
        (0, 3, 6),  # Left column
        (1, 4, 7),  # Middle column
        (2, 5, 8),  # Right column
        (0, 4, 8),  # Diagonal from top-left
        (2, 4, 6)   # Diagonal from top-right
    ]

    # Check each winning combination.
    for a, b, c in winning_combinations:
        # If the first cell is not empty and all three are equal,
        # then that player has won.
        if board[a] != 0 and board[a] == board[b] == board[c]:
            return board[a]
    
    # No winner found.
    return 0

def generate_neighbors_of(board):
    """
    Given a board, generates all the boards it can become in the next step, in canonical form
    """
    nextcanons = set()
    boardnext = list(board)[:]
    if board.count(1) - board.count(2) > 0:
        nextMove = 2
    else:
        nextMove = 1
    for i in range(9):
        if boardnext[i] == 0:
            temp = boardnext.copy()
            temp[i] = nextMove
            nextcanons.add(canonical(temp))
    assert len(nextcanons) < 8
    return nextcanons

def get_boards():
    allboards = set()
    for board in product([0, 1, 2], repeat=9):
        allboards.add(canonical(board))

    circmoveboards = set()
    crossmoveboards = set()
    for board in allboards:
        diff = board.count(1) - board.count(2)
        if diff == 1:
            crossmoveboards.add(board)
        elif diff == 0:
            circmoveboards.add(board)

    G = nx.DiGraph()
    for board in circmoveboards:
        filled = sum(1 for x in board if x != 0)
        G.add_node(board, level=filled)

    for board in crossmoveboards:
        filled = sum(1 for x in board if x != 0)
        G.add_node(board, level=filled)

    for sboard in circmoveboards.union(crossmoveboards):
        if not check_winner(sboard):
            for tboard in generate_neighbors_of(sboard):
                G.add_edge(sboard,tboard)
    
    return G

