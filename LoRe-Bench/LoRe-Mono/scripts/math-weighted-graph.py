"""
Generate the harder linear mono data: weighted-walk update (reduce to 4-node graph)
"""
import argparse
import json
from pathlib import Path
from copy import deepcopy  # 保留以防后续扩展；当前未使用

TASK_TYPE = "linear-monotonicity-math-weighted-graph"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def step_once(u: int, W: dict, edges: dict) -> tuple[int, int]:
    """
    执行一步：
      - 若 W(u) 为奇 -> 走第1条出边；偶 -> 走第2条出边
      - 记分 += W(next)（不更新 next 的权）
      - 更新出发点 u 的权: W(u) = (W(u) % 4) + 1
      - 返回 (next, add_score)
    """
    Wu = W[u]
    take_first = (Wu % 2 == 1)
    next_v = edges[u][0] if take_first else edges[u][1]
    add = W[next_v]
    W[u] = (W[u] % 4) + 1
    return next_v, add

def build_task_text(step: int, mod_num: int, v0: int, edges: dict, init_W: dict) -> str:
    """
    生成题面（英文，含完整规则与给定实例），n=step。
    """
    edges_text = (
        "1: 1st→2, 2nd→3; "
        "2: 1st→3, 2nd→4; "
        "3: 1st→4, 2nd→1; "
        "4: 1st→1, 2nd→2"
    )
    w_text = f"W(1)={init_W[1]}, W(2)={init_W[2]}, W(3)={init_W[3]}, W(4)={init_W[4]}"
    task = f"""Given a small directed graph V={{1,2,3,4}} with fixed outgoing-edge order per node:
{edges_text}.
Initial position v0={v0}.
Initial weights (only initially constrained to {{1,2,3}}): {w_text}.
Let mod_num={mod_num}.

For t=1..n (here n={step}), repeat once per step:
1) If the current node is u, look at W(u):
   - odd  → take the 1st outgoing edge of u,
   - even → take the 2nd outgoing edge of u.
   Let next be the chosen neighbor.
2) Score update: score += W(next) (use next's current weight; do NOT update next this step).
3) Update only the departure node: W(u) ← (W(u) mod 4) + 1 (i.e., 1→2→3→4→1 cycle).
4) Set current node v_t ← next.

Finally output S = score mod mod_num.
Return S as the final answer."""
    return task

def main():
    parser = argparse.ArgumentParser(description="Generate linear mono 'weighted-walk update' tasks")
    parser.add_argument("--num_step", type=int, default=40,
                        help="Number of steps to generate (each line uses n=1..num_step).")
    parser.add_argument("--out_path", type=str, default="linear-mono-math-weighted-graph.jsonl",
                        help="Path to output .jsonl file.")
    parser.add_argument("--mod_num", type=int, default=97,
                        help="Modulus for the final S = score % mod_num (default: 97).")
    args = parser.parse_args()

    # 固定实例（与示例一致）
    v0 = 1
    edges = {
        1: (2, 3),  # 1: 第1条→2, 第2条→3
        2: (3, 4),  # 2: 第1条→3, 第2条→4
        3: (4, 1),  # 3: 第1条→4, 第2条→1
        4: (1, 2),  # 4: 第1条→1, 第2条→2
    }
    init_W = {1: 2, 2: 3, 3: 1, 4: 2}

    # 逐步推进（保证第 i 行等价“从初始出发走 i 步”的结果）
    u = v0
    W = dict(init_W)
    score = 0

    dataset = []
    for i in range(args.num_step):
        step = i + 1
        # 做一步
        u, add = step_once(u, W, edges)
        score += add
        S = score % args.mod_num

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": build_task_text(step=step, mod_num=args.mod_num, v0=v0, edges=edges, init_W=init_W),
            "gt_ans": int(S),
        }
        dataset.append(data_line)

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_file}")

if __name__ == "__main__":
    main()
