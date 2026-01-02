"""
Generate the Test Output Prediction data: Rotating Caesar (position-dependent, 0-based indexing)
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path
from typing import Tuple

TASK_TYPE = "rotating-caesar-positional"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_rotating_caesar(state: Tuple[str, int]) -> Tuple[str, int]:
    """
    Update rule (pure function), 0-based indexing:
      - State is a pair (s, t):
          s: a lowercase ASCII string ('a'..'z')
          t: a non-negative integer step counter
      - Produce s' by shifting each character s[i] forward by (t + i) mod 26 positions.
        (i starts at 0)
      - Return the next state (s', t+1).
    """
    s, t = state
    out_chars = []
    for i, ch in enumerate(s):  # i is 0-based
        shift = (t + i) % 26
        x = (ord(ch) - 97 + shift) % 26
        out_chars.append(chr(97 + x))
    return ("".join(out_chars), t + 1)

def main():
    parser = argparse.ArgumentParser(description="Run Rotating Caesar updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of records to generate; record k uses N=k iterations (1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-2-top-rotating-caesar.jsonl",
                        help="Path to output .jsonl file")
    args = parser.parse_args()

    # Seed state (string + step counter)
    init_s = "abz"
    init_t = 0
    state = (init_s, init_t)

    dataset = []

    for i in range(args.num_step):
        step = i + 1

        # Apply exactly ONE update per loop so that after i+1 loops we have f^{step}(initial_state)
        state = update_rotating_caesar(state)

        # Ground-truth answer for easy verification: the current s after step updates
        gt_s, gt_t = state

        print(gt_s, gt_t)

        # Build the executable Code-Execution prompt (0-based indexing is used)
        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports). 
This is a Code Execution task. Indices/cursors are 0-based.
Return only the final string ANSWER (no extra text, quotes, or formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run the code as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it as a plain string (no extra text).

N = {step}  # number of iterations (non-negative integer)
s = "{init_s}"  # initial lowercase string
t = {init_t}    # initial step counter (integer, starts at 0)

def f(state):
    # state: (s, t); indices are 0-based
    s, t = state
    out = []
    for i, ch in enumerate(s):  # i is 0-based
        shift = (t + i) % 26
        x = (ord(ch) - 97 + shift) % 26
        out.append(chr(97 + x))
    return ("".join(out), t + 1)

# iterate N times
state = (s, t)
for _ in range(N):
    state = f(state)

# final answer is the resulting string s_N
ANSWER = state[0]
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt_s  # ground-truth final string after N steps
        }
        dataset.append(data_line)

    # Save all data_line records to a .jsonl file
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
