"""
Generate the Test Output Prediction data: Torus Ant (Langton-like, wraparound)
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "torus-ant-torus-wrap"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_torus_ant(state, i=None):
    """
    Pure state-update (0-based indexing, torus wraparound).

    State format:
        (grid, r, c, d)
        - grid: List[List[int]] of 0/1 values (H rows, W cols)
        - r, c: current row/col (0-based)
        - d: direction (0: up, 1: right, 2: down, 3: left)

    Update rule per step:
        - If grid[r][c] == 0: turn right (d = (d+1) % 4), flip cell to 1
          Else (cell == 1):  turn left  (d = (d+3) % 4), flip cell to 0
        - Move forward 1 cell in direction d, wrapping on edges (torus).

    Returns:
        (new_grid, new_r, new_c, new_d)
    """
    grid, r, c, d = state
    H, W = len(grid), len(grid[0])
    ng = [row[:] for row in grid]  # copy to keep function pure

    if ng[r][c] == 0:
        d = (d + 1) % 4
        ng[r][c] = 1
    else:
        d = (d + 3) % 4
        ng[r][c] = 0

    if d == 0:       # up
        r = (r - 1) % H
    elif d == 1:     # right
        c = (c + 1) % W
    elif d == 2:     # down
        r = (r + 1) % H
    else:            # left
        c = (c - 1) % W

    return (ng, r, c, d)


def parse_init_state(init_state_str: str):
    """
    Parse init_state from a compact string.

    Format (all parts 0-based):
        "L;ROWS;r,c,d"

        - L: grid side length (creates an LxL grid)
        - ROWS: optional; slash-separated strings of '0'/'1' of length L for each row.
                 If omitted or empty, the grid defaults to all zeros.
                 Example for L=5: "00000/00000/00000/00000/00000"
        - r,c,d: starting row, column, direction (0:up,1:right,2:down,3:left)

    Examples:
        "5;;0,0,0"                             -> 5x5 all-zero grid, start (0,0), up
        "5;00000/00000/00000/00000/00000;0,0,0"

    Returns:
        (grid, r, c, d)
    """
    parts = [p.strip() for p in init_state_str.split(";")]
    if len(parts) < 1 or not parts[0]:
        raise ValueError("init_state must start with grid side L")
    L = int(parts[0])

    rows_part = parts[1] if len(parts) > 1 else ""
    if rows_part:
        row_tokens = [rt.strip() for rt in rows_part.split("/")]
        if len(row_tokens) != L:
            raise ValueError("ROW count must equal L")
        grid = [[int(ch) for ch in row] for row in row_tokens]
        for row in grid:
            if len(row) != L or any(ch not in (0, 1) for ch in row):
                raise ValueError("Each ROW must be length L with only 0/1")
    else:
        grid = [[0] * L for _ in range(L)]

    if len(parts) < 3 or not parts[2]:
        r, c, d = 0, 0, 0
    else:
        rcd = [int(tok) for tok in parts[2].split(",")]
        if len(rcd) != 3:
            raise ValueError("r,c,d must have exactly 3 integers")
        r, c, d = rcd

    H, W = L, L
    if not (0 <= r < H and 0 <= c < W and 0 <= d <= 3):
        raise ValueError("r,c must be within grid, d in {0,1,2,3}")

    return (grid, r, c, d)


def main():
    parser = argparse.ArgumentParser(description="Run Torus Ant (Langton-like) state updates for Test Output Prediction")
    parser.add_argument(
        "--num_step",
        type=int,
        default=30,
        help="Number of records to generate; record t uses N = t iterations (1..num_step)",
    )
    parser.add_argument(
        "--out_path",
        type=str,
        default="linear-mono-code-9-top-torus-ant.jsonl",
        help="Path to output .jsonl file",
    )
    parser.add_argument(
        "--init_state",
        type=str,
        default="5;;0,0,0",
        help="Init format 'L;ROWS;r,c,d' with 0-based indices. "
             "ROWS is slash-separated L strings of 0/1 (optional). Example: '5;00000/00000/00000/00000/00000;0,0,0'",
    )
    args = parser.parse_args()

    # Parse initial state
    init_grid, init_r, init_c, init_d = parse_init_state(args.init_state)
    dataset = []

    updated_state = None  # will hold (grid, r, c, d)
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_torus_ant((init_grid, init_r, init_c, init_d), i)
        else:
            updated_state = update_torus_ant(updated_state, i)

        grid, r, c, d = updated_state
        ones = sum(sum(row) for row in grid)

        ANSWER = f"{r},{c},{d},{ones}"
        print(ANSWER)

        # Build the executable task text (English, Code-Execution oriented, 0-based indexing)
        # The code below is fully runnable as-is (no imports). The solver should just run and return ANSWER.
        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports).
This is a Code Execution task: run the program; do not translate or rewrite it. Indexing is 0-based throughout.

Grid and cursor semantics (0-based):
- grid is a list of lists of integers 0/1, size HxW (here a square grid).
- (r, c) is the current row/column; d is the direction with 0:up, 1:right, 2:down, 3:left.
- One step does:
  * If grid[r][c] == 0: turn right (d = (d+1) % 4) and flip cell to 1.
    Else (==1): turn left (d = (d+3) % 4) and flip cell to 0.
  * Move forward one cell in direction d, wrapping on edges (torus).
Return only ANSWER (no extra text, no formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run this code exactly as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it with no extra text.

N = {step}  # number of iterations (positive integer)
grid = {init_grid!r}  # initial HxW grid of 0/1, 0-based indexing
r, c, d = {init_r}, {init_c}, {init_d}  # start row, col, direction (0:up,1:right,2:down,3:left)

def step_once(state):
    grid, r, c, d = state
    H, W = len(grid), len(grid[0])

    # copy grid to keep updates local to this step
    ng = [row[:] for row in grid]

    if ng[r][c] == 0:
        d = (d + 1) % 4  # turn right
        ng[r][c] = 1
    else:
        d = (d + 3) % 4  # turn left
        ng[r][c] = 0

    if d == 0:        # up
        r = (r - 1) % H
    elif d == 1:      # right
        c = (c + 1) % W
    elif d == 2:      # down
        r = (r + 1) % H
    else:             # left
        c = (c - 1) % W

    return (ng, r, c, d)

state = (grid, r, c, d)
for _ in range(N):
    state = step_once(state)

grid, r, c, d = state

# For easy verification, return the final cursor and a simple checksum:
# ANSWER format: "r,c,d,total_ones"
ones = 0
for row in grid:
    for v in row:
        ones += v
ANSWER = f"{{r}},{{c}},{{d}},{{ones}}"
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": ANSWER
        }
        dataset.append(data_line)

    # Save to .jsonl
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
