"""
Generate the harder linear mono data: matrix update, reduce to 2 by 2 matrix
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "linear-monotonicity-matrix-harder"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_complex(complex: np.ndarray, mod_num):
    """
    update the matrix, the rule is as follow:
        1. update the element independently
        2. transpose this updated matrix
        3. multiply the original matrix with this updated matrix
        4. take element-wise modulo 100 on the result
        5. return the updated matrix

    Parameters:
         matrix: original matrix
         mod_num: modulation number

    Returns:
        updated matrix
    """
    # 2. add the matrix by 1
    complex = complex + 1
    print(complex)
    # 3. multiply with the original one
    conj_complex = complex * np.array([1, -1])  # conjugate
    print(conj_complex)
    conj_complex = np.array([np.min(conj_complex)]*2)
    print(conj_complex)
    complex = np.array([complex[0]*conj_complex[0] - complex[1]*conj_complex[1], complex[0]*conj_complex[1] + complex[1]*conj_complex[0]])
    # 4. element-wise modulo 100
    print(complex)
    # mod_num = 101
    complex = np.mod(complex, mod_num)
    print(complex)
    print('\n')

    return complex

def main():
    parser = argparse.ArgumentParser(description="Run complex update for linear recurrence")
    parser.add_argument("--num_step", type=int, default=40,
                        help="Number of steps to run the matrix update (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-complex.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-math-matrix.jsonl)")
    args = parser.parse_args()

    init_complex = np.array([5, 2])
    mod_num = 31
    dataset = []

    for i in range(args.num_step):
        step = i+1
        if i == 0:
            updated_complex = update_complex(init_complex, mod_num)
        else:
            updated_complex = update_complex(updated_complex, mod_num)

        print(updated_complex)

        sum_answer = np.sum(updated_complex)

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": f"""Given integer \\(n={step}\\), update the initial complex number \\( c_0 = {init_complex[0]} + {init_complex[1]}i\\) iteratively with the following rules:
1. Addition. Add \\( m = 1 + i \\) to the complex number \\(c_t\\): \\(a_t = c_t + m\\)
2. Let \\(s_t\\) be the conjugate of \\(a_t\\): \\(s_t=\\overline{{a_t}}\\)
3. Replace both parts of \\(s_t\\) with the minimum of these two parts, creating a new complex number \\(n_t = min(Re(s_t), Im(s_t)) + min(Re(s_t), Im(s_t))i\\) 
4. Multiply. Form the product: \\(p_t = a_t \\cdot n_t\\).
5. Modulo. Update the state by taking element-wise modulo {mod_num}: \\(c_{{t+1}} = (Re(p_t) mod {mod_num}) + (Im(p_t) mod {mod_num})\\).
Start with the initial complex number \\( c_0 = {init_complex[0]} + {init_complex[1]}i\\) and repeat the above until you obtain \\(c_{step}\\). If taking one step of iteration is enough to obtain \\(c_{step}\\), just do one iteration.
Finally, return the scalar \\(x = Re(c_t) + Im(c_t)\\) as the final answer.""",
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
