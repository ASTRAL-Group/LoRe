"""
Generate the tri-register extreme+xor data: three-register update with max/min/abs, mod p, then conditional XOR; return (a+b+c) mod M
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "tri-register-extreme-xor"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"


def update_registers(registers: np.ndarray, p: int, t: int) -> np.ndarray:
    """
    Perform ONE iteration (step t) of the tri-register update.

    Update order (strict):
        1) Compute u = max(a,b), v = min(b,c), w = |a-c|
        2) Full update modulo p: (a,b,c) := ((u+v)%p, (v+w)%p, (w+u)%p)
        3) Conditional XOR based on t % 3:
               if t % 3 == 0: a = a ^ b
               if t % 3 == 1: b = b ^ c
               if t % 3 == 2: c = c ^ a
       Return the final (a,b,c) for this step.

    Parameters:
        registers: current state as np.array([a, b, c]) of non-negative integers
        p        : the modulus used in step (2)
        t        : the current 1-based step index (affects which register is XORed)

    Returns:
        np.ndarray: next state after completing step t
    """
    a, b, c = (int(registers[0]), int(registers[1]), int(registers[2]))

    # 1) compute u, v, w
    u = max(a, b)
    v = min(b, c)
    w = abs(a - c)
    print(f"[t={t}] u={u}, v={v}, w={w}")

    # 2) modulo-p update
    na = (u + v) % p
    nb = (v + w) % p
    nc = (w + u) % p
    print(f"[t={t}] after mod p: (a,b,c)=({na},{nb},{nc})")

    # 3) conditional XOR
    r = t % 3
    if r == 0:
        na = na ^ nb
        print(f"[t={t}] t%3==0 → a = a ^ b → a={na}")
    elif r == 1:
        nb = nb ^ nc
        print(f"[t={t}] t%3==1 → b = b ^ c → b={nb}")
    else:  # r == 2
        nc = nc ^ na
        print(f"[t={t}] t%3==2 → c = c ^ a → c={nc}")

    nxt = np.array([na, nb, nc], dtype=int)
    print(f"[t={t}] state → {nxt}\n")
    return nxt


def main():
    parser = argparse.ArgumentParser(description="Generate tri-register extreme+xor iterative data")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps (n) to run the tri-register update (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-tri-register-extreme-xor.jsonl",
                        help="Path to output .jsonl file (default: tri-register-extreme-xor.jsonl)")
    args = parser.parse_args()

    # You can change the defaults below to create a different dataset.
    init_registers = np.array([1, 2, 3], dtype=int)  # (a0, b0, c0)
    p = 31       # per-step modulus
    mod_num = 97 # final output modulus M
    dataset = []

    updated_registers = None

    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_registers = update_registers(init_registers, p, step)
        else:
            updated_registers = update_registers(updated_registers, p, step)

        # Ground-truth answer: (a+b+c) mod M after 'step' iterations
        gt_value = int((int(updated_registers[0]) + int(updated_registers[1]) + int(updated_registers[2])) % mod_num)

        a0, b0, c0 = int(init_registers[0]), int(init_registers[1]), int(init_registers[2])

        task_text = f"""Given integer \\(n={step}\\), initial registers \\((a_0,b_0,c_0)=({a0},{b0},{c0})\\), a per-step modulus \\(p={p}\\), and a final modulus \\(M={mod_num}\\).
For \\(t=1,2,\\dots,n\\), perform one round in the **strict order**:

1. Compute
\\[
u_t=\\max(a_{{t-1}},\\,b_{{t-1}}),\\quad
v_t=\\min(b_{{t-1}},\\,c_{{t-1}}),\\quad
w_t=\\lvert a_{{t-1}}-c_{{t-1}}\\rvert.
\\]

2. **First**, do the full modulo-\\(p\\) update (temporary values):
\\[
\\tilde a_t=(u_t+v_t)\\bmod p,\\quad
\\tilde b_t=(v_t+w_t)\\bmod p,\\quad
\\tilde c_t=(w_t+u_t)\\bmod p.
\\]

3. **Then**, apply a conditional bitwise XOR (\\(\\oplus\\), same as `^` in most languages) to obtain \\((a_t,b_t,c_t)\\):
\\[
\\begin{{cases}}
a_t=\\tilde a_t\\oplus\\tilde b_t, & \\text{{if}} t\\equiv 0\\pmod 3;\\\\
b_t=\\tilde b_t\\oplus\\tilde c_t, & \\text{{if}} t\\equiv 1\\pmod 3;\\\\
c_t=\\tilde c_t\\oplus\\tilde a_t, & \\text{{if}} t\\equiv 2\\pmod 3.
\\end{{cases}}
\\]

Repeat until you obtain \\((a_{step},b_{step},c_{step})\\). Finally, return
\\[
x=\\big(a_{step}+b_{step}+c_{step}\\big)\\bmod M.
\\]
as the final answer.

**Notes.**
- Step 2 (the modulo-\\(p\\) update) must be completed before step 3 (the XOR) in every round.
- All values are non-negative integers; XOR acts on the binary representation of non-negative integers.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt_value
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
