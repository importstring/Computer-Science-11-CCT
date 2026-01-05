# Battleship – ICS3U CCT

## General Information

- **Title:** Battleship (Terminal Edition)
- **Author:** Simon Bergeron
- **Date:** January 4, 2026
- **Course:** ICS3U – Introduction to Computer Science
- **Teacher:** Mr. G
- **Github link:** https://github.com/importstring/Computer-Science-11-CCT
---

## Project Pitch

This project is a fully playable, terminal-based version of the classic game **Battleship** where a human player faces off against a computer-controlled opponent. Instead of simple text prompts, the game uses a curses-driven interface that lets the player move a cursor with arrow keys, rotate ships, and interact with a dynamic 10×10 grid. The player places ships manually while the computer auto-places its own fleet, which creates a satisfying setup phase before the real battle begins. Once the game starts, both sides take turns firing shots, with hits, misses, and sunk ships tracked and displayed clearly.

Under the hood, the computer uses a two-phase targeting strategy: “hunt” mode uses a parity pattern to search efficiently, and “target” mode focuses around successful hits to finish off damaged ships. This makes the AI feel smarter and more engaging than pure random guessing. The game includes a scoring system for situations where all possible guesses are used: remaining ship segments on each board are converted into points based on ship size, and the higher total wins. The code is organized into multiple classes and files, demonstrating clean structure, modularity, and use of many ICS3U concepts at a high level.

---

## Tech / Framework

This project is written in **Python 3** and runs in a terminal environment using the standard library only. The user interface is built with the `curses` module, which handles screen drawing, keyboard input (arrow keys, Enter, letter keys), and simple animations for the computer’s shots. The game logic relies on standard Python features such as lists, dictionaries, loops, functions with default parameters, and classes for organizing the main pieces of the game (`Game`, `Board`, `Attack`, `PlaceBoat`).

To run the game, you need a Python 3 interpreter and a terminal that supports `curses`. On macOS and Linux, this works out of the box. On Windows, the recommended approach is to run the game in a WSL (Windows Subsystem for Linux) terminal or a compatible environment that supports `curses`. No external libraries or internet connection are required, and all files can be kept together in a single project folder.

---

## License / Property Model

This project is intended for **educational and personal use** as part of the ICS3U CCT. The code may be viewed, run, and modified by the instructor and classmates for grading, feedback, or learning purposes. It is not formally licensed as open source, and redistribution or reuse outside of this academic context should only be done with the author’s permission. In short, treat it as a student project: respect the originality of the work and avoid copying it for other graded assignments.

---

## Features

- **Interactive ship placement:**

  - Player places ships of sizes 2, 3, 4, and 5 using arrow keys and rotation, with immediate visual feedback for legal and illegal positions.

- **Turn-based gameplay with clear feedback:**

  - Separate grids for attacks and ship positions, with `X` for misses and `!` for hits, plus a quick toggle to view your own board.

- **Computer AI with hunt/target modes:**

  - The computer alternates between a parity-based search and focused targeting around hits to simulate a more intelligent opponent.

- **Scoring and no-move endgame:**

  - If all ships on one side are sunk, that player loses. If both sides run out of possible guesses, the game compares remaining ship points (ship size = point value) to decide the winner.

- **Modular, object-oriented design:**

  - Multiple classes and files organize the game into clear responsibilities, making it easier to maintain and extend.

- **Simple shot animation:**
  - When the computer hits a player ship, a small animation shows a projectile moving across a blank grid to the impact location, adding a bit of polish to the experience.

---

## How to Use

1. **Setup**

   - Ensure Python 3 is installed. (https://realpython.com/installing-python/)
   - Place all project files (e.g., `battleship.py`, `extras.py`, and any other helper modules) in the same folder.

2. **Running the game**

   - Open a terminal in the project folder.
   - Run:
     ```bash
     python main.py
     ```
   - If an input/demo sequence appears first (to practice input and list methods), follow the prompts; the game will start afterward.

3. **Placing ships**

   - Use **arrow keys** to move the current ship around the 10×10 grid.
   - Press **R** to rotate the ship in 90° increments.
   - Legal positions are highlighted differently from illegal ones (off-board or overlapping).
   - Press **Enter** to confirm placement for each ship size (2, 3, 4, 5).

4. **Taking a shot**

   - On your turn, move the cursor with the arrow keys over the opponent grid.
   - Press **V** to briefly view your own ships, hits, and misses.
   - Press **Enter** to fire at the highlighted cell.
   - The grid updates to show whether the shot was a hit or miss; sunk ships are handled internally and can award replacement ships, depending on your game rules.

5. **Ending the game**
   - Play continues with alternating turns until:
     - One side has all ships sunk, or
     - Both boards are fully guessed / no more shots are possible.
   - In the second case, the game calculates a score based on remaining ship sizes and announces the winner or a tie.

---

## FAQ

**1. Why does the game use a curses-based UI instead of simple text prompts?**  
Using `curses` allows the game to draw a live grid and move a cursor around, which makes Battleship feel much closer to a board game than a series of numbered prompts. It also demonstrates comfort with a more advanced standard library module and gives room for features like animations and real-time highlight feedback.

**2. How does the computer decide where to shoot?**  
The AI starts in “hunt” mode, using a parity strategy tuned to the smallest remaining ship size (for example, skipping cells that cannot fit a size‑3 or size‑4 ship). When it scores a hit, it switches into “target” mode, adding neighboring cells around the hit to a stack and focusing shots there. This makes the computer better at finishing off ships instead of scattering hits randomly across the board.

**3. What happens when a ship is sunk?**  
Each ship is tracked with a unique ID and lists of hit and unhit coordinates. When the last unhit coordinate for a ship is hit, that ship is marked as sunk: its live coordinates are removed from the board’s occupancy list, and the tracking dictionaries are updated. In this version of the game, sinking ships can also trigger additional behavior such as allowing ships to be re-placed, depending on the rules you are using.

**4. What if both players run out of possible guesses?**  
Because the boards are 10×10, each side has at most 100 guesses. If both attack grids eventually fill up, the game looks at the total remaining ship points on each side. Ship sizes correspond to their point value (size‑5 ship = 5 points, and so on). The player with the higher remaining total wins; if the totals are equal, the game declares a tie.

**5. Can this code be extended with more features?**  
Yes. The modular design (separate classes and files) makes it straightforward to add features such as multiple difficulty levels, different ship layouts, a hit-streak bonus, sound effects via another library, or a logging system that writes game results to a file. The AI logic can also be swapped out or upgraded without rewriting the entire game.

---

## Easter Eggs & Cheats

- There are some pretty funny metadata variables at the top of the main file
- You can also tweak internal constants such as animation speed or AI behavior if you want a “secret” easier or harder mode while testing the game.
- Additional hidden behaviour, like auto-placing all player ships or skipping the AI animation, can be added behind simple flags if needed, but by default the game runs in a fair, standard mode suitable for the assignment.


