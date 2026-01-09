# Wordle Draw

A tool that helps you create pixel art patterns on your Wordle grid. By selecting a target word and painting the grid with your desired colors (Gray, Yellow, Green), the tool calculates the exact words you need to guess to achieve that visual pattern.


## Usage

1.  Run the script:
    ```bash
    python draw_wordle.py
    ```
2.  **Target Word**: Enter the 5-letter word that is the *actual* answer for the day (or the word you are pretending is the target).
3.  **Draw Pattern**: Click on the grid cells to change their colors.
    -   **Gray**: Letter is not in the target.
    -   **Yellow**: Letter is in the target but in the wrong spot.
    -   **Green**: Letter is in the target and in the correct spot.
4.  **Solve**: Click the **Solve** button. The tool will populate the grid with words that generate your drawn pattern.
