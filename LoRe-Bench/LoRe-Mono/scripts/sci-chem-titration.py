"""
Generate advanced discrete titration (ledger-only) tasks:
Diprotic weak acid H2A (two protons) under stepwise strong base/acid additions.
Return species counts and equivalence info after N steps.
"""
import argparse
import json
from pathlib import Path

# ---- Metadata / IO ----
TASK_TYPE = "chem-titration"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# ---- One-step update rules (ledger-only, O(1) per step) ----
def base_step(nH2A: int, nHA: int, nA2: int, nOH: int, nH: int, delta_base: int):
    """
    Strong base addition (B): add Δ_base OH-, then stoichiometric updates.

    Order per step:
      0) Reagent add:            nOH += Δ_base
      1) Strong neutralization:  z = min(nH, nOH);      H+ + OH- -> H2O
      2) First deprotonation:    x1 = min(nH2A, nOH);   H2A + OH- -> HA- + H2O
      3) Second deprotonation:   x2 = min(nHA, nOH);    HA- + OH- -> A2- + H2O
    """
    nOH += delta_base

    z = min(nH, nOH)          # annihilate strong acid/base first
    nH  -= z
    nOH -= z

    x1 = min(nH2A, nOH)       # stepwise deprotonations
    nH2A -= x1
    nHA  += x1
    nOH  -= x1

    x2 = min(nHA, nOH)
    nHA  -= x2
    nA2  += x2
    nOH  -= x2

    return nH2A, nHA, nA2, nOH, nH

def acid_step(nH2A: int, nHA: int, nA2: int, nOH: int, nH: int, delta_acid: int):
    """
    Strong acid addition (A): add Δ_acid H+, then stoichiometric updates.

    Order per step:
      0) Reagent add:            nH += Δ_acid
      1) Strong neutralization:  z = min(nH, nOH);      H+ + OH- -> H2O
      2) First protonation:      y1 = min(nA2, nH);     A2- + H+ -> HA-
      3) Second protonation:     y2 = min(nHA, nH);     HA- + H+ -> H2A
    """
    nH += delta_acid

    z = min(nH, nOH)          # annihilate strong acid/base first
    nH  -= z
    nOH -= z

    y1 = min(nA2, nH)         # stepwise protonations
    nA2 -= y1
    nHA += y1
    nH  -= y1

    y2 = min(nHA, nH)
    nHA -= y2
    nH2A += y2
    nH  -= y2

    return nH2A, nHA, nA2, nOH, nH

def classify_region(nH2A: int, nHA: int, nA2: int, nOH: int, nH: int) -> str:
    """
    Regions for diprotic titration (informational; helps make the task richer):
      - pre_eq1: before the first equivalence (H2A still present; no strong excess)
      - at_eq1: exactly first equivalence (H2A=0, A2-=0, no strong acid/base leftover)
      - between_eq1_eq2: between the two equivalence points (H2A=0, some HA- present; no strong leftover)
      - at_eq2: exactly second equivalence (H2A=0, HA-=0, no strong leftover)
      - base_excess: past second equivalence (OH- leftover)
      - acid_excess: strong acid leftover (H+ > 0)
    """
    if nH > 0:
        return "acid_excess"
    if nOH > 0 and nH2A == 0 and nHA == 0 and nH == 0:
        return "base_excess"
    if nH2A == 0 and nHA == 0 and nH == 0 and nOH == 0:
        return "at_eq2"
    if nH2A == 0 and nH == 0 and nOH == 0 and nHA > 0:
        return "at_eq1" if nA2 == 0 else "between_eq1_eq2"
    return "pre_eq1"

def main():
    parser = argparse.ArgumentParser(description="Generate diprotic titration (ledger-only) tasks")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of lines (instances) to generate; instance i uses n=i steps (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-chem-discrete-titration.jsonl",
                        help="Path to output .jsonl file (default: chem-diprotic-discrete-titration-ledger.jsonl)")
    parser.add_argument("--schedule", type=str, default="BAABABBBABBAABBBBABABBBABBAAAB",
                        help="Sequence of steps using 'B' (base) or 'A' (acid); the first n chars are applied for instance n")
    parser.add_argument("--delta_base", type=int, default=2,
                        help="Δ_base added OH- per 'B' step (default: 2)")
    parser.add_argument("--delta_acid", type=int, default=2,
                        help="Δ_acid added H+ per 'A' step (default: 2)")
    args = parser.parse_args()

    # ---- Fixed but non-trivial initial state (diprotic system) ----
    # S0 = (n_H2A, n_HA-, n_A2-, n_OH-, n_H+)
    init_state = dict(nH2A=16, nHA=5, nA2=2, nOH=0, nH=3)

    # Working copies
    nH2A = init_state["nH2A"]
    nHA  = init_state["nHA"]
    nA2  = init_state["nA2"]
    nOH  = init_state["nOH"]
    nH   = init_state["nH"]

    # Track first times we exactly hit equivalence
    teq1 = None  # first time H2A == 0 and H+ == 0 with no strong leftover and A2- == 0
    teq2 = None  # first time H2A == 0 and HA- == 0 and H+ == 0 with no strong leftover

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    dataset = []

    for i in range(args.num_step):
        step = i + 1
        # Decide reagent for this step from schedule prefix
        ch = args.schedule[i] if i < len(args.schedule) else "B"
        if ch.upper() == "A":
            nH2A, nHA, nA2, nOH, nH = acid_step(nH2A, nHA, nA2, nOH, nH, args.delta_acid)
            mode = "ACID"
        else:
            nH2A, nHA, nA2, nOH, nH = base_step(nH2A, nHA, nA2, nOH, nH, args.delta_base)
            mode = "BASE"

        region = classify_region(nH2A, nHA, nA2, nOH, nH)

        # Record first hits of equivalence points (exact hits only)
        if teq1 is None and region == "at_eq1":
            teq1 = step
        if teq2 is None and region == "at_eq2":
            teq2 = step

        # Boolean flags for "past" equivalence (useful, but still simple):
        passed_eq2 = (region == "base_excess")  # beyond second equivalence under base titration

        # ---- Build task text (compact, precise, simulation-friendly) ----
        init_tuple = (init_state["nH2A"], init_state["nHA"], init_state["nA2"], init_state["nOH"], init_state["nH"])
        schedule_prefix = (args.schedule[:step] if step <= len(args.schedule) else (args.schedule + "B"*(step-len(args.schedule))))  # what has been applied so far

        task_text = f"""Discrete diprotic titration (ledger model, integers only; no equilibria, no pKa).
Given an integer \\(n={step}\\), the initial ledger of species is
\\(S_0=(n_{{H_2A}}, n_{{HA^-}}, n_{{A^{{2-}}}}, n_{{OH^-}}, n_{{H^+}})={init_tuple}\\).
Let \\(\\mathbf{{S}}\\in\\{{\\text{{B}},\\text{{A}}\\}}^*\\) be a fixed reagent schedule; for this instance, use the first \\(n\\) characters shown below.
Each step applies exactly ONE reagent and updates the ledger in the STRICT order listed; each sub-step uses the counts **after** the previous sub-step. All counts remain non-negative due to \\(\\min\\).

**If the step is 'B' (base):**
0) Reagent add: \\(n_{{OH^-}}\\mathrel{{+}}=\\Delta_{{base}}\\).  
1) Strong neutralization: \\(z=\\min(n_{{H^+}}, n_{{OH^-}})\\); then  
\\(n_{{H^+}}\\mathrel{{-}}=z,\\; n_{{OH^-}}\\mathrel{{-}}=z\\)  (\\(H^+ + OH^- \\to H_2O\\)).  
2) First deprotonation: \\(x_1=\\min(n_{{H_2A}}, n_{{OH^-}})\\);  
\\(n_{{H_2A}}\\mathrel{{-}}=x_1,\\; n_{{HA^-}}\\mathrel{{+}}=x_1,\\; n_{{OH^-}}\\mathrel{{-}}=x_1\\)  
(\\(H_2A + OH^- \\to HA^- + H_2O\\)).  
3) Second deprotonation: \\(x_2=\\min(n_{{HA^-}}, n_{{OH^-}})\\);  
\\(n_{{HA^-}}\\mathrel{{-}}=x_2,\\; n_{{A^{{2-}}}}\\mathrel{{+}}=x_2,\\; n_{{OH^-}}\\mathrel{{-}}=x_2\\)  
(\\(HA^- + OH^- \\to A^{{2-}} + H_2O\\)).

**If the step is 'A' (acid):**
0) Reagent add: \\(n_{{H^+}}\\mathrel{{+}}=\\Delta_{{acid}}\\).  
1) Strong neutralization: \\(z=\\min(n_{{H^+}}, n_{{OH^-}})\\); then  
\\(n_{{H^+}}\\mathrel{{-}}=z,\\; n_{{OH^-}}\\mathrel{{-}}=z\\)  (\\(H^+ + OH^- \\to H_2O\\)).  
2) First protonation: \\(y_1=\\min(n_{{A^{{2-}}}}, n_{{H^+}})\\);  
\\(n_{{A^{{2-}}}}\\mathrel{{-}}=y_1,\\; n_{{HA^-}}\\mathrel{{+}}=y_1,\\; n_{{H^+}}\\mathrel{{-}}=y_1\\)  
(\\(A^{{2-}} + H^+ \\to HA^-\\)).  
3) Second protonation: \\(y_2=\\min(n_{{HA^-}}, n_{{H^+}})\\);  
\\(n_{{HA^-}}\\mathrel{{-}}=y_2,\\; n_{{H_2A}}\\mathrel{{+}}=y_2,\\; n_{{H^+}}\\mathrel{{-}}=y_2\\)  
(\\(HA^- + H^+ \\to H_2A\\)).

Schedule prefix used here: \"{schedule_prefix}\"  
Parameters: \\(\\Delta_{{base}}={args.delta_base}\\), \\(\\Delta_{{acid}}={args.delta_acid}\\).

**Task.** After \\(n={step}\\) {"step" if step == 1 else "steps"}, output a single integer \\(n_{{HA^-}}\\) as the final answer."""
        # (a) \\(S_n=(n_{{H_2A}}, n_{{HA^-}}, n_{{A^{{2-}}}}, n_{{OH^-}}, n_{{H^+}})\\);
# (b) first-step indices \\(t_{{eq1}}\\) (exact first equivalence: \\(H_2A=0,\\ A^{{2-}}=0\\), no strong leftover) and \\(t_{{eq2}}\\) (exact second equivalence: \\(H_2A=0,\\ HA^-=0\\), no strong leftover);
# (c) a region label in \\{{pre\\_eq1, at\\_eq1, between\\_eq1\\_eq2, at\\_eq2, base\\_excess, acid\\_excess\\}}.
#
# Schedule prefix used here: \"{schedule_prefix}\".
# Return the tuple in (a), then \\(t_{{eq1}}\\), \\(t_{{eq2}}\\), and the region label."""

        # gt = {
        #     "Sn": {"n_H2A": int(nH2A), "n_HA-": int(nHA), "n_A2-": int(nA2), "n_OH-": int(nOH), "n_H+": int(nH)},
        #     "t_eq1": int(teq1) if teq1 is not None else None,
        #     "t_eq2": int(teq2) if teq2 is not None else None,
        #     "region": region,
        #     "passed_eq2": bool(passed_eq2),
        #     "delta_base": int(args.delta_base),
        #     "delta_acid": int(args.delta_acid),
        #     "schedule_prefix": schedule_prefix,
        #     "mode_this_step": mode
        # }

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": int(nHA)
        }
        dataset.append(data_line)

        # (Optional) quick trace
        print(f"step={step:>3}  S=({nH2A},{nHA},{nA2},{nOH},{nH})  region={region}  teq1={teq1} teq2={teq2}  step_mode={mode}")

    # Save to .jsonl
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_file}")

if __name__ == "__main__":
    main()
