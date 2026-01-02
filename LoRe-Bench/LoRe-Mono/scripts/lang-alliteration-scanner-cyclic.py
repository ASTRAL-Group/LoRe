"""
Generate the alliterative scanner data: cyclic per-word letter, stepwise scoring, modulo at the end
"""
import argparse
import json
import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "alliteration-scanner-cyclic-harder"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# -------------------------------
# Problem mechanics (implementation)
# -------------------------------

def _char_cyclic(word: str, k: int) -> str:
    """
    Return the k-th character of `word`, wrapping around when k exceeds length.
    k is 1-based. Assumes word is non-empty.
    """
    idx = (k - 1) % len(word)
    return word[idx]

def update_scanner(state: dict, tokens: list[str], mod_num: int) -> dict:
    """
    Advance the alliteration scanner by exactly one step.

    State fields:
        - t:     number of steps already performed (integer, starts at 0)
        - score: accumulated integer score (starts at 0)
        - prev:  the letter used at the previous step (None for the very first step)
        - cnt:   per-token visit counts (numpy array of shape [L], all zeros initially)

    Rules implemented:
        - Move left-to-right across tokens; after the last token, loop back to the first.
        - When visiting token i for the k-th time, use its k-th character (lowercased),
          where the character index wraps around within that word.
        - Scoring:
            * Step 1: add +1 (no alliteration bonus yet).
            * Step >= 2: compare the current letter to the previous step's letter:
                - same letter → +2
                - different   → +1
    """
    L = len(tokens)
    t_next = state["t"] + 1
    i = (t_next - 1) % L  # 0-based index into tokens

    # this token's visit count becomes k
    state["cnt"][i] += 1
    k = int(state["cnt"][i])

    cur_letter = _char_cyclic(tokens[i], k).lower()

    if t_next == 1:
        state["score"] += 1
    else:
        if state["prev"] is not None and cur_letter == state["prev"]:
            state["score"] += 2
        else:
            state["score"] += 1

    state["prev"] = cur_letter
    state["t"] = t_next
    return state

# -------------------------------
# Dataset writer
# -------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate alliteration-scanner tasks (cyclic per-word letter).")
    parser.add_argument("--num_step", type=int, default=30,
                        help="How many steps to run (also how many items to emit, 1..num_step). Default: 30")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-alliteration-scanner-cyclic.jsonl",
                        help="Path to output .jsonl file (default: alliteration-scanner-cyclic.jsonl)")
    args = parser.parse_args()

    # A single poetic line, tokenized (each token must be non-empty).
    tokens = ["Bold", "dogs", "brown", "arrow", "allow"]
    mod_num = 31

    # Initial state (before any step):
    state = {
        "t": 0,
        "score": 0,
        "prev": None,
        "cnt": np.zeros(len(tokens), dtype=int)
    }

    dataset = []

    for i in range(args.num_step):
        # Advance by one step
        state = update_scanner(state, tokens, mod_num)

        # Ground-truth answer for N = step is total_score % mod_num
        step = state["t"]
        gt = int(state["score"] % mod_num)

        # Task text (clear, alliteration-flavored, minimal math)
        task_text = f"""Alliteration Scoring — “letter-by-letter, round-and-round”

You are given one line of verse, already split into words:
T = {tokens}

We will “walk the line” for N = {step} {"steps" if step > 1 else "step"}. Start at the first word, move right one word per step,
and after the last word loop back to the first, continuing until you have taken N = {step} {"steps" if step > 1 else "step"}.

Per-word letter choice (the heart of the task):
• Each word keeps its own visit counter. The first time you meet a word, listen to its 1st character; the next time you meet that same word, listen to its 2nd character; and so on.
• If you run past the end of the word, wrap around to its beginning (cyclic pick).
• Before comparing, lowercase the character you just listened to. (Non-letters remain unchanged by lowercasing.)

Scoring as you go:
• Step 1: add 1 point — it’s a fresh start, no alliteration bonus yet.
• From Step 2 onward: compare the current character to the one you heard on the immediately previous step:
  – If the two characters match, add 2 points (an alliterative hit).
  – Otherwise, add 1 point.

State update:
• After each step, remember the character you just used; it becomes the “previous character” for the next step.
• Each word’s visit counter advances only when that word is visited.

At the end of N = {step} {"steps" if step > 1 else "step"}, report a single integer:
(total points) modulo {mod_num} as the final answer.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt
        }
        dataset.append(data_line)

    # Save all data_line records to a .jsonl file
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
