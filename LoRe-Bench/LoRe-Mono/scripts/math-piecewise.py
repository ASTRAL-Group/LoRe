"""
Generate the piecewise modular iteration with XOR branch (scalar update)
"""
import argparse
import json
from pathlib import Path

TASK_TYPE = "linear-mono-math-piecewise-xor"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_state(x: int, a: int, b: int, c: int, m: int, q: int, mod_num: int):
    """
    Perform ONE step of the piecewise update and return:
        - the new state x_{t+1}
        - the contribution to S modulo mod_num, i.e., (x_{t+1} % q) % mod_num

    Piecewise rule (branching by x % 5):
        1) if x % 5 in {0, 1}: x' = (3*x + a) % m
        2) if x % 5 in {2, 3}: x' = (x*x + b) % m
        3) otherwise (i.e., x % 5 == 4): x' = x ^ c     # bitwise XOR, NO modulo m here

    Parameters:
        x (int): current state x_t
        a, b, c (int): constants
        m (int): modulus for branches (1) and (2)
        q (int): per-step accumulation modulus
        mod_num (int): final answer modulus

    Returns:
        (new_x, contrib_mod): tuple[int, int]
            new_x: x_{t+1}
            contrib_mod: (new_x % q) % mod_num
    """
    r = x % 5
    if r in (0, 1):
        new_x = (3 * x + a) % m
    elif r in (2, 3):
        new_x = (x * x + b) % m
    else:  # r == 4
        new_x = x ^ c  # bitwise XOR, no modulo m

    contrib_mod = (new_x % q) % mod_num
    return new_x, contrib_mod


def main():
    parser = argparse.ArgumentParser(description="Generate jsonl for piecewise modulo iteration with XOR branch")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps/examples to generate (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-piecewise.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-math-piecewise.jsonl)")
    args = parser.parse_args()

    # Fixed parameters for the dataset (can be modified if desired)
    x0 = 7
    a, b, c = 3, 5, 10
    m = 100
    q = 12
    mod_num = 17

    dataset = []

    # Running state for producing ground-truth that matches "n = step" iterations from x0
    cur_x = x0
    S_mod = 0  # we maintain S modulo mod_num

    for i in range(args.num_step):
        step = i + 1

        # Do ONE update, carry state forward so after i+1 loops we've done (i+1) total iterations from x0
        cur_x, contrib = update_state(cur_x, a, b, c, m, q, mod_num)
        S_mod = (S_mod + contrib) % mod_num

        # Build task text (very clear English, self-contained)
        task_text = f"""Given an integer \\(n={step}\\), update a scalar state \\(x_t\\) starting from \\(x_0={x0}\\) using the following piecewise rule for \\(t=1,2,\\dots,n\\):

Branch by the value of \\(x_t \\bmod 5\\):
1) If \\(x_t \\bmod 5 \\in {{0,1}}\\): \\(x_{{t+1}} = (3x_t + {a}) \\bmod {m}\\).
2) If \\(x_t \\bmod 5 \\in {{2,3}}\\): \\(x_{{t+1}} = (x_t^2 + {b}) \\bmod {m}\\).
3) Otherwise (i.e., when \\(x_t \\bmod 5 = 4\\)): \\(x_{{t+1}} = x_t \\oplus {c}\\), where \\(\\oplus\\) is bitwise XOR. **No modulo {m} is applied in this branch.**

After each step, accumulate
\\[
S \\leftarrow S + (x_{{t+1}} \\bmod {q}).
\\]
After completing all \\(n={step}\\) steps, output the single integer
\\[
S \\bmod {mod_num}.
\\]
as the final answer.

Conventions:
- Modulo returns a non-negative remainder.
- \\(\\oplus\\) denotes bitwise XOR on non-negative integers.
- Fixed parameters for this instance: \\(a={a},\\; b={b},\\; c={c},\\; m={m},\\; q={q},\\; \\text{{mod\\_num}}={mod_num},\\; x_0={x0}\\).

Return only the integer value of \\(S \\bmod {mod_num}\\) as the final answer."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(S_mod),
        }
        dataset.append(data_line)

    # Ensure output directory exists
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Save all data_line records to a .jsonl file
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
