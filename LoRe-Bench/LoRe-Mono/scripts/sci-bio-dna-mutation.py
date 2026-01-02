"""
Generate DNA context-dependent mutation tasks: 1D cellular automaton over A/C/G/T,
return the count of 'A' after N synchronous updates.
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

# ---- Metadata / IO ----
TASK_TYPE = "bio-dna-context-dependent-CA"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# ---- Biology-flavored rule (context-dependent mutation) ----
# Purines (R) and Pyrimidines (Y)
R = {"A", "G"}
Y = {"C", "T"}

# Transition / Transversion mappings
TRANSITION_Y_TO_R = {"C": "A", "T": "G"}  # Y -> R
TRANSITION_R_TO_Y = {"A": "T", "G": "C"}  # R -> Y
TRANSVERSION = {"A": "T", "T": "C", "C": "G", "G": "A"}  # swap across classes

def update_dna(seq: str) -> str:
    """
    Synchronous update on a circular (wrap-around) 1D lattice of nucleotides.
    Context-dependent mutation rule f(l,c,r) -> c':
      1) If l and r are both purines (R) and c ∈ Y: c' = transition Y->R  (C→A, T→G).
      2) If l and r are both pyrimidines (Y) and c ∈ R: c' = transition R->Y  (A→T, G→C).
      3) If l and r are of different classes (one in R, one in Y): c' is updated from c with mapping: (A→T, T→C, C→G, G→A).
      4) Otherwise: c' = c (no change).
    """
    L = len(seq)
    out = [""] * L
    for i in range(L):
        l = seq[(i - 1) % L]
        c = seq[i]
        r = seq[(i + 1) % L]

        if (l in R) and (r in R) and (c in Y):
            out[i] = TRANSITION_Y_TO_R[c]
        elif (l in Y) and (r in Y) and (c in R):
            out[i] = TRANSITION_R_TO_Y[c]
        elif ((l in R) != (r in R)):  # different classes on the flanks
            out[i] = TRANSVERSION[c]
        else:
            out[i] = c
    return "".join(out)

def count_motif_linear(seq: str, motif: str = "A") -> int:
    """Count overlapping occurrences of motif on the linear sequence (no wrap-around)."""
    m = len(motif)
    return sum(1 for i in range(len(seq) - m + 1) if seq[i:i + m] == motif)

def main():
    parser = argparse.ArgumentParser(description="Generate DNA CA tasks with 'A' counting")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of lines (instances) to generate; instance i uses n=i steps (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-bio-dna-ca.jsonl",
                        help="Path to output .jsonl file (default: linear-mono-bio-dna-ca.jsonl)")
    args = parser.parse_args()

    # You can customize the initial sequence; odd L often avoids trivial symmetries.
    init_seq = "ACGTACGTTGCAACGTA"  # L = 17
    L = len(init_seq)

    seq = init_seq
    dataset = []

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(args.num_step):
        step = i + 1

        # evolve exactly one step each loop to build increasing-N tasks
        seq = update_dna(seq)

        # ground-truth answer: count 'A' occurrences (overlap allowed, no wrap-around)
        gt = count_motif_linear(seq, "A")

        # Build task text (biology-tilted, precise and simulation-friendly)
        task_text = f"""Given integer \\(n={step}\\), start with the DNA sequence \\(s_0 = "{init_seq}"\\) (length \\(L={L}\\)).
At each step \\(t=1,2,\\dots,n\\), update all nucleotides **simultaneously** under circular (wrap-around) boundary conditions.
For position \\(i\\), let \\(\\ell = s_t[(i-1)\\bmod L]\\), \\(c = s_t[i]\\), \\(r = s_t[(i+1)\\bmod L]\\). Define the context-dependent mutation \\(s_{{t+1}}[i] = f(\\ell,c,r)\\) with:

• Let purines \\(R=\\{{\\text{{A}},\\text{{G}}\\}}\\) and pyrimidines \\(Y=\\{{\\text{{C}},\\text{{T}}\\}}\\).  
1) If \\(\\ell,r\\in R\\) and \\(c\\in Y\\): **transition Y→R** with mapping \\(\\text{{C}}\\to\\text{{A}},\\ \\text{{T}}\\to\\text{{G}}\\).  
2) If \\(\\ell,r\\in Y\\) and \\(c\\in R\\): **transition R→Y** with mapping \\(\\text{{A}}\\to\\text{{T}},\\ \\text{{G}}\\to\\text{{C}}\\).  
3) If \\(\\ell\\) and \\(r\\) are of **different classes** (one in \\(R\\), one in \\(Y\\)): update \\(c\\) by the fixed cyclic mapping \\(\\text{{A}}\\rightarrow\\text{{T}},\\text{{T}}\\rightarrow\\text{{C}}, \\text{{C}}\\rightarrow\\text{{G}}, \\text{{G}}\\rightarrow\\text{{A}}\\).  
4) Otherwise: \\(c' = c\\) (no change).

After \\(n={step}\\) {"step" if step==1 else "steps"}, obtain \\(s_{step}\\) and count occurrences of the base "A" in the **linear sequence**.  
Return that integer count as the final answer."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(gt)
        }
        dataset.append(data_line)

        # (Optional) print the evolving sequence for debugging/inspection
        print(f"step={step:>3}  s={seq}  A_count={gt}")

    # Save to .jsonl
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_file}")

if __name__ == "__main__":
    main()
