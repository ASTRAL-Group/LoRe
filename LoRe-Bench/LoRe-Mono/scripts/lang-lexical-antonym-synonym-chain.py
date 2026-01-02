"""
Generate the synonym–antonym (duality pairs) word-walk data:
swap on odd-initial letters, otherwise follow the single-valued synonym table
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "lexical-antonym-synonym-chain"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# --- Problem tables (example set; deterministic and closed over the words below) ---

# Duality pairs: each pair is two-way (x <-> y). All words are lowercase.
PAIRS_LIST = [
    ("true", "false"),
    ("left", "right"),
    ("bright", "dark"),
    ("near", "far"),
    ("rich", "poor"),
    ("visible", "hidden"),
    ("thin", "fat"),
    ("heavy", "light"),
    ("domestic", "foreign"),
    ("fiction", "nonfiction"),
    ("narrow", "broad"),
    ("present", "past"),
    ("profit", "loss"),
    ("push", "pull"),
    ("borrower", "lender"),
    ("leader", "follower"),
    ("birth", "death"),
    ("victory", "defeat"),
    ("neutral", "biased"),
    ("positive", "negative"),
]

# Build a two-way lookup from PAIRS_LIST
PAIRS_MAP = {}
for a, b in PAIRS_LIST:
    PAIRS_MAP[a] = b
    PAIRS_MAP[b] = a

# Single-valued synonym table (each word maps to exactly one word, all within domain)
SYN_MAP = {
    "bright": "light",
    "light": "visible",
    "visible": "true",
    "true": "positive",
    "positive": "victory",
    "victory": "profit",
    "profit": "rich",
    "rich": "leader",
    "leader": "borrower",
    "borrower": "present",
    "present": "near",
    "near": "narrow",
    "narrow": "thin",
    "thin": "domestic",
    "domestic": "fiction",
    "fiction": "birth",
    "birth": "left",
    "left": "push",
    "push": "heavy",
    "heavy": "dark",
    "dark": "hidden",
    "hidden": "false",
    "false": "negative",
    "negative": "defeat",
    "defeat": "loss",
    "loss": "poor",
    "poor": "lender",
    "lender": "past",
    "past": "far",
    "far": "broad",
    "broad": "fat",
    "fat": "foreign",
    "foreign": "nonfiction",
    "nonfiction": "death",
    "death": "right",
    "right": "pull",
    "pull": "neutral",
    "neutral": "follower",
    "follower": "biased",
    "biased": "bright",  # closes the 40-cycle
}

# Letters are split into two classes. If a word starts with a letter in ODD_LETTERS,
# we flip via PAIRS; otherwise we use SYN_MAP.
ODD_LETTERS = set("acegikmoqsuwy")  # the rest of a–z are the "even" class

def update_word(word: str) -> str:
    """
    One step of the word-walk:
      - If the first letter (lowercased) is in ODD_LETTERS -> swap to its paired word via PAIRS_MAP.
      - Else -> replace the word using SYN_MAP.
    Returns the updated word.
    """
    if not word:
        raise ValueError("Empty word encountered in update_word.")
    first = word[0].lower()
    if first in ODD_LETTERS:
        if word not in PAIRS_MAP:
            raise KeyError(f"Word '{word}' not found in PAIRS_MAP when an odd-letter swap was required.")
        return PAIRS_MAP[word]
    else:
        if word not in SYN_MAP:
            raise KeyError(f"Word '{word}' not found in SYN_MAP when a synonym step was required.")
        return SYN_MAP[word]

def main():
    parser = argparse.ArgumentParser(description="Generate synonym–antonym (duality pairs) word-walk dataset")
    parser.add_argument("--num_step", type=int, default=30,
                        help="How many steps N to include (we will create N items with n=1..N) (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-lexical-antonym-synonym-chain.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-language-lexical-antonym-synonym-chain.jsonl)")
    parser.add_argument("--start_word", type=str, default="true",
                        help="Starting word w0 (must be present in the tables) (default: cold)")
    args = parser.parse_args()

    init_word = args.start_word.strip().lower()
    if init_word not in PAIRS_MAP and init_word not in SYN_MAP:
        raise ValueError(f"start_word '{init_word}' is not covered by the provided tables.")

    dataset = []
    current_word = init_word

    for i in range(args.num_step):
        step = i + 1
        # advance exactly one step to build the next example
        current_word = update_word(current_word)

        print(current_word)

        # Compose a clear, non-mathy task description tailored to this setting
        task_text = (
f"""You're going to take a tiny "word walk" using two lookup tables: PAIRS (two-way opposites/duality) and SYN (a single, fixed near-synonym mapping). 
Start from the word w0="{init_word}". Move exactly n={step} {"steps" if step>1 else 'step'}. At each step, do **only one** of the following based on the first letter of the current word:

1) If the first letter (lowercase) is in the ODD set {sorted(ODD_LETTERS)}:
   • **Flip to its partner** using the PAIRS table (pairs are two-way: if A pairs with B, then B pairs with A).
2) Otherwise (the first letter is not in that ODD set, i.e., it's in the EVEN class):
   • **Replace it using the SYN table**, which is single-valued (each word maps to exactly one word). Use the mapping **as-is**, don't invent alternatives.

Keep stepping like this until you've made exactly n moves, then output the final word (lowercase) with no extra text.

Details you must use (copy-paste level exactness):
• PAIRS (two-way):
{PAIRS_LIST}

• SYN (single-valued):
{SYN_MAP}

• Letter classes:
  - ODD letters: {sorted(ODD_LETTERS)}
  - EVEN letters: all other lowercase English letters (a–z) not listed above

Notes:
- All words are lowercase.
- The tables are complete for this task; every lookup you need is present.
- Do not perform any other changes (no stemming, no spelling fixes, no punctuation).
- If n=0 (not in this prompt), you would just return w0 unchanged.

What is the word after exactly n={step} {"steps" if step>1 else "step"} starting from w0="{init_word}"? Output this word as the final answer."""
        )

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": current_word
        }
        dataset.append(data_line)

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
