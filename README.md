### Rock-Paper-Scissors Board Game

A strategic board game implementation of the classic Rock-Paper-Scissors game, built with Python and Pygame.

## 🎮 Game Overview

This Rock-Paper-Scissors Board Game transforms the simple hand game into a strategic board experience. Players control pieces representing rock, paper, and scissors, moving them across a 6x6 grid to capture opponent pieces following the classic rules:

- Rock crushes Scissors
- Paper covers Rock
- Scissors cut Paper


When pieces of the same type meet, both are removed from the board.





## ✨ Features

- **Multiple Game Modes**:

- 2-player mode
- 3-player mode
- Play against AI with 4 difficulty levels
- Watch AI vs AI matches



- **AI Difficulty Levels**:

- Easy (RandomAI): Makes completely random moves
- Medium (BasicAI): Uses basic rules and priorities
- Hard (AdvancedAI): Uses advanced evaluation and limited look-ahead
- Expert (MinimaxAI): Uses minimax algorithm with alpha-beta pruning



- **Polished User Interface**:

- Animated menu with visual effects
- Intuitive game board with highlighted valid moves
- Game information panel showing piece counts
- Turn timer with visual and audio feedback



- **Sound Effects and Music**:

- Background music
- Sound effects for piece selection, movement, and combat
- Victory and defeat sounds





## 🚀 Installation

### Prerequisites

- Python 3.6 or higher
- Pygame library


### Setup

1. Clone this repository:

```shellscript
git clone https://github.com/Tahas13/rock-paper-scissors-board-game.git
cd rock-paper-scissors-board-game
```


2. Install the required dependencies:

```shellscript
pip install pygame
```


3. Run the game:

```shellscript
python game.py
```




## 🎯 How to Play

1. **Starting the Game**:

1. Launch the game and select your preferred game mode from the menu
2. The board will be set up with pieces randomly placed in each player's starting area



2. **Game Rules**:

1. Players take turns moving one piece at a time
2. Pieces can move one space horizontally or vertically
3. When a piece moves onto a space occupied by an opponent's piece, combat occurs
4. Combat follows Rock-Paper-Scissors rules
5. If the same type of pieces meet, both are removed from the board
6. Each turn has a 15-second time limit



3. **Winning the Game**:

1. The last player with pieces remaining on the board wins
2. If all players lose their pieces simultaneously, the game ends in a draw





## 🎛️ Controls

- **Mouse**: Click to select and move pieces
- **ESC**: Return to the main menu
- **SPACE**: Return to menu after game over


## 🧠 AI Implementation

The game features four levels of AI difficulty:

1. **RandomAI (Easy)**:

1. Makes completely random moves
2. Suitable for beginners



2. **BasicAI (Medium)**:

1. Prioritizes capturing moves
2. Avoids risky moves
3. Makes occasional strategic decisions



3. **AdvancedAI (Hard)**:

1. Evaluates board position
2. Considers piece type distribution
3. Looks for threats and opportunities



4. **MinimaxAI (Expert)**:

1. Uses minimax algorithm with alpha-beta pruning
2. Evaluates multiple moves ahead
3. Considers material advantage, type balance, and strategic positioning





## 🛠️ Technical Details

- **Language**: Python 3
- **Graphics Library**: Pygame
- **Architecture**: Object-oriented design with separate classes for:

- Game logic (Game, Board, Piece, Player)
- AI players (RandomAI, BasicAI, AdvancedAI, MinimaxAI)
- Sound management (SoundManager)
- GUI (GameGUI)





## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

- Report bugs
- Suggest new features
- Submit pull requests


## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Pygame community for the excellent game development library
- Rock-Paper-Scissors for the timeless game mechanic

  

---

## 📄 Project Report

You can read the full project report here:  
[📥 Download Project Report (PDF)](https://github.com/Tahas13/rock-paper-scissors-board-game/blob/main/Rock_Paper_Scissors_AI_Game_Report%20.pdf)

## 🎥 Demo Video

Watch our gameplay demo and AI explanation here:  
[▶️ Watch on YouTube](https://github.com/Tahas13/rock-paper-scissors-board-game/blob/main/AI_Project%20Demo.mp4)



---

Created by [Tahas13](https://github.com/Tahas13)
