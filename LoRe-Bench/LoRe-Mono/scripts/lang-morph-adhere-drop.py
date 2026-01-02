"""
Generate morphology rotate data: a cyclic prefix–suffix–root “always rotate” machine
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "morphology-adhere-drop-cyclic"  # keep the same type tag for compatibility
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# --- Inventories (fixed for this generator) ---
ROOTS = ["play", "work", "write", "cook", "travel"]
PREFIXES = ["un", "re", "pre", "anti"]
SUFFIXES = ["s", "ed", "ing", "er"]

# --- Index tables (cycled independently when that class is visited) ---
# Read as: whenever a class is visited, set that class to the NEXT item of its table (wrap around).
# Prefix/Suffix tables have length 4; Root table has length 5 (includes the original root).
PREFIX_INDEX_TABLE = [2, 0, 1, 3]          # → ["pre", "un", "re", "anti"] repeating
SUFFIX_INDEX_TABLE = [2, 1, 0, 3]          # → ["ing", "ed", "s", "er"] repeating
ROOT_INDEX_TABLE   = [1, 3, 2, 4, 0]       # → ["work", "cook", "write", "travel", "play"] repeating

CYCLE = ["prefix", "suffix", "root"]  # prefix → suffix → root → prefix → ...


def surface_form(state):
    """Linear spell-out without orthographic adjustments."""
    p = "" if state["p"] is None else PREFIXES[state["p"]]
    r = ROOTS[state["r"]]
    s = "" if state["s"] is None else SUFFIXES[state["s"]]
    return f"{p}{r}{s}"


def update_word(state, counters):
    """
    Run ONE step of the cycle, using pure rotation (no removals).

    Rotation rule (plain English):
    - The machine visits classes in order: prefix → suffix → root → (repeat).
    - When a class is visited, you SET that class to the NEXT item from its index table (wrap around).
      * For the first time a class is ever visited, this simply "attaches" its first table item.
      * Afterwards it always "rotates" to the next table item.
    - After the update, the surface form is prefix + root + suffix (plain concatenation).
    """
    which = CYCLE[state["t"] % len(CYCLE)]

    if which == "prefix":
        idx = PREFIX_INDEX_TABLE[counters["p"] % len(PREFIX_INDEX_TABLE)]
        counters["p"] += 1
        state["p"] = idx

    elif which == "suffix":
        idx = SUFFIX_INDEX_TABLE[counters["s"] % len(SUFFIX_INDEX_TABLE)]
        counters["s"] += 1
        state["s"] = idx

    elif which == "root":
        idx = ROOT_INDEX_TABLE[counters["r"] % len(ROOT_INDEX_TABLE)]
        counters["r"] += 1
        state["r"] = idx

    # advance time
    state["t"] += 1
    return state


def build_task_text(step, init_state, tables_snapshot):
    """
    Produce a clear, morphology-centered English instruction for data generation (rotate-only semantics).
    """
    w0 = surface_form(init_state)
    task = f"""You are given a tiny morphology machine that builds words by
gluing morphemes in a fixed cycle and **always rotating** choices by index tables.

### Inventories
- Roots (R): {ROOTS}
- Prefixes (P): {PREFIXES}
- Suffixes (S): {SUFFIXES}

### Start state
- Original root: R[0] = "{ROOTS[0]}"
- No prefix and no suffix are attached initially.
- Surface word at step 0: w0 = "{w0}"

### Cycle order
The machine visits classes in this exact loop:
prefix → suffix → root → prefix → suffix → root → …

### Rotation rule when a class is visited
- You **SET** that class to the **next** item given by its index table (wrapping around).
  - On the very first visit to a class, this acts like an initial "attach".
  - On later visits, it **rotates** to the next item; nothing is ever removed.
  - Prefix and suffix therefore remain present once first attached.
  - The root cycles through the root inventory according to its index table (including the original root).

### Index tables
The tables below are lists of integer indices (0-based). Each time you visit a class,
advance one position in that class’s table (cycling if necessary) and set the class to
the corresponding item from the inventory.

- Prefix index table: {tables_snapshot['P']}
- Suffix index table: {tables_snapshot['S']}
- Root index table:   {tables_snapshot['R']}

**Example (prefix):**
If the prefix index table is [2,0,1,3], then across successive prefix steps you set:
P[2] → P[0] → P[1] → P[3] → (wrap) P[2] → …

### Spelling-out
After each update, spell the surface form as: [prefix][root][suffix]
(plain concatenation; no orthographic tweaks).

### Your task
Start from w0 and run **exactly N = {step} steps** following the cycle and rotation rule above.
Return the final surface form w_N(w_{step}) as a single string (no quotes)."""
    return task


def main():
    parser = argparse.ArgumentParser(description="Generate morphology rotate (cyclic) tasks")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to simulate for each record (1..N for each line) (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-morph-adhere-drop.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-language-morph-rotate.jsonl)")
    args = parser.parse_args()

    # Initial machine state
    init_state = {
        "original_root": ROOTS[0],  # kept for task text clarity
        "p": None,                  # index into PREFIXES or None (before first prefix visit)
        "s": None,                  # index into SUFFIXES or None (before first suffix visit)
        "r": 0,                     # index into ROOTS; start at the original root
        "t": 0                      # step counter
    }

    # Independent position counters for each class’s index table
    counters = {"p": 0, "s": 0, "r": 0}

    # For reproducibility in the task text
    tables_snapshot = {
        "P": PREFIX_INDEX_TABLE,
        "S": SUFFIX_INDEX_TABLE,
        "R": ROOT_INDEX_TABLE
    }

    dataset = []
    state = deepcopy(init_state)

    for i in range(args.num_step):
        step = i + 1
        # Perform exactly one update step
        state = update_word(state, counters)

        # Ground-truth answer after 'step' steps
        wN = surface_form(state)
        print(wN)

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": build_task_text(step, init_state, tables_snapshot),
            "gt_ans": wN
        }
        dataset.append(data_line)

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")


if __name__ == "__main__":
    main()
