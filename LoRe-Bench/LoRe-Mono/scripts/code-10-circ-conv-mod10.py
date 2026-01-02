"""
Generate the Test Output Prediction data: Salted Neighbor Sum (cyclic, mod 10, with carry)
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "salted-neighsum-mod10-cyclic"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_salted_neighsum(state, i=None):
    """
    Update rule (pure function, 0-based indexing, cyclic neighbor, with carry):
        Given a length-L list of digits a[0..L-1] (each 0..9), and current step index 'i' (0-based),
        produce out where for every index j:
            salt = (j + (i or 0)) % 10
            total = a[j] + a[(j-1) % L] + salt + carry
            out[j] = total % 10
            carry  = total // 10
        The carry resets to 0 at the start of each iteration and ripples left->right within that iteration.

    Args:
        state: list of ints in [0,9]
        i: iteration index (0-based), required to inject time-dependent salt

    Returns:
        list of ints in [0,9], same length as input.
    """
    a = list(state)
    L = len(a)
    out = [0] * L
    carry = 0
    step = 0 if i is None else i
    for j in range(L):
        salt = (j + step) % 10
        total = a[j] + a[(j - 1) % L] + salt + carry
        out[j] = total % 10
        carry = total // 10
    return out

def main():
    parser = argparse.ArgumentParser(description="Run Salted Neighbor Sum (cyclic, mod 10, with carry) updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of records to generate; record t uses N = t iterations (1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-10-top-salted-neighsum-mod10.jsonl",
                        help="Path to output .jsonl file")
    parser.add_argument("--init_state", type=str, default="1,2,3,4,5,6",
                        help="Comma-separated digits 0..9 as the initial state vector (e.g., '1,2,3,4,5,6')")
    args = parser.parse_args()

    # Seed state (vector of digits 0..9). Parsing from comma-separated string.
    init_state = [int(tok.strip()) for tok in args.init_state.split(",") if tok.strip() != ""]
    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_salted_neighsum(init_state, i)
        else:
            updated_state = update_salted_neighsum(updated_state, i)

        ANSWER = ''.join(map(str, updated_state))
        print(ANSWER)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports).
This is a Code Execution task: run the program; do not rewrite it. Indexing is 0-based. The vector uses cyclic wrap-around for neighbors.
Each iteration passes the current 0-based step into f; within a single iteration, a carry ripples left-to-right.

Return only the value of ANSWER (no other text, no formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run this code exactly as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it with no extra text.

N = {step}  # number of iterations (non-negative integer)
x = {init_state!r}  # initial list of digits (each 0..9)

def f(vec, step):
    L = len(vec)
    out = [0] * L
    carry = 0
    for i in range(L):
        salt = (i + step) % 10
        total = vec[i] + vec[(i - 1) % L] + salt + carry
        out[i] = total % 10
        carry = total // 10
    return out

for step in range(N):  # step goes 0..N-1
    x = f(x, step)

ANSWER = ''.join(map(str, x))
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

    # Save all data_line records to a .jsonl file
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
