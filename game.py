import pygame
import sys
import random
import time
import os
from typing import List, Tuple, Dict, Optional
from pygame import mixer

#initialize pygame and mixer     
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

# Player colors
PLAYER_COLORS = [
    (220, 20, 60),    # Player 1: Crimson
    (30, 144, 255),   # Player 2: Dodger Blue
    (50, 205, 50)     # Player 3: Lime Green
]

# Sound effects paths
SOUNDS = {
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

class SoundManager:
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
            
        # Define sound files - in a real implementation, you would have actual files
        sound_files = {
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
        
        # Try to load sound files if they exist, otherwise create dummy sounds
        for sound_name, file_name in sound_files.items():
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



class GameGUI:
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
        
    def load_fonts(self):
        """Load fonts for the game"""
        try:
            self.font = pygame.font.SysFont("Arial", 24)
            self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
            self.button_font = pygame.font.SysFont("Arial", 32)
        except:
            # Fallback to default font if custom font fails
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 32)
    
    def update_cell_size(self):
        """Update cell size based on screen dimensions"""
        # Calculate the maximum cell size that will fit on the screen
        max_width = (self.screen.get_width() - 2 * BOARD_MARGIN) // BOARD_SIZE
        max_height = (self.screen.get_height() - 2 * BOARD_MARGIN) // BOARD_SIZE
        self.cell_size = min(max_width, max_height)
    
    def create_background(self):
        """Create a background image"""
        # Create a gradient background
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            # Create a gradient from dark blue to light blue
            color = (
                int(20 + (y / SCREEN_HEIGHT) * 50),
                int(20 + (y / SCREEN_HEIGHT) * 50),
                int(50 + (y / SCREEN_HEIGHT) * 150)
            )
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
            
        # Add some decorative elements
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            radius = random.randint(1, 3)
            color = (255, 255, 255, random.randint(50, 150))
            pygame.draw.circle(background, color, (x, y), radius)
            
        return background
    
    def create_logo(self):
        """Create a game logo"""
        logo_size = 200
        logo = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        
        # Draw a circular background
        pygame.draw.circle(logo, (200, 200, 200, 200), (logo_size//2, logo_size//2), logo_size//2)
        
        # Draw the three symbols in a circle
        radius = logo_size // 3
        center = (logo_size//2, logo_size//2)
        
        # Rock (top)
        rock_pos = (center[0], center[1] - radius//2)
        pygame.draw.circle(logo, (150, 150, 150), rock_pos, radius//3)
        
        # Paper (bottom left)
        paper_pos = (center[0] - radius//2, center[1] + radius//2)
        pygame.draw.rect(logo, (250, 250, 250), (paper_pos[0] - radius//4, paper_pos[1] - radius//4, radius//2, radius//2))
        
        # Scissors (bottom right)
        scissors_pos = (center[0] + radius//2, center[1] + radius//2)
        pygame.draw.line(logo, (200, 200, 200), 
                        (scissors_pos[0] - radius//4, scissors_pos[1] - radius//4),
                        (scissors_pos[0] + radius//4, scissors_pos[1] + radius//4), 5)
        pygame.draw.line(logo, (200, 200, 200), 
                        (scissors_pos[0] - radius//4, scissors_pos[1] + radius//4),
                        (scissors_pos[0] + radius//4, scissors_pos[1] - radius//4), 5)
        
        # Draw connecting lines
        pygame.draw.line(logo, (255, 255, 255), rock_pos, paper_pos, 2)
        pygame.draw.line(logo, (255, 255, 255), paper_pos, scissors_pos, 2)
        pygame.draw.line(logo, (255, 255, 255), scissors_pos, rock_pos, 2)
        
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
            # Draw a rock shape with player color
            pygame.draw.circle(surface, player_color, (size//2, size//2), size//2)
            # Add some details to make it look like a rock
            for _ in range(5):
                x = random.randint(size//4, 3*size//4)
                y = random.randint(size//4, 3*size//4)
                r = random.randint(2, 5)
                # Darken or lighten the player color for details
                detail_color = tuple(max(0, min(255, c + random.randint(-50, 50))) for c in player_color)
                pygame.draw.circle(surface, detail_color, (x, y), r)
            
        elif piece_type == 'P':  # Paper
            # Draw a paper shape with player color
            pygame.draw.rect(surface, player_color, (5, 5, size-10, size-10))
            # Add some lines to represent paper
            line_color = tuple(max(0, min(255, c + 50)) for c in player_color)
            pygame.draw.line(surface, line_color, (10, size//3), (size-10, size//3), 1)
            pygame.draw.line(surface, line_color, (10, 2*size//3), (size-10, 2*size//3), 1)
            
        elif piece_type == 'S':  # Scissors
            # Draw scissors with player color
            # Draw scissors handle
            pygame.draw.circle(surface, player_color, (size//4, size//2), size//6)
            pygame.draw.circle(surface, player_color, (3*size//4, size//2), size//6)
            # Draw blades
            blade_color = tuple(max(0, min(255, c - 30)) for c in player_color)
            pygame.draw.line(surface, blade_color, (size//4, size//3), (3*size//4, size//3), 3)
            pygame.draw.line(surface, blade_color, (size//4, 2*size//3), (3*size//4, 2*size//3), 3)
        
        # Add text label
        text = self.font.render(piece_type, True, BLACK)
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        # Add a border
        pygame.draw.rect(surface, BLACK, (0, 0, size, size), 2, border_radius=5)
        
        return surface
    
    def draw_board(self):
        """Draw the game board"""
        board_width = BOARD_SIZE * self.cell_size
        board_height = BOARD_SIZE * self.cell_size
        board_x = (self.screen.get_width() - board_width) // 2
        board_y = (self.screen.get_height() - board_height) // 2
        
        # Draw board background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (board_x, board_y, board_width, board_height))
        
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
        
        # Draw coordinates
        for i in range(BOARD_SIZE):
            # Row numbers
            row_text = self.font.render(str(i), True, BLACK)
            self.screen.blit(row_text, (board_x - 20, board_y + i * self.cell_size + self.cell_size // 2 - 10))
            
            # Column numbers
            col_text = self.font.render(str(i), True, BLACK)
            self.screen.blit(col_text, (board_x + i * self.cell_size + self.cell_size // 2 - 5, board_y - 20))
        
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
                    board_x + col * self.cell_size, 
                    board_y + row * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
            )
        
        # Highlight valid moves
        for row, col in self.valid_moves:
            pygame.draw.rect(
                self.screen, 
                VALID_MOVE, 
                (
                    board_x + col * self.cell_size, 
                    board_y + row * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
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
        pygame.draw.rect(self.screen, DARK_GRAY, (timer_x, timer_y, timer_width, timer_height))
        
        # Calculate remaining time percentage
        time_percent = max(0, min(1, self.game.turn_timer / TURN_TIME))
        
        # Choose color based on remaining time
        if time_percent < 0.3:
            timer_color = TIMER_WARNING
        else:
            timer_color = player_color
        
        # Draw timer bar
        pygame.draw.rect(self.screen, timer_color, (timer_x, timer_y, int(timer_width * time_percent), timer_height))
        
        # Draw timer text
        timer_text = self.font.render(f"{int(self.game.turn_timer)}s", True, WHITE)
        timer_text_rect = timer_text.get_rect(center=(timer_x + timer_width // 2, timer_y + timer_height // 2))
        self.screen.blit(timer_text, timer_text_rect)
        
        # Play tick sound when timer is low
        if 0 < self.game.turn_timer <= 5 and int(self.game.turn_timer) != int(self.game.turn_timer + 0.1):
            self.sound_manager.play('timer_tick')
    
    def draw_game_info(self):
        """Draw game information"""
        # Draw current player
        current_player = self.game.players[self.game.current_player_index]
        player_color = PLAYER_COLORS[current_player.id - 1]
        
        player_text = self.font.render(f"Current Turn: {current_player.name}", True, player_color)
        self.screen.blit(player_text, (20, 40))
        
        # Draw piece counts for each player
        y_offset = 70
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
        
        y_offset = self.screen.get_height() - 80
        for instruction in instructions:
            text = self.font.render(instruction, True, WHITE)
            self.screen.blit(text, (20, y_offset))
            y_offset += 25
    
    def draw_menu(self):
        """Draw the main menu"""
        # Draw background
        self.screen.blit(self.background_img, (0, 0))
        
        # Draw logo
        logo_rect = self.logo_img.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(self.logo_img, logo_rect)
        
        # Draw title with animation
        title_color = (255, 255, 255)
        title_shadow_color = (100, 100, 100)
        
        # Add a shadow effect
        title_shadow = self.title_font.render("Rock-Paper-Scissors Board Game", True, title_shadow_color)
        title_shadow_rect = title_shadow.get_rect(center=(self.screen.get_width() // 2 + 3, 250 + 3))
        self.screen.blit(title_shadow, title_shadow_rect)
        
        # Main title
        title = self.title_font.render("Rock-Paper-Scissors Board Game", True, title_color)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 250))
        self.screen.blit(title, title_rect)
        
        # Draw menu options as buttons
        options = [
            "Play Game (2 Players)",
            "Play Game (3 Players)",
            "Watch AI Game (2 Players)",
            "Watch AI Game (3 Players)",
            "Quit"
        ]
        
        button_width = 400
        button_height = 50
        button_margin = 20
        y_offset = 320
        
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
            button_color = (100, 100, 200)
            text_color = WHITE
            
            if button_rect.collidepoint(mouse_pos):
                button_color = (150, 150, 250)
                
            # Draw button
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)
            
            # Draw button text
            text = self.button_font.render(option, True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            y_offset += button_height + button_margin
        
        # Draw instructions
        instructions = "Click on an option to select"
        text = self.font.render(instructions, True, WHITE)
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
        self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over message
        game_over = self.title_font.render("Game Over", True, WHITE)
        game_over_rect = game_over.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(game_over, game_over_rect)
        
        # Draw winner message
        if self.game.winner:
            winner_color = PLAYER_COLORS[self.game.winner.id - 1]
            winner = self.font.render(f"{self.game.winner.name} wins!", True, winner_color)
            # Play win sound if not already played
            self.sound_manager.play('win')
        else:
            winner = self.font.render("It's a draw!", True, WHITE)
        
        winner_rect = winner.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(winner, winner_rect)
        
        # Draw instructions
        instructions = self.font.render("Press SPACE to return to menu", True, WHITE)
        instructions_rect = instructions.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
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
        y_offset = 320
        
        for i in range(5):  # 5 menu options
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
                elif i == 2:  # Watch AI Game (2 Players)
                    self.start_game(2, ai_mode=True)
                elif i == 3:  # Watch AI Game (3 Players)
                    self.start_game(3, ai_mode=True)
                elif i == 4:  # Quit
                    pygame.quit()
                    sys.exit()
                
                break
            
            y_offset += button_height + button_margin
    
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
                success, combat_type = self.game.play_turn(row, col, to_row, to_col)
                
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
        self.sound_manager.play('game_start')
    
    def handle_resize(self, new_size):
        """Handle window resize event"""
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.update_cell_size()
        self.update_piece_images()
        
        # Recreate background to match new size
        self.background_img = self.create_background()
    
    def draw(self):
        """Draw the current game state"""
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "game":
            # Draw a simpler background for the game
            self.screen.fill((50, 50, 80))
            self.draw_board()
            self.draw_game_info()
            self.draw_timer()
        elif self.game_state == "game_over":
            # Draw the game state behind the overlay
            self.screen.fill((50, 50, 80))
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
                    elif self.game_state == "game" and not self.ai_mode:
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
