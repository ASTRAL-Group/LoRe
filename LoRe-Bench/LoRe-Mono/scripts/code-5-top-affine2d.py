"""
Generate the Test Output Prediction data: Affine2D with step bias (mod 200)
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "affine2d-stepbias-mod1000"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_affine2d(state):
    """
    Update rule (pure function), modulo 200 on each component:
        Given the current state (x, y, t), compute
            x' = (2*x + 1*y + 5 + t) % 200
            y' = (3*x + 1*y + 7      ) % 200
            t' = (t + 1) % 200
        Return (x', y', t').
    """
    x, y, t = state
    nx = (2 * x + y + 5 + t) % 200
    ny = (3 * x + y + 7) % 200
    nt = (t + 1) % 200
    return (nx, ny, nt)

def main():
    parser = argparse.ArgumentParser(description="Run Affine2D (with step bias) updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to generate (each line uses step t = 1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-5-top-affine2d.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-code-5-top-affine2d.jsonl)")
    args = parser.parse_args()

    # Seed state (x, y, t), all integers are taken modulo 200 inside the update
    init_state = (1, 2, 0)
    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_affine2d(init_state)
        else:
            updated_state = update_affine2d(updated_state)

        # Ground truth as an easy-to-compare string "x,y,t"
        gt_str = f"{updated_state[0]},{updated_state[1]},{updated_state[2]}"

        print(gt_str)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports). No cursor/indexing is used in this task. Return only the string ANSWER (no other text).
Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run the code as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it exactly as a plain string (no extra text).

N = {step}  # number of iterations (non-negative integer)
x, y, t = {init_state}  # initial state (x, y, t), all integers

def f(x: int, y: int, t: int):
    # Affine update with a step-dependent bias on x and modulo 200 on each component:
    #   x' = (2*x + y + 5 + t) % 200
    #   y' = (3*x + y + 7    ) % 200
    #   t' = (t + 1) % 200
    nx = (2 * x + y + 5 + t) % 200
    ny = (3 * x + y + 7) % 200
    nt = (t + 1) % 200
    return nx, ny, nt

for _ in range(N):
    x, y, t = f(x, y, t)

# ANSWER must be a single string with comma-separated integers, easy to verify.
ANSWER = f"{{x}},{{y}},{{t}}"
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt_str
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
