"""
Generate alternating RLE task data (Scheme C):
Odd steps:   for each run d^k -> decimal(k) + d
Even steps:  for each run d^k -> decimal(k)
Then sum digits of S_n modulo mod_num.
"""
import argparse
import json
from pathlib import Path

TASK_TYPE = "rle-alt-odd_len_digit-even_len-sum-mod"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"


def rle_len_only_next(s: str) -> str:
    """
    Even-step transform (Length only):
    Split s into maximal runs of identical digits and replace each run by
    the base-10 length of that run (no leading zeros). Concatenate in order.

    Examples:
      "7777"        -> "4"
      "0000000000"  -> "10"
      "3322251"     -> "2311"   # "33","222","5","1" -> "2","3","1","1"
    """
    if not s:
        return s
    out = []
    i, n = 0, len(s)
    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1
        out.append(str(j - i))
        i = j
    return "".join(out)


def rle_len_digit_next(s: str) -> str:
    """
    Odd-step transform (Length + Digit):
    Split s into maximal runs of identical digits. For each run d^k, output the
    decimal representation of k (no leading zeros) immediately followed by d.

    Examples:
      "7777"        -> "47"          # k=4 then digit 7
      "0000000000"  -> "100"         # k=10 then digit 0
      "3322251"     -> "23321511"    # "33","222","5","1" -> "23","32","15","11"
    """
    if not s:
        return s
    out = []
    i, n = 0, len(s)
    while i < n:
        j = i + 1
        d = s[i]
        while j < n and s[j] == d:
            j += 1
        k = j - i
        out.append(str(k))
        out.append(d)
        i = j
    return "".join(out)


def sum_digits_mod(s: str, mod_num: int) -> int:
    """Treat each character in s as a decimal digit; sum them and return sum % mod_num."""
    total = 0
    for ch in s:
        total += ord(ch) - 48  # ord('0') == 48
    return total % mod_num


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSONL for alternating RLE (odd: length+digit, even: length-only)"
    )
    parser.add_argument(
        "--num_step", type=int, default=30,
        help="Number of task instances; instance k uses n=k (default: 30)"
    )
    parser.add_argument(
        "--out_path", type=str, default="linear-mono-math-rle-length-digit-encoding.jsonl",
        help="Path to output .jsonl file (default: linear-mono-math-rle-alt-oddA-evenL.jsonl)"
    )
    args = parser.parse_args()

    # You can change these defaults as needed.
    init_digits = "339993422222"
    mod_num = 97

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    dataset = []

    # Build S1, S2, ...; instance k uses S_k. We keep a rolling current string.
    curr = init_digits
    for i in range(args.num_step):
        step = i + 1  # this instance uses n = step

        # Apply the alternating rule for this step:
        if step % 2 == 1:  # odd step: Length + Digit
            curr = rle_len_digit_next(curr)
        else:              # even step: Length only
            curr = rle_len_only_next(curr)

        print(curr)

        # Ground truth for this instance: sum of digits of S_step modulo mod_num
        gt = sum_digits_mod(curr, mod_num)

        # English task text (clear and self-contained)
        task_text = f"""\
You are given:
- Initial digit string S0 = "{init_digits}" (characters are '0'..'9' only)
- Number of iterations n = {step}
- Modulus mod_num = {mod_num}

We define two transforms on any digit string S, both operating on maximal runs of identical digits:

1) Odd-step transform R_odd (Length + Digit):
   For each run consisting of digit d repeated k times (i.e., d^k),
   write the base-10 decimal representation of k (no leading zeros),
   immediately followed by the digit d. Concatenate these pieces from left to right.

2) Even-step transform R_even (Length only):
   For each run d^k, write only the base-10 decimal representation of k (no leading zeros).
   Concatenate the lengths from left to right.

Iteration:
- Starting from S0, apply exactly n transforms, alternating by step parity:
  S1 = R_odd(S0), S2 = R_even(S1), S3 = R_odd(S2), and so on.
  In general, if t is odd use R_odd; if t is even use R_even, producing S_t.

Worked example (two steps):
- Let S0 = "3322251".
  · Odd step (R_odd):  S1 = "23321511"   ("33"→"23", "222"→"32", "5"→"15", "1"→"11")
  · Even step (R_even): S2 = "121112"    (run lengths of S1 concatenated)

Objective:
- Treat every character in S_{step} as a decimal digit and sum them; call the result sum.
- Output a single integer: sum mod {mod_num}.

Notes:
- Run lengths can be multi-digit (e.g., k=10 yields the two characters '1' and '0').
- No separators are used at any time; all outputs are raw digit strings.
Return only the final integer."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(gt)
        }
        dataset.append(data_line)

    # Save to .jsonl
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_file.name}")


if __name__ == "__main__":
    main()
