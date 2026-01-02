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

def update_matrix(matrix: np.ndarray, mod_num):
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
    matrix = matrix + np.array([[0,0], [0,1]])
    # 3. multiply with the original one
    swapped_matrix = matrix[[1, 0]]  # 交换第一、二行
    matrix = matrix @ swapped_matrix
    # 4. element-wise modulo 100
    # mod_num = 101
    matrix = np.mod(matrix, mod_num)

    return matrix

def main():
    parser = argparse.ArgumentParser(description="Run matrix update for linear recurrence")
    parser.add_argument("--num_step", type=int, default=40,
                        help="Number of steps to run the matrix update (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-matrix.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-math-matrix.jsonl)")
    args = parser.parse_args()

    init_matrix = np.array([[1, 2], [5, -3]])
    mod_num = 11
    dataset = []

    for i in range(args.num_step):
        step = i+1
        if i == 0:
            updated_matrix = update_matrix(init_matrix, mod_num)
        else:
            updated_matrix = update_matrix(updated_matrix, mod_num)

        sum_answer = np.sum(updated_matrix)
        print(updated_matrix)

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": f"""Given integer \\(n={step}\\), update the initial matrix \\( M_0 = \\begin{{bmatrix}} {init_matrix[0][0]} & {init_matrix[0][1]} \\\\ {init_matrix[1][0]} & {init_matrix[1][1]} \\end{{bmatrix}} \\) iteratively with the following rules:
1. Addition. Add \\( m = \\begin{{bmatrix}} 0 & 0 \\\\ 0 & 1 \\end{{bmatrix}} \\) to the matrix \\(M_t\\): \\(A_t = M_t + m\\)
2. Swap the first and second line of \\(A_t\\) to get \\(S_t\\): \\(S_t[0]=A_t[1], S_t[1]=A_t[0]\\)
3. Multiply. Form the product: \\(P_t = A_t \\cdot S_t\\).
4. Modulo. Update the state by taking element-wise modulo {mod_num}: \\(M_{{t+1}} = P_t \\bmod {mod_num}\\).
Start with \\(M_0 = \\begin{{bmatrix}} {init_matrix[0][0]} & {init_matrix[0][1]} \\\\ {init_matrix[1][0]} & {init_matrix[1][1]} \\end{{bmatrix}}\\) and repeat the above until you obtain \\(M_{step}\\). If taking one step of iteration is enough to obtain \\(M_{step}\\), just do one iteration.
Finally, compute the sum of all elements in \\(M_{step}\\) as \\(S=\\sum_{{i,j}} a_{{ij}}\\).
Provide \\(S\\) as the final answer.""",
            "gt_ans_latex": f"\\( \\begin{{bmatrix}} {updated_matrix[0][0]} & {updated_matrix[0][1]} \\\\ {updated_matrix[1][0]} & {updated_matrix[1][1]} \\end{{bmatrix}} \\)",
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
