import tkinter as tk
from tkinter import messagebox
import csv
import os

# --- Logic ---

class WordleSolver:
    def __init__(self, words_file):
        self.words = []
        self.word_freq = {}
        self.load_words(words_file)

    def load_words(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    w = row['word'].lower().strip()
                    if len(w) == 5:
                        # Use occurrence as frequency score, default to 0 if missing
                        freq = float(row['occurrence']) if row.get('occurrence') and row['occurrence'].strip() else 0.0
                        self.words.append(w)
                        self.word_freq[w] = freq
            # Sort words by frequency descending to prefer common words
            self.words.sort(key=lambda w: self.word_freq[w], reverse=True)
        except Exception as e:
            print(f"Error loading words: {e}")
            # Fallback list if file fails
            self.words = ["apple", "bread", "crane", "doubt", "eagle"]

    def get_pattern(self, guess, target):
        """
        Calculates the Wordle pattern for a guess against a target.
        Returns a list of 5 integers: 0 (Gray), 1 (Yellow), 2 (Green).
        """
        pattern = [0] * 5
        guess = list(guess)
        target_list = list(target)
        
        # Pass 1: Green (Exact matches)
        for i in range(5):
            if guess[i] == target_list[i]:
                pattern[i] = 2
                guess[i] = None # Mark as handled
                target_list[i] = None

        # Pass 2: Yellow (Present but wrong spot)
        for i in range(5):
            if pattern[i] == 0: # If not already green
                char = guess[i]
                if char is not None and char in target_list:
                    pattern[i] = 1
                    # Remove one instance of char from target_list to handle duplicates correctly
                    target_list[target_list.index(char)] = None
        
        return pattern

    def solve_row(self, target, desired_pattern):
        """
        Finds a word in the dictionary that produces `desired_pattern` when guessed against `target`.
        """
        for word in self.words:
            if self.get_pattern(word, target) == desired_pattern:
                return word
        return None

# --- GUI ---

class WordleDrawApp:
    def __init__(self, root, solver):
        self.root = root
        self.solver = solver
        self.root.title("Wordle Draw")
        self.root.geometry("400x550")
        
        # Colors
        self.COLOR_MAP = {0: '#787c7e', 1: '#c9b458', 2: '#6aaa64'} # Official Wordle colors (Gray, Yellow, Greenish)
        self.COLOR_NAMES = {0: 'Gray', 1: 'Yellow', 2: 'Green'}
        
        # Main Layout
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(expand=True, fill='both')
        
        # Target Word
        input_frame = tk.Frame(main_frame)
        input_frame.pack(pady=(0, 10))
        
        tk.Label(input_frame, text="Target Word (5 letters):", font=('Arial', 10, 'bold')).pack(side='left')
        self.target_var = tk.StringVar()
        self.target_entry = tk.Entry(input_frame, textvariable=self.target_var, width=10, font=('Arial', 10))
        self.target_entry.pack(side='left', padx=5)
        
        # Grid
        self.grid_frame = tk.Frame(main_frame)
        self.grid_frame.pack(pady=10)
        
        self.buttons = []      # The button widgets
        self.grid_state = []   # Integers 0, 1, 2 representing colors
        
        for r in range(6):
            row_buttons = []
            row_state = []
            for c in range(5):
                # Init with Gray (0)
                btn = tk.Button(self.grid_frame, bg=self.COLOR_MAP[0], width=4, height=2,
                                font=('Arial', 14, 'bold'), fg='white',
                                command=lambda r=r, c=c: self.on_cell_click(r, c))
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_buttons.append(btn)
                row_state.append(0)
            self.buttons.append(row_buttons)
            self.grid_state.append(row_state)
            
        # Options
        options_frame = tk.Frame(main_frame)
        options_frame.pack(pady=10)
        
        self.no_yellow_var = tk.BooleanVar(value=False)
        self.chk_no_yellow = tk.Checkbutton(options_frame, text="Disable Yellows", 
                                            variable=self.no_yellow_var, font=('Arial', 10))
        self.chk_no_yellow.pack()
        
        # Actions
        action_frame = tk.Frame(main_frame)
        action_frame.pack(pady=10, fill='x')
        
        self.clear_btn = tk.Button(action_frame, text="Clear Grid", command=self.clear_grid, font=('Arial', 12))
        self.clear_btn.pack(side='left', expand=True, fill='x', padx=(20, 5))

        self.solve_btn = tk.Button(action_frame, text="Solve", command=self.solve_grid, font=('Arial', 12, 'bold'), bg='#dddddd')
        self.solve_btn.pack(side='left', expand=True, fill='x', padx=(5, 20))
        
    def on_cell_click(self, r, c):
        # Reset text if any
        self.buttons[r][c].configure(text="")
        
        current_val = self.grid_state[r][c]
        
        # Cycle logic
        # If "Disable Yellows" is checked: Gray (0) -> Green (2) -> Gray (0)
        # Else: Gray (0) -> Yellow (1) -> Green (2) -> Gray (0)
        
        if self.no_yellow_var.get():
            new_val = 2 if current_val == 0 else 0
            # If current was Yellow (from before checking box), it goes to Green
            if current_val == 1: new_val = 2
        else:
            new_val = (current_val + 1) % 3
            
        self.grid_state[r][c] = new_val
        self.buttons[r][c].configure(bg=self.COLOR_MAP[new_val])

    def clear_grid(self):
        for r in range(6):
            for c in range(5):
                self.grid_state[r][c] = 0
                self.buttons[r][c].configure(bg=self.COLOR_MAP[0], text="")

    def solve_grid(self):
        target_word = self.target_var.get().strip().lower()
        
        if len(target_word) != 5:
            messagebox.showerror("Invalid Input", "Target word must be exactly 5 letters.")
            return
            
        # Check if basic chars
        if not target_word.isalpha():
            messagebox.showerror("Invalid Input", "Target word must contain only letters.")
            return

        # Clear text first
        for r in range(6):
            for c in range(5):
                self.buttons[r][c].configure(text="")

        found_words = []
        
        for r in range(6):
            pattern = self.grid_state[r]
            match = self.solver.solve_row(target_word, pattern)
            
            if match:
                found_words.append(match)
                # Preview letters on grid
                for c in range(5):
                    letter = match[c].upper()
                    self.buttons[r][c].configure(text=letter)
            else:
                messagebox.showwarning("Impossible", f"No word found for Row {r+1} matching the pattern against '{target_word}'.")
                return

        # Success message
        word_list_str = "\n".join([f"Row {i+1}: {w.upper()}" for i, w in enumerate(found_words)])
        messagebox.showinfo("Success!", f"Found 6 words:\n\n{word_list_str}")

if __name__ == "__main__":
    # Path to wordle.csv assumed to be in the same directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'wordle.csv')
    
    # Check if exists
    if not os.path.exists(csv_path):
        # Fallback for dev environment or wrong CWD
        possible_path = r"d:\Files\Code\Wordle_Draw\wordle.csv"
        if os.path.exists(possible_path):
            csv_path = possible_path
        else:
            print("Warning: wordle.csv not found.")

    solver = WordleSolver(csv_path)
    
    root = tk.Tk()
    app = WordleDrawApp(root, solver)
    root.mainloop()
