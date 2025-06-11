# 3D Tic-Tac-Toe (PyOpenGL Project)

## Project Overview

This project implements a 3D version of the classic Tic-Tac-Toe game. It utilizes Pygame for window management, event handling, and font rendering, and PyOpenGL for 3D graphics rendering. Players can interact with a 3x3 grid of cubes, clicking on them to place their 'X' or 'O'. The game features cube animations, texture mapping, and two distinct game modes.

This README provides an overview of the project structure, features, and instructions for running the game, based on the provided Python script.

## Features

*   **3D Game Board:** A 3x3 grid of interactive cubes forming the Tic-Tac-Toe board.
*   **Textured Cubes:** Cubes are textured using `crate.png` as a base. When a player makes a move, the cube's texture changes to indicate 'X' (using `crate_x.png`) or 'O' (using `crate_o.png`) on specific faces.
*   **Click Interaction:** Players can click on cubes using the mouse. Ray-casting (`is_point_inside`, `get_ray`) is used to determine which cube is selected.
*   **Cube Animation:** Selected cubes rotate smoothly to reveal the 'X' or 'O' face.
*   **Game Modes:**
    *   **Mode Selection Screen:** At the start, the player can choose a game mode.
    *   **Turn-based Mode (T):** Players 'X' and 'O' take turns.
    *   **Random Mode (R):** After a player clicks a cube, the owner ('X' or 'O') is assigned randomly.
*   **Win/Draw Detection:** The game checks for win conditions (three in a row, column, or diagonal) and draw conditions (all cubes filled without a winner).
*   **OpenGL UI:** Game status (current turn, winner, mode selection) is displayed using text rendered directly within the OpenGL scene via Pygame font surfaces converted to OpenGL textures (`draw_text_gl`, `draw_ui`).
*   **Restart Functionality:** After a game ends (win or draw), players can press the `SPACE` bar to reset the game and return to the mode selection screen.

## Project Structure

The core logic is contained within a single Python script. Key components include:

*   **Global Variables:**
    *   `MODE_SELECT`, `RANDOM_MODE`: Control the game state.
    *   `vertices`, `faces`: Define the geometry of a single cube.
*   **`load_texture(filename)`:** Loads an image file and prepares it as an OpenGL texture.
*   **`Cube` Class:**
    *   Manages the state of individual cubes (position, rotation, owner, textures).
    *   `update(dt)`: Handles the rotation animation.
    *   `draw()`: Renders the cube using OpenGL.
    *   `draw_faces()`: Applies textures to the cube faces.
    *   `is_point_inside()`: Implements ray-cube intersection for mouse picking.
    *   `click()`: Logic for when a cube is selected by a player.
*   **OpenGL Utility Functions:**
    *   `init_gl()`: Basic OpenGL setup (depth testing, clear color).
    *   `get_ray()`: Converts 2D mouse coordinates to a 3D ray for picking.
*   **Game Logic Functions:**
    *   `check_winner(cubes)`: Determines if a player has won.
    *   `is_draw(cubes)`: Checks if the game is a draw.
*   **UI Rendering Functions:**
    *   `draw_text_gl()`: Renders a Pygame font surface as an OpenGL texture on a 2D quad.
    *   `draw_ui()`: Displays game information (turn, winner, mode selection) using `draw_text_gl`.
*   **`main()` Function:**
    *   Initializes Pygame and OpenGL.
    *   Sets up the camera perspective.
    *   Loads textures.
    *   Creates the grid of `Cube` objects (`make_cubes`).
    *   Contains the main game loop, handling events, updating game state, and rendering both the 3D scene and the 2D UI.

## Requirements

*   Python 3.x
*   Pygame: `pip install pygame`
*   PyOpenGL: `pip install PyOpenGL PyOpenGL_accelerate`
*   NumPy: `pip install numpy`
*   Texture files:
    *   `crate.png` (default cube texture)
    *   `crate_x.png` (texture for 'X' player)
    *   `crate_o.png` (texture for 'O' player)
    These image files must be present in the same directory as the Python script.

## How to Run

1.  Ensure all prerequisites (Python libraries and texture files) are met and available.
2.  Save the provided code as a Python file (e.g., `3d_tic_tac_toe.py`).
3.  Place `crate.png`, `crate_x.png`, and `crate_o.png` in the same directory as the script.
4.  Run the script from your terminal:
    ```bash
    python 3d_tic_tac_toe.py
    ```

## Gameplay Instructions

1.  **Mode Selection:**
    *   When the game starts, you will be prompted to select a mode.
    *   Press `R` for "Random Mode" (cube owner 'X' or 'O' is chosen randomly on click).
    *   Press `T` for "Turn-based Mode" (players 'X' and 'O' alternate turns).
2.  **Playing the Game:**
    *   Click on an empty cube to place your mark (or a random mark in Random Mode).
    *   The cube will animate, rotating to show the 'X' or 'O'.
    *   In Turn-based Mode, the turn will switch to the other player.
3.  **Winning/Drawing:**
    *   The game ends when a player gets three marks in a row, column, or diagonal, or when all cubes are filled resulting in a draw.
    *   A message indicating the winner or a draw will be displayed.
4.  **Restarting:**
    *   After a game ends, press the `SPACE` bar to reset the board and return to the mode selection screen.
