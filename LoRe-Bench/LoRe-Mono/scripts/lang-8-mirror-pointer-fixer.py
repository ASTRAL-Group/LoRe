"""
Generate palindrome pointer-fixer data: two-pointer mirror repair on a word
"""
import argparse
import json

import numpy as np  # kept for parity with the template (not required)
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "palindrome-pointer-fixer"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# ---------------------------
# Core mechanics
# ---------------------------

def build_mirror_map():
    """
    Define the mirror pairs and self-mirroring letters.
    You can expand this as needed; any missing character mirrors to itself.
    """
    pairs = [('b', 'd'), ('p', 'q')]
    self_chars = list("aomnxyzc ehilstuvwxyz".replace(" ", ""))  # common self-mirroring letters (loose set)

    mirror = {}
    for a, b in pairs:
        mirror[a] = b
        mirror[b] = a
    for ch in self_chars:
        mirror[ch] = ch
    return mirror, pairs

def first_unmatched_pair(word, mirror):
    """
    Return (i, j) indices (0-based) of the first pair from the left that doesn't mirror-match.
    If all pairs are matched, return None.
    """
    m = len(word)
    for i in range(m):
        j = m - 1 - i
        if word[i] != mirror.get(word[j], word[j]):
            return i, j
    return None

def run_pointer_machine(w0: str, steps: int, mirror: dict) -> str:
    """
    Run exactly `steps` edits of the pointer-based mirror repair machine,
    starting with L=1, R=len(w0) (user-facing 1-based; internally 0-based).
    """
    w = list(w0)
    m = len(w)

    # 0-based cursors (but the TASK TEXT will specify cursors are 1-based)
    L = 0
    R = m - 1

    for _ in range(steps):
        left = w[L]
        right = w[R]
        # If not a mirror-match: overwrite the right with mirror(left)
        if left != mirror.get(right, right):
            w[R] = mirror.get(left, left)
        else:
            # If mirror-match: overwrite the left with mirror(right) (usually no visible change)
            w[L] = mirror.get(right, right)

        # Move the cursors inward
        L += 1
        R -= 1

        # Finished a sweep? Wrap to the first still-unmatched pair (if any)
        if L > R:
            um = first_unmatched_pair(w, mirror)
            if um is None:
                # Everything already mirror-matches; resetting is fine—further edits won’t change the word
                L, R = 0, m - 1
            else:
                L, R = um

    return "".join(w)

# ---------------------------
# Dataset writer
# ---------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate palindrome pointer-fixer tasks (mirror-repair machine)")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of records to generate; each record uses n = 1..num_step")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-8-mirror-pointer-fixer.jsonl",
                        help="Path to output .jsonl file")
    args = parser.parse_args()

    # Initial word and mirror map used for all tasks
    init_word = "bdpqamqxtvasdifuhasdgnkjasdfoisapoqewzxcvidenvdsckjvbxzcber"  # feel free to change this seed word
    mirror_map, mirror_pairs = build_mirror_map()
    pairs_text = ", ".join([f"{a}↔{b}" for a, b in mirror_pairs])

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    dataset = []

    for i in range(args.num_step):
        step = i + 1
        final_word = run_pointer_machine(init_word, step, mirror_map)

        task_text = f"""You will operate a simple two-pointer “mirror repair” machine that nudges a word toward a mirror-palindrome.

Start with this word:
- w0 = "{init_word}"

Mirror rule:
- Mirror pairs: {pairs_text}.
- Any character not listed mirrors to itself.
- Two letters “mirror-match” when the left letter equals the mirror of the right letter.

Cursors (indexing):
- Use 1-based positions. L starts at 1 (the first letter) and R starts at len(w0) (the last letter).

Each step does exactly this:
1) Look at the two letters under L and R.
   • If they do NOT mirror-match, overwrite the RIGHT letter with mirror(LEFT letter).
   • Otherwise (they mirror-match), overwrite the LEFT letter with mirror(RIGHT letter).
2) Move the cursors inward: L ← L + 1, R ← R − 1.
3) If L passes R, you’ve finished a sweep:
   • Scan from the left to find the first pair (i, j) that still doesn’t mirror-match (where j = len(word) − i + 1).
   • If such a pair exists, set L ← i and R ← j and keep going.
   • If every pair already mirror-matches, you may reset L=1 and R=len(word) and continue—further steps won’t change the word.

Your task:
- Run exactly n = {step} {"steps" if step>1 else 'step'} starting from w0 and the initial cursors (L=1, R=len(w0)).
- Return the final word after these n = {step} {"steps" if step>1 else 'step'} as plain text (just the word, no extra commentary)."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": final_word
        }
        dataset.append(data_line)

    # Save all data_line records to a .jsonl file
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
