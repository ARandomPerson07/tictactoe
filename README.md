## Project Statement
The project aims to graph the entirety of possible board states of tic-tac-toe into a single directed graph, and visualize the result using a suitable medium. Given sufficient time, it will also produce an AI trained on this graph to perfectly play tic-tac-toe.

### Rationale

Graphs are an important tool for analyzing game-states. By leveraging directed edges and representing board states as nodes, systematic analysis is possible. Tic-tac-toe is chosen here for practical reasons, but the methods are intended to be conceptual and scaleable to other examples. Other board games are the intended target of this scaling, but any situation that can be gamified and encapsulated is a candidate for this type of analysis.

Tic-tac-toe is a two-player, adversarial pen-and-paper game where two players claim squares in a 3x3 grid, and the first player to claim three in a row (horizontal, vertical, or diagonally) is declared the winner. Key factors in choosing tic-tac-toe as the subject matter include:

1. Sequential - Each game state necessarily precedes or succeeds another, except start and end states
2. Independent - The current board completely enapsulates the state of the game, with no dependency on previous states
3. Finite - Every game ends in a finite number of steps. In our case, 9 moves is the absolute maximum

These properties facilitate the encapsulation of all of tic-tac-toe in a connected, directed acyclic graph (DAG) of less than $3^9 = 19683$ nodes*. In particular, the graph is also _10-partite_ due to the finite nature. Such comprehensive encapsulation entails the possibility of equally comprehensive analysis. For example, training an AI to play perfect tic-tac-toe would be very easy with this graph.

*In fact, the final graph will have significantly less than this number of nodes because at any given time, the differences in the number of marks between player 1 and player 2 is at most 1. It is closer to $9!$ board states in general.

Of course, tic-tac-toe is a "solved" game, and it takes no more than an afternoon to master its strategies for a decently rational player. But the method scales decently well to other, much more complicated board games. Chess, famously, uses a similar graph-based structure to train its most powerful engine, Stockfish. Stockfish ["looks into the future" using a tree search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) to compute the best move at any given time, with successively increasing "depth".

### Scope
The project will create, using NumPy, Plotly-Dash, and NetworkX, a graph of all possible game states, starting from the empty board. The graph will be viewable as a Dash webpage and allow for some interaction to better visualise the problem. If time is sufficient, an AI opponent will be available to play against.

### Limitations
- In reality, most situations (and board games) can have cyclical paths, which massively increases the complexity of possible states.
- There are ultimately far too many nodes and edges to visualize at once, so the graph will likely get messy. This is alleviated somewhat by the design of the webapp.

## Overview
### Files
- `tictactoe_graph.py` contains the `get_graph()` function, which returns the `NetworkX.DiGraph` object that contains the graph of all possible tic-tac-toe board states. Simply do `from tictactoe_graph import get_graph` to use it
- `tictactoe_dash.py` starts a local web server on `http://127.0.0.1:8050/` by default. To run it, make sure you have the proper installed packages as instructed in `requirements.txt` using `pip install -r requirements.txt`, then do `python3 tictactoedash.py`
### Web Application
- Copy-paste the `http://127.0.0.1:8050/` into your browser after running the `.py` file to start the application
- Mouse wheel zooms in or out
- Click and drag to move around the graph
- Each board is represented as a 3x3 grid of numbers. `0` represents an empty space, while `1` and `2` represent players 1 and 2's marks, respectively
- Click on a board state to focus on it. The node will become the new root of the graph, and the webpage will only show you possible board states from that position
- Click the "back" button to view the entire graph again
- To exit, close the tab in your browser and `Ctrl-C` on the terminal you used to run `tictactoedash.py`

## Implementation

### Graph Building
For this project, boards are exclusively represented by length-9 tuples.

First we recognize that many board states of tic-tac-toe are identical. In particular, any rotation or flip of a board (totalling eight variations) is effectively the same board. Thus, we define `canonical` that unifies identical board states into a canonical form. In this case, we just take the one with the least lexicographical value. `canonical` is implemented in `tictactoe_graph.py`

Using `canonical` as well as checking that `num moves by 1 - num moves by 2 = {0,1}` generates for us all the possible board states reachable by normal play in tic-tac-toe.

Next, we define a function `generate_neighbors_of` that takes in a `board` tuple and returns the set of all possible next board states in canonical form. A move here is always defined as changing a `0` entry in the tuple to a `1` entry.

To generate the final graph, we add all the nodes to a `NetworkX.DiGraph` graph `G`. Completing the graph is then a matter of iterating over every valid board state and adding all its possible next states as children.

### Visualization
Using `Dash`, we can directly convert the `NetworkX` graph into a renderable element. The number of non-zero entries in the board state are used to determine a `level` attribute of the nodes, which determines its position in the `nx.multipartite_layout`. We also add color-coded nodes and edges for easier visualisation.

Finally, we add some callbacks to the webapp so that clicking a node shows the subgraph with it as the root, and add the back button to reset the view.

## Result
### Visualisation

### AI
