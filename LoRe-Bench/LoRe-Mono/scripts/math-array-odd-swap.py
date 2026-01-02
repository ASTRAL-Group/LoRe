"""
Generate the linear mono data: ring array update with odd-swap and modular scoring
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "linear-monotonicity-array-odd-swap"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_array_one_step(A: np.ndarray, m: int, t: int):
    """
    Perform ONE step (t is 1-based) of the ring update with odd-swap and return:
        - updated array A (in-place updated and also returned)
        - the step contribution 'val' to the running score (A[i] AFTER possible swap)

    Rules for step t:
        K = len(A)
        i = (t-1) mod K
        L = (i-1) mod K
        R = (i+1) mod K

        1) A[i] <- (A[i] + A[L]) mod m
        2) If A[i] is odd, swap A[i] and A[R]
        3) step contribution val = A[i] (AFTER swap)

    Notes:
        - All modulo operations are non-negative residues in [0, m-1].
        - The function mutates A in-place and also returns it for convenience.

    Parameters:
        A (np.ndarray): current array state (dtype=int)
        m (int): modulus used in the element update
        t (int): current step index (1-based)

    Returns:
        (np.ndarray, int): (updated array, step contribution to score)
    """
    K = A.shape[0]
    i = (t - 1) % K
    L = (i - 1) % K
    R = (i + 1) % K

    # 1) update A[i]
    A[i] = (int(A[i]) + int(A[L])) % m

    # 2) odd -> swap with right neighbor
    if A[i] % 2 == 1:
        A[i], A[R] = A[R], A[i]

    # 3) contribution to score after possible swap
    val = int(A[i])

    # (Optional debug prints; comment out if noisy)
    print(f"t={t}, i={i}, L={L}, R={R}")
    print("A after step:", A.tolist())
    print("step contribution:", val, "\n")

    return A, val


def main():
    parser = argparse.ArgumentParser(description="Generate ring-array odd-swap modular scoring data")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to simulate (default: 30). Each step yields one .jsonl record with n=step.")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-array-odd-swap.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-array-odd-swap.jsonl)")
    args = parser.parse_args()

    # ----- You can change these defaults to produce a different dataset -----
    init_A = np.array([1, 2, 3, 5,9 ,3 ,1 , 1], dtype=int)  # initial array
    m = 10                                    # element-update modulus
    mod_num = 11                                # final scoring modulus
    # ----------------------------------------------------------------------

    # Ensure all entries are reduced modulo m at the start (non-negative)
    A = deepcopy(init_A) % m

    dataset = []
    score_mod = 0  # running score modulo mod_num

    for i in range(args.num_step):
        step = i + 1
        # one update step
        A, step_contrib = update_array_one_step(A, m, step)
        score_mod = (score_mod + step_contrib) % mod_num

        # Prepare a crystal-clear task statement for this specific n=step
        task_text = f"""Given integers K={len(init_A)}, m={m}, n={step}, and mod_num={mod_num}, and the initial 0-indexed array
A_0 = {init_A.tolist()}.

Before the loop, reduce every entry of A_0 modulo m, ensuring all values lie in [0, m-1].

For t = 1..n, repeat the following on a ring (indices mod K):
1) Let i = (t-1) mod K, L = (i-1) mod K, R = (i+1) mod K.
2) Update A[i] ← (A[i] + A[L]) mod m.   (All modulo results are taken as non-negative residues in [0, m-1].)
3) If A[i] is odd, swap A[i] and A[R].
4) Accumulate score: score ← score + A[i], where A[i] is the value AFTER the possible swap in step 3.

Initialize score = 0 and A = A_0. After completing all n steps, output:
    (score mod mod_num)

Return this single integer as the final answer.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(score_mod)
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
