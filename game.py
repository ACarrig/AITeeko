import random
import copy
import math

class TeekoPlayer:
    # An object representation for an AI game player for the game Teeko.

    board = [[' ' for j in range(5)] for i in range(5)]
    pieces = ['b', 'r']

    """ Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
    """
    def __init__(self):
        # basically give yourself and opponent color randomly (will be either b or r, then opposite for opponent)
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]
        

    """ 
        Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.
    """
    def make_move(self, state):

        # Count the # of pieces on the board to see if we are in the drop phase
        count = 0
        for i in range(5):
            for j in range(5):
                if state[i][j] != ' ':
                    count += 1

        if count < 8:
            drop_phase = True
        else:
            drop_phase = False
        
        # Normal Game State: choose a piece to move and remove it from the board
        #     Determine the best successor state
        #     Compare best successor state to current board
        #       best_succ should have a blank where current board has a piece, and vice versa
        #     Figure out the move needed to get to the best_succ state from current board
        #       Have move consist of two tuples: <To> --> <From>
        if not drop_phase:
            move = []
            best_succ = self.max_value(state, 0)
            for i in range(5):
                for j in range(5):
                    if state[i][j] != ' ' and best_succ[i][j] == ' ': # moving a piece from i,j
                        move.append((i, j))
                    if best_succ[i][j] != ' ' and state[i][j] == ' ': # moving a piece to i,j
                        move.insert(0, (i, j))
            return move
        # endif

        # Drop Phase
        #     Determine the best successor state
        #     Look over the board and compare to best successor state
        #     If a piece is in best_succ and not current board, add it to cur board 
        #       because that will be the ideal move
        #     Add the coords of that move to a tuple, add tuple to moves[]
        move = []
        # If board has < '2' pieces, play randomly else, normally
        (row, col) = (random.randint(1, 3), random.randint(1, 3))
        if count < 2:
            while not state[row][col] == ' ':
                (row, col) = (random.randint(1, 3), random.randint(1, 3))
        else:
            best_succ = self.max_value(state, 0)
            for i in range(5):
                for j in range(5):
                    if state[i][j] != best_succ[i][j]:
                        #print(state)
                        #print(best_succ)
                        (row, col) = (i, j)

        # ensure the destination (row,col) tuple is at the beginning of the move list
        move.insert(0, (row, col))
        return move


    def max_value(self, state, depth):
        if depth > 3:
            return self.heuristic_game_value(state)

        # check if terminal state
        game_value_value = self.game_value(state)
        if game_value_value != 0:
            return game_value_value
        else:
            succ_list = self.succ(state)
            succ_to_return = state
            alpha = -10
            for successor in succ_list:
                # Want to choose biggest min val
                min_val_of_succs = self.min_value(successor, depth+1)
                if min_val_of_succs > alpha:
                    alpha = min_val_of_succs
                    succ_to_return = successor

            return succ_to_return


    def min_value(self, state, depth):
        if depth > 3:
            return self.heuristic_game_value(state)

        # check if terminal state
        game_value_value = self.game_value(state)
        if game_value_value != 0:
            return game_value_value
        else:
            succ_list = self.succ(state)
            beta = 10
            for successor in succ_list:
                # Want to choose smallest max val
                max_val_of_succs = self.max_value(successor, depth+1)
                if isinstance(max_val_of_succs, list):
                    max_val_of_succs = self.heuristic_game_value(max_val_of_succs)
                if max_val_of_succs < beta:
                    beta = max_val_of_succs

            return beta
        

    '''
    Evaluate non-terminal states
    '''
    def heuristic_game_value(self, state):
        # Call game_value function to see if this is a win/lose state
        result = self.game_value(state)
        if result != 0:
            return result
        
        my_piece_locations = []
        enemy_piece_locations = []

        # Step 1) calculate some 'distance' or value of the piece layout for each color red and black 
        #     to determine how well off they are in the current board
        
        # Add a tuple of the coordinates of the piece to the appropriate list
        for i in range(5):
            for j in range(5):
                if state[i][j] != ' ':
                    if state[i][j] == self.my_piece:
                        my_piece_locations.append((i, j))
                    else:
                        enemy_piece_locations.append((i, j))

        my_dist = 0
        enemy_dist = 0

        # Heuristic #1
        # Now that we know where every piece is, calculate the distance from each piece to every other piece
        for i in range(len(my_piece_locations)):
            cur_piece = my_piece_locations[i]
            for piece in my_piece_locations:
                if piece[0] == cur_piece[0] and piece[1] == cur_piece[1]:
                    continue
                x_gap = abs(cur_piece[0] - piece[0])
                y_gap = abs(cur_piece[1] - piece[1])
                my_dist += math.sqrt((x_gap ** 2) + (y_gap ** 2))

        for i in range(len(enemy_piece_locations)):
            cur_piece = enemy_piece_locations[i]
            for piece in enemy_piece_locations:
                if piece[0] == cur_piece[0] and piece[1] == cur_piece[1]:
                    continue
                x_gap = abs(cur_piece[0] - piece[0])
                y_gap = abs(cur_piece[1] - piece[1])
                enemy_dist += math.sqrt((x_gap ** 2) + (y_gap ** 2))

        # if enemy_dist is 0, returned succ_val will always end up being 0 due to how my_dist is normalized
        # to counteract this, set enemy_dist to be dist between the enemy and the piece we are going to place
        if enemy_dist == 0:
            x_gap = abs(my_piece_locations[len(my_piece_locations) - 1][0] - enemy_piece_locations[0][0])
            y_gap = abs(my_piece_locations[len(my_piece_locations) - 1][1] - enemy_piece_locations[0][1])
            enemy_dist += math.sqrt((x_gap ** 2) + (y_gap ** 2))
        
        # Step 2) Normalize these values so we return something representative of the board between -1 and 1
        #     Get % of total distance, ie my_pieces_dist makes up 30% of the total distance between all pieces
        #          and set my_dist to be fraction of total_dist
        #     Multiply these fractions by 2, then have 1 subtract them -> this will lead to big distances ending up negative (bad)
        
        dist_sum = my_dist + enemy_dist
        my_dist = (my_dist / dist_sum) * 2

        # Boards where my_dist is < enemy_dist should return a positive (favorable) value, others negative
        return 1 - my_dist
        

    '''
    Takes in a board state and returns a list of the legal successors. 
    During the drop phase, this simply means adding a new piece of the current player's type to the board; 
    During continued gameplay, this means moving any one of the current player's pieces to an unoccupied
    location on the board, adjacent to that piece.
    '''
    def succ(self, state):
        succ_list = []
        count = 0
        for i in range(5):
            for j in range(5):
                if state[i][j] != ' ':
                    count += 1

        if count < 8:
            drop_phase = True
        else:
            drop_phase = False
        
        if drop_phase:
            # Loop over board, if there is a blank spot, we can drop player's piece there
            for i in range(5):
                for j in range(5):
                    if state[i][j] == ' ':
                        state_copy = copy.deepcopy(state)
                        state_copy[i][j] = self.my_piece
                        succ_list.append(state_copy)
        else:
            # Loop over board, check if each spot is our player's piece or not (r or b)
            # For each of player's pieces (self.my_piece == state[i][j] being true)
            #     Check if we can move that piece up, down, left, right, and all 4 of the diagonals
            for i in range(5):
                for j in range(5):
                    if state[i][j] != ' ' and state[i][j] == self.my_piece:
                        # up
                        if j != 0 and state[i][j-1] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i][j-1] = state[i][j] # update spot to move piece to in state_copy
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)
                        
                        # down
                        if j != 4 and state[i][j+1] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i][j+1] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)

                        # left
                        if i != 0 and state[i-1][j] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i-1][j] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)
                        
                        # right
                        if i != 4 and state[i+1][j] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i+1][j] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)
                        
                        # up-left
                        if j != 0 and i != 0 and state[i-1][j-1] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i-1][j-1] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)

                        # up-right
                        if j != 0 and i != 4 and state[i+1][j-1] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i+1][j-1] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)

                        # down-left
                        if j != 4 and i != 0 and state[i-1][j+1] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i-1][j+1] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)
                        
                        # down-right
                        if j != 4 and i != 4 and state[i+1][j+1] == ' ':
                            state_copy = copy.deepcopy(state)
                            state_copy[i+1][j+1] = state[i][j]
                            state_copy[i][j] = ' '
                            succ_list.append(state_copy)
        
        return succ_list
    

    """ Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner
    """
    def game_value(self, state):
        
        # check horizontal wins
        for row in state:
            for i in range(2):
                if row[i] != ' ' and row[i] == row[i+1] == row[i+2] == row[i+3]:
                    return 1 if row[i]==self.my_piece else -1
        
        # check vertical wins
        for col in range(5):
            for i in range(2):
                if state[i][col] != ' ' and state[i][col] == state[i+1][col] == state[i+2][col] == state[i+3][col]:
                    return 1 if state[i][col]==self.my_piece else -1

        # check \ diagonal wins
        for i in range(2):
            for j in range(2):
                if state[i][j] != ' ' and state[i][j] == state[i+1][j+1] == state[i+2][j+2] == state[i+3][j+3]:
                    return 1 if state[i][j]==self.my_piece else -1
        
        # check / diagonal wins
        for i in range(3, 4):
            for j in range(2):
                if state[i][j] != ' ' and state[i][j] == state[i-1][j+1] == state[i-2][j+2] == state[i-3][j+3]:
                    return 1 if state[i][j]==self.my_piece else -1
        
        # check box wins
        for i in range(4):
            for j in range(4):
                if state[i][j] != ' ' and state[i][j] == state[i+1][j] == state[i][j+1] == state[i+1][j+1]:
                    return 1 if state[i][j]==self.my_piece else -1

        return 0 # no winner yet
        

    """ 
    Validates the opponent's next move against the internal board representation.
    """
    def opponent_move(self, move):
        
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)


    """ 
    Modifies the board representation using the specified move and piece
    """
    def place_piece(self, move, piece):
        
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    
    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")


############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################

def main():
    print('Hello, this is Samaritan')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()