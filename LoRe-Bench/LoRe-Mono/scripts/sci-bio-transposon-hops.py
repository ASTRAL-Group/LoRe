"""
Generate transposon-hop data: 1D circular genome with parity-dependent hops.
After N steps, split the genome into two halves and interpret each half as a
big-endian binary integer; return the decimal sum of these two integers.
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np  # kept for parity with the original template (not strictly required)

TASK_TYPE = "transposon-hops-binary-halves-sum"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"


def update_once(d, i, step_idx, hop_table):
    """
    Perform exactly one step of the transposon hopping process.

    Rules (0-based indices, L = len(d)):
      - Let Δ = hop_table['odd'] if step_idx is odd; otherwise hop_table['even'].
        Δ ∈ {-2, -1, +1, +2}.
      - If d[i] == 1 (the head is on a transposon):
          * Compute j = (i + Δ) mod L   (wrap-around on the genome circle).
          * Swap d[i] and d[j] (the transposon at i "hops" to j).
          * Set the head to i <- j.
        Else (d[i] == 0):
          * Move the head rightwards (i -> i+1 -> i+2 -> ...) until the first index r
            with d[r] == 1 is found; this search DOES NOT wrap.
          * If such r exists, set i <- r; otherwise keep i unchanged and leave d unchanged.

    Returns:
      d (list[int]): updated genome bitstring after one step
      i (int): updated head index
    """
    L = len(d)
    if d[i] == 1:
        delta = hop_table["odd"] if (step_idx % 2 == 1) else hop_table["even"]
        j = (i + delta) % L
        d[i], d[j] = d[j], d[i]
        i = j
    else:
        r = i + 1
        while r < L and d[r] != 1:
            r += 1
        if r < L:
            i = r
        # else: i unchanged, d unchanged
    return d, i


def bits_to_int(bits):
    """
    Interpret a sequence of bits as a big-endian binary integer.
    Example: [1,0,1] -> 5 because 1*2^2 + 0*2^1 + 1*2^0.
    """
    val = 0
    for b in bits:
        val = (val << 1) | int(b)
    return int(val)


def binary_halves_sum(d):
    """
    Split d into two contiguous halves at mid = floor(L/2):
      Left  = d[0 : mid]
      Right = d[mid : L]
    Interpret each as big-endian binary and return their decimal sum.
    """
    L = len(d)
    mid = L // 2
    left  = d[:mid]
    right = d[mid:]
    return bits_to_int(left) + bits_to_int(right)


def build_task_text(N, L, d0, i0, hop_table):
    """
    Create a clear, self-contained English task description for step N.
    """
    d0_str = "[" + ", ".join(str(int(x)) for x in d0) + "]"
    odd_delta = hop_table["odd"]
    even_delta = hop_table["even"]

    return (
        f"Consider a circular DNA of length L={L} represented by a 0/1 bitstring d[0..L-1], "
        f"where 1 marks a transposon and 0 marks an empty site. A transposase head (a pointer) "
        f"sits at index i₀={i0}. The initial genome is d₀={d0_str}. The hop policy depends on "
        f"step parity: on odd-numbered steps use Δ_odd={odd_delta}, on even-numbered steps use "
        f"Δ_even={even_delta}, with Δ drawn from {{-2, -1, +1, +2}}.\n\n"
        f"Index arithmetic for hops uses wrap-around (mod L). Searches to the right do NOT wrap.\n\n"
        f"At each step t = 1..N (1-indexed):\n"
        f"1) If the head is on a transposon (d[i_t] == 1), let Δ = Δ_odd if t is odd else Δ_even. "
        f"   Compute j = (i_t + Δ) mod L, swap the bits at i_t and j (the transposon at i_t hops to j), "
        f"   and set the next head position i_(t+1) = j.\n"
        f"2) Otherwise (d[i_t] == 0), move the head rightward (i_t+1, i_t+2, ...) until the first index r "
        f"   with d[r] == 1 is found; if such r exists set i_(t+1) = r; if none exists, keep i_(t+1) = i_t "
        f"   and leave d unchanged for this step.\n\n"
        f"After exactly N={N} steps, split DNA d_{N} at mid = floor(L/2) into two contiguous halves:\n"
        f"  Left  = d_N[0 .. mid-1],  Right = d_N[mid .. L-1].\n"
        f"Interpret each half DNA sequence as a big-endian binary integer (index increasing from left to right is "
        f"most-significant to least-significant; e.g., [1,0,1] = 5, where 1 marks a transposon and 0 marks an empty site). Return the base-10 integer\n"
        f"  y = int(Left) + int(Right).\n"
        f"Indices are 0-based; step parity uses t starting at 1."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate transposon-hop tasks and answers (sum of binary halves after N steps)."
    )
    parser.add_argument(
        "--num_step",
        type=int,
        default=30,
        help="Number of steps to simulate to generate records for N=1..num_step (default: 30)",
    )
    parser.add_argument(
        "--out_path",
        type=str,
        default="linear-mono-sci-bio-transposon-hops.jsonl",
        help="Path to output .jsonl file (default: transposon-hops-binary-halves.jsonl)",
    )
    args = parser.parse_args()

    # Fixed initial configuration (analogous to fixed init in the original template)
    d0 = [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1]  # L = 16
    L = len(d0)
    i0 = 1  # points to a 1 initially
    hop_table = {"odd": +2, "even": -1}  # Δ depends on step parity

    # Ensure output dir exists
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare dataset
    dataset = []
    d = deepcopy(d0)
    i = int(i0)

    for step in range(1, args.num_step + 1):
        # One step of the process
        d, i = update_once(d, i, step, hop_table)

        # Ground-truth: sum of binary values of two halves after 'step' steps
        y = binary_halves_sum(d)

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": build_task_text(step, L, d0, i0, hop_table),
            "gt_ans": int(y),
        }
        dataset.append(data_line)

    # Save to .jsonl
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(dataset)} records to {args.out_path}")


if __name__ == "__main__":
    main()
