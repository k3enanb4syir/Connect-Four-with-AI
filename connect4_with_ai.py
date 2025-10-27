import numpy as np
import random
import pygame
import sys
import math

# --- Constants ---

# Colors (RGB)
BLUE = (0,0,255)
GREEN = (0, 255, 0)     
BLACK = (0,0,0)
BLACK = (0,0,0) # Note: This is defined twice
RED = (255,0,0)
YELLOW = (255,255,0)

# Piece-specific colors for 3D-like effect
RED_LIGHT = (255, 80, 80)   
RED_DARK = (180, 0, 0)    
YELLOW_LIGHT = (255, 255, 150)
YELLOW_DARK = (200, 200, 0) 

# Board dimensions
ROW_COUNT = 6
COLUMN_COUNT = 7

# Hole-specific colors for 3D effect (unused in current draw_board)
HOLE_SHADOW = (20, 20, 20)     
HOLE_HIGHLIGHT = (80, 80, 80)

# Player turn identifiers
PLAYER = 0
AI = 1

# Piece identifiers for the board matrix
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

# Length of a winning line
WINDOW_LENGTH = 4

# --- Core Game Logic Functions ---

def create_board():
	"""Creates a new 6x7 Connect Four board, initialized with zeros."""
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	"""Places a player's piece at the specified row and column."""
	board[row][col] = piece

def is_valid_location(board, col):
	"""Checks if a piece can be dropped in the given column."""
	# A column is valid if its top-most cell (ROW_COUNT-1) is empty (0)
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	"""Finds the lowest available row in a given column."""
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	"""Prints the board to the console, flipped vertically for correct orientation."""
	# np.flip(board, 0) flips the 2D array along the x-axis (axis 0)
	print(np.flip(board, 0))

def winning_move(board, piece):
	"""Checks the board for any 4-in-a-row winning condition for the given piece."""
	
	# Check horizontal locations for win
	# Iterate through all possible starting positions for a horizontal win
	for c in range(COLUMN_COUNT-3): # -3 because a 4-piece window needs 3 extra spots
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	# Iterate through all possible starting positions for a vertical win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3): # -3 for the same reason
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diagonals
	# A positive slope means row and column increase together
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diagonals
	# A negative slope means row decreases as column increases (or vice-versa)
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT): # Start from row 3 (0-indexed) to be able to go "down" 3 spots
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

# --- AI Logic Functions ---

def evaluate_window(window, piece):
	"""Scores a 4-piece "window" (horizontal, vertical, or diagonal) for the AI."""
	score = 0
	# Determine the opponent's piece
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	# --- Heuristic Scoring ---
	# Prioritize winning
	if window.count(piece) == 4:
		score += 100
	# Prioritize setting up a 3-in-a-row
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	# Slight preference for 2-in-a-row
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	# Penalize the opponent for having 3-in-a-row (blocking)
	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4 # This is a crucial blocking move

	return score

def score_position(board, piece):
	"""Calculates the total score for the entire board, based on the AI's piece."""
	score = 0

	## Score center column
	# The center column is strategically important
	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3 # Give 3 points for each piece in the center

	## Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		# Slide a 4-piece window across the row
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		# Slide a 4-piece window down the column
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINDOW_LENGTH]
			score += evaluate_window(window, piece)

	## Score positive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			# Create a window by stepping (r+i, c+i)
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	## Score negative sloped diagonal
	for r in range(ROW_COUNT-3): # This should be range(3, ROW_COUNT)
		for c in range(COLUMN_COUNT-3):
			# Create a window by stepping (r-i, c+i). 
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def is_terminal_node(board):
	"""Checks if the game has ended."""
	return winning_move(board, PLAYER_PIECE) or \
		   winning_move(board, AI_PIECE) or \
		   len(get_valid_locations(board)) == 0 # Game is a draw

def minimax(board, depth, alpha, beta, maximizingPlayer):
	"""
	Implements the Minimax algorithm with Alpha-Beta Pruning.
	- depth: How many moves ahead to look.
	- alpha: The best score found so far for the Maximizer (AI).
	- beta: The best score found so far for the Minimizer (Player).
	- maximizingPlayer: True if it's the AI's turn, False if it's the Player's.
	"""
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)

	# --- Base Cases ---
	# If we've reached the max depth or the game is over
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, 100000000000000) # AI wins (very high score)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -10000000000000) # Player wins (very low score)
			else: # Game is a draw
				return (None, 0)
		else: # Depth is zero
			# Return the heuristic score of the current board
			return (None, score_position(board, AI_PIECE))

	# --- Recursive Steps ---
	
	if maximizingPlayer: # AI's turn
		value = -math.inf # Initialize to negative infinity
		column = random.choice(valid_locations) # Pick a random move to start
		# Iterate through all possible moves
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy() # Create a temporary board
			drop_piece(b_copy, row, col, AI_PIECE)
			# Recursively call minimax for the minimizing player
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1] # [1] gets the score
			
			if new_score > value:
				value = new_score
				column = col # This is the best move found so far
			
			alpha = max(alpha, value) # Update alpha
			if alpha >= beta: # Alpha-Beta Pruning
				break # Stop searching this branch, as Minimizer will avoid it
		return column, value

	else: # Minimizing player's turn (Human)
		value = math.inf # Initialize to positive infinity
		column = random.choice(valid_locations)
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			# Recursively call minimax for the maximizing player
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			
			if new_score < value:
				value = new_score
				column = col
			
			beta = min(beta, value) # Update beta
			if alpha >= beta: # Alpha-Beta Pruning
				break # Stop searching, as Maximizer will avoid this branch
		return column, value

def get_valid_locations(board):
	"""Returns a list of all columns that are not full."""
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):
	"""A simpler (non-minimax) AI that just picks the move with the best immediate score."""
	# NOTE: This function is not used by the main AI loop, which uses minimax.
	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	# Simulate dropping a piece in each valid column
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		# Score the resulting board
		score = score_position(temp_board, piece)
		# Keep track of the best score and column
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

# --- Pygame Graphics Functions ---

def draw_board(board):
	"""Renders the game board using Pygame."""
	
	# Calculate offsets for 3D piece effect
	piece_offset = int(RADIUS * 0.15) 
	hole_offset = int(RADIUS * 0.1)   # This is defined but not used

	# --- Draw the Board Structure (Blue Rects and Green Holes) ---
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			# Draw the blue rectangle for each cell
			# (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, ...)
			# The +SQUARESIZE in Y is to leave space at the top (row 0)
			pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			
			# Calculate center of the hole
			hole_center_x = int(c*SQUARESIZE+SQUARESIZE/2)
			hole_center_y = int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)

			# Draw the "empty" hole (green circle)
			pygame.draw.circle(screen, GREEN, (hole_center_x, hole_center_y), RADIUS)
	
	# --- Draw the Player and AI Pieces ---
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			# Calculate center of the piece
			center_x = int(c*SQUARESIZE+SQUARESIZE/2)
			# Y-coordinate is flipped: height - ...
			center_y = height-int(r*SQUARESIZE+SQUARESIZE/2)

			if board[r][c] == PLAYER_PIECE:
				# Draw 3 circles to give a 3D effect
				pygame.draw.circle(screen, RED_DARK, (center_x + piece_offset, center_y + piece_offset), RADIUS)
				pygame.draw.circle(screen, RED, (center_x, center_y), RADIUS)
				pygame.draw.circle(screen, RED_LIGHT, (center_x - piece_offset, center_y - piece_offset), RADIUS)

			elif board[r][c] == AI_PIECE: 
				# Draw 3 circles for AI piece
				pygame.draw.circle(screen, YELLOW_DARK, (center_x + piece_offset, center_y + piece_offset), RADIUS)
				pygame.draw.circle(screen, YELLOW, (center_x, center_y), RADIUS)
				pygame.draw.circle(screen, YELLOW_LIGHT, (center_x - piece_offset, center_y - piece_offset), RADIUS)
			
	pygame.display.update() # Update the display after drawing

# --- Game Initialization ---

board = create_board()
print_board(board)
game_over = False

pygame.init() # Initialize Pygame

# Define screen size based on constants
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE # +1 row for the top "hover" area
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5) # Radius of pieces, with a 5px margin

# Set up the screen
screen = pygame.display.set_mode(size)
screen.fill(GREEN) # Fill background with green
draw_board(board) # Draw the initial empty board
pygame.display.update()

# Set up the font for messages
myfont = pygame.font.SysFont("arial", 60)

# Randomly choose who starts
turn = random.randint(PLAYER, AI)

# --- Main Game Loop ---

while not game_over:

	# --- Event Handling ---
	for event in pygame.event.get():
		# Handle window close
		if event.type == pygame.QUIT:
			sys.exit()

		# Handle mouse movement
		if event.type == pygame.MOUSEMOTION:
			# Clear the top "hover" row
			pygame.draw.rect(screen, GREEN, (0,0, width, SQUARESIZE)) 
			posx = event.pos[0]
			# Draw the player's piece "floating" at the top
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
			
		pygame.display.update() # Update display to show the floating piece

		# Handle mouse click
		if event.type == pygame.MOUSEBUTTONDOWN:
			# Clear the top "hover" row again
			pygame.draw.rect(screen, GREEN, (0,0, width, SQUARESIZE))
			
			# --- Player 1's Turn (Human) ---
			if turn == PLAYER:
				posx = event.pos[0]
				# Determine which column was clicked
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					# Check for win
					if winning_move(board, PLAYER_PIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						label_rect = label.get_rect()
						label_rect.center = (width / 2, SQUARESIZE / 2) 
						screen.blit(label, label_rect)
						game_over = True
					
					# Switch turns
					turn += 1
					turn = turn % 2 # (0 -> 1, 1 -> 0)

					# Update console and screen
					print_board(board)
					draw_board(board)


	# --- Player 2's Turn (AI) ---
	if turn == AI and not game_over:				

		# Call the minimax function to get the best column
		# Depth 5 means it looks 5 moves ahead
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			# Optional: add a slight delay to simulate "thinking"
			# pygame.time.wait(500) 
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)

			# Check for win
			if winning_move(board, AI_PIECE):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				label_rect = label.get_rect()
				label_rect.center = (width / 2, SQUARESIZE / 2)
				screen.blit(label, label_rect)
				game_over = True
			
			# Update console and screen
			print_board(board)
			draw_board(board)

			# Switch turns
			turn += 1
			turn = turn % 2

	# If the game is over, wait 3 seconds before closing
	if game_over:
		pygame.time.wait(3000)
