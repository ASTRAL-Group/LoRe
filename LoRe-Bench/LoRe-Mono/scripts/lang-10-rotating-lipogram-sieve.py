"""
Generate rotating lipogram-sieve data: cycle banned-letter sets and scan a circular word list with a 0-based cursor
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "rotating-lipogram-sieve"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def find_next_word(W, banned_set, cursor):
    """
    From cursor (inclusive), scan forward on W (treated as circular) to find
    the first word that contains NONE of the letters in banned_set.
    Return (word, next_cursor). If no such word exists, return (None, cursor).
    """
    n = len(W)
    for k in range(n):
        i = (cursor + k) % n
        if set(W[i]).isdisjoint(banned_set):
            return W[i], (i + 1) % n
    return None, cursor

def main():
    parser = argparse.ArgumentParser(description="Generate dataset for the rotating banned-letters lipogram sieve")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps (and records) to generate; step t returns w_t (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-10-rotating-lipogram-sieve.jsonl",
                        help="Path to output .jsonl file (default: rotating-lipogram-sieve.jsonl)")
    args = parser.parse_args()

    # Fixed word list (order matters) and rotating banned-letter sets.
    # The word list is treated as CIRCULAR, and positions are 0-based.
    W = [
        "mango", "steel", "drip", "knot", "glyph", "brunch",
        "flare", "sprint", "mock", "proud", "mint", "roam",
        "brrr", "sky", "lynx",
        "cable", "pearl", "vivid", "crown", "flute", "march",
        "stork", "blend", "quartz", "prism", "lofty", "amber",
        "climb", "creek", "board", "stain", "flock", "mirth",
        "quote", "plain", "spore", "thrum", "crisp", "glare",
        "brown", "smelt", "trick", "storm", "plume", "crave",
        "gnash", "spike", "froth", "clout", "spare", "brisk",
        "cloud", "blade", "grain", "syrup", "crypt", "rhythm",
        "sly", "spry", "lynch", "sylph", "myth", "shy",
        "trump", "gloss", "arbor", "druid", "mauve", "oxide",
        "perch", "grind", "candor", "elope", "irony", "umbra",
        "shorn", "tweak", "grove", "plush", "vapor", "ember",
        "scion", "wring", "blunt", "croft", "smirk", "dowel"
    ]
    # Cycle through these, step by step, then wrap back to the first:
    B_list = [
        set("a"),  # ban 'a'
        set("e"),  # ban 'e'
        set("i"),  # ban 'i'
        set("o"),  # ban 'o'
        set("u"),  # ban 'u'
    ]
    r = len(B_list)

    # Cursor starts at p0 (0-based index).
    p0 = 0
    cursor = p0
    dataset = []

    # Helpful string forms for the task text
    W_json = json.dumps(W, ensure_ascii=False)
    B_json = json.dumps([sorted(list(s)) for s in B_list], ensure_ascii=False)

    # We generate step-by-step: at record t we output w_t, carrying the evolving cursor.
    for i in range(args.num_step):
        step = i + 1
        banned = B_list[i % r]
        word, next_cursor = find_next_word(W, banned, cursor)
        if word is None:
            gt_ans = "NO VALID WORD"
        else:
            gt_ans = word
            cursor = next_cursor  # advance for the next record

        print(gt_ans)

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": (
                f"""Rotating Lipogram Sieve (plain-language spec)

You are given:
- A word list W in a fixed order, treated as a circle (after the last word, continue from the first again).
- A ring of banned-letter sets B that repeats in order step by step.
- A cursor p0 that marks where to start scanning in W.
- A step count N.

All positions use 0-based indexing. Scanning is inclusive of the current cursor position.

For this instance:
- W = {W_json}
- B (in order, then repeats) = {B_json}
- p0 = {p0}
- N = {step}

What to do (one step at a time):
1) Think of W as circular and keep a cursor that starts at p0 (0-based).
2) On each step, use the next banned set in B (go in order and wrap to the start when you reach the end).
3) Starting from the cursor (inclusive), scan forward through W (wrapping around as needed) to find the FIRST word that contains NONE of the letters in the active banned set.
4) Pick that word as this step’s output, then move the cursor to the slot immediately AFTER that word (still 0-based, wrapping around the list length).
5) Repeat until you have picked exactly N words in total.

Your task:
Return ONLY the N-th picked word (w_N) as a plain string. Do not include explanations or extra text.

If during any step every word is blocked (i.e., all contain at least one banned letter), return the exact string "NO VALID WORD" instead (this should not occur with the data above)."""
            ),
            "gt_ans": gt_ans
        }
        dataset.append(data_line)

    # Save to .jsonl
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
