"""
Generate toroidal rover sampling tasks: 2D grid with {B,R,I} tiles,
return the cumulative count C_r of regolith samples after N steps.
"""
import argparse
import json
from pathlib import Path

# ---- Metadata / IO ----
TASK_TYPE = "geo-torus-sampler-S1"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# ---- Map / Directions ----
# Static grid using characters:
#   B = basalt, R = regolith, I = ice
MAP_ROWS = [
    "BRIBRIB",
    "RIRBBRI",
    "BRRIBRI",
    "IIBRBRI",
]
H = len(MAP_ROWS)
W = len(MAP_ROWS[0])
assert all(len(row) == W for row in MAP_ROWS), "All rows must have equal width."

# Directions and rotations
VEC = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
RIGHT = {"N": "E", "E": "S", "S": "W", "W": "N"}
LEFT  = {"N": "W", "W": "S", "S": "E", "E": "N"}

def step_once(x: int, y: int, dir_: str, Cb: int, Cr: int, Ci: int):
    """
    One rover step (sample -> turn -> move) on a torus HxW.
    Returns updated (x,y,dir_,Cb,Cr,Ci) and the tile sampled.
    """
    tile = MAP_ROWS[y][x]  # current cell

    # 1) sample
    if tile == "B":
        Cb += 1
    elif tile == "R":
        Cr += 1
    elif tile == "I":
        Ci += 1
    else:
        raise ValueError(f"Unknown tile {tile} at (x={x}, y={y})")

    # 2) turn
    if tile == "B":       # basalt -> right turn
        dir_ = RIGHT[dir_]
    elif tile == "I":     # ice -> left turn
        dir_ = LEFT[dir_]
    else:                 # regolith -> straight (no change)
        pass

    # 3) move forward with torus wrap
    dx, dy = VEC[dir_]
    x = (x + dx) % W
    y = (y + dy) % H

    return x, y, dir_, Cb, Cr, Ci, tile

def format_map_rows(rows):
    # Pretty print as Python-like list of strings for the task text
    inner = ", ".join(f"\"{r}\"" for r in rows)
    return "[" + inner + "]"

def main():
    parser = argparse.ArgumentParser(description="Generate toroidal rover sampling tasks with C_r counting")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of lines (instances) to generate; instance i uses n=i steps (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-sci-geo-torus-sampler.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-geo-torus-sampler.jsonl)")
    # Optional overrides for initial pose if desired
    parser.add_argument("--x0", type=int, default=1, help="Initial x (column index, default: 1)")
    parser.add_argument("--y0", type=int, default=0, help="Initial y (row index, default: 0)")
    parser.add_argument("--dir0", type=str, default="E", choices=list(VEC.keys()),
                        help="Initial direction in {N,E,S,W} (default: E)")

    args = parser.parse_args()

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Initial state (t = 0): no sampling yet
    x, y, dir_ = args.x0, args.y0, args.dir0
    Cb = Cr = Ci = 0

    dataset = []

    # Build static description strings
    map_literal = format_map_rows(MAP_ROWS)
    dir_vecs = 'N=(0,-1), E=(1,0), S=(0,1), W=(-1,0)'

    for i in range(args.num_step):
        step = i + 1

        # Evolve exactly one step each loop to build increasing-N tasks
        x, y, dir_, Cb, Cr, Ci, tile = step_once(x, y, dir_, Cb, Cr, Ci)

        # Ground-truth answer: C_r after n = step steps
        gt = int(Cr)

        # Task text (precise, simulation-friendly, mirrors the step order)
        task_text = f"""Mission brief — S-1 rover on a stitched ring-world surface

Setting
- You pilot the S-1 surface sampler across a {H}×{W} stitched map of terrains:
  B = basalt (dark lava plains), R = regolith (loose dust/soil), I = ice (glazed sheets).
- The planet is seamless: crossing any edge re-enters from the opposite side (toroidal wrap).
- Map rows from y=0 to y={H - 1}: G_rows = {map_literal}.

Start state
- Rover starts at (x0, y0) = ({args.x0}, {args.y0}), facing dir0 = "{args.dir0}".
- Directions use unit vectors: N=(0,-1), E=(1,0), S=(0,1), W=(-1,0).
- Sample counters at t=0: C_b = C_r = C_i = 0. (No sample at t=0.)

Terrain behavior (why the rover turns)
- Basalt (B): jagged outcrops bias the steering **right** (N→E→S→W→N).
- Ice (I): low friction causes a controlled **left** slide (N→W→S→E→N).
- Regolith (R): good traction, keep **straight** (no turn).

Rover loop (operational order, repeat for t = 1..n with n={step})
1) SAMPLE the square the rover is on:
   if B → C_b += 1; if R → C_r += 1; if I → C_i += 1.
2) TURN according to the terrain just sampled:
   B → turn right; I → turn left; R → keep direction.
3) MOVE one square forward in the current heading with wrap:
   (x, y) ← ((x + dx) mod {W}, (y + dy) mod {H}),
   where (dx,dy) is the unit vector of the current direction.

Objective
- After exactly n={step} {'step' if step==1 else 'steps'} of field work, report the total regolith samples C_r as the final answer."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt
        }
        dataset.append(data_line)

        # (Optional) debug print
        print(f"step={step:>3}  pos=({x},{y})  dir={dir_}  last_tile={tile}  C=(b{Cb}, r{Cr}, i{Ci})")

    # Save to .jsonl
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_file}")

if __name__ == "__main__":
    main()
