"""
Generate the rotating-board + center-flip boolean data: 3x3 board, XOR neighborhood, accumulate score mod M
"""
import argparse
import json

import numpy as np
from pathlib import Path

TASK_TYPE = "linear-mono-math-boolean-rotflip-3x3"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def rotate90_cw(board: np.ndarray) -> np.ndarray:
    """Return the 3x3 array rotated 90 degrees clockwise."""
    # np.rot90(..., -1) == rotate clockwise
    return np.rot90(board, -1)

def step_update(board: np.ndarray):
    """
    Perform one step of the transformation and return (next_board, ones_count).

    One step:
      1) Rotate the whole board 90° clockwise.
      2) Flip (toggle) the center cell (1↔0).
      3) Synchronously update the 8 non-center cells:
         For every non-center cell (r,c), set it to the XOR of its 4-neighbors
         in the post-rotation-and-center-flip board F:
             up/down/left/right, out-of-bounds treated as 0.
         The center cell keeps F[1,1].
      4) ones_count = sum of all 9 cells of the new board.
    """
    # 1) rotate
    F = rotate90_cw(board).copy()

    # 2) flip center
    F[1, 1] ^= 1

    # 3) synchronous update from F -> H
    H = np.zeros((3, 3), dtype=np.int64)
    H[1, 1] = F[1, 1]  # center stays

    # helper to safely read with zero padding
    def safe(F, r, c):
        if 0 <= r < 3 and 0 <= c < 3:
            return int(F[r, c])
        return 0

    for r in range(3):
        for c in range(3):
            if r == 1 and c == 1:
                continue
            up = safe(F, r - 1, c)
            down = safe(F, r + 1, c)
            left = safe(F, r, c - 1)
            right = safe(F, r, c + 1)
            H[r, c] = up ^ down ^ left ^ right

    ones = int(H[2, 0] + H[1, 1] + H[0, 2])
    return H, ones

def main():
    parser = argparse.ArgumentParser(description="Run 3x3 boolean rot+flip XOR update and build a JSONL dataset")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to generate (default: 30). Each record uses n=1..num_step.")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-boolean-rotflip-3x3.jsonl",
                        help="Output .jsonl file name (default: boolean-rotflip-3x3.jsonl)")
    args = parser.parse_args()

    # Initial board G0 (rows as strings '0'/'1'). Feel free to change if needed.
    init_board = np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
    ], dtype=np.int64)

    # modulus for the final score
    mod_num = 1000

    # Pre-format the initial board as three lines for task text
    init_rows = ["".join(str(int(x)) for x in init_board[r]) for r in range(3)]

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    dataset = []

    # We iterate once per record so that record i corresponds to n=i
    board = init_board.copy()
    score_mod = 0  # running score modulo mod_num

    for i in range(args.num_step):
        step = i + 1

        # Do exactly one step more to move from n=step-1 to n=step
        board, ones = step_update(board)
        score_mod = (score_mod + ones) % mod_num

        task_text = f"""Given an integer n={step}, a 3×3 binary board G_0 (0/1) as three row-strings:

{init_rows[0]}
{init_rows[1]}
{init_rows[2]}

Apply the following procedure for t = 1..n to obtain G_t and a running score:

1) **Rotate** the whole board 90° clockwise.
2) **Flip center**: toggle the middle cell (row=1, col=1; 0-indexed) between 0 and 1.
3) **Synchronous neighborhood XOR update**:
   Let F be the board after steps (1) and (2). Build G_t from F *synchronously*:
   - The center cell keeps F[1][1].
   - For every other cell (r,c), set
       G_t[r][c] = F[r-1][c] ⊕ F[r+1][c] ⊕ F[r][c-1] ⊕ F[r][c+1],
     where out-of-bounds neighbors are treated as 0, and ⊕ is XOR over {{0,1}}.
   (Synchronous means all reads are from F; the update order does not matter.)
4) **Score accumulation** (anti-diagonal / secondary diagonal, bottom-left → top-right):
   After you obtain G_t, add s_t = G_t[2][0] + G_t[1][1] + G_t[0][2] to the running total：
    score ← score + s_t.

Finally, output the integer x = score mod {mod_num} as the final answer.
Conventions: indices r,c ∈ {{0,1,2}}; the clockwise rotation mapping is (r,c) → (c, 2−r)."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(score_mod),
        }
        dataset.append(data_line)

    # Save to .jsonl
    out_fp = DATA_SAVE_DIR / args.out_path
    with open(out_fp, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_fp}")

if __name__ == "__main__":
    main()
