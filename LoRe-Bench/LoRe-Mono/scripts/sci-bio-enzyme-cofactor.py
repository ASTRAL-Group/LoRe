"""
Generate cofactor-cycled enzymatic queue tasks: batch bioreactor with periodic cofactor regeneration; return B after n steps
"""
import argparse
import json
from pathlib import Path

TASK_TYPE = "bio-enzyme-cofactor-queue"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def one_tick(A: int, B: int, C: int, t: int, k: int):
    """
    Execute ONE discrete reaction tick at time index t (1-based), with
    'reaction' happening before 'regeneration'.

    Reaction (if possible):
        if A > 0 and C > 0:
            A -= 1
            B += 1
            C -= 1

    Regeneration (post-reaction):
        if t % k == 0:
            C += 1

    Returns:
        (A, B, C) after this tick
    """
    # Reaction first
    if A > 0 and C > 0:
        A -= 1
        B += 1
        C -= 1

    # Regeneration after reaction
    if t % k == 0:
        C += 1

    return A, B, C

def main():
    parser = argparse.ArgumentParser(description="Generate enzymatic queue (cofactor cycle) tasks")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of ticks n to include in the dataset (records n=1..num_step; default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-sci-bio-enzyme-cofactor-queue.jsonl",
                        help="Path to output .jsonl file (default: bio-enzyme-cofactor-queue.jsonl)")
    # You can change these defaults to produce different instances
    parser.add_argument("--A0", type=int, default=12, help="Initial substrate count A0 (default: 12)")
    parser.add_argument("--B0", type=int, default=0, help="Initial product count B0 (default: 0)")
    parser.add_argument("--C0", type=int, default=3, help="Initial cofactor tokens C0 (default: 3)")
    parser.add_argument("--k", type=int, default=5, help="Cofactor regeneration period k (default: 5)")
    args = parser.parse_args()

    A, B, C = args.A0, args.B0, args.C0
    k = args.k
    dataset = []

    # Build n=1..num_step by incrementally simulating ticks
    for i in range(args.num_step):
        t = i + 1
        A, B, C = one_tick(A, B, C, t=t, k=k)
        # Ground-truth answer for this record is B after n=t ticks
        gt_ans = int(B)

        task_text = f"""You are modeling a **batch bioreactor** where an enzyme E converts substrate A to product B, but each catalytic event requires a recyclable **cofactor token** C (e.g., NAD⁺/NADH).
Let \\(A_t, B_t, C_t\\) be the nonnegative integer counts of A, B, and C **after** completing tick \\(t\\).
You are given fixed initial counts and a regeneration period:
- \\(A_0 = {args.A0}\\), \\(B_0 = {args.B0}\\), \\(C_0 = {args.C0}\\)
- Regeneration period \\(k = {k}\\)

For **each discrete tick** \\(t = 1,2,\\dots,n\\) (with \\(n={t}\\)), apply the following **biochemical rule order**:

1) **Reaction (consumes cofactor)** — if both substrate and cofactor are available:
   - If \\(A_{{t-1}} > 0\\) **and** \\(C_{{t-1}} > 0\\), then one catalytic turnover occurs:
     \\[
     A_t = A_{{t-1}} - 1,\\quad B_t = B_{{t-1}} + 1,\\quad C_t = C_{{t-1}} - 1.
     \\]
   - Otherwise, no reaction this tick:
     \\[
     A_t = A_{{t-1}},\\ B_t = B_{{t-1}},\\ C_t = C_{{t-1}}.
     \\]

2) **Cofactor regeneration (post-reaction)** — models an external respiratory/oxidative cycle returning the cofactor to its usable form at fixed intervals:
   - If \\(t \\bmod k = 0\\), then **after** the reaction stage:
     \\[
     C_t \\leftarrow C_t + 1.
     \\]

All updates are integer and at most \\(\\pm 1\\) per tick (“min/+=1” granularity).  
**Output** the product count \\(B_n\\) after completing exactly \\(n={t}\\) ticks (i.e., after applying the regeneration rule at tick \\(n\\))."""

        data_line = {
            "idx": t,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt_ans
        }
        dataset.append(data_line)

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
