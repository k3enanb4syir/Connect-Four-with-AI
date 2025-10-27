# Connect 4 with AI

This is a classic Connect 4 game built in Python using the Pygame library. It features a graphical user interface (GUI) and a challenging AI opponent that uses the Minimax algorithm with alpha-beta pruning to determine its moves.

## Features

* **Graphical Interface:** A clean, 2D game board rendered with Pygame.
* **Human vs. AI:** Play as Player 1 (Red) against an AI opponent (Yellow).
* **Unbeatable AI:** The AI uses the Minimax algorithm (set to a depth of 5) to find the optimal move, making it a challenging opponent.
* **Simple Controls:** Just click the mouse in the column where you want to drop your piece.

## Requirements

The project requires the following Python libraries:

* `numpy`
* `pygame`

These are listed in the `requirements.txt` file.

## Installation & Usage

There are two ways to run this project: using the setup script or manually.

### 1. Using the Setup Script (Recommended)

The `setup.sh` script automates the entire process.

1.  Make the script executable:
    ```bash
    chmod +x setup.sh
    ```

2.  Run the script:
    ```bash
    ./setup.sh
    ```

    This will:
    * Create a Python virtual environment named `venv_connect4`.
    * Activate the environment.
    * Install the required packages from `requirements.txt`.
    * Launch the game.

### 2. Manual Setup

If you prefer to set up the environment yourself:

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv_connect4
    ```

2.  **Activate the virtual environment:**
    * On macOS/Linux:
        ```bash
        source venv_connect4/bin/activate
        ```
    * On Windows:
        ```bash
        .\venv_connect4\Scripts\activate
        ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the game:**
    ```bash
    python3 connect4_with_ai.py
    ```

## How to Play

1.  The game window will open.
2.  The game randomly decides who goes first (Player 1 or the AI).
3.  If it's your turn (Player 1), move your mouse to the top of the screen. A red piece will follow your cursor.
4.  Click on the column where you wish to drop your piece.
5.  The AI will then "think" (using Minimax) and make its move.
6.  The first player to get four of their pieces in a row (horizontally, vertically, or diagonally) wins.
7.  The winner will be announced at the top of the screen, and the game will pause for 3 seconds before closing.

## Files in This Repository

* **`connect4_with_ai.py`**: The main Python script containing all the game logic, AI, and Pygame rendering.
* **`requirements.txt`**: A list of the Python dependencies needed to run the game.
* **`setup.sh`**: A shell script to automate environment setup and execution.
* **`README.md`**: This file.
