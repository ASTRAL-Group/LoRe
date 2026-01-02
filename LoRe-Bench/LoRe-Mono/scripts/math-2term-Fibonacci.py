"""
Generate order-2 nonlinear recurrence modulo with alternating +/− rule (return x_n)
"""
import argparse
import json
from pathlib import Path

# 保持数据格式不变：字段名与结构一致
TASK_TYPE = "linear-monotonicity-altpm"  # 为了完全兼容下游读取逻辑，字段名与原值保持不变
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"


def phi(z: int, M: int) -> int:
    """
    A mild nonlinear transform. We use (z + 1)^2 modulo M.
    Returning it modulo M is safe because C * (z^2) mod M ≡ C * ((z^2 mod M)) mod M.
    """
    return ((z + 1) * (z + 1)) % M


def next_term_alt_pm(step_idx: int, x_k: int, x_km1: int, A: int, B: int, C: int, M: int) -> int:
    """
    Compute ONE update for the sequence under an alternating rule with a parity-dependent nonlinear boost.

    Definitions:
      - We count updates by t = 1, 2, 3, ...
      - Update t takes (x_k, x_{k-1}) and produces x_{k+1}.
      - By convention, t = 1 is the update that produces x_2 from (x_1, x_0).

    Alternating rule (parity of t), with a nonlinear term:
      - Nonlinear map:  φ(z) = (z + 1)^2 (computed modulo M).
      - If t is odd:   x_{k+1} ≡  A*x_k + B*x_{k-1} + C*φ(x_k)    (mod M)
      - If t is even:  x_{k+1} ≡  A*x_k - B*x_{k-1} + C*φ(x_{k-1}) (mod M)

    Inputs:
        step_idx : t (the 1-based update index producing x_{k+1})
        x_k      : current term x_k
        x_km1    : previous term x_{k-1}
        A, B, C  : integer coefficients (C weights the nonlinear boost)
        M        : positive modulus
    Returns:
        x_{k+1} as a non-negative integer in [0, M-1].
    """
    if step_idx % 2 == 1:  # odd step => plus and φ on x_k
        val = A * x_k + B * x_km1 + C * phi(x_k, M)
    else:                  # even step => minus and φ on x_{k-1}
        val = A * x_k - B * x_km1 + C * phi(x_km1, M)
    return val % M  # Python's % yields a non-negative remainder


def main():
    parser = argparse.ArgumentParser(
        description="Generate jsonl for an order-2 nonlinear recurrence modulo problem with alternating +/- rule (return x_n)."
    )
    parser.add_argument(
        "--num_step", type=int, default=30,
        help="Number of records to generate, starting from n = 2 (default: 30, i.e., n = 2..31)."
    )
    parser.add_argument(
        "--out_path", type=str, default="linear-mono-math-Fibonacci.jsonl",
        help="Path to output .jsonl file (default: linear-monotonicity-altpm.jsonl)"
    )
    args = parser.parse_args()

    # Fixed parameters for this dataset (same A,B,M,x0,x1; add C for nonlinearity)
    A, B = 8, 5          # linear coefficients
    C = 3                # nonlinear coefficient (mild but noticeable)
    M = 73               # modulus (prime is convenient)
    x0 = 68
    x1 = 55

    dataset = []

    # Running state so each line outputs the ground-truth x_n for its n.
    prev2 = x0  # x_{k-1}
    prev1 = x1  # x_{k}

    # Emit records for n = 2, 3, ..., 1 + num_step.
    for i in range(args.num_step):
        t = i + 1        # update index (t = 1 produces x_2)
        n = i + 2        # target term index

        # Perform ONE alternating update with the nonlinear boost to get x_n
        x_next = next_term_alt_pm(t, prev1, prev2, A, B, C, M)

        # Slide the window
        prev2, prev1 = prev1, x_next

        # Build a clear, self-contained task statement in English
        task_text = f"""Given an integer \\(n={n}\\), consider the order-2 recurrence over integers modulo {M} with an alternating update rule and a mild nonlinear term.
You are given the initial values
\\[
x_0 = {x0},\\quad x_1 = {x1}.
\\]

We update the sequence one step at a time. Let \\(t = 1,2,3,\\dots\\,n) denote the update index, where \\(t=1\\) is the update that produces \\(x_2\\) from \\((x_1, x_0)\\).
At each update \\(t\\), compute \\(x_{{k+1}}\\) from \\((x_k, x_{{k-1}})\\) using the parity of \\(t\\):

- Define the nonlinear map \\(\\varphi(z) = (z + 1)^2\\). (You may reduce intermediate values modulo {M} at any time.)

- **Odd step (t odd):**
  \\[
  x_{{k+1}} \\equiv {A}x_k + {B}x_{{k-1}} + {C}\\,\\varphi(x_k) \\pmod{{{M}}}.
  \\]

- **Even step (t even):**
  \\[
  x_{{k+1}} \\equiv {A}x_k - {B}x_{{k-1}} + {C}\\,\\varphi(x_{{k-1}}) \\pmod{{{M}}}.
  \\]

For clarity, the first two updates are:
\\[
\\begin{{aligned}}
t=1:\\;& x_2 \\equiv {A}x_1 + {B}x_0 + {C}\\,\\varphi(x_1) \\pmod{{{M}}},\\\\
t=2:\\;& x_3 \\equiv {A}x_2 - {B}x_1 + {C}\\,\\varphi(x_1) \\pmod{{{M}}}.
\\end{{aligned}}
\\]

Apply exactly \\(n-1\\) updates starting from \\(x_0, x_1\\) to reach \\(x_n (n={n})\\), and **return \\(x_{n}\\)** as a single non-negative integer in \\([0, {M-1}]\\).

Conventions:
- All modular reductions are taken modulo {M} and return a non-negative remainder.
- The alternating rule depends on the **update index** \\(t\\).
- Output only the integer value of \\(x_n\\) (no extra text)."""

        data_line = {
            "idx": i + 1,
            "type": TASK_TYPE,  # 字段名与位置保持不变
            "task": task_text,  # 英文任务说明更详细
            "gt_ans": int(x_next),
        }
        dataset.append(data_line)

    # Ensure output directory exists
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Save to JSONL
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(dataset)} records to {out_file.name} (n ranges from 2 to {1 + args.num_step}).")


if __name__ == "__main__":
    main()
