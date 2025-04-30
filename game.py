import pygame
import sys
import random
import time
from typing import List, Tuple, Dict, Optional

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_SIZE = 6
CELL_SIZE = 70
BOARD_MARGIN = 50
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
HIGHLIGHT = (255, 255, 0, 100)  # Semi-transparent yellow
VALID_MOVE = (0, 255, 0, 100)   # Semi-transparent green

# Player colors
PLAYER_COLORS = [
    (220, 20, 60),    # Player 1: Crimson
    (30, 144, 255),   # Player 2: Dodger Blue
    (50, 205, 50)     # Player 3: Lime Green
]

class Piece:
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
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> Tuple[bool, Optional[Piece]]:
        """
        Move a piece on the board and handle combat if necessary
        
        Args:
            from_row: Starting row
            from_col: Starting column
            to_row: Destination row
            to_col: Destination column
            
        Returns:
            Tuple[bool, Optional[Piece]]: (Success, Captured piece if any)
        """
        # Check if move is valid
        if not (0 <= from_row < self.size and 0 <= from_col < self.size and 
                0 <= to_row < self.size and 0 <= to_col < self.size):
            return False, None
        
        # Check if source has a piece
        if self.grid[from_row][from_col] is None:
            return False, None
        
        # Check if move is only one step in any direction
        if abs(to_row - from_row) + abs(to_col - from_col) != 1:
            return False, None
        
        moving_piece = self.grid[from_row][from_col]
        target_piece = self.grid[to_row][to_col]
        
        # If target cell is empty, just move
        if target_piece is None:
            self.grid[to_row][to_col] = moving_piece
            self.grid[from_row][from_col] = None
            return True, None
        
        # If target cell has a piece from the same player, invalid move
        if target_piece.player_id == moving_piece.player_id:
            return False, None
        
        # Combat resolution based on RPS rules
        result = self.resolve_combat(moving_piece, target_piece)
        
        if result == 1:  # Moving piece wins
            self.grid[to_row][to_col] = moving_piece
            self.grid[from_row][from_col] = None
            return True, target_piece
        elif result == -1:  # Target piece wins
            self.grid[from_row][from_col] = None
            return True, moving_piece
        else:  # Draw
            self.grid[from_row][from_col] = None
            self.grid[to_row][to_col] = None
            return True, moving_piece  # Both pieces are removed
    
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
    
    def play_turn(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """
        Play a turn by moving a piece
        
        Args:
            from_row: Starting row
            from_col: Starting column
            to_row: Destination row
            to_col: Destination column
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        current_player = self.players[self.current_player_index]
        
        # Check if the piece belongs to the current player
        if self.board.grid[from_row][from_col] is None or \
           self.board.grid[from_row][from_col].player_id != current_player.id:
            return False
        
        # Try to move the piece
        success, captured = self.board.move_piece(from_row, from_col, to_row, to_col)
        
        if success:
            self.next_turn()
            return True
        
        return False

class GameGUI:
    def __init__(self):
        """Initialize the game GUI"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rock-Paper-Scissors Board Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)
        
        # Game state
        self.game = None
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = "menu"  # menu, game, game_over
        self.animation_timer = 0
        self.combat_animation = None
        
        # Load images
        self.images = {
            'R': self.create_piece_image('R', 'rock'),
            'P': self.create_piece_image('P', 'paper'),
            'S': self.create_piece_image('S', 'scissors')
        }
    
    def create_piece_image(self, piece_type, name):
        """Create a surface with the piece image"""
        # Create a base circle for the piece
        size = CELL_SIZE - 10
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw the piece based on type
        if piece_type == 'R':  # Rock
            pygame.draw.circle(surface, (150, 150, 150), (size//2, size//2), size//2)
            pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//2, 2)
        elif piece_type == 'P':  # Paper
            pygame.draw.rect(surface, (250, 250, 250), (5, 5, size-10, size-10))
            pygame.draw.rect(surface, (200, 200, 200), (5, 5, size-10, size-10), 2)
            # Add some lines to represent paper
            pygame.draw.line(surface, (200, 200, 200), (10, size//3), (size-10, size//3), 1)
            pygame.draw.line(surface, (200, 200, 200), (10, 2*size//3), (size-10, 2*size//3), 1)
        elif piece_type == 'S':  # Scissors
            # Draw scissors handle
            pygame.draw.circle(surface, (200, 200, 200), (size//4, size//2), size//6)
            pygame.draw.circle(surface, (200, 200, 200), (3*size//4, size//2), size//6)
            # Draw blades
            pygame.draw.line(surface, (150, 150, 150), (size//4, size//3), (3*size//4, size//3), 3)
            pygame.draw.line(surface, (150, 150, 150), (size//4, 2*size//3), (3*size//4, 2*size//3), 3)
        
        # Add text label
        text = self.font.render(piece_type, True, BLACK)
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        return surface
    
    def draw_board(self):
        """Draw the game board"""
        board_width = BOARD_SIZE * CELL_SIZE
        board_height = BOARD_SIZE * CELL_SIZE
        board_x = (SCREEN_WIDTH - board_width) // 2
        board_y = (SCREEN_HEIGHT - board_height) // 2
        
        # Draw board background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (board_x, board_y, board_width, board_height))
        
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen, 
                DARK_GRAY, 
                (board_x + i * CELL_SIZE, board_y), 
                (board_x + i * CELL_SIZE, board_y + board_height),
                2 if i == 0 or i == BOARD_SIZE else 1
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen, 
                DARK_GRAY, 
                (board_x, board_y + i * CELL_SIZE), 
                (board_x + board_width, board_y + i * CELL_SIZE),
                2 if i == 0 or i == BOARD_SIZE else 1
            )
        
        # Draw coordinates
        for i in range(BOARD_SIZE):
            # Row numbers
            row_text = self.font.render(str(i), True, BLACK)
            self.screen.blit(row_text, (board_x - 20, board_y + i * CELL_SIZE + CELL_SIZE // 2 - 10))
            
            # Column numbers
            col_text = self.font.render(str(i), True, BLACK)
            self.screen.blit(col_text, (board_x + i * CELL_SIZE + CELL_SIZE // 2 - 5, board_y - 20))
        
        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.game.board.grid[row][col]
                if piece is not None:
                    self.draw_piece(row, col, piece)
        
        # Highlight selected piece
        if self.selected_piece:
            row, col = self.selected_piece
            pygame.draw.rect(
                self.screen, 
                HIGHLIGHT, 
                (
                    board_x + col * CELL_SIZE, 
                    board_y + row * CELL_SIZE, 
                    CELL_SIZE, 
                    CELL_SIZE
                )
            )
        
        # Highlight valid moves
        for row, col in self.valid_moves:
            pygame.draw.rect(
                self.screen, 
                VALID_MOVE, 
                (
                    board_x + col * CELL_SIZE, 
                    board_y + row * CELL_SIZE, 
                    CELL_SIZE, 
                    CELL_SIZE
                )
            )
    
    def draw_piece(self, row, col, piece):
        """Draw a piece on the board"""
        board_x = (SCREEN_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
        board_y = (SCREEN_HEIGHT - BOARD_SIZE * CELL_SIZE) // 2
        
        # Get player color
        player_color = PLAYER_COLORS[piece.player_id - 1]
        
        # Create a colored circle for the player
        piece_surface = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10), pygame.SRCALPHA)
        pygame.draw.circle(piece_surface, (*player_color, 180), (CELL_SIZE // 2 - 5, CELL_SIZE // 2 - 5), CELL_SIZE // 2 - 5)
        
        # Blit the piece type image on top
        piece_surface.blit(self.images[piece.type], (0, 0))
        
        # Draw the piece on the board
        self.screen.blit(
            piece_surface, 
            (
                board_x + col * CELL_SIZE + 5, 
                board_y + row * CELL_SIZE + 5
            )
        )
    
    def draw_game_info(self):
        """Draw game information"""
        # Draw current player
        current_player = self.game.players[self.game.current_player_index]
        player_color = PLAYER_COLORS[current_player.id - 1]
        
        player_text = self.font.render(f"Current Turn: {current_player.name}", True, player_color)
        self.screen.blit(player_text, (20, 20))
        
        # Draw piece counts for each player
        y_offset = 50
        for player in self.game.players:
            pieces = self.game.board.get_player_pieces(player.id)
            piece_counts = {'R': 0, 'P': 0, 'S': 0}
            
            for _, _, piece in pieces:
                piece_counts[piece.type] += 1
            
            total = sum(piece_counts.values())
            player_color = PLAYER_COLORS[player.id - 1]
            
            player_text = self.font.render(
                f"{player.name}: {total} pieces (R: {piece_counts['R']}, P: {piece_counts['P']}, S: {piece_counts['S']})", 
                True, 
                player_color
            )
            self.screen.blit(player_text, (20, y_offset))
            y_offset += 25
        
        # Draw game instructions
        instructions = [
            "Click on your piece to select it",
            "Click on a highlighted cell to move",
            "Press ESC to return to menu"
        ]
        
        y_offset = SCREEN_HEIGHT - 80
        for instruction in instructions:
            text = self.font.render(instruction, True, BLACK)
            self.screen.blit(text, (20, y_offset))
            y_offset += 25
    
    def draw_menu(self):
        """Draw the main menu"""
        # Draw title
        title = self.title_font.render("Rock-Paper-Scissors Board Game", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw menu options
        options = [
            "1. Play Game (2 Players)",
            "2. Play Game (3 Players)",
            "3. Watch AI Game (2 Players)",
            "4. Watch AI Game (3 Players)",
            "5. Quit"
        ]
        
        y_offset = 200
        for option in options:
            text = self.font.render(option, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40
        
        # Draw instructions
        instructions = "Press the number key to select an option"
        text = self.font.render(instructions, True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over message
        game_over = self.title_font.render("Game Over", True, WHITE)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over, game_over_rect)
        
        # Draw winner message
        if self.game.winner:
            winner_color = PLAYER_COLORS[self.game.winner.id - 1]
            winner = self.font.render(f"{self.game.winner.name} wins!", True, winner_color)
        else:
            winner = self.font.render("It's a draw!", True, WHITE)
        
        winner_rect = winner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(winner, winner_rect)
        
        # Draw instructions
        instructions = self.font.render("Press SPACE to return to menu", True, WHITE)
        instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instructions, instructions_rect)
    
    def handle_board_click(self, mouse_pos):
        """Handle clicks on the board"""
        board_x = (SCREEN_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
        board_y = (SCREEN_HEIGHT - BOARD_SIZE * CELL_SIZE) // 2
        
        # Check if click is within board boundaries
        if not (board_x <= mouse_pos[0] <= board_x + BOARD_SIZE * CELL_SIZE and
                board_y <= mouse_pos[1] <= board_y + BOARD_SIZE * CELL_SIZE):
            return
        
        # Convert mouse position to board coordinates
        col = (mouse_pos[0] - board_x) // CELL_SIZE
        row = (mouse_pos[1] - board_y) // CELL_SIZE
        
        # If no piece is selected, try to select one
        if self.selected_piece is None:
            piece = self.game.board.grid[row][col]
            current_player = self.game.players[self.game.current_player_index]
            
            if piece is not None and piece.player_id == current_player.id:
                self.selected_piece = (row, col)
                self.valid_moves = self.game.get_valid_moves(row, col)
        
        # If a piece is already selected, try to move it
        else:
            selected_row, selected_col = self.selected_piece
            
            # Check if the clicked cell is a valid move
            if (row, col) in self.valid_moves:
                # Try to move the piece
                success = self.game.play_turn(selected_row, selected_col, row, col)
                
                if success:
                    # Check if game is over
                    self.game.check_game_over()
                    if self.game.game_over:
                        self.game_state = "game_over"
            
            # Reset selection
            self.selected_piece = None
            self.valid_moves = []
    
    def play_ai_turn(self):
        """Play a turn for AI player"""
        current_player = self.game.players[self.game.current_player_index]
        pieces = self.game.board.get_player_pieces(current_player.id)
        
        if not pieces:
            return
        
        # Try each piece until finding one with valid moves
        random.shuffle(pieces)
        for row, col, piece in pieces:
            valid_moves = self.game.get_valid_moves(row, col)
            if valid_moves:
                # Prioritize capturing enemy pieces
                capturing_moves = []
                safe_moves = []
                
                for to_row, to_col in valid_moves:
                    target = self.game.board.grid[to_row][to_col]
                    if target is None:
                        safe_moves.append((to_row, to_col))
                    else:
                        # Check if we can win this combat
                        result = self.game.board.resolve_combat(piece, target)
                        if result == 1:  # We win
                            capturing_moves.append((to_row, to_col))
                        # If we lose, don't add to any list
                
                # Choose a move, prioritizing captures
                if capturing_moves:
                    to_row, to_col = random.choice(capturing_moves)
                elif safe_moves:
                    to_row, to_col = random.choice(safe_moves)
                else:
                    # If no good moves, just pick a random one
                    to_row, to_col = random.choice(valid_moves)
                
                # Highlight the selected piece and move
                self.selected_piece = (row, col)
                self.valid_moves = [(to_row, to_col)]
                
                # Pause to show the selection
                self.draw()
                pygame.display.flip()
                time.sleep(0.5)
                
                # Make the move
                self.game.play_turn(row, col, to_row, to_col)
                
                # Reset selection
                self.selected_piece = None
                self.valid_moves = []
                
                # Check if game is over
                self.game.check_game_over()
                if self.game.game_over:
                    self.game_state = "game_over"
                
                return
        
        # If we get here, no valid moves were found
        self.game.next_turn()
    
    def start_game(self, num_players, ai_mode=False):
        """Start a new game"""
        self.game = Game(num_players)
        self.game.setup_board()
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = "game"
        self.ai_mode = ai_mode
    
    def draw(self):
        """Draw the current game state"""
        self.screen.fill(WHITE)
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "game":
            self.draw_board()
            self.draw_game_info()
        elif self.game_state == "game_over":
            self.draw_board()
            self.draw_game_info()
            self.draw_game_over()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == "menu":
                        if event.key == pygame.K_1:
                            self.start_game(2)
                        elif event.key == pygame.K_2:
                            self.start_game(3)
                        elif event.key == pygame.K_3:
                            self.start_game(2, ai_mode=True)
                        elif event.key == pygame.K_4:
                            self.start_game(3, ai_mode=True)
                        elif event.key == pygame.K_5:
                            running = False
                    
                    elif self.game_state == "game":
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                    
                    elif self.game_state == "game_over":
                        if event.key == pygame.K_SPACE:
                            self.game_state = "menu"
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    if self.game_state == "game" and not self.ai_mode:
                        self.handle_board_click(event.pos)
            
            # AI turn logic
            if self.game_state == "game" and self.ai_mode:
                self.play_ai_turn()
                time.sleep(0.5)  # Add delay between AI turns
            
            # Draw everything
            self.draw()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game"""
    game_gui = GameGUI()
    game_gui.run()

if __name__ == "__main__":
    main()