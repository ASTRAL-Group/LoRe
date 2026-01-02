"""
Generate the Test Output Prediction data: 1D Cellular Automaton - Rule 90 (ring)
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "rule90-ring"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_rule90(b: str) -> str:
    """
    Update rule (pure function), 0-based indexing, ring boundary:
        For each position i in the binary string b (characters '0' or '1'),
        the next bit is the XOR of its two neighbors on a ring:
            b_next[i] = b[(i-1) % L] XOR b[(i+1) % L]
        where L = len(b). Center cell is ignored in the rule (classic Rule 90).
    Returns:
        The next state string (same length, consisting only of '0' and '1').
    """
    L = len(b)
    out = []
    for i in range(L):
        left = 1 if b[(i - 1) % L] == '1' else 0
        right = 1 if b[(i + 1) % L] == '1' else 0
        out.append('1' if (left ^ right) else '0')
    return "".join(out)

def main():
    parser = argparse.ArgumentParser(description="Run Rule-90 ring updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to generate (each line uses step t = 1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-3-top-rule90.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-code-3-top-rule90.jsonl)")
    args = parser.parse_args()

    # Seed state: a binary string; ring size = len(init_state)
    init_state = "0101011101001"
    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_rule90(init_state)
        else:
            updated_state = update_rule90(updated_state)

        # Optionally print for inspection
        print(updated_state)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports). 
This is a Code-Execution task. The binary string is treated as cells on a ring (wrap-around). 
Use 0-based indexing for positions. Return only the string ANSWER (no other text).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run the code as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it as a plain string (no extra text).

N = {step}  # number of iterations (non-negative integer)
b = "{init_state}"  # initial binary state (characters '0' or '1')

def f(b: str) -> str:
    L = len(b)
    out = []
    for i in range(L):
        left = 1 if b[(i - 1) % L] == '1' else 0
        right = 1 if b[(i + 1) % L] == '1' else 0
        out.append('1' if (left ^ right) else '0')
    return "".join(out)

for _ in range(N):
    b = f(b)

ANSWER = b
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
