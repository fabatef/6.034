# MIT 6.034 Lab 3: Games
# Written by 6.034 staff

from game_api import *
from boards import *
from toytree import GAME1

INF = float('inf')

# Please see wiki lab page for full description of functions and API.

#### Part 1: Utility Functions #################################################

#A game is over if all columns are full, or if theirs a chain of length >=4
def is_game_over_connectfour(board):
    """Returns True if game is over, otherwise False."""
    if board.count_pieces()==0:
        return False
    else:
        columns_full = all([board.is_column_full(i) for i in range(board.num_cols)])
        longest_chain = max([len(chain) for chain in board.get_all_chains()])
        return (columns_full or longest_chain >= 4)
    
#you can move in a column as long as the game's not over and the column is not full
def next_boards_connectfour(board):
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    next_boards = []
    if is_game_over_connectfour(board):
        return next_boards
    else:
        #current_player_id = 1 if board.players[0]== board.get_player_name(1) else 2
        for c in range(board.num_cols):
            if not board.is_column_full(c):
                next_boards.append(board.add_piece(c))
        return next_boards


# a tie when the board fills up with no chains of 4, -1000 if current player is a maximizer, else 1000
def endgame_score_connectfour(board, is_current_player_maximizer):
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""

    columns_full = all([board.is_column_full(i) for i in range(board.num_cols)])
    longest_chain = max([len(chain) for chain in board.get_all_chains()])

    if (columns_full and longest_chain < 4):
        return 0
    else:
        return -1000 if is_current_player_maximizer else 1000
        
#number of pieces on the board = 42
# winner = -/+1000 -/+ (42 - current pieces on the board)
def endgame_score_connectfour_faster(board, is_current_player_maximizer):
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    score = endgame_score_connectfour(board, is_current_player_maximizer)
    time_bonus = board.num_cols*board.num_rows - board.count_pieces()
    
    if score !=0:
        score = score + time_bonus if score == 1000 else score - time_bonus
    return score

#long chains are good. the score is how well current_player's doing compared to the opponent
#a chain of length 1-> weighs 1, 2 ->10, 3->100, 4 -> 1000 (non-endgame board, so 4 won't happen)
def heuristic_connectfour(board, is_current_player_maximizer):
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    #score player 1
    score_maximizer = sum([1 if len(chain) == 1 else 10 if len(chain) == 2 else 100 \
                 for chain in board.get_all_chains(is_current_player_maximizer)])
    score_minimizer = sum([1 if len(chain) == 1 else 10 if len(chain) == 2 else 100 \
                 for chain in board.get_all_chains(not is_current_player_maximizer)])
    return score_maximizer - score_minimizer
    

# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### Part 2: Searching a Game Tree #############################################

# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.

#def build_paths(state):

    


def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""

    agenda = [[state]]
    dfs_paths = []
    static_evaluations = 0
    
    while (agenda):
        current_path = agenda.pop(0)
        last_state = current_path[-1]
        
        if last_state.is_game_over():
            end_score = last_state.get_endgame_score()
            static_evaluations += 1
            dfs_paths.append([current_path, end_score])
        else:
            extend = [current_path[:] + [next_state] for next_state in last_state.generate_next_states()]
            agenda = extend + agenda  #adding paths to the front of the agenda

    return max (dfs_paths, key = lambda entry: entry[1])+[static_evaluations]



# Uncomment the line below to try your dfs_maximizing on an
# AbstractGameState representing the games tree "GAME1" from toytree.py:

#pretty_print_dfs_type(dfs_maximizing(GAME1))


def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""
    counter = 0
    #print (maximize)
    def minimax_helper(state, maximize):
        nonlocal counter
        #if the game is over, find the score of the leaf and return the path with it as the only node
        if state.is_game_over():
            end_score = state.get_endgame_score(maximize)
            counter +=1
            return [[state], end_score]

        path, score = [], 0

        #if maximizing, find the max of the scores after minimizer has picked optimally, and vice versa
        if maximize:
            path, score = max([minimax_helper(child, not maximize) for child in state.generate_next_states()], key = lambda entry: entry[1])
        else:
            path, score = min([minimax_helper(child, not maximize) for child in state.generate_next_states()], key = lambda entry: entry[1])

        path = [state] + path
        return [path, score]

    return minimax_helper(state, maximize) + [counter]

# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

#pretty_print_dfs_type(minimax_endgame_search(GAME1, False))

##depth = 0
def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    """Performs standard minimax search. Same return type as dfs_maximizing."""
    static_evals = 0
    def help_minimax(state, heuristic_fn, depth_limit, maximize, d):
        nonlocal static_evals

        #if the depth limit has been reached or the game is over, do static evaluation on the leaf/limit
        if d == depth_limit or state.is_game_over():
            #print ('IN HERE')
            static_evals += 1
            if state.is_game_over():
                end_score = state.get_endgame_score(maximize)
                return [[state], end_score, d]
            else:
                end_score = heuristic_fn(state.get_snapshot(), maximize)
                return [[state], end_score, d]
            
        path, score = [], 0

        # d keeps track of the current state's depth, maximize does the same thing as before
        # since it's looking down at the childern, d+1 is the argument. the returned depth is
        # the level below the current state, so report depth - 1 when recursion is complete.
        if maximize:
            path, score, depth = max([help_minimax(child, heuristic_fn, depth_limit, not maximize, d+1) \
                               for child in state.generate_next_states()],key = lambda entry: entry[1])
        else:
            #print (state.is_game_over())
            path, score, depth = min([help_minimax(child, heuristic_fn, depth_limit, not maximize, d+1)\
                               for child in state.generate_next_states()], key = lambda entry: entry[1])

        path = [state] + path
        return [path, score, depth-1]
    
    return help_minimax(state, heuristic_fn, depth_limit, maximize, 0)[0:2] + [static_evals]
        
        


# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1. Try increasing the value of depth_limit to see what happens:

#pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    """"Performs minimax with alpha-beta pruning. Same return type 
    as dfs_maximizing."""

    static_evals = 0
    def help_alphabeta(state, alpha, beta, heuristic_fn, depth_limit, maximize, d):
        nonlocal static_evals

        #if the depth limit has been reached or the game is over, do static evaluation on the leaf/limit
        if d == depth_limit or state.is_game_over():
            #print ('IN HERE')
            static_evals += 1
            if state.is_game_over():
                end_score = state.get_endgame_score(maximize)
                return [[state], end_score, d]
            else:
                end_score = heuristic_fn(state.get_snapshot(), maximize)
                return [[state], end_score, d]

        if maximize:
            best_path = []
            for child in state.generate_next_states():
                path, score, depth = help_alphabeta(child, alpha, beta, heuristic_fn, depth_limit,not maximize, d+1)
                if score > alpha:
                    best_path = path
                    alpha = score
                    
                if alpha >= beta:
                    break

            path = [state] + best_path
            return [path, alpha, depth-1]
 
        else:
            best_path = []
            for child in state.generate_next_states():
                path, score, depth = help_alphabeta(child, alpha, beta, heuristic_fn, depth_limit, not maximize, d+1)
                if score < beta:
                    best_path = path
                    beta = score  
                if alpha >= beta:
                    break

            path = [state] + best_path
            return [path, beta, depth-1]
    
    return help_alphabeta(state, alpha, beta, heuristic_fn, depth_limit, maximize, 0)[0:2] + [static_evals]
    


# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4. Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

#pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    #print (depth_limit)

    output = AnytimeValue()
    for d in range(1,depth_limit+1):
        output.set_value(minimax_search_alphabeta(state,-INF, INF, heuristic_fn, d, maximize))
        
    return output


# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4. Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

# progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


# Progressive deepening is NOT optional. However, you may find that 
#  the tests for progressive deepening take a long time. If you would
#  like to temporarily bypass them, set this variable False. You will,
#  of course, need to set this back to True to pass all of the local
#  and online tests.
TEST_PROGRESSIVE_DEEPENING = True
if not TEST_PROGRESSIVE_DEEPENING:
    def not_implemented(*args): raise NotImplementedError
    progressive_deepening = not_implemented


#### Part 3: Multiple Choice ###################################################

ANSWER_1 = '4'

ANSWER_2 = '1'

ANSWER_3 = '4'

ANSWER_4 = '5'


#### SURVEY ###################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 12
WHAT_I_FOUND_INTERESTING = "Writing the minimax functions. It was frustrating to debug but rewarding in the end"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = "The feedback when tests fail is vague. A more detailed feedback would be better."
