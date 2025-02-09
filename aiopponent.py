import argparse
from tictactoe_graph import get_boards, canonical

G = get_boards()

def get_turn(board):
    if board.count(1) == board.count(2):
        return 1
    else:
        return 2

def is_win(board, player):
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
        (0, 4, 8), (2, 4, 6)               # diagonals
    ]
    for a, b, c in winning_combinations:
        if board[a] == board[b] == board[c] == player:
            return True
    return False

def is_draw(board):
    return 0 not in board and not is_win(board, 1) and not is_win(board, 2)

def is_terminal(board):
    return is_win(board, 1) or is_win(board, 2) or is_draw(board)


# we use minimax with back-propagation for our "AI" logic
minimax_cache = {}

def minimax(board, ai_player):
    """
    Recursively computes the minimax value for the board from the perspective
    of ai_player. The value is defined as:
       - 1.0 if, with perfect play, ai_player can force a win.
       - 0.0 if ai_player is forced to lose.
       - 0.5 for a draw.
       
    Parameters:
        board (tuple): the current board state.
        ai_player (int): the player number (1 or 2) for which we are computing the value.
        
    Returns:
        float: the value (preference rate) of this board state.
    """
    if board in minimax_cache:
        return minimax_cache[board]
    
    if is_terminal(board):
        # Terminal state: assign values based on outcome.
        if is_draw(board):
            value = 0.5
        elif is_win(board, ai_player):
            value = 1.0
        else:
            value = 0.0
        minimax_cache[board] = value
        return value
    
    turn = get_turn(board)
    # Get all possible next board states from the graph
    children = list(G.successors(board))
    
    # In case there are no legal moves (should not happen in a proper tic-tac-toe game),
    # we treat it as a draw.
    if not children:
        minimax_cache[board] = 0.5
        return 0.5

    if turn == ai_player:
        # It's ai_player's turn, so choose the move that maximizes our chance.
        value = max(minimax(child, ai_player) for child in children)
    else:
        # It's the opponent's turn, assume they choose the move that minimizes our chance.
        value = min(minimax(child, ai_player) for child in children)
    
    minimax_cache[board] = value
    return value

def best_move(board):
    """
    Given the current board state and that it is ai_player's turn,
    returns the board state that results from the best move (the move with
    the highest minimax value).
    """
    print("Input board:", board)
    board = canonical(board)
    print("Canonical form is", board)
    ai_player = get_turn(board)
    children = list(G.successors(board))
    if not children:
        return None  # No moves available
    
    # Evaluate each possible move
    moves = {child: minimax(child, ai_player) for child in children}
    
    # Choose the move with the highest value.
    best_child = max(moves, key=moves.get)
    #print("Move ratings:", moves)
    print("Best move is", best_child)
    print("Best move has value:", moves[best_child])
    return best_child

def main():
    parser = argparse.ArgumentParser(
        description="Tic Tac Toe AI: Given a board state, returns the best move (new board state)."
    )
    parser.add_argument(
        '--board', type=str, required=True,
        help='Board state as comma-separated 9 values (0,1,2). For example: "0,0,0,0,0,0,0,0,0"'
    )
    args = parser.parse_args()

    # Parse the board string into a tuple of 9 integers.
    try:
        board = tuple(int(x.strip()) for x in args.board.split(','))
        if len(board) != 9:
            raise ValueError("Board must have exactly 9 values.")
    except Exception as e:
        print(f"Error parsing board argument: {e}")
        return

    return best_move(board)

if __name__ == '__main__':
    main()