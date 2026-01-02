"""
Generate the Test Output Prediction data: 8-byte deck (perfect out-shuffle + position ADD mod 32)
"""
import argparse
import json

from pathlib import Path

TASK_TYPE = "deck8-outshuffle-add"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_shuffle_add(state, i=None):
    """
    Update rule (pure function, 0-based indexing):

    State is a tuple (deck, t):
        - deck: list of 8 integers in [0, 255]
        - t:    non-negative integer step counter

    One update step does:
        1) Perfect out-shuffle (0-based positions):
           [0,1,2,3,4,5,6,7] -> [0,4,1,5,2,6,3,7]
        2) Position-wise ADD with step-dependent offset:
           For each index i in 0..7:
               deck[i] = (deck[i] + t + i) % 32
        3) Increment t by 1

    Args:
        state: (deck, t)
        i: optional iteration index (accepted for template compatibility; not used)

    Returns:
        (new_deck, t+1)
    """
    deck, t = state
    deck = list(deck)
    assert len(deck) == 8, "deck must have length 8"
    # Step 1: out-shuffle (0-based)
    deck2 = [deck[0], deck[4], deck[1], deck[5], deck[2], deck[6], deck[3], deck[7]]
    # Step 2: add (t + i) mod 32 at position i (0-based)
    deck3 = []
    for idx, v in enumerate(deck2):
        deck3.append((v + t + idx) % 32)
    # Step 3: bump t
    return (deck3, t + 1)

def main():
    parser = argparse.ArgumentParser(description="Run 8-byte deck updates (out-shuffle + position ADD mod 32) for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of records to generate; record t uses N = t iterations (1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-7-top-deck8-outshuffle-add.jsonl",
                        help="Path to output .jsonl file")
    parser.add_argument("--init_state", type=str, default="0,1,2,3,4,5,6,7",
                        help="Comma-separated 8 integers in [0,255] as the initial deck")
    parser.add_argument("--start_t", type=int, default=0,
                        help="Initial step counter t (non-negative integer)")
    args = parser.parse_args()

    # Parse initial deck
    init_deck = [int(tok.strip()) for tok in args.init_state.split(",") if tok.strip() != ""]
    if len(init_deck) != 8:
        raise ValueError("init_state must contain exactly 8 comma-separated integers")
    for v in init_deck:
        if not (0 <= v <= 255):
            raise ValueError("All deck values must be in [0,255]")

    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1
        if i == 0:
            updated_state = update_shuffle_add((init_deck, args.start_t), i)
        else:
            updated_state = update_shuffle_add(updated_state, i)

        # Ground truth answer for this record: deck values as a space-separated string
        deck_ans, t_now = updated_state
        ANSWER = ' '.join(map(str, deck_ans))
        print(ANSWER)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports).
This is a Code Execution task: run the program, do not rewrite or translate it. Indexing is 0-based.
Return only the value of ANSWER (no other text, no formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run this code exactly as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it with no extra text.

N = {step}  # number of iterations (non-negative integer)
deck = {init_deck!r}  # list of 8 integers in [0, 255]
t = {args.start_t}     # step counter (0-based)

def out_shuffle(arr):
    return [arr[0], arr[4], arr[1], arr[5], arr[2], arr[6], arr[3], arr[7]]

for _ in range(N):
    deck = out_shuffle(deck)
    # ADD with (t + i) % 32 at 0-based index i
    for i in range(8):
        deck[i] = (deck[i] + t + i) % 32
    t += 1  # increment step counter

ANSWER = ' '.join(str(x) for x in deck)
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": ANSWER  # string; judge can compare exact match
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
