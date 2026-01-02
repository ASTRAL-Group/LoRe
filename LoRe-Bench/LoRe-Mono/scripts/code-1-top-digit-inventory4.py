"""
Generate the Test Output Prediction data: Digit Inventory-4 (fixed 8-char state)
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "digit-inventory-4-fixed8"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_inventory(s: str, i) -> str:
    """
    Update rule (pure function):
        1) Count how many times each character '0','1','2','3' appears in s.
        2) For each count, format it as exactly two decimal digits with a leading zero if needed.
        3) Concatenate the four 2-digit counts in the order: count('0'), count('1'), count('2'), count('3').
           The result is an 8-character numeric string.
    Returns:
        The next state string (length always 8 after the first update).
    """
    c0 = s.count('0')
    c1 = s.count('1')
    c2 = s.count('2')
    c3 = s.count('3')
    c4 = s.count('4')
    if i%2==0:
        return f"{(c0+1)%5}{(c1+2)%5}{(c2+1)%5}{(c3+1)%5}{c4}"
    else:
        return f"{(c0 + 2) % 5}{(c1 + 1) % 5 if c1>=3 else (2*c1 + 1) % 5}{(c2 + 3) % 5}{(c3 + 1) % 5}{c4}"

def main():
    parser = argparse.ArgumentParser(description="Run Digit Inventory-4 state updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to generate (each line uses step t = 1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-1-top-digit-inventory4.jsonl",
                        help="Path to output .jsonl file (default: top-digit-inventory4.jsonl)")
    args = parser.parse_args()

    # Seed state (can be any decimal string; after one update the state is always 8 characters)
    init_state = "01938"
    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_inventory(init_state, i)
        else:
            updated_state = update_inventory(updated_state, i)

        # Ground-truth answer for easy verification: sum of the 8 digits of the current state
        # sum_answer = sum(int(ch) for ch in updated_state)

        print(updated_state)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports). Cursor/indexing is not used in this task. Return only the integer ANSWER (no other text).
Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run the code as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it as a plain integer (no extra text).

N = {step}  # number of iterations (non-negative integer)
s = "{init_state}"  # initial state (string of digits)

def f(s: str) -> str:
    c0 = s.count('0')
    c1 = s.count('1')
    c2 = s.count('2')
    c3 = s.count('3')
    c4 = s.count('4')
    if i%2==0:
        return f"{{(c0+1)%5}}{{(c1+2)%5}}{{(c2+1)%5}}{{(c3+1)%5}}{{c4}}"
    else:
        return f"{{(c0 + 2) % 5}}{{(c1 + 1) % 5 if c1 >= 3 else (2 * c1 + 1) % 5}}{{(c2 + 3) % 5}}{{(c3 + 1) % 5}}{{c4}}"

for _ in range(N):
    s = f(s)

ANSWER = s
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": updated_state
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
