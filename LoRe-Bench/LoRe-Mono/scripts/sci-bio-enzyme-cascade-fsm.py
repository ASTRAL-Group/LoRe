"""
Enzyme Cascade FSM with cyclic ternary input: count target-state visits
"""
import argparse
import json

import numpy as np
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "enzyme-cascade-fsm-tertiary-input"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_fsm(state: int, cnt: int, T: np.ndarray, u: np.ndarray, Etar: int, t: int):
    """
    Advance the Enzyme Cascade FSM by one step under a cyclic ternary input.

    Update rule (single step):
        1. Read u_t from the ring buffer: u_t = u[t mod L]
        2. Transition: state <- T[state, u_t]
        3. If state == Etar: cnt++

    Parameters:
        state: current state index (integer, e.g., 0 for E0)
        cnt: current hit counter for the target state
        T: (num_states x 3) transition table; columns correspond to inputs 0,1,2
        u: ring buffer of inputs with values in {0,1,2}
        Etar: target state index (integer)
        t: global step index (0-based)

    Returns:
        (new_state, new_cnt)
    """
    ut = u[t % len(u)]
    new_state = int(T[state, ut])
    new_cnt = cnt + (1 if new_state == Etar else 0)
    return new_state, new_cnt

def main():
    parser = argparse.ArgumentParser(description="Generate Enzyme Cascade FSM tasks with cyclic ternary input")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to run the FSM (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-sci-bio-enzyme-cascade-fsm.jsonl",
                        help="Path to output .jsonl file (default: enzyme-cascade-fsm.jsonl)")
    args = parser.parse_args()

    # ---- Fixed FSM specification (shared by all generated items) ----
    # States: E0..E4  (encoded as integers 0..4)
    num_states = 5
    E0 = 0
    Etar = 2  # target state is E3

    # Transition table T (rows = current state index, cols = input u in {0,1,2})
    # T[i, j] = next state index when in Ei and seeing input j
    T = np.array([
        [0, 1, 2],  # from E0 on u=0,1,2
        [2, 3, 1],  # from E1 ...
        [3, 2, 4],  # from E2 ...
        [1, 4, 3],  # from E3 ...
        [4, 0, 2],  # from E4 ...
    ], dtype=int)

    # Cyclic ternary input ring buffer u[0..L-1]
    u = np.array([2, 0, 1, 2], dtype=int)  # values in {0,1,2}
    L = len(u)

    # Preformatted table string for embedding in the task text (human-readable)
    table_lines = [
        "| Current state → next | u=0 | u=1 | u=2 |",
        "|---|---|---|---|",
        "| E0 | E0 | E1 | E2 |",
        "| E1 | E2 | E3 | E1 |",
        "| E2 | E3 | E2 | E4 |",
        "| E3 | E1 | E4 | E3 |",
        "| E4 | E4 | E0 | E2 |",
    ]
    T_table_md = "\n".join(table_lines)

    # Running state for dataset generation
    state = E0
    cnt = 0
    dataset = []

    # Ensure output directory exists
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(args.num_step):
        step = i + 1  # n = number of steps to simulate
        # advance one step of the FSM
        state, cnt = update_fsm(state, cnt, T, u, Etar, step)
        print(state)

        # Build task text (English, enzyme-cascade FSM phrasing)
        E_set_str = "{E0, E1, E2, E3, E4}"
        u_list_str = "[" + ", ".join(map(str, u.tolist())) + "]"

        task_text = (
            f"Given integer \\(n={step}\\), consider an **Enzyme Cascade Finite State Machine (FSM)** that abstracts a multi-stage catalytic pathway.\n\n"
            f"**System definition (fixed across all queries):**\n"
            f"- **States:** \\(E = {E_set_str}\\).\n"
            f"- **Cyclic ternary input buffer:** \\(u[0..{L-1}]\\in\\{{0,1,2\\}}\\) with values \\(u = {u_list_str}\\). "
            f"The input at step \\(t\\) is \\(u_t = u[t \\\\bmod {L}]\\).\n"
            f"- **Transition table \\(T\\):** on input \\(u\\in\\{{0,1,2\\}}\\), the next state is \\(s' = T(s, u)\\). "
            f"The Enzyme Cascade table below lists \\(T\\) row-by-row (rows = current state; columns = input value):\n\n"
            f"{T_table_md}\n\n"
            f"- **Initial state:** \\(s_0 = E0\\).\n"
            f"- **Target state:** \\(E_{{tar}} = E{Etar}\\).\n\n"
            f"**Update & counting rule (biochemical interpretation):**\n"
            f"For \\(t = 1,2,\\dots,n\\):\n"
            f"1. Read the stimulus \\(u_t\\) from the ring buffer.\n"
            f"2. Apply the enzyme-cascade transition: \\(s_{{t+1}} \\\\leftarrow T(s_t, u_t)\\).\n"
            f"3. If \\(s_{{t+1}} = E_{{tar}}\\), increment the hit counter \\(\\\\text{{cnt}}\\).\n\n"
            f"**What to return:** After exactly \\(n\\) steps, return the single integer \\(\\\\text{{cnt}}\\) "
            f"(the number of visits to \\(E_{{tar}}\\)).  "
            f"*Note:* Only count hits **after** a transition (do **not** count the initial state unless it is reached again after a step)."
            f"Only output hit count as the final answer after running {step} {'steps' if step > 1 else 'step'}."
        )

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(cnt)
        }
        dataset.append(data_line)

    # Save all data_line records to a .jsonl file
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
