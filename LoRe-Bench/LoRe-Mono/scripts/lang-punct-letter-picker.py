"""
Punctuation-guided letter picker: simulate a circular cursor over text with punctuation jumps
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "punctuation-guided-letter-picker"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# Fixed text T with prime length (71) to discourage short periodic cycles.
# It mixes letters and multiple punctuation types from P so jumps are diverse.
TEXT = "ab,cd.ef!gh?ij;kl:mn,op.qr!st?uv;wx:yz,ab.cd!ef?gh;ij:kl,mn.op!qr?st;uv"

# Punctuation jump table (P and jump)
JUMP_MAP = {
    ",": 2,
    ".": 3,
    "!": 5,
    "?": 7,
    ";": 11,
    ":": 13,
}
PUNCT_SET = set(JUMP_MAP.keys())

def run_picker(T: str, i0: int, N: int, mod_num: int, k: int, jump_map: dict, punct_set: set):
    """
    Simulate the punctuation-guided letter picker:

    - T sits on a circular tape. The cursor index i is ZERO-BASED: the first character is i=0.
    - Start at i = i0. Maintain a string buffer B (initially empty, store lowercase letters),
      and an integer score (initially 0).
    - Repeat steps up to N times, or stop earlier as soon as |B| >= k:
        1) Look at T[i].
        2) If it is a letter (A–Z or a–z):
              - append its lowercase form to B
              - move the cursor one position to the right: i <- i + 1 (wrap to start if needed)
           Else (it is punctuation from P):
              - do NOT append anything
              - jump forward by jump(T[i]) positions: i <- i + jump(T[i]) (with wrap)
              - add jump(T[i]) to score
        3) If after this step |B| >= k, stop immediately.
    - Output:
        * If you stopped because |B| >= k: return the last k letters of B as a lowercase word.
        * Otherwise (took N steps without collecting k letters): return score mod mod_num as an integer.

    Notes:
      - The tape is circular; every cursor move wraps around len(T).
      - Only A–Z/a–z count as letters; everything else in T is punctuation from P.
      - Do not assume any short cycle; simulate exactly as written.
    """
    L = len(T)
    i = i0 % L
    B = []
    score = 0

    for _ in range(N):
        c = T[i]
        if c.isalpha():
            B.append(c.lower())
            i = (i + 1) % L
            if len(B) >= k:
                return "".join(B[-k:])
        else:
            # punctuation
            s = jump_map.get(c, 0)
            i = (i + s) % L
            score += s

    return score % mod_num  # int


def main():
    parser = argparse.ArgumentParser(description="Generate punctuation-guided letter picker tasks")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of task instances to generate (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-punct-letter-picker.jsonl",
                        help="Path to output .jsonl file (default: punct-letter-picker.jsonl)")
    args = parser.parse_args()

    T = TEXT
    L = len(T)
    mod_num = 1_000_003  # large prime to avoid short mod cycles
    dataset = []

    # We vary i0 and k per instance to diversify tasks while keeping N generous.
    for i in range(args.num_step):
        step = i + 1
        i0 = 1                    # wander around the tape
        N = i + 1                  # ample steps; discourages hitting the mod branch accidentally
        k = 20                     # target length between 3 and 6

        # Compute ground-truth answer by simulation
        gt = run_picker(T, i0, N, mod_num, k, JUMP_MAP, PUNCT_SET)

        # Pretty-print jump table for the task text
        jump_items = ", ".join([f"'{p}'→{JUMP_MAP[p]}" for p in [",", ".", "!", "?", ";", ":"]])

        task_text = f"""Punctuation-Guided Letter Picker

You are controlling a tiny cursor that walks around a circular strip of text. The strip never ends: when you step past the last character, you wrap around to the beginning.

Inputs for this instance:
- text T (length {L}): "{T}"
- cursor start index i0 = {i0} (ZERO-BASED: the very first character of T is at index 0)
- maximum steps N = {N}
- target word length k = {k}
- modulus mod_num = {mod_num}
- punctuation set P and jump table: {jump_items}

How to run the picker:
1) Look at the character under the cursor i.
   • If it is a letter (A–Z or a–z): append its LOWERCASE form to the end of buffer B, then move the cursor one position to the right (i ← i + 1, with wraparound).
   • If it is punctuation in P: DO NOT collect anything. Instead, jump forward by jump(c) positions (i ← i + jump(c), with wraparound) and add jump(c) to a running integer score.
2) Stop immediately as soon as the buffer length reaches k. If that never happens, stop after at most N steps.

What to output:
- If you stopped because the buffer reached k letters, output the last k letters of B as a lowercase word (in the order they were collected).
- Otherwise, output the integer value (score mod mod_num).

Important details:
- The cursor index is ZERO-BASED and starts at i0.
- The tape is circular; all cursor moves wrap around len(T).
- Treat letters case-insensitively; only A–Z/a–z are letters. All other characters in T are punctuation from P.
- Do not try to “shortcut” by assuming periodic patterns; just follow the steps exactly.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt  # string (word) or int (score % mod_num), depending on the run
        }
        dataset.append(data_line)

    # Ensure output directory exists
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Save all records to a .jsonl file
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")


if __name__ == "__main__":
    main()
