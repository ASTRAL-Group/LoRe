"""
Generate letter-maze walk data with self-modifying grid to avoid short cycles.
Rule summary:
- Decide move by current cell (vowel → RIGHT, consonant → DOWN), torus wrap.
- Append the letter at the destination cell to S.
- Then mutate the grid:
    * If the letter you moved *from* was a vowel: rotate the destination COLUMN up by 1.
    * Otherwise (consonant): rotate the destination ROW left by 1.
We recompute each task from the initial grid so outputs are not periodic across n.
"""
import argparse
import json
from pathlib import Path
from copy import deepcopy  # kept for parity with the template

TASK_TYPE = "letter-maze-vowel-right-consonant-down-with-rotations"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

VOWELS = set("aeiouAEIOU")

# Fixed grid and parameters
GRID = [
    "abcde",
    "fghij",
    "klmno",
    "pqrst",
]
H, W = len(GRID), len(GRID[0])
R0, C0 = 0, 0
K = 4  # ensure K <= n+1

def rotate_row_left(grid, r, w):
    grid[r] = grid[r][1:] + grid[r][:1]

def rotate_col_up(grid, c, h):
    first = grid[0][c]
    for i in range(h - 1):
        grid[i][c] = grid[i + 1][c]
    grid[h - 1][c] = first

def update_maze(state, grid, h, w, k):
    """
    Advance the maze by one step according to the rules:

    State carries:
        - r, c: current row/col (before moving)
        - buf: list of the last up-to-k letters (the tail of S), in order

    One update performs:
        1) Let ch = grid[r][c] (current cell *before* moving).
        2) Move:
            - if ch is a vowel (a,e,i,o,u; case-insensitive): c = (c + 1) % w (RIGHT)
            - else: r = (r + 1) % h (DOWN)
        3) Append the letter at the *destination* cell grid[r][c] to the rolling buffer.
        4) Mutate the grid based on ch (the letter we moved *from*):
            - If ch is a vowel: Rotate the destination COLUMN c up by 1 (cyclic).
            - Otherwise:       Rotate the destination ROW r left by 1 (cyclic).
        Keep only the last k letters in the buffer.
    """
    r, c, buf = state["r"], state["c"], state["buf"]
    ch = grid[r][c]

    # move
    if ch.lower() in "aeiou":
        c = (c + 1) % w
    else:
        r = (r + 1) % h

    # append the letter at the destination (before mutation)
    buf.append(grid[r][c])
    if len(buf) > k:
        buf.pop(0)

    # mutate grid depending on ch
    if ch.lower() in "aeiou":
        rotate_col_up(grid, c, h)
    else:
        rotate_row_left(grid, r, w)

    return {"r": r, "c": c, "buf": buf}

def simulate_last_k(n, k):
    """
    Simulate exactly n moves starting from the initial grid and position,
    applying grid mutations each step, and return the last-k letters of S.
    """
    # start from a FRESH copy of the initial grid for each n
    grid = [list(row) for row in GRID]
    state = {"r": R0, "c": C0, "buf": [grid[R0][C0]]}  # S starts with the initial cell letter
    for _ in range(n):
        state = update_maze(state, grid, H, W, k)
    return "".join(state["buf"])

def main():
    parser = argparse.ArgumentParser(description="Run letter-maze updates with grid mutations and emit JSONL tasks")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps (n) to simulate for the maze (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-letter-maze.jsonl",
                        help="Path to output .jsonl file (default: letter-maze-rot.jsonl)")
    args = parser.parse_args()

    # Prepare human-readable grid block for the task statement
    grid_block = "\n".join(" ".join(row) for row in GRID)

    dataset = []
    for i in range(args.num_step):
        step = i + 1  # n = number of moves performed

        # Compute ground truth independently from the initial grid for this n
        last_k_word = simulate_last_k(step, K)
        print(last_k_word)

        task_text = f"""You are given a letter maze and a number of moves n={step}. The maze is a rectangular grid of letters G with h={H} rows and w={W} columns:

{grid_block}

Start at the cell (r0, c0) = ({R0}, {C0}). Build a string S as you move:
1) First, write down the starting letter G[r0][c0] into S. (This is done before any moves.)
2) Then repeat the following exactly n={step} times (t = 1..n):
   • Let (r, c) be your current cell BEFORE moving, and let ch = G[r][c].
   • Move one step based on ch (case-insensitive):
       – If ch ∈ {{a, e, i, o, u}} (a vowel): move RIGHT → c ← (c + 1) mod {W}
       – Otherwise (a consonant): move DOWN → r ← (r + 1) mod {H}
   • After moving to the destination cell (r, c), append its letter G[r][c] to S.
   • Now mutate the grid based on ch (the letter you moved FROM):
       – If ch is a vowel: cyclically rotate COLUMN c upward by 1.
         (Formally, for all i: G[i][c] ← old G[(i + 1) mod {H}][c].)
       – Otherwise (ch is a consonant): cyclically rotate ROW r left by 1.
         (Formally, for all j: G[r][j] ← old G[r][(j + 1) mod {W}].)

Important: The mutation happens AFTER appending G[r][c] to S, and it affects the grid used for the NEXT iteration. Indices are 0-based and the maze wraps around like a torus.

Thus, after n moves, S has length n + 1 (because the starting letter was included).

Let k = {K}. Your task is to return the word W made by the LAST k letters of S (in order). Output W as a plain string."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": last_k_word
        }
        dataset.append(data_line)

    # Save all records to a .jsonl file
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
