"""
Generate the Belt Functional Graph walk tasks: count distinct visited nodes up to n steps
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "functional-graph-belt-walk"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def update_belt_state(state, next_map):
    """
    Perform one step of the belt walk:
        1) v <- next[v]
        2) vis[v] += 1
        3) if vis[v] was 0 before, distinct += 1

    Parameters:
        state: dict with fields
            - 'cur': current node (int, 1-based)
            - 'vis': list[int] length M+1, visit counts (1-based indexing)
            - 'distinct': number of nodes with vis[v] > 0 so far
            - 'M': number of nodes
        next_map: list[int] length M+1, 1-based next pointers

    Returns:
        state (mutated and returned for convenience)
    """
    v = next_map[state['cur']]
    state['cur'] = v
    if state['vis'][v] == 0:
        state['distinct'] += 1
    state['vis'][v] += 1
    return state

def main():
    parser = argparse.ArgumentParser(description="Generate tasks for Belt Functional Graph (distinct visited count up to step n)")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of tasks (n from 1..num_step). Each task asks for S(n). (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-sci-geo-belt-functional-graph.jsonl",
                        help="Path to output .jsonl file (default: belt-functional-graph.jsonl)")
    args = parser.parse_args()

    # ----- Problem instance (fixed across all tasks) -----
    # M nodes labeled 1..M; next_map is 1-based with a dummy 0 at index 0.
    # This instance has a clear tail+cycle from v0=1: 1->2->3->4->5->3 (tail length 2, cycle length 3)
    M = 16
    v0 = 1
    next_map = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 5, 8, 3, 4, 5]  # 1→2→3→4→5→3, 6→7→8→6, 9↔10

    # Initial state (do NOT count v0 unless we land on it later)
    state = {
        'cur': v0,
        'vis': [0] * (M + 1),
        'distinct': 0,
        'M': M,
    }

    dataset = []
    # We will generate tasks for n = 1..num_step by doing one update per n
    for i in range(args.num_step):
        step = i + 1
        update_belt_state(state, next_map)
        gt_ans = int(state['distinct'])  # S(n): number of distinct nodes visited among landings v1..vn

        # Prepare a human/LLM-readable task text tightly aligned to the asteroid-belt functional graph setting
        task_text = f"""Belt Functional Graph Walk

You are given a "functional graph" route network in the asteroid belt: there are \\(M\\) stations numbered \\(1..M\\). Each station \\(v\\) has exactly one directed jump link, denoted \\(\\text{{next}}[v]\\).

**Start**: at station \\(v_0\\); all visit counters \\(\\text{{vis}}[v]=0\\).

**Each jump (for steps \\(t=1..n\\), in order)**:
1. Move: \\(v \\leftarrow \\text{{next}}[v]\\)
2. Record: \\(\\text{{vis}}[v] \\leftarrow \\text{{vis}}[v] + 1\\)

Define
\\[
S(n) = \\bigl|\\{{\\, v \\mid \\text{{vis}}[v] > 0 \\,\\}}\\bigr|
\\]
i.e., the number of distinct stations visited among the landing sequence \\(v_1, v_2, \\dots, v_n\\). Note: the initial station \\(v_0\\) is **not** counted unless it is visited again later.

You may view the path's topology as "**tail + cycle**": a simple tail segment that enters a directed cycle and then loops within it; however, regardless of whether you use this structure explicitly, you must compute \\(S(n)\\) exactly by the rules above.

**Instance parameters (1-based)**:
- \\(M = {M}\\)
- \\(v_0 = {v0}\\)
- \\(\\text{{next}}[1..M] = {next_map[1:]}\\)

**Task**: given \\(n = {step}\\), perform \\(n\\) jumps from \\(v_0\\) according to the rules and output the integer **\\(S(n)\\)**."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt_ans
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
