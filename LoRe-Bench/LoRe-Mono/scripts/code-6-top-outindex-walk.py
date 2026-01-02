"""
Generate the Test Output Prediction data: Out-index Walk (degree-dependent, 0-based)
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "outindex-walk"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# Default directed graph (0-based node ids) used by the update rule.
# Each node maps to a non-empty list of outgoing neighbors.
DEFAULT_ADJ = {
    0: [1, 2],
    1: [2, 3, 4],
    2: [3, 0],
    3: [4, 5],
    4: [0, 2],
    5: [5],
}

def update_outindex_walk(state, i=None, adj=None):
    """
    Update rule (pure function, 0-based indexing):
        State is a pair (u, t) where:
          - u is the current node id (non-negative integer, 0-based)
          - t is the current step counter (non-negative integer)
        Given a fixed adjacency list ADJ (dict[int, list[int]]), perform:
            deg = len(ADJ[u])                  # out-degree of u (must be >= 1)
            idx = (t + u) % deg               # pick edge by index, 0-based
            u' = ADJ[u][idx]                  # follow that edge
            t' = t + 1
        Return the next state (u', t').

        The optional 'i' (iteration index) is accepted for signature compatibility
        but is not used in this rule. Pass a custom adjacency via 'adj' if needed.
    """
    u, t = state
    A = adj if adj is not None else DEFAULT_ADJ
    deg = len(A[u])
    idx = (t + u) % deg
    return (A[u][idx], t + 1)

def main():
    parser = argparse.ArgumentParser(description="Run Out-index Walk state updates for Test Output Prediction")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of records to generate; record t uses N = t iterations (1..num_step)")
    parser.add_argument("--out_path", type=str, default="linear-mono-code-6-top-outindex-walk.jsonl",
                        help="Path to output .jsonl file")
    parser.add_argument("--init_state", type=str, default="1,0",
                        help="Comma-separated 'u,t' (e.g., '1,0') as the initial state")
    args = parser.parse_args()

    # Parse initial state (u,t)
    toks = [int(tok.strip()) for tok in args.init_state.split(",") if tok.strip() != ""]
    if len(toks) != 2:
        raise ValueError("init_state must be exactly two integers: 'u,t'")
    init_state = (toks[0], toks[1])

    dataset = []
    updated_state = None

    for i in range(args.num_step):
        step = i + 1  # N = number of iterations for this record

        if i == 0:
            updated_state = update_outindex_walk(init_state, i)
        else:
            updated_state = update_outindex_walk(updated_state, i)

        # Ground-truth answer for this record: the node id after N steps
        ANSWER = str(updated_state[0])
        print(ANSWER)

        # Build the Code Execution task text (English, explicit 0-based indexing)
        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports).
This is a Code Execution task: run the program, do NOT rewrite it. Indexing is 0-based throughout.

What the program does:
- It defines a fixed directed graph ADJ where node ids and list indices are 0-based.
- State (u, t) means: currently at node u with step counter t.
- One update step is:
    deg = len(ADJ[u])           # out-degree of u (>=1)
    idx = (t + u) % deg         # choose which outgoing edge by index (0-based)
    u = ADJ[u][idx]             # move to that neighbor
    t = t + 1
- It repeats this update exactly N times starting from the provided (u, t),
  then sets ANSWER to the final node id as a string.

Return only the final value of ANSWER (no other text, no formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run this code exactly as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it with no extra text.

N = {step}  # number of iterations (positive integer)
ADJ = {DEFAULT_ADJ!r}  # 0-based adjacency list (dict[int, list[int]])
u, t = {init_state!r}  # initial (node, step_counter), both non-negative ints

def f(u, t):
    deg = len(ADJ[u])           # out-degree (>=1)
    idx = (t + u) % deg         # 0-based index into ADJ[u]
    u_next = ADJ[u][idx]
    return u_next, t + 1

for _ in range(N):
    u, t = f(u, t)

ANSWER = str(u)
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": ANSWER
        }
        dataset.append(data_line)

    # Save all data_line records to a .jsonl file
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_fp = DATA_SAVE_DIR / args.out_path
    with open(out_fp, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
