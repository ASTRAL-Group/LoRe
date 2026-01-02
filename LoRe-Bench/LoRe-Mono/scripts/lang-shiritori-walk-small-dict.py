"""
Generate Shiritori walk data: small-dictionary tail-to-head walk
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "shiritori-walk-small-dict"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def shiritori_step(current_word, D):
    """
    Take one Shiritori step on dictionary D from the current_word.

    Rules:
      - Next(w): all words in D that START with the last character of w,
                 sorted in standard lexicographic order (Unicode code points).
      - If Next(w) is empty: stay put (w_{t+1} = w_t).
      - Else:
          s = sum of Unicode code points of w (ord(c) for c in w)
          k = s % len(Next(w))   # ZERO-BASED index
          w_{t+1} = Next(w)[k]

    Returns:
      next_word (str)
    """
    if not current_word:
        return current_word

    last_char = current_word[-1]
    candidates = sorted([w for w in D if w and w[0] == last_char])

    if not candidates:
        # stay put
        return current_word

    s = sum(ord(c) for c in current_word)
    k = s % len(candidates)  # ZERO-BASED
    return candidates[k]

def main():
    parser = argparse.ArgumentParser(description="Generate Shiritori walk tasks on a small dictionary")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to run the Shiritori walk (default: 30)")
    parser.add_argument(
        "--out_path",
        type=str,
        default="linear-mono-language-shiritori-walk-small-dict.jsonl",
        help="Path to output .jsonl file (default: shiritori-walk-small-dict.jsonl)",
    )
    args = parser.parse_args()

    # Fixed small dictionary (distinct, lowercase words), and start word in D
    # D = ["am", "me", "eat", "eel", "ear", "egg", "rat", "top", "tap", "pan", "nancy", "yes","sam", "ant", "let"]
    # Fixed small dictionary (26 real words, one per starting letter a..z)
    D = [
        "alas",  # a -> s
        "basic",  # b -> c
        "candid",  # c -> d
        "dill",  # d -> l
        "elf",  # e -> f
        "fang",  # f -> g
        "graph",  # g -> h
        "haji",  # h -> i
        "improv",  # i -> v
        "jazz",  # j -> z
        "kebab",  # k -> b
        "laptop",  # l -> p
        "mule",  # m -> e
        "new",  # n -> w
        "oven",  # o -> n
        "prism",  # p -> m
        "quipu",  # q -> u
        "raj",  # r -> j
        "suq",  # s -> q
        "taco",  # t -> o
        "ugly",  # u -> y
        "vex",  # v -> x
        "war",  # w -> r
        "xyst",  # x -> t
        "yolk",  # y -> k
        "zebra"  # z -> a
    ]

    # Choose an in-cycle start; keep w0 ∈ D
    w0 = "alas"

    # We'll generate a sequence w_0, w_1, ..., and write a task for each n = 1..num_step
    dataset = []
    current_word = w0  # this is w_0

    for i in range(args.num_step):
        # advance one step
        current_word = shiritori_step(current_word, D)
        step = i + 1  # n = number of steps taken so far

        # Build the human-friendly task text (English, plain, and specific to Shiritori)
        task_text = (
            f"Shiritori walk on a small dictionary.\n\n"
            f"You are given:\n"
            f"- A fixed dictionary D (list of distinct lowercase words): {D}.\n"
            f"- A start word w0 in D: \"{w0}\".\n"
            f"- A non-negative integer n={step} telling how many steps to walk.\n\n"
            f"At each step t (t = 1 .. n), do:\n"
            f"1) Build the candidate list Next(w_t): all words in D that START with the last character of w_t. "
            f"   Sort this list in standard lexicographic order (Unicode code points). "
            f"   If this list is empty, you stay where you are forever: set w_(t+1) = w_t and keep doing that for any remaining steps.\n"
            f"2) If Next(w_t) is not empty, compute s = sum of Unicode code points of all characters in w_t, "
            f"   then let k = s mod |Next(w_t)|. Use ZERO-BASED indexing and pick Next(w_t)[k] "
            f"   (this is the (k+1)-th item in human counting) as your next word, i.e., w_(t+1).\n\n"
            f"After exactly n steps, output w_n (just the word). If n=0, output w_0.\n\n"
            f"Notes:\n"
            f"- Do not change letter casing, do not add or remove words, and treat the strings exactly as shown.\n"
            f"- Sorting and indexing are as described above; the index k is ZERO-BASED."
        )

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": current_word,  # the word after exactly 'step' steps
        }
        dataset.append(deepcopy(data_line))

    # Ensure output directory exists
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Save all data_line records to a .jsonl file
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
