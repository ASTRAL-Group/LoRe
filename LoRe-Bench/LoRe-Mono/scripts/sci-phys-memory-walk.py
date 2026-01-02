"""
Generate memory-lattice walk tasks: 1D ring with flip-on-visit field (history-dependent walk).
Return the particle position x after N steps (Q1).
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

# ---- Metadata / IO ----
TASK_TYPE = "linear-mono-phys-memory-walk-1D"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# ---- Dynamics (P-1: Charged particle on a 1D ring with memory) ----
def step_once(x: int, dir_: int, F: list) -> tuple[int, int]:
    """
    One update step on ring of length L = len(F).
    Read old field at current site, decide turn, flip field, move 1 site.

    Rules (read old field BEFORE flipping):
      1) Let b = F[x] in {0,1}.
         - If b == 0: keep direction (dir stays).
         - If b == 1: reverse direction (dir = -dir).
      2) Flip field at current site: F[x] = 1 - b.
      3) Move: x = (x + dir) mod L.

    Returns:
        (x_next, dir_next) with F mutated in-place.
    """
    L = len(F)
    b = F[x]
    if b == 1:
        dir_ = -dir_
    F[x] = 1 - b
    x = (x + dir_) % L
    return x, dir_

def main():
    parser = argparse.ArgumentParser(description="Generate P-1 memory-walk tasks with Q1 (final position)")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of lines (instances) to generate; instance i uses n=i steps (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-phys-memory-walk-1d.jsonl",
                        help="Path to output .jsonl file (default: phys-memory-walk-1d.jsonl)")
    args = parser.parse_args()

    # ---- Fixed reproducible initial condition (can be customized) ----
    F0_str = "0101100100010110011"  # length L = 19
    F0 = [int(ch) for ch in F0_str]
    L = len(F0)
    x0 = 0          # start site (0-indexed)
    dir0 = +1       # initial direction in {-1, +1}

    # Work state that we evolve exactly one step per loop
    F = deepcopy(F0)
    x = x0
    dir_ = dir0

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_SAVE_DIR / args.out_path

    with open(out_file, "w", encoding="utf-8") as f:
        for i in range(args.num_step):
            step = i + 1

            # Evolve exactly one step to build increasing-N ground truths from the same initial state
            x, dir_ = step_once(x, dir_, F)

            # Ground-truth for Q1: final position after n steps
            gt = int(x)

            # ---- Physics-embedded task text (clear, simulation-friendly) ----
            task_text = f"""A charged probe moves on a 1D circular crystal (ring) with \\(L={L}\\) equally spaced lattice sites
indexed \\(0,1,\\dots,L-1\\). Each site hosts a **bistable local domain** (a two-state field)
\\(F_t[i]\\in\\{{0,1\\}}\\): state **0** acts like a *transmitting* domain, state **1** acts like a
*reflecting* domain. The probe has a position \\(x_t\\in\\{{0,\\dots,L-1\\}}\\) and a direction
\\(dir_t\\in\\{{-1,+1\\}}\\); one time step advances it by one site (units are “sites per step”).
Periodic boundary conditions apply (movement is taken modulo \\(L\\)).

**Initial condition.** The probe starts at \\(x_0={x0}\\) with \\(dir_0={dir0}\\). The initial field is
given as a 0/1 string (index 0 = leftmost character):
\\[
F_0 = \"{F0_str}\".
\\]

**Microscopic interaction with memory (use the pre-impact state).** For steps \\(t=0,1,\\dots,n-1\\),
perform the following in order:

(1) (*Scattering decision from the local domain*) Read the **old** domain at the current site:
   \\(b := F_t[x_t]\\in\\{{0,1\\}}\\).
   - If \\(b=0\\) (*transmit*): the probe keeps its direction, \\(dir_{{t+1}} = dir_t\\).
   - If \\(b=1\\) (*reflect*): the probe reverses direction (specular backscattering),
     \\(dir_{{t+1}} = -\\,dir_t\\).

(2) (*Memory write to the medium*) The impact flips the local domain: \\(F_t[x_t] \\leftarrow 1-b\\)
   to obtain the updated field.

(3) (*Transport on the ring*) Advance one site with periodic wrap-around:
   \\(x_{{t+1}} = (x_t + dir_{{t+1}}) \\bmod L\\).

(4) Set \\(F_{{t+1}}\\) to the field updated in (2).

**Task.** For the instance with \\(n={step}\\) {"step" if step==1 else "steps"}, execute the dynamics
above **exactly in this order** (in particular, decide the turn using the **pre-flip** domain in step 1).
Return the **final position** \\(x_{step}\\) as an integer in \\([0, L-1]\\) (0-based index)."""

            rec = {
                "idx": step,
                "type": TASK_TYPE,
                "task": task_text,
                "gt_ans": gt
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            # Optional progress line for debugging
            print(f"step={step:>3}  x={gt}  dir={dir_:+d}")

    print(f"Wrote {args.num_step} records to {out_file}")

if __name__ == "__main__":
    main()
