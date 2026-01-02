"""
Generate the harder linear mono data: matrix update, reduce to 2 by 2 matrix
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "linear-monotonicity-cellular-automaton"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_complex(bi_string: np.ndarray):
    """
    update the matrix, the rule is as follow:
        1. update the element independently
        2. transpose this updated matrix
        3. multiply the original matrix with this updated matrix
        4. take element-wise modulo 100 on the result
        5. return the updated matrix

    Parameters:
         bi_string: binary string array
         
    Returns:
        updated binary string
    """
    rules = {
        (0,0,0) : 0,
        (0,0,1) : 1,
        (0,1,0) : 1,
        (1,0,0) : 1,
        (1,1,0) : 0,
        (1,0,1) : 0,
        (0,1,1) : 1,
        (1,1,1) : 0,
    }
    
    # Create a copy to avoid modifying during iteration
    update_bi_string = [0]*len(bi_string)


    for i in range(len(bi_string)):
        # Handle boundary conditions with periodic boundary
        left = bi_string[i-1]
        center = bi_string[i]
        right = bi_string[(i+1) % len(bi_string)]
        
        neighborhood = (int(left), int(center), int(right))
        update_bi_string[i] = rules[neighborhood]

    
    return update_bi_string

def main():
    parser = argparse.ArgumentParser(description="Run complex update for linear recurrence")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to run the matrix update (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-cellular-automaton.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-math-matrix.jsonl)")
    args = parser.parse_args()

    init_bi_string = np.array([0,1,0,0,0,0,1])
    mod_num = 31
    dataset = []

    for i in range(args.num_step):
        step = i+1
        if i == 0:
            updated_bi_string = update_complex(init_bi_string)
        else:
            updated_bi_string = update_complex(updated_bi_string)

        print(updated_bi_string)

        sum_answer = np.sum([updated_bi_string[i] * 2**(len(updated_bi_string) - 1 - i) for i in range(len(updated_bi_string))])

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": f"""Given integer \\(n={step}\\), start with the binary string \\(s_0 = {init_bi_string.tolist()}\\) (length \\(L={len(init_bi_string)}\\)). For each step \\(t=0,1,\\dots,n-1\\), update all bits simultaneously to obtain \\(s_{{t+1}}\\) using a radius-1 cellular automaton with wrap-around (periodic) boundaries:

For each index \\(i\\), let \\(\\ell = s_t[(i-1) \\bmod L]\\), \\(c = s_t[i]\\), \\(r = s_t[(i+1) \\bmod L]\\). The next bit is \\(s_{{t+1}}[i] = f(\\ell,c,r)\\) where \\(f\\) is defined by:
\\(000 \\to 0,\\; 001 \\to 1,\\; 010 \\to 1,\\; 011 \\to 1,\\; 100 \\to 1,\\; 101 \\to 0,\\; 110 \\to 0,\\; 111 \\to 0\\).
(This is Wolfram's Rule 30.)

After \\(n={step}\\) steps, encode \\(s_{step}\\) as a base-2 integer in big-endian order:
\\(x = \\sum_{{i=0}}^{{L-1}} s_{step}[i] \\cdot 2^{{L-1-i}}\\).
Return \\(x\\) as the final answer.""",

            "gt_ans": int(sum_answer)
        }
        dataset.append(data_line)

    # Save all data_line records to a .jsonl file
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
