"""
Generate the Test Output Prediction data: Ducci Sequence (cyclic, mod 1000)
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "ducci-mod1000-cyclic"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_ducci(state, i=None):
    """
    Update rule (pure function, 0-based indexing, cyclic ring):
        Given a length-K vector of non-negative integers x[0..K-1],
        produce y where:
            y[i] = abs(x[i] - x[(i+1) % K]) % 1000
        i (step index) is accepted for signature compatibility with the template
        but is not used in this update rule.

    Args:
        state: list/tuple of non-negative ints (the current vector)
        i: optional iteration index (ignored)

    Returns:
        list of ints (the next vector), length K is unchanged.
    """
    x = list(state)
    K = len(x)
    y = [0] * K
    for j in range(K):
        y[j] = abs(x[j if j<=2 else 2*j%K] - x[(j + 1 if j<=5 else j-2) % K]) % 1000
    return y

def main():
    parser = argparse.ArgumentParser(description="Run Ducci (cyclic, mod 1000) state updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of records to generate; record t uses N = t iterations (1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-4-top-ducci-mod1000.jsonl",
                        help="Path to output .jsonl file")
    parser.add_argument("--init_state", type=str, default="11,5,3,16,12,1,5,8,2",
                        help="Comma-separated non-negative integers as the initial state vector (e.g., '1,5,3,7')")
    args = parser.parse_args()

    # Seed state (vector of non-negative integers). Parsing from comma-separated string.
    init_state = [int(tok.strip()) for tok in args.init_state.split(",") if tok.strip() != ""]
    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_ducci(init_state, i)
        else:
            updated_state = update_ducci(updated_state, i)

        # Optional sanity metric (not stored): simple checksum for quick local verification
        # checksum = sum(updated_state) % 1000000007

        ANSWER = ''.join(map(str,updated_state))
        print(ANSWER)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports). 
This is a Code Execution task: run the program, do not rewrite it. Indexing is 0-based.
Return only the value of ANSWER (no other text, no formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run this code exactly as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it with no extra text.

N = {step}  # number of iterations (non-negative integer)
x = {init_state!r}  # initial vector of non-negative integers

def f(vec):
    K = len(vec)
    out = [0] * K
    for i in range(K):
        out[i] = abs(vec[j if j<=2 else 2*j%K] - vec[(j + 1 if j<=5 else j-2) % K]) % 1000
    return out

for _ in range(N):
    x = f(x)

ANSWER = ''.join(map(str,x))
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": ANSWER  # stored as list of ints; judge can compare to tuple(x) easily
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
