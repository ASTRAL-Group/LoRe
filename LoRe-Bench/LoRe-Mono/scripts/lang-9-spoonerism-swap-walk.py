"""
Generate Spoonerism swap-walk data: swap initial consonant clusters, hop by index, return the N-th step's second word
"""
import argparse
import json
from pathlib import Path
from copy import deepcopy

TASK_TYPE = "spoonerism-swap-walk"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# --------- Core Spoonerism helpers ---------
def sort_clusters_longest_first(clusters):
    """Return clusters sorted by length (desc) so longest-prefix wins."""
    return sorted(clusters, key=len, reverse=True)

def initial_cluster(word: str, clusters_sorted):
    """
    Find the initial consonant cluster of `word` by longest-prefix matching
    against `clusters_sorted`. If none matches, return empty string "".
    """
    for c in clusters_sorted:
        if word.startswith(c):
            return c
    return ""

def spooner_step_get_yprime_and_jump(x: str, y: str, clusters_sorted):
    """
    Perform one Spoonerism step on the pair (x, y):
        - take initial clusters c1 (from x), c2 (from y), using longest-prefix
        - swap them: x' = c2 + rest(x), y' = c1 + rest(y)
    Return:
        y_prime (the new second word for this step),
        jump (the index hop = len(x) + len(y), computed from the ORIGINAL x,y)
    """
    c1 = initial_cluster(x, clusters_sorted)
    c2 = initial_cluster(y, clusters_sorted)
    x_rest = x[len(c1):]
    y_rest = y[len(c2):]
    y_prime = c1 + y_rest  # what we need to output for this step
    jump = len(x) + len(y)  # based on ORIGINAL words for this step
    return y_prime, jump

# --------- Task text template (English, clear & linguistics-oriented) ---------
def make_task_text(P, i0, CL, N):
    """
    Create the per-item task text. Indexing explicitly stated as ZERO-BASED.
    """
    phrases_str = "[" + ", ".join([f"({repr(x)}, {repr(y)})" for x, y in P]) + "]"
    cl_str = "[" + ", ".join([repr(c) for c in CL]) + "]"

    return f"""Spoonerism Swap Walk (zero-based indexing)

You’re given:
• A list of two-word phrases P indexed from 0: {phrases_str}
• A starting index i0 = {i0} (0-based cursor into P)
• A set of allowed initial consonant clusters CL = {cl_str}
• A step count N = {N}

At each step, do a classic Spoonerism on the CURRENT pair (x, y) taken directly from P[i]:
1) Find each word’s initial consonant cluster using CL and the **longest prefix** rule.
   - If no cluster applies (e.g., the word begins with a vowel or no CL prefix matches), treat the cluster as the empty string "".
2) Swap those two clusters:
   - Strip the cluster off each word and put the other word’s cluster in front.
   - The second word for this step becomes: y' = (cluster from x) + (y without its own cluster).
   - Example (with CL including "br" and "f"): ("brown", "fairy") → y' = "brairy".
3) Record y' for this step (this is the only thing you output from the step).
4) Jump the cursor to the next phrase using the ORIGINAL x and y lengths (before swapping):
   i ← (i + len(x) + len(y)) mod |P|
   (len counts letters, and indexing of P is zero-based.)
5) Repeat until you have completed N steps, always fetching the next (x, y) fresh from P via the updated cursor i.
   Do **not** write swapped words back into P; P never changes.

Output:
Return the single lowercase word produced as the answer and the second word on the **N-th** step (i.e., the y' from the last swap you perform)."""

def main():
    parser = argparse.ArgumentParser(description="Generate Spoonerism swap-walk tasks and ground truths")
    parser.add_argument("--num_step", type=int, default=30,
                        help="How many task records to generate; record k uses N=k (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-9-spoonerism-swap-walk.jsonl",
                        help="Path to output .jsonl file (default: spoonerism-swap-walk.jsonl)")
    args = parser.parse_args()

    # You can customize the phrases, cluster set, and starting index here.
    # All words should be lowercase alphabetic for simplicity.
    P = [
        ("brown", "orange"),  # 5+6=11
        ("cloud", "animal"),
        ("flake", "flower"),
        ("grape", "silver"),
        ("pride", "island"),
        ("crisp", "artist"),
        ("stone", "spirit"),
        ("blaze", "planet"),
        ("trail", "stream"),
        ("dream", "string"),
        ("skate", "shield"),
        ("screw", "thrush"),
        ("glaze", "butter"),
        ("brink", "cheese"),
        ("clang", "mother"),
        ("frond", "father"),
        ("plume", "oyster"),
        ("snipe", "anchor"),
        ("smile", "apples"),
        ("spore", "angles"),
        ("skiff", "embers"),
        ("swept", "candle"),
        ("twine", "tongue"),
        ("shred", "shores"),
        ("throb", "stones"),
        ("splay", "prisms"),
        ("scrim", "bridle"),
        ("spree", "cradle"),
        ("prong", "dragon"),
        ("bland", "shrine"),
        ("crone", "garden"),
    ]
    M = len(P)

    # A practical cluster set (you can expand as needed).
    # Longest-prefix rule will prefer, e.g., "str" over "st".
    CL = [
        "str","spr","spl","scr","shr","thr",
        "ch","sh","th","ph","gh",
        "bl","br","cl","cr","dr","fl","fr","gl","gr","pl","pr","sl","sm","sn","sp","st","tr","sk","sc","sw","tw",
        "qu","wh","wr","kn","gn"
    ]

    # Sort clusters once for longest-prefix matching
    CL_sorted = sort_clusters_longest_first(CL)

    # Zero-based starting index (explicitly stated in the task text)
    i0 = 0

    # We generate num_step lines; line k corresponds to running N=k steps
    dataset = []

    # We simulate once and reuse the evolving cursor so that record k is exactly the k-th step from the start.
    i = deepcopy(i0)
    for step in range(1, args.num_step + 1):
        x, y = P[i]
        y_prime, jump = spooner_step_get_yprime_and_jump(x, y, CL_sorted)
        print(y_prime)
        # advance cursor for the NEXT global step
        i = (i + jump) % M

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": make_task_text(P, i0, CL, step),
            "gt_ans": y_prime  # the y' produced on the N-th (= step-th) swap
        }
        dataset.append(data_line)

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
