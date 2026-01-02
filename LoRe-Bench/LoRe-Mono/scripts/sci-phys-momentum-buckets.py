"""
Generate harder discrete momentum-bucket transfer tasks (S2):
- 3 buckets with hysteresis threshold, compensation debt, periodic recycle,
  and an auxiliary bit g. Return a weighted modular sum after N steps.
"""
import argparse
import json
from pathlib import Path

# ---- Metadata / IO ----
TASK_TYPE = "phys-momentum-buckets-S2"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

# ---- One-step update rule (hysteresis + debt + recycle) ----
def step_once_hard(
    p0: int, p1: int, p2: int, f: int, g: int, c: int,
    tau_low: int, tau_high: int,
    recycle_period: int, debt_threshold: int,
    t: int,
):
    """
    Perform exactly one update step with added dynamics.

    Effective threshold (hysteresis):
        tau_eff = tau_high if f==0 else tau_low

    Primary branch (A/B/C):
      A) If p0 >= tau_eff:
           p0 -= 1; p1 += 1; f ^= 1
           # g toggles if p1 is odd AFTER this increment
           if (p1 & 1): g ^= 1
      B) Else if p1 > 0:
           p1 -= 1; p2 += 1  # f unchanged
           # g toggles if p2 becomes even AFTER this increment
           if (p2 % 2) == 0: g ^= 1
      C) Else (p1 == 0):
           # thermal compensation (no decrement)
           p1 += 1
           c += 1              # track 'debt' from compensation; f,g unchanged

    End-of-step maintenance:
      1) Debt settlement (P-conserving):
           while c >= debt_threshold:
               c -= debt_threshold
               if p2 > 0:
                   p2 -= 1; p0 += 1
               elif p1 > 0:
                   p1 -= 1; p0 += 1
               # else: nothing to move; settlement is skipped

      2) Periodic recycle (every recycle_period steps):
           if t % recycle_period == 0 and p2 >= 2:
               p2 -= 2; p0 += 1   # note: P decreases by 1 here
               f ^= 1             # extra gating flip on recycle

    Returns updated (p0,p1,p2,f,g,c), and a branch label plus maintenance notes.
    """
    notes = []
    tau_eff = tau_high if f == 0 else tau_low

    # ---- Primary branch ----
    if p0 >= tau_eff:
        p0 -= 1
        p1 += 1
        f ^= 1
        # toggle g if p1 is odd AFTER increment
        if (p1 & 1) == 1:
            g ^= 1
        branch = "A(p0>=tau_eff)"
    else:
        if p1 > 0:
            p1 -= 1
            p2 += 1
            # toggle g if p2 becomes even AFTER increment
            if (p2 % 2) == 0:
                g ^= 1
            branch = "B(p0<tau_eff,p1>0)"
        else:
            p1 += 1
            c += 1
            branch = "C(compensate p1+=1; debt c+=1)"

    # ---- Debt settlement ----
    settled = 0
    while c >= debt_threshold:
        c -= debt_threshold
        if p2 > 0:
            p2 -= 1; p0 += 1
            settled += 1
        elif p1 > 0:
            p1 -= 1; p0 += 1
            settled += 1
        else:
            # Nothing to shift; break to avoid infinite loop
            break
    if settled > 0:
        notes.append(f"settle×{settled}")

    # ---- Periodic recycle ----
    if recycle_period > 0 and (t % recycle_period) == 0 and p2 >= 2:
        p2 -= 2
        p0 += 1
        f ^= 1
        notes.append("recycle(p2-=2,p0+=1,f^=1)")

    label = branch + ("" if not notes else " | " + ",".join(notes))
    return p0, p1, p2, f, g, c, label


def main():
    parser = argparse.ArgumentParser(
        description="Generate harder momentum-bucket tasks with hysteresis/debt/recycle and weighted modulo query"
    )
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of lines (instances) to generate; instance i uses n=i steps (default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-phys-momentum-buckets.jsonl",
                        help="Output .jsonl (default: linear-mono-phys-momentum-buckets-S2.jsonl)")

    # ---- Modulus ----
    parser.add_argument("--M", type=int, default=97, help="Prime modulus M used only at query time (default: 97)")

    # ---- Hysteresis thresholds ----
    parser.add_argument("--tau_low", type=int, default=5, help="Lower threshold when f==1 (default: 5)")
    parser.add_argument("--tau_high", type=int, default=9, help="Higher threshold when f==0 (default: 9)")

    # ---- Periodic recycle & debt ----
    parser.add_argument("--recycle_period", type=int, default=4, help="Recycle period R (every R steps) (default: 4)")
    parser.add_argument("--debt_threshold", type=int, default=3, help="Debt settlement threshold K (default: 3)")

    # ---- Initial state ----
    parser.add_argument("--p0", type=int, default=5, help="Initial p0 (>=0)")
    parser.add_argument("--p1", type=int, default=0, help="Initial p1 (>=0)")
    parser.add_argument("--p2", type=int, default=3, help="Initial p2 (>=0)")
    parser.add_argument("--f0", type=int, default=0, choices=[0,1], help="Initial f in {0,1} (default: 0)")
    parser.add_argument("--g0", type=int, default=0, choices=[0,1], help="Initial g in {0,1} (default: 0)")
    parser.add_argument("--c0", type=int, default=0, help="Initial debt counter c (>=0)")

    # ---- Weighted query ----
    parser.add_argument("--w0", type=int, default=1, help="Weight for p0 (default: 1)")
    parser.add_argument("--w1", type=int, default=2, help="Weight for p1 (default: 2)")
    parser.add_argument("--w2", type=int, default=3, help="Weight for p2 (default: 3)")
    parser.add_argument("--wf", type=int, default=4, help="Weight for f (default: 4)")
    parser.add_argument("--wg", type=int, default=5, help="Weight for g (default: 5)")
    parser.add_argument("--wc", type=int, default=1, help="Weight for c (default: 1)")

    args = parser.parse_args()
    assert args.num_step >= 1
    assert args.M >= 3, "M must be >= 3 (and should be prime)."
    assert 1 <= args.tau_low <= args.tau_high < args.M, "Require 1 <= tau_low <= tau_high < M."
    assert args.p0 >= 0 and args.p1 >= 0 and args.p2 >= 0 and args.c0 >= 0

    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize state deterministically
    p0, p1, p2 = int(args.p0), int(args.p1), int(args.p2)
    f, g, c = int(args.f0), int(args.g0), int(args.c0)

    dataset = []

    # Static description strings
    setting_line = (
        "Three nonnegative integer 'momentum buckets' p0,p1,p2, flip-bit f∈{0,1}, "
        "aux-bit g∈{0,1}, and a nonnegative debt counter c."
    )
    conservation_note = (
        "Total P = p0+p1+p2 is conserved on branches A/B and during debt settlement; "
        "increases by +1 on branch C (compensation), and decreases by −1 on periodic recycle "
        "(when it triggers). Modulo is applied only at the very end."
    )

    for i in range(args.num_step):
        step = i + 1

        # Evolve exactly one step each loop to build increasing-N tasks
        p0, p1, p2, f, g, c, branch = step_once_hard(
            p0, p1, p2, f, g, c,
            args.tau_low, args.tau_high,
            args.recycle_period, args.debt_threshold,
            step,
        )

        # Ground-truth answer: weighted sum modulo M after n=step steps
        total_weighted = (
            args.w0 * p0 + args.w1 * p1 + args.w2 * p2 +
            args.wf * f + args.wg * g + args.wc * c
        )
        gt = int(total_weighted % args.M)

        # Task text
        task_text = f"""Granular lab run — discrete momentum reservoirs with hysteresis & debt

Setting
- {setting_line}
- Prime modulus M = {args.M} is used only in the final query (no per-step modular reductions).

Start state
- At t=0: (p0, p1, p2) = ({args.p0}, {args.p1}, {args.p2}), f = {args.f0}, g = {args.g0}, c = {args.c0}.
- Hysteresis thresholds: τ_low = {args.tau_low}, τ_high = {args.tau_high}.
- Recycle period R = {args.recycle_period}; debt settlement threshold K = {args.debt_threshold}.

Per-step update (repeat for t = 1..n with n={step})
1) Let τ_eff = τ_high if f=0 else τ_low.
2) Primary branch:
   A) If p0 ≥ τ_eff:
        p0 ← p0 − 1;  p1 ← p1 + 1;  f ← f ⊕ 1;
        if (p1 is odd) then g ← g ⊕ 1.
   B) Else if p1 > 0:
        p1 ← p1 − 1;  p2 ← p2 + 1;  (f unchanged);
        if (p2 is even) then g ← g ⊕ 1.
   C) Else (p1 = 0):
        # thermal compensation (no decrement)
        p1 ← p1 + 1;  c ← c + 1;  (f, g unchanged).

3) End-of-step maintenance:
   a) Debt settlement (repeat while c ≥ K):
        c ← c − K;  if p2>0 then (p2 ← p2 − 1; p0 ← p0 + 1)
                     else if p1>0 then (p1 ← p1 − 1; p0 ← p0 + 1)
                     else (no-op).
   b) Periodic recycle:
        If (t mod R = 0) and p2 ≥ 2:
            p2 ← p2 − 2;  p0 ← p0 + 1;  f ← f ⊕ 1.

Notes
- {conservation_note}

Objective
- After exactly n={step} {"step" if step==1 else "steps"}, report the integer
  S = (w0·p0 + w1·p1 + w2·p2 + wf·f + wg·g + wc·c) mod M
  with weights (w0,w1,w2,wf,wg,wc)=({args.w0},{args.w1},{args.w2},{args.wf},{args.wg},{args.wc})."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": gt
        }
        dataset.append(data_line)

        # (Optional) debug print
        P = p0 + p1 + p2
        print(
            f"step={step:>3}  p=({p0},{p1},{p2})  f={f} g={g} c={c}  "
            f"branch={branch}  P={P}  S={total_weighted % args.M}"
        )

    # Save to .jsonl
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DATA_SAVE_DIR / args.out_path
    with open(out_file, "w", encoding="utf-8") as f_out:
        for rec in dataset:
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {out_file}")


if __name__ == "__main__":
    main()
