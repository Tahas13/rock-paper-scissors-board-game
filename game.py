import pygame
import sys
import random
import time
import os
import math
from typing import List, Tuple, Dict, Optional
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Get the screen info for maximizing
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w - 100
SCREEN_HEIGHT = screen_info.current_h - 100

# Constants
BOARD_SIZE = 6
CELL_SIZE_BASE = 70  # Base size that will be scaled
BOARD_MARGIN = 50
FPS = 60
TURN_TIME = 15  # 15 seconds per turn

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
HIGHLIGHT = (255, 255, 0, 100)  # Semi-transparent yellow
VALID_MOVE = (0, 255, 0, 100)   # Semi-transparent green
TIMER_WARNING = (255, 50, 50)   # Red for timer warning

# Menu colors
MENU_BG_TOP = (25, 10, 80)      # Dark purple
MENU_BG_BOTTOM = (45, 20, 100)  # Slightly lighter purple
BUTTON_COLOR = (70, 90, 180)    # Blue-purple
BUTTON_HOVER = (90, 110, 210)   # Lighter blue-purple
BUTTON_BORDER = (120, 140, 255) # Light blue-purple

# Player colors
PLAYER_COLORS = [
    (220, 20, 60),    # Player 1: Crimson
    (30, 144, 255),   # Player 2: Dodger Blue
    (50, 205, 50)     # Player 3: Lime Green
]

# Sound effects paths - these would be replaced with actual file paths
SOUND_FILES = {
    'select': 'select.wav',
    'move': 'move.wav',
    'combat_rock': 'combat_rock.wav',
    'combat_paper': 'combat_paper.wav',
    'combat_scissors': 'combat_scissors.wav',
    'win': 'win.wav',
    'lose': 'lose.wav',
    'timer_tick': 'timer_tick.wav',
    'menu_click': 'menu_click.wav',
    'game_start': 'game_start.wav',
    'background': 'background_music.wav'
}

#------------------------------------------------------------------------------
# Game Classes
#------------------------------------------------------------------------------

class Piece:
    """Represents a game piece (Rock, Paper, or Scissors)"""
    def __init__(self, piece_type: str, player_id: int):
        """
        Initialize a game piece
        
        Args:
            piece_type: 'R' for Rock, 'P' for Paper, 'S' for Scissors
            player_id: ID of the player who owns this piece
        """
        self.type = piece_type
        self.player_id = player_id
    
    def __str__(self) -> str:
        """String representation of the piece with player ID"""
        return f"{self.type}{self.player_id}"

class Board:
    """Represents the game board"""
    def __init__(self, size: int = 6):
        """
        Initialize the game board
        
        Args:
            size: Size of the board (default 6x6)
        """
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
    
    def place_piece(self, row: int, col: int, piece: Piece) -> bool:
        """
        Place a piece on the board
        
        Args:
            row: Row index
            col: Column index
            piece: Piece to place
            
        Returns:
            bool: True if placement was successful, False otherwise
        """
        if 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] is None:
            self.grid[row][col] = piece
            return True
        return False
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> Tuple[bool, Optional[Piece], str]:
        """
        Move a piece on the board and handle combat if necessary
        
        Args:
            from_row: Starting row
            from_col: Starting column
            to_row: Destination row
            to_col: Destination column
            
        Returns:
            Tuple[bool, Optional[Piece], str]: (Success, Captured piece if any, Combat type)
        """
        # Check if move is valid
        if not (0 <= from_row < self.size and 0 <= from_col < self.size and 
                0 <= to_row < self.size and 0 <= to_col < self.size):
            return False, None, ""
        
        # Check if source has a piece
        if self.grid[from_row][from_col] is None:
            return False, None, ""
        
        # Check if move is only one step in any direction
        if abs(to_row - from_row) + abs(to_col - from_col) != 1:
            return False, None, ""
        
        moving_piece = self.grid[from_row][from_col]
        target_piece = self.grid[to_row][to_col]
        combat_type = ""
        
        # If target cell is empty, just move
        if target_piece is None:
            self.grid[to_row][to_col] = moving_piece
            self.grid[from_row][from_col] = None
            return True, None, ""
        
        # If target cell has a piece from the same player, invalid move
        if target_piece.player_id == moving_piece.player_id:
            return False, None, ""
        
        # Combat resolution based on RPS rules
        result = self.resolve_combat(moving_piece, target_piece)
        
        # Determine combat type for sound effects
        if moving_piece.type == 'R' or target_piece.type == 'R':
            combat_type = "combat_rock"
        elif moving_piece.type == 'P' or target_piece.type == 'P':
            combat_type = "combat_paper"
        elif moving_piece.type == 'S' or target_piece.type == 'S':
            combat_type = "combat_scissors"
        
        if result == 1:  # Moving piece wins
            self.grid[to_row][to_col] = moving_piece
            self.grid[from_row][from_col] = None
            return True, target_piece, combat_type
        elif result == -1:  # Target piece wins
            self.grid[from_row][from_col] = None
            return True, moving_piece, combat_type
        else:  # Draw
            self.grid[from_row][from_col] = None
            self.grid[to_row][to_col] = None
            return True, moving_piece, combat_type  # Both pieces are removed
    
    def resolve_combat(self, piece1: Piece, piece2: Piece) -> int:
        """
        Resolve combat between two pieces based on RPS rules
        
        Args:
            piece1: First piece
            piece2: Second piece
            
        Returns:
            int: 1 if piece1 wins, -1 if piece2 wins, 0 if draw
        """
        if piece1.type == piece2.type:
            return 0  # Draw
        
        if (piece1.type == 'R' and piece2.type == 'S') or \
           (piece1.type == 'P' and piece2.type == 'R') or \
           (piece1.type == 'S' and piece2.type == 'P'):
            return 1  # piece1 wins
        
        return -1  # piece2 wins
    
    def get_player_pieces(self, player_id: int) -> List[Tuple[int, int, Piece]]:
        """
        Get all pieces belonging to a player
        
        Args:
            player_id: ID of the player
            
        Returns:
            List[Tuple[int, int, Piece]]: List of (row, col, piece) tuples
        """
        pieces = []
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] is not None and self.grid[row][col].player_id == player_id:
                    pieces.append((row, col, self.grid[row][col]))
        return pieces

class Player:
    """Represents a player in the game"""
    def __init__(self, player_id: int, name: str, piece_types: List[str], piece_count: int = 4):
        """
        Initialize a player
        
        Args:
            player_id: Unique ID for the player
            name: Player's name
            piece_types: List of piece types the player can use
            piece_count: Number of pieces per type
        """
        self.id = player_id
        self.name = name
        self.piece_types = piece_types
        self.piece_count = piece_count
        self.pieces = []
        
        # Initialize pieces
        for piece_type in piece_types:
            for _ in range(piece_count):
                self.pieces.append(Piece(piece_type, player_id))
    
    def get_random_piece(self) -> Optional[Piece]:
        """Get a random piece from the player's available pieces"""
        if not self.pieces:
            return None
        
        piece_index = random.randint(0, len(self.pieces) - 1)
        piece = self.pieces[piece_index]
        self.pieces.pop(piece_index)
        return piece

class Game:
    """Main game logic class"""
    def __init__(self, num_players: int = 2):
        """
        Initialize the game
        
        Args:
            num_players: Number of players (2 or 3)
        """
        if num_players not in [2, 3]:
            raise ValueError("Number of players must be 2 or 3")
        
        self.board = Board()
        self.num_players = num_players
        self.players = []
        self.current_player_index = 0
        self.game_over = False
        self.winner = None
        self.turn_timer = TURN_TIME
        
        # Initialize players
        piece_types = ['R', 'P', 'S']
        for i in range(num_players):
            self.players.append(Player(i + 1, f"Player {i + 1}", piece_types))
    
    def setup_board(self) -> None:
        """Set up the board with randomized starting positions"""
        # Define starting areas for each player
        starting_areas = [
            [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), 
             (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5)],  # Player 1 (top)
            [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), 
             (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)],  # Player 2 (bottom)
        ]
        
        if self.num_players == 3:
            # Adjust starting areas for 3 players
            starting_areas = [
                [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)],  # Player 1 (top-left)
                [(0, 4), (0, 5), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)],  # Player 2 (right)
                [(4, 0), (4, 1), (4, 2), (4, 3), (5, 0), (5, 1), (5, 2), (5, 3)],  # Player 3 (bottom-left)
            ]
        
        # Place pieces randomly in each player's starting area
        for player_id, player in enumerate(self.players, 1):
            area = starting_areas[player_id - 1].copy()
            random.shuffle(area)
            
            # Place 4 of each piece type (R, P, S)
            for _ in range(4 * 3):  # 4 pieces of each of the 3 types
                if not area:
                    break
                
                piece = player.get_random_piece()
                if piece is None:
                    continue
                
                row, col = area.pop()
                self.board.place_piece(row, col, piece)
    
    def next_turn(self) -> None:
        """Move to the next player's turn"""
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        self.turn_timer = TURN_TIME  # Reset timer for new player
        
        # Skip players with no pieces
        while not self.board.get_player_pieces(self.players[self.current_player_index].id) and not self.check_game_over():
            self.current_player_index = (self.current_player_index + 1) % self.num_players
    
    def check_game_over(self) -> bool:
        """
        Check if the game is over
        
        Returns:
            bool: True if game is over, False otherwise
        """
        active_players = 0
        last_active_player = None
        
        for player in self.players:
            pieces = self.board.get_player_pieces(player.id)
            if pieces:
                active_players += 1
                last_active_player = player
        
        if active_players <= 1:
            self.game_over = True
            self.winner = last_active_player
            return True
        
        return False
    
    def get_valid_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get valid moves for a piece at the given position
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            List[Tuple[int, int]]: List of valid (row, col) destinations
        """
        valid_moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if 0 <= new_row < self.board.size and 0 <= new_col < self.board.size:
                # If empty or enemy piece, it's a valid move
                if self.board.grid[new_row][new_col] is None or \
                   self.board.grid[new_row][new_col].player_id != self.board.grid[row][col].player_id:
                    valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def play_turn(self, from_row: int, from_col: int, to_row: int, to_col: int) -> Tuple[bool, str]:
        """
        Play a turn by moving a piece
        
        Args:
            from_row: Starting row
            from_col: Starting column
            to_row: Destination row
            to_col: Destination column
            
        Returns:
            Tuple[bool, str]: (Success, Combat type for sound)
        """
        current_player = self.players[self.current_player_index]
        
        # Check if the piece belongs to the current player
        if self.board.grid[from_row][from_col] is None or \
           self.board.grid[from_row][from_col].player_id != current_player.id:
            return False, ""
        
        # Try to move the piece
        success, captured, combat_type = self.board.move_piece(from_row, from_col, to_row, to_col)
        
        if success:
            self.next_turn()
            return True, combat_type
        
        return False, ""
    
    def update_timer(self, dt: float) -> bool:
        """
        Update the turn timer
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            bool: True if timer expired, False otherwise
        """
        self.turn_timer -= dt
        
        if self.turn_timer <= 0:
            self.next_turn()
            return True
        
        return False

#------------------------------------------------------------------------------
# AI Classes
#------------------------------------------------------------------------------

class AIPlayer:
    """Base class for all AI players"""
    def __init__(self, game, difficulty="medium"):
        self.game = game
        self.difficulty = difficulty
        self.thinking_time = 0.5  # Default thinking time in seconds
    
    def choose_move(self):
        """Choose a move based on the current game state"""
        # Base implementation - should be overridden by subclasses
        pass
    
    def get_valid_pieces_with_moves(self, player_id):
        """Get all pieces with valid moves for a player"""
        valid_pieces = []
        pieces = self.game.board.get_player_pieces(player_id)
        
        for row, col, piece in pieces:
            valid_moves = self.game.get_valid_moves(row, col)
            if valid_moves:
                valid_pieces.append((row, col, piece, valid_moves))
        
        return valid_pieces

class RandomAI(AIPlayer):
    """Easy difficulty AI - makes completely random moves"""
    def __init__(self, game):
        super().__init__(game, "easy")
        self.thinking_time = 0.3  # Faster decisions for easy AI
    
    def choose_move(self):
        """Choose a completely random move"""
        current_player = self.game.players[self.game.current_player_index]
        valid_pieces = self.get_valid_pieces_with_moves(current_player.id)
        
        if not valid_pieces:
            return None, None, None, None
        
        # Select a random piece and a random valid move
        row, col, piece, valid_moves = random.choice(valid_pieces)
        to_row, to_col = random.choice(valid_moves)
        
        return row, col, to_row, to_col

class BasicAI(AIPlayer):
    """Medium difficulty AI - uses basic rules and priorities"""
    def __init__(self, game):
        super().__init__(game, "medium")
        self.thinking_time = 0.5
    
    def choose_move(self):
        """Choose a move using basic rules"""
        current_player = self.game.players[self.game.current_player_index]
        valid_pieces = self.get_valid_pieces_with_moves(current_player.id)
        
        if not valid_pieces:
            return None, None, None, None
        
        # Shuffle to add some randomness
        random.shuffle(valid_pieces)
        
        # For each piece, categorize its moves
        for row, col, piece, valid_moves in valid_pieces:
            capturing_moves = []
            safe_moves = []
            risky_moves = []
            
            for to_row, to_col in valid_moves:
                target = self.game.board.grid[to_row][to_col]
                
                if target is None:
                    # Empty cell - safe move
                    safe_moves.append((to_row, to_col))
                else:
                    # Combat will happen - evaluate outcome
                    result = self.game.board.resolve_combat(piece, target)
                    if result == 1:  # We win
                        capturing_moves.append((to_row, to_col))
                    elif result == -1:  # We lose
                        risky_moves.append((to_row, to_col))
                    # Draw is also risky, so add to risky_moves
                    else:
                        risky_moves.append((to_row, to_col))
            
            # Choose the best move for this piece based on priority
            if capturing_moves:
                return row, col, *random.choice(capturing_moves)
            elif safe_moves:
                return row, col, *random.choice(safe_moves)
            elif risky_moves and random.random() < 0.2:  # 20% chance to make a risky move
                return row, col, *random.choice(risky_moves)
        
        # If we get here, just pick a random move
        row, col, piece, valid_moves = random.choice(valid_pieces)
        to_row, to_col = random.choice(valid_moves)
        return row, col, to_row, to_col

class AdvancedAI(AIPlayer):
    """Hard difficulty AI - uses advanced evaluation and limited look-ahead"""
    def __init__(self, game):
        super().__init__(game, "hard")
        self.thinking_time = 0.8
    
    def choose_move(self):
        """Choose a move using advanced evaluation"""
        current_player = self.game.players[self.game.current_player_index]
        valid_pieces = self.get_valid_pieces_with_moves(current_player.id)
        
        if not valid_pieces:
            return None, None, None, None
        
        best_score = float('-inf')
        best_move = None
        
        # Evaluate each possible move
        for row, col, piece, valid_moves in valid_pieces:
            for to_row, to_col in valid_moves:
                # Simulate the move
                score = self.evaluate_move(row, col, to_row, to_col, current_player.id)
                
                # Keep track of the best move
                if score > best_score:
                    best_score = score
                    best_move = (row, col, to_row, to_col)
        
        if best_move:
            return best_move
        
        # Fallback to random move if no good move found
        row, col, piece, valid_moves = random.choice(valid_pieces)
        to_row, to_col = random.choice(valid_moves)
        return row, col, to_row, to_col
    
    def evaluate_move(self, from_row, from_col, to_row, to_col, player_id):
        """Evaluate a potential move"""
        # Get the current state
        board = self.game.board
        moving_piece = board.grid[from_row][from_col]
        target_piece = board.grid[to_row][to_col]
        
        # Base score
        score = 0
        
        # Evaluate combat outcome if applicable
        if target_piece is not None:
            result = board.resolve_combat(moving_piece, target_piece)
            if result == 1:  # We win
                score += 10  # Capturing an opponent's piece is good
            elif result == -1:  # We lose
                score -= 15  # Losing our piece is bad
            else:  # Draw
                score -= 5  # Draws are slightly negative as we lose a piece
        
        # Evaluate position
        # Center control is valuable
        center_value = 4 - (abs(to_row - 2.5) + abs(to_col - 2.5))
        score += center_value
        
        # Evaluate piece type distribution after move
        my_pieces = board.get_player_pieces(player_id)
        type_counts = {'R': 0, 'P': 0, 'S': 0}
        
        for r, c, p in my_pieces:
            if r == from_row and c == from_col:
                continue  # Skip the piece that's moving
            type_counts[p.type] += 1
        
        # Add the moving piece in its new position
        type_counts[moving_piece.type] += 1
        
        # Penalize imbalanced distribution
        min_count = min(type_counts.values())
        score += min_count * 2  # Reward having all types
        
        # Look for threats and opportunities
        score += self.evaluate_threats_and_opportunities(to_row, to_col, moving_piece, player_id)
        
        return score
    
    def evaluate_threats_and_opportunities(self, row, col, piece, player_id):
        """Evaluate threats and opportunities from a position"""
        score = 0
        board = self.game.board
        
        # Check adjacent cells
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if 0 <= new_row < board.size and 0 <= new_col < board.size:
                target = board.grid[new_row][new_col]
                
                if target is not None and target.player_id != player_id:
                    # There's an opponent piece adjacent
                    result = board.resolve_combat(piece, target)
                    if result == 1:  # We can capture it next turn
                        score += 3
                    elif result == -1:  # It can capture us next turn
                        score -= 5
        
        return score

class MinimaxAI(AIPlayer):
    """Expert difficulty AI - uses minimax with alpha-beta pruning"""
    def __init__(self, game):
        super().__init__(game, "expert")
        self.thinking_time = 1.2
        self.max_depth = 2  # Maximum search depth
    
    def choose_move(self):
        """Choose a move using minimax algorithm"""
        current_player = self.game.players[self.game.current_player_index]
        valid_pieces = self.get_valid_pieces_with_moves(current_player.id)
        
        if not valid_pieces:
            return None, None, None, None
        
        best_score = float('-inf')
        best_move = None
        
        # Use minimax to evaluate each possible move
        for row, col, piece, valid_moves in valid_pieces:
            for to_row, to_col in valid_moves:
                # Create a copy of the board for simulation
                board_copy = self.copy_board()
                
                # Simulate the move
                self.make_move_on_copy(board_copy, row, col, to_row, to_col)
                
                # Evaluate using minimax
                score = self.minimax(board_copy, self.max_depth - 1, False, 
                                    current_player.id, float('-inf'), float('inf'))
                
                # Keep track of the best move
                if score > best_score:
                    best_score = score
                    best_move = (row, col, to_row, to_col)
        
        if best_move:
            return best_move
        
        # Fallback to random move if no good move found
        row, col, piece, valid_moves = random.choice(valid_pieces)
        to_row, to_col = random.choice(valid_moves)
        return row, col, to_row, to_col
    
    def copy_board(self):
        """Create a copy of the current board state"""
        # This is a simplified copy that just tracks piece positions
        # A full implementation would copy the entire game state
        board_copy = []
        for row in range(self.game.board.size):
            board_row = []
            for col in range(self.game.board.size):
                piece = self.game.board.grid[row][col]
                if piece:
                    board_row.append((piece.type, piece.player_id))
                else:
                    board_row.append(None)
            board_copy.append(board_row)
        return board_copy
    
    def make_move_on_copy(self, board_copy, from_row, from_col, to_row, to_col):
        """Make a move on the copied board"""
        moving_piece = board_copy[from_row][from_col]
        target_piece = board_copy[to_row][to_col]
        
        if target_piece is None:
            # Simple move to empty space
            board_copy[to_row][to_col] = moving_piece
            board_copy[from_row][from_col] = None
        else:
            # Combat resolution
            piece_type, player_id = moving_piece
            target_type, target_player_id = target_piece
            
            # Determine combat outcome
            if piece_type == target_type:
                # Draw - both pieces removed
                board_copy[from_row][from_col] = None
                board_copy[to_row][to_col] = None
            elif ((piece_type == 'R' and target_type == 'S') or
                  (piece_type == 'P' and target_type == 'R') or
                  (piece_type == 'S' and target_type == 'P')):
                # Moving piece wins
                board_copy[to_row][to_col] = moving_piece
                board_copy[from_row][from_col] = None
            else:
                # Target piece wins
                board_copy[from_row][from_col] = None
    
    def minimax(self, board, depth, is_maximizing, player_id, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        # Base case: reached max depth or game over
        if depth == 0:
            return self.evaluate_board(board, player_id)
        
        # Get next player
        next_player_index = (self.game.current_player_index + (0 if is_maximizing else 1)) % len(self.game.players)
        next_player_id = self.game.players[next_player_index].id
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_possible_moves(board, player_id):
                from_row, from_col, to_row, to_col = move
                
                # Create a copy and make the move
                board_copy = [row[:] for row in board]
                self.make_move_on_copy(board_copy, from_row, from_col, to_row, to_col)
                
                # Recursive evaluation
                eval = self.minimax(board_copy, depth - 1, False, player_id, alpha, beta)
                max_eval = max(max_eval, eval)
                
                # Alpha-beta pruning
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_possible_moves(board, next_player_id):
                from_row, from_col, to_row, to_col = move
                
                # Create a copy and make the move
                board_copy = [row[:] for row in board]
                self.make_move_on_copy(board_copy, from_row, from_col, to_row, to_col)
                
                # Recursive evaluation
                eval = self.minimax(board_copy, depth - 1, True, player_id, alpha, beta)
                min_eval = min(min_eval, eval)
                
                # Alpha-beta pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                
            return min_eval
    
    def get_possible_moves(self, board, player_id):
        """Get all possible moves for a player on the given board"""
        moves = []
        for row in range(len(board)):
            for col in range(len(board[row])):
                piece = board[row][col]
                if piece and piece[1] == player_id:
                    # This is the player's piece, find valid moves
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_row, new_col = row + dr, col + dc
                        
                        if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                            target = board[new_row][new_col]
                            
                            # Valid move if empty or enemy piece
                            if target is None or target[1] != player_id:
                                moves.append((row, col, new_row, new_col))
        
        return moves
    
    def evaluate_board(self, board, player_id):
        """Evaluate the board position for a player"""
        score = 0
        
        # Count pieces and their types
        my_pieces = {'R': 0, 'P': 0, 'S': 0}
        opponent_pieces = {}
        
        for row in board:
            for piece in row:
                if piece:
                    piece_type, pid = piece
                    if pid == player_id:
                        my_pieces[piece_type] += 1
                    else:
                        if pid not in opponent_pieces:
                            opponent_pieces[pid] = {'R': 0, 'P': 0, 'S': 0}
                        opponent_pieces[pid][piece_type] += 1
        
        # Material advantage
        my_total = sum(my_pieces.values())
        opponent_total = sum(sum(p.values()) for p in opponent_pieces.values())
        score += (my_total - opponent_total) * 10
        
        # Type balance
        min_type_count = min(my_pieces.values())
        score += min_type_count * 5
        
        # Position evaluation - control of center
        center_positions = [(2, 2), (2, 3), (3, 2), (3, 3)]
        for r, c in center_positions:
            if 0 <= r < len(board) and 0 <= c < len(board[0]):
                piece = board[r][c]
                if piece and piece[1] == player_id:
                    score += 3
        
        # Strategic positioning - evaluate matchups against opponent pieces
        for row_idx, row in enumerate(board):
            for col_idx, piece in enumerate(row):
                if piece and piece[1] == player_id:
                    piece_type = piece[0]
                    
                    # Check adjacent cells for favorable matchups
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_row, new_col = row_idx + dr, col_idx + dc
                        
                        if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                            target = board[new_row][new_col]
                            
                            if target and target[1] != player_id:
                                target_type = target[0]
                                
                                # Evaluate matchup
                                if ((piece_type == 'R' and target_type == 'S') or
                                    (piece_type == 'P' and target_type == 'R') or
                                    (piece_type == 'S' and target_type == 'P')):
                                    # Favorable matchup
                                    score += 2
                                elif ((piece_type == 'R' and target_type == 'P') or
                                      (piece_type == 'P' and target_type == 'S') or
                                      (piece_type == 'S' and target_type == 'R')):
                                    # Unfavorable matchup
                                    score -= 2
        
        return score

#------------------------------------------------------------------------------
# Sound Manager
#------------------------------------------------------------------------------

class SoundManager:
    """Manages game sound effects and music"""
    def __init__(self):
        """Initialize the sound manager"""
        # Initialize mixer if not already initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except:
                print("Warning: Sound system could not be initialized. Game will run without sound.")
                self.sound_enabled = False
                return
        
        self.sound_enabled = True
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        """Load all sound effects"""
        if not self.sound_enabled:
            return
            
        # Try to load sound files if they exist, otherwise create dummy sounds
        for sound_name, file_name in SOUND_FILES.items():
            try:
                # Check if the file exists
                if os.path.exists(file_name):
                    self.sounds[sound_name] = mixer.Sound(file_name)
                else:
                    # Create a dummy sound (1ms of silence)
                    self.create_dummy_sound(sound_name)
            except Exception as e:
                print(f"Could not load sound '{sound_name}': {e}")
                # Create a dummy sound on error
                self.create_dummy_sound(sound_name)
    
    def create_dummy_sound(self, sound_name):
        """Create a dummy sound (silent)"""
        try:
            # Create a very short silent sound (8 bit, mono, 22050 Hz)
            buffer = bytearray(22050 // 1000)  # 1ms of silence
            dummy_sound = pygame.mixer.Sound(buffer=buffer)
            self.sounds[sound_name] = dummy_sound
        except:
            # If even this fails, just mark the sound as None
            self.sounds[sound_name] = None
            print(f"Warning: Could not create dummy sound for '{sound_name}'")
        
    def play(self, sound_name):
        """Play a sound effect"""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                self.sounds[sound_name].play()
            except:
                # Silently fail if playing doesn't work
                pass
            
    def play_background_music(self):
        """Play background music on loop"""
        if not self.sound_enabled:
            return
            
        if 'background' in self.sounds and self.sounds['background'] is not None:
            try:
                self.sounds['background'].play(-1)  # -1 means loop indefinitely
            except:
                # Silently fail if playing doesn't work
                pass
            
    def stop_background_music(self):
        """Stop background music"""
        if not self.sound_enabled:
            return
            
        if 'background' in self.sounds and self.sounds['background'] is not None:
            try:
                self.sounds['background'].stop()
            except:
                # Silently fail if stopping doesn't work
                pass

#------------------------------------------------------------------------------
# Game GUI
#------------------------------------------------------------------------------

class GameGUI:
    """Main game GUI class"""
    def __init__(self):
        """Initialize the game GUI"""
        # Set up the display with resizable flag
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Rock-Paper-Scissors Board Game")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.load_fonts()
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Game state
        self.game = None
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = "menu"  # menu, game, game_over
        self.animation_timer = 0
        self.combat_animation = None
        self.ai_mode = False
        self.ai_vs_ai = False
        self.ai_difficulty = "medium"  # Default difficulty
        self.ai_player = None
        self.last_time = time.time()
        
        # Load background images
        self.background_img = self.create_background()
        self.logo_img = self.create_logo()
        
        # Calculate cell size based on screen dimensions
        self.update_cell_size()
        
        # Load images
        self.images = {}
        self.update_piece_images()
        
        # Animation variables
        self.animations = []
        self.menu_animation_time = 0
        
        # Start background music
        self.sound_manager.play_background_music()
        
    def load_fonts(self):
        """Load fonts for the game"""
        try:
            # Try to use nicer fonts if available
            self.font = pygame.font.SysFont("Arial", 18)
            self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
            self.button_font = pygame.font.SysFont("Arial", 24)
        except:
            # Fallback to default font if custom font fails
            self.font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 24)
    
    def update_cell_size(self):
        """Update cell size based on screen dimensions"""
        # Calculate the maximum cell size that will fit on the screen
        max_width = (self.screen.get_width() - 2 * BOARD_MARGIN) // BOARD_SIZE
        max_height = (self.screen.get_height() - 2 * BOARD_MARGIN) // BOARD_SIZE
        self.cell_size = min(max_width, max_height)
    
    def create_background(self):
        """Create a background image with stars"""
        # Create a gradient background from dark blue to purple
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            # Create a gradient from dark blue to purple
            progress = y / SCREEN_HEIGHT
            r = int(MENU_BG_TOP[0] + progress * (MENU_BG_BOTTOM[0] - MENU_BG_TOP[0]))
            g = int(MENU_BG_TOP[1] + progress * (MENU_BG_BOTTOM[1] - MENU_BG_TOP[1]))
            b = int(MENU_BG_TOP[2] + progress * (MENU_BG_BOTTOM[2] - MENU_BG_TOP[2]))
            color = (r, g, b)
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
    
        # Add stars (small white dots)
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            radius = random.randint(1, 2)
            brightness = random.randint(180, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(background, color, (x, y), radius)
    
        return background
    
    def create_logo(self):
        """Create a game logo matching the design"""
        logo_size = 200
        logo = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
    
        # Draw a circular gray background
        pygame.draw.circle(logo, (180, 180, 190, 220), (logo_size//2, logo_size//2), logo_size//2)
    
        # Draw the three symbols in white
        center = (logo_size//2, logo_size//2)
    
        # Rock (triangle at top)
        rock_points = [
            (center[0], center[1] - 40),  # Top
            (center[0] - 30, center[1] + 20),  # Bottom left
            (center[0] + 30, center[1] + 20)   # Bottom right
        ]
        pygame.draw.polygon(logo, (255, 255, 255), rock_points, 2)
    
        # Paper (square at bottom left)
        paper_rect = pygame.Rect(center[0] - 50, center[1] - 10, 30, 30)
        pygame.draw.rect(logo, (255, 255, 255), paper_rect)
    
        # Scissors (X at bottom right)
        scissors_center = (center[0] + 30, center[1])
        pygame.draw.line(logo, (255, 255, 255), 
                        (scissors_center[0] - 15, scissors_center[1] - 15),
                        (scissors_center[0] + 15, scissors_center[1] + 15), 2)
        pygame.draw.line(logo, (255, 255, 255), 
                        (scissors_center[0] - 15, scissors_center[1] + 15),
                        (scissors_center[0] + 15, scissors_center[1] - 15), 2)
    
        return logo
    
    def update_piece_images(self):
        """Update piece images based on cell size"""
        # Create piece images for each player
        for piece_type in ['R', 'P', 'S']:
            for player_id in range(1, 4):  # Support up to 3 players
                self.images[f"{piece_type}{player_id}"] = self.create_piece_image(piece_type, player_id)
    
    def create_piece_image(self, piece_type, player_id):
        """Create a surface with the piece image"""
        # Get player color
        player_color = PLAYER_COLORS[player_id - 1]
        
        # Create a base surface for the piece
        size = self.cell_size - 10
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw the piece based on type and player
        if piece_type == 'R':  # Rock
            # Draw a rock shape (triangle) with player color
            points = [
                (size//2, size//5),  # Top
                (size//5, 4*size//5),  # Bottom left
                (4*size//5, 4*size//5)  # Bottom right
            ]
            pygame.draw.polygon(surface, player_color, points)
            pygame.draw.polygon(surface, BLACK, points, 2)  # Border
            
        elif piece_type == 'P':  # Paper
            # Draw a paper shape (square) with player color
            paper_rect = pygame.Rect(size//5, size//5, 3*size//5, 3*size//5)
            pygame.draw.rect(surface, player_color, paper_rect)
            pygame.draw.rect(surface, BLACK, paper_rect, 2)  # Border
            
            # Add some lines to represent paper
            line_color = BLACK
            pygame.draw.line(surface, line_color, (size//4, size//2), (3*size//4, size//2), 1)
            pygame.draw.line(surface, line_color, (size//4, 2*size//3), (3*size//4, 2*size//3), 1)
            
        elif piece_type == 'S':  # Scissors
            # Draw scissors (X shape) with player color
            center = (size//2, size//2)
            length = size//3
            
            # Draw the X
            pygame.draw.line(surface, player_color, 
                            (center[0] - length, center[1] - length),
                            (center[0] + length, center[1] + length), 5)
            pygame.draw.line(surface, player_color, 
                            (center[0] - length, center[1] + length),
                            (center[0] + length, center[1] - length), 5)
            
            # Draw border
            pygame.draw.line(surface, BLACK, 
                            (center[0] - length, center[1] - length),
                            (center[0] + length, center[1] + length), 1)
            pygame.draw.line(surface, BLACK, 
                            (center[0] - length, center[1] + length),
                            (center[0] + length, center[1] - length), 1)
        
        # Add text label
        text = self.font.render(piece_type, True, BLACK)
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        # Add a circular background
        circle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (*player_color, 100), (size//2, size//2), size//2)
        
        # Combine surfaces
        final_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        final_surface.blit(circle_surface, (0, 0))
        final_surface.blit(surface, (0, 0))
        
        return final_surface
    
    def draw_board(self):
        """Draw the game board with improved visuals"""
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        board_x = (self.screen.get_width() - board_width) // 2
        board_y = (self.screen.get_height() - board_height) // 2
        
        # Draw board background with a slight gradient
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                cell_rect = pygame.Rect(
                    board_x + x * self.cell_size,
                    board_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Checkerboard pattern
                if (x + y) % 2 == 0:
                    cell_color = (220, 220, 220)  # Light gray
                else:
                    cell_color = (200, 200, 200)  # Slightly darker gray
                    
                pygame.draw.rect(self.screen, cell_color, cell_rect)
    
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen, 
                DARK_GRAY, 
                (board_x + i * self.cell_size, board_y), 
                (board_x + i * self.cell_size, board_y + board_height),
                2 if i == 0 or i == BOARD_SIZE else 1
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen, 
                DARK_GRAY, 
                (board_x, board_y + i * self.cell_size), 
                (board_x + board_width, board_y + i * self.cell_size),
                2 if i == 0 or i == BOARD_SIZE else 1
            )
    
        # Draw coordinates with better styling
        for i in range(BOARD_SIZE):
            # Row numbers
            row_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(row_bg, (50, 50, 80, 180), (10, 10), 10)
            self.screen.blit(row_bg, (board_x - 25, board_y + i * self.cell_size + self.cell_size // 2 - 10))
            
            row_text = self.font.render(str(i), True, WHITE)
            row_text_rect = row_text.get_rect(center=(board_x - 15, board_y + i * self.cell_size + self.cell_size // 2))
            self.screen.blit(row_text, row_text_rect)
            
            # Column numbers
            col_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(col_bg, (50, 50, 80, 180), (10, 10), 10)
            self.screen.blit(col_bg, (board_x + i * self.cell_size + self.cell_size // 2 - 10, board_y - 25))
            
            col_text = self.font.render(str(i), True, WHITE)
            col_text_rect = col_text.get_rect(center=(board_x + i * self.cell_size + self.cell_size // 2, board_y - 15))
            self.screen.blit(col_text, col_text_rect)
    
        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.game.board.grid[row][col]
                if piece is not None:
                    self.draw_piece(row, col, piece)
    
        # Highlight selected piece with a glowing effect
        if self.selected_piece:
            row, col = self.selected_piece
            
            # Draw multiple circles with decreasing opacity for glow effect
            for radius in range(10, 0, -2):
                glow_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                alpha = 100 - radius * 8
                pygame.draw.rect(
                    glow_surface, 
                    (255, 255, 0, alpha), 
                    (0, 0, self.cell_size, self.cell_size),
                    border_radius=radius
                )
                self.screen.blit(
                    glow_surface, 
                    (board_x + col * self.cell_size, board_y + row * self.cell_size)
                )
    
        # Highlight valid moves with a pulsing effect
        for row, col in self.valid_moves:
            # Calculate pulse effect based on time
            pulse = (math.sin(time.time() * 5) + 1) / 2  # Value between 0 and 1
            alpha = int(100 + pulse * 100)  # Alpha between 100 and 200
            
            move_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.rect(
                move_surface, 
                (0, 255, 0, alpha), 
                (0, 0, self.cell_size, self.cell_size),
                border_radius=5
            )
            self.screen.blit(
                move_surface, 
                (board_x + col * self.cell_size, board_y + row * self.cell_size)
            )
    
    def draw_piece(self, row, col, piece):
        """Draw a piece on the board"""
        board_x = (self.screen.get_width() - BOARD_SIZE * self.cell_size) // 2
        board_y = (self.screen.get_height() - BOARD_SIZE * self.cell_size) // 2
        
        # Get the piece image
        piece_img = self.images[f"{piece.type}{piece.player_id}"]
        
        # Draw the piece on the board
        self.screen.blit(
            piece_img, 
            (
                board_x + col * self.cell_size + 5, 
                board_y + row * self.cell_size + 5
            )
        )
    
    def draw_timer(self):
        """Draw the turn timer"""
        if not self.game:
            return
            
        # Get current player color
        current_player = self.game.players[self.game.current_player_index]
        player_color = PLAYER_COLORS[current_player.id - 1]
        
        # Calculate timer position
        timer_width = 200
        timer_height = 20
        timer_x = (self.screen.get_width() - timer_width) // 2
        timer_y = 10
        
        # Draw timer background
        pygame.draw.rect(self.screen, DARK_GRAY, (timer_x, timer_y, timer_width, timer_height), border_radius=10)
        
        # Calculate remaining time percentage
        time_percent = max(0, min(1, self.game.turn_timer / TURN_TIME))
        
        # Choose color based on remaining time
        if time_percent < 0.3:
            timer_color = TIMER_WARNING
        else:
            timer_color = player_color
        
        # Draw timer bar with rounded corners
        if time_percent > 0:
            inner_rect = pygame.Rect(timer_x, timer_y, int(timer_width * time_percent), timer_height)
            pygame.draw.rect(self.screen, timer_color, inner_rect, border_radius=10)
        
        # Draw timer text
        timer_text = self.font.render(f"{int(self.game.turn_timer)}s", True, WHITE)
        timer_text_rect = timer_text.get_rect(center=(timer_x + timer_width // 2, timer_y + timer_height // 2))
        self.screen.blit(timer_text, timer_text_rect)
        
        # Play tick sound when timer is low
        if 0 < self.game.turn_timer <= 5 and int(self.game.turn_timer) != int(self.game.turn_timer + 0.1):
            self.sound_manager.play('timer_tick')
    
    def draw_game_info(self):
        """Draw game information"""
        # Create a semi-transparent panel for game info
        info_panel = pygame.Surface((300, 200), pygame.SRCALPHA)
        pygame.draw.rect(info_panel, (0, 0, 50, 150), (0, 0, 300, 200), border_radius=10)
        self.screen.blit(info_panel, (20, 20))
        
        # Draw current player
        current_player = self.game.players[self.game.current_player_index]
        player_color = PLAYER_COLORS[current_player.id - 1]
        
        # Create a highlight for current player
        player_highlight = pygame.Surface((280, 30), pygame.SRCALPHA)
        pygame.draw.rect(player_highlight, (*player_color, 100), (0, 0, 280, 30), border_radius=5)
        self.screen.blit(player_highlight, (30, 30))
        
        player_text = self.font.render(f"Current Turn: {current_player.name}", True, WHITE)
        self.screen.blit(player_text, (40, 35))
        
        # Draw piece counts for each player
        y_offset = 70
        for player in self.game.players:
            pieces = self.game.board.get_player_pieces(player.id)
            piece_counts = {'R': 0, 'P': 0, 'S': 0}
            
            for _, _, piece in pieces:
                piece_counts[piece.type] += 1
            
            total = sum(piece_counts.values())
            player_color = PLAYER_COLORS[player.id - 1]
            
            # Create a colored background for each player's info
            player_bg = pygame.Surface((280, 25), pygame.SRCALPHA)
            pygame.draw.rect(player_bg, (*player_color, 50), (0, 0, 280, 25), border_radius=5)
            self.screen.blit(player_bg, (30, y_offset))
            
            player_text = self.font.render(
                f"{player.name}: {total} pieces (R: {piece_counts['R']}, P: {piece_counts['P']}, S: {piece_counts['S']})", 
                True, 
                WHITE
            )
            self.screen.blit(player_text, (40, y_offset + 5))
            y_offset += 30
        
        # Display AI difficulty if in AI mode
        if self.ai_mode and not self.ai_vs_ai:
            difficulty_text = self.font.render(f"AI Difficulty: {self.ai_difficulty.capitalize()}", True, WHITE)
            self.screen.blit(difficulty_text, (40, y_offset + 5))
            y_offset += 30
        elif self.ai_vs_ai:
            ai_text = self.font.render("AI vs AI Game", True, WHITE)
            self.screen.blit(ai_text, (40, y_offset + 5))
            y_offset += 30
        
        # Draw game instructions
        instructions_panel = pygame.Surface((300, 100), pygame.SRCALPHA)
        pygame.draw.rect(instructions_panel, (0, 0, 50, 150), (0, 0, 300, 100), border_radius=10)
        self.screen.blit(instructions_panel, (20, self.screen.get_height() - 120))
        
        instructions = [
            "Click on your piece to select it",
            "Click on a highlighted cell to move",
            "Press ESC to return to menu"
        ]
        
        y_offset = self.screen.get_height() - 110
        for instruction in instructions:
            text = self.font.render(instruction, True, WHITE)
            self.screen.blit(text, (40, y_offset))
            y_offset += 25
    
    def draw_menu(self):
        """Draw the main menu with improved UI"""
        # Draw background
        self.screen.blit(self.background_img, (0, 0))
        
        # Update menu animation time
        self.menu_animation_time += 0.01
        
        # Draw animated stars (twinkling effect)
        for _ in range(5):
            x = random.randint(0, self.screen.get_width())
            y = random.randint(0, self.screen.get_height())
            size = random.randint(1, 3)
            brightness = int(200 + 55 * math.sin(self.menu_animation_time * 5))
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (x, y), size)
        
        # Draw logo with subtle animation
        logo_scale = 1.0 + 0.03 * math.sin(self.menu_animation_time)
        scaled_logo = pygame.transform.smoothscale(
            self.logo_img, 
            (int(self.logo_img.get_width() * logo_scale), 
             int(self.logo_img.get_height() * logo_scale))
        )
        logo_rect = scaled_logo.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(scaled_logo, logo_rect)
        
        # Draw title with shadow effect
        title_shadow = self.title_font.render("Rock-Paper-Scissors Board Game", True, (0, 0, 0))
        title = self.title_font.render("Rock-Paper-Scissors Board Game", True, WHITE)
        
        # Add a subtle animation
        title_y = 280 + math.sin(self.menu_animation_time * 3) * 5
        title_shadow_rect = title_shadow.get_rect(center=(self.screen.get_width() // 2 + 3, title_y + 3))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, title_y))
        
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
    
        # Draw menu options as buttons
        options = [
            "Play Game (2 Players)",
            "Play Game (3 Players)",
            "Play vs AI (Easy)",
            "Play vs AI (Medium)",
            "Play vs AI (Hard)",
            "Play vs AI (Expert)",
            "Watch AI Game",
            "Quit"
        ]
    
        button_width = 400
        button_height = 50
        button_margin = 20
        y_offset = 340
    
        for i, option in enumerate(options):
            # Button background
            button_rect = pygame.Rect(
                (self.screen.get_width() - button_width) // 2,
                y_offset,
                button_width,
                button_height
            )
        
            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            hover = button_rect.collidepoint(mouse_pos)
        
            # Create a gradient button color (purple/blue)
            if hover:
                button_color = BUTTON_HOVER
                # Add a glow effect when hovering
                glow_surface = pygame.Surface((button_width + 10, button_height + 10), pygame.SRCALPHA)
                for r in range(5, 0, -1):
                    alpha = 50 - r * 8
                    pygame.draw.rect(glow_surface, (*BUTTON_BORDER, alpha), 
                                    (5-r, 5-r, button_width+r*2, button_height+r*2), 
                                    border_radius=15)
                self.screen.blit(glow_surface, 
                                (button_rect.x - 5, button_rect.y - 5))
            else:
                button_color = BUTTON_COLOR
        
            # Draw button with rounded corners
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, BUTTON_BORDER, button_rect, 2, border_radius=10)
        
            # Draw button text
            text = self.button_font.render(option, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            
            # Add a subtle bounce animation to the text when hovering
            if hover:
                text_rect.y += int(math.sin(self.menu_animation_time * 10) * 2)
                
            self.screen.blit(text, text_rect)
        
            y_offset += button_height + button_margin
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Create a panel for game over info
        panel_width = 500
        panel_height = 300
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (40, 40, 100, 200), (0, 0, panel_width, panel_height), border_radius=20)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Draw game over message with glow effect
        for r in range(5, 0, -1):
            alpha = 100 - r * 15
            game_over_shadow = self.title_font.render("Game Over", True, (200, 200, 255, alpha))
            shadow_rect = game_over_shadow.get_rect(center=(panel_x + panel_width // 2 + r, panel_y + 70 + r))
            self.screen.blit(game_over_shadow, shadow_rect)
            
        game_over = self.title_font.render("Game Over", True, WHITE)
        game_over_rect = game_over.get_rect(center=(panel_x + panel_width // 2, panel_y + 70))
        self.screen.blit(game_over, game_over_rect)
        
        # Draw winner message with animation
        if self.game.winner:
            winner_color = PLAYER_COLORS[self.game.winner.id - 1]
            
            # Create animated background for winner
            winner_bg = pygame.Surface((400, 60), pygame.SRCALPHA)
            pulse = (math.sin(time.time() * 3) + 1) / 2  # Value between 0 and 1
            bg_alpha = int(100 + pulse * 100)
            pygame.draw.rect(winner_bg, (*winner_color, bg_alpha), (0, 0, 400, 60), border_radius=10)
            self.screen.blit(winner_bg, (panel_x + 50, panel_y + 120))
            
            winner_text = self.button_font.render(f"{self.game.winner.name} wins!", True, WHITE)
            winner_rect = winner_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
            self.screen.blit(winner_text, winner_rect)
            
            # Play win sound if not already played
            self.sound_manager.play('win')
        else:
            draw_text = self.button_font.render("It's a draw!", True, WHITE)
            draw_rect = draw_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
            self.screen.blit(draw_text, draw_rect)
        
        # Draw instructions
        instructions = self.button_font.render("Press SPACE to return to menu", True, WHITE)
        instructions_rect = instructions.get_rect(center=(panel_x + panel_width // 2, panel_y + 220))
        self.screen.blit(instructions, instructions_rect)
    
    def handle_board_click(self, mouse_pos):
        """Handle clicks on the board"""
        board_x = (self.screen.get_width() - BOARD_SIZE * self.cell_size) // 2
        board_y = (self.screen.get_height() - BOARD_SIZE * self.cell_size) // 2
        
        # Check if click is within board boundaries
        if not (board_x <= mouse_pos[0] <= board_x + BOARD_SIZE * self.cell_size and
                board_y <= mouse_pos[1] <= board_y + BOARD_SIZE * self.cell_size):
            return
        
        # Convert mouse position to board coordinates
        col = (mouse_pos[0] - board_x) // self.cell_size
        row = (mouse_pos[1] - board_y) // self.cell_size
        
        # If no piece is selected, try to select one
        if self.selected_piece is None:
            piece = self.game.board.grid[row][col]
            current_player = self.game.players[self.game.current_player_index]
            
            if piece is not None and piece.player_id == current_player.id:
                self.selected_piece = (row, col)
                self.valid_moves = self.game.get_valid_moves(row, col)
                self.sound_manager.play('select')
        
        # If a piece is already selected, try to move it
        else:
            selected_row, selected_col = self.selected_piece
            
            # Check if the clicked cell is a valid move
            if (row, col) in self.valid_moves:
                # Try to move the piece
                success, combat_type = self.game.play_turn(selected_row, selected_col, row, col)
                
                if success:
                    # Play appropriate sound
                    if combat_type:
                        self.sound_manager.play(combat_type)
                    else:
                        self.sound_manager.play('move')
                    
                    # Check if game is over
                    self.game.check_game_over()
                    if self.game.game_over:
                        self.game_state = "game_over"
            
            # Reset selection
            self.selected_piece = None
            self.valid_moves = []
    
    def handle_menu_click(self, mouse_pos):
        """Handle clicks on the menu"""
        button_width = 400
        button_height = 50
        button_margin = 20
        y_offset = 340
        
        for i in range(8):  # 8 menu options now
            button_rect = pygame.Rect(
                (self.screen.get_width() - button_width) // 2,
                y_offset,
                button_width,
                button_height
            )
            
            if button_rect.collidepoint(mouse_pos):
                self.sound_manager.play('menu_click')
                
                if i == 0:  # Play Game (2 Players)
                    self.start_game(2)
                elif i == 1:  # Play Game (3 Players)
                    self.start_game(3)
                elif i == 2:  # Play vs AI (Easy)
                    self.start_game(2, ai_mode=True)
                    self.ai_difficulty = "easy"
                    self.ai_player = None  # Will be created when needed
                elif i == 3:  # Play vs AI (Medium)
                    self.start_game(2, ai_mode=True)
                    self.ai_difficulty = "medium"
                    self.ai_player = None
                elif i == 4:  # Play vs AI (Hard)
                    self.start_game(2, ai_mode=True)
                    self.ai_difficulty = "hard"
                    self.ai_player = None
                elif i == 5:  # Play vs AI (Expert)
                    self.start_game(2, ai_mode=True)
                    self.ai_difficulty = "expert"
                    self.ai_player = None
                elif i == 6:  # Watch AI Game
                    self.start_ai_vs_ai_game()
                elif i == 7:  # Quit
                    pygame.quit()
                    sys.exit()
                
                break
            
            y_offset += button_height + button_margin
    
    def create_ai_player(self, difficulty="medium"):
        """Create an AI player with the specified difficulty"""
        if difficulty == "easy":
            return RandomAI(self.game)
        elif difficulty == "medium":
            return BasicAI(self.game)
        elif difficulty == "hard":
            return AdvancedAI(self.game)
        elif difficulty == "expert":
            return MinimaxAI(self.game)
        else:
            # Default to medium
            return BasicAI(self.game)
    
    def play_ai_turn(self):
        """Play a turn for AI player"""
        if not hasattr(self, 'ai_player') or self.ai_player is None:
            self.ai_player = self.create_ai_player(self.ai_difficulty)
        
        # Let the AI choose a move
        from_row, from_col, to_row, to_col = self.ai_player.choose_move()
        
        if from_row is None:  # No valid moves
            self.game.next_turn()
            return
        
        # Highlight the selected piece and move for visual feedback
        self.selected_piece = (from_row, from_col)
        self.valid_moves = [(to_row, to_col)]
        
        # Draw to show the selection
        self.draw()
        pygame.display.flip()
        time.sleep(self.ai_player.thinking_time)  # Pause to show the AI "thinking"
        
        # Make the move
        success, combat_type = self.game.play_turn(from_row, from_col, to_row, to_col)
        
        # Play appropriate sound
        if combat_type:
            self.sound_manager.play(combat_type)
        else:
            self.sound_manager.play('move')
        
        # Reset selection
        self.selected_piece = None
        self.valid_moves = []
        
        # Check if game is over
        self.game.check_game_over()
        if self.game.game_over:
            self.game_state = "game_over"
    
    def start_ai_vs_ai_game(self):
        """Start a game with AI players only"""
        self.start_game(2, ai_mode=True)
        self.ai_vs_ai = True
        
        # Create two different AI players
        self.ai_players = {
            1: self.create_ai_player("hard"),
            2: self.create_ai_player("medium")
        }
    
    def start_game(self, num_players, ai_mode=False):
        """Start a new game"""
        self.game = Game(num_players)
        self.game.setup_board()
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = "game"
        self.ai_mode = ai_mode
        self.ai_vs_ai = False
        self.ai_player = None
        self.sound_manager.play('game_start')
    
    def handle_resize(self, new_size):
        """Handle window resize event"""
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.update_cell_size()
        self.update_piece_images()
        
        # Recreate background to match new size
        self.background_img = self.create_background()
    
    def draw(self):
        """Draw the current game state with improved visuals"""
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "game":
            # Draw a gradient background for the game
            for y in range(self.screen.get_height()):
                # Create a gradient from dark blue to slightly lighter blue
                progress = y / self.screen.get_height()
                r = int(20 + progress * 20)
                g = int(20 + progress * 20)
                b = int(50 + progress * 30)
                color = (r, g, b)
                pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y))
        
            # Add some stars to the background
            for _ in range(30):
                x = random.randint(0, self.screen.get_width())
                y = random.randint(0, self.screen.get_height())
                radius = random.randint(1, 2)
                brightness = random.randint(150, 200)
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (x, y), radius)
        
            self.draw_board()
            self.draw_game_info()
            self.draw_timer()
        elif self.game_state == "game_over":
            # Draw the game state behind the overlay
            for y in range(self.screen.get_height()):
                # Create a gradient from dark blue to slightly lighter blue
                progress = y / self.screen.get_height()
                r = int(20 + progress * 20)
                g = int(20 + progress * 20)
                b = int(50 + progress * 30)
                color = (r, g, b)
                pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y))
        
            self.draw_board()
            self.draw_game_info()
            self.draw_game_over()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Calculate time delta
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize((event.w, event.h))
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "game":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                    
                    elif self.game_state == "game_over":
                        if event.key == pygame.K_SPACE:
                            self.game_state = "menu"
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if self.game_state == "menu":
                        self.handle_menu_click(event.pos)
                    elif self.game_state == "game":
                        # In AI mode, only allow clicks when it's the human player's turn (Player 1)
                        if not self.ai_mode or (self.ai_mode and self.game.players[self.game.current_player_index].id == 1):
                            self.handle_board_click(event.pos)
            
            # Update game state
            if self.game_state == "game":
                # Update timer
                if self.game and not self.game.game_over:
                    if self.game.update_timer(dt) and not self.ai_mode:
                        # Timer expired, play sound
                        self.sound_manager.play('lose')
                
                # AI turn logic
                if self.ai_mode and not self.game.game_over:
                    current_player_id = self.game.players[self.game.current_player_index].id
                    
                    if self.ai_vs_ai:
                        # AI vs AI mode - both players are AI
                        self.ai_player = self.ai_players[current_player_id]
                        self.play_ai_turn()
                    elif current_player_id == 2:  # Assuming player 2 is AI
                        self.play_ai_turn()
            
            # Draw everything
            self.draw()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            pygame.time.Clock().tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game"""
    game_gui = GameGUI()
    game_gui.run()

if __name__ == "__main__":
    main()
