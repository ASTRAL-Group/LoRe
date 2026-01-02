"""
Generate the Test Output Prediction data: Digit Rotate-and-Add chain (simple, easy to read)
(Simplified version of Task 8)
"""
import argparse
import json

from pathlib import Path

TASK_TYPE = "digit-rot-add-mod10"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"


def update_digit_rot_add(state: str, i=None) -> str:
    """
    Update rule (pure function, 0-based indexing):

        State is a string of decimal digits, e.g., "12345678".
        One update step does the following:

        1) Rotate-left the string by 1 position:
           "abcd" -> "bcda"  (0-based positions shift left; index 0 goes to the end)

        2) For each position j (0..L-1), add (t + j) modulo 10 to that digit,
           where t is the 0-based iteration index of this step and L = len(state).

           Example with L=4 and t=2 on "1357" after rotation:
             j=0 add (2+0)=2, j=1 add (2+1)=3, j=2 add (2+2)=4, j=3 add (2+3)=5

        The function accepts the iteration index i (treated as t) for compatibility
        with the generator; if i is None, t defaults to 0.

    Args:
        state: str of digits '0'..'9'
        i:     0-based iteration index t (int)

    Returns:
        Next state as a str of digits with the same length.
    """
    s = state
    L = len(s)
    t = 0 if i is None else int(i)

    # Step 1: rotate-left by 1 (0-based)
    s = s[1:] + s[:1]

    # Step 2: add (t + j) mod 10 to each digit
    out_chars = []
    for j, ch in enumerate(s):
        d = (ord(ch) - 48 + (t + j)) % 10
        out_chars.append(chr(48 + d))
    return "".join(out_chars)


def main():
    parser = argparse.ArgumentParser(
        description="Run Digit Rotate-and-Add updates (simple Code Execution style) for Test Output Prediction"
    )
    parser.add_argument(
        "--num_step",
        type=int,
        default=30,
        help="Number of records to generate; record t uses N = t iterations (1..num_step)",
    )
    parser.add_argument(
        "--out_path",
        type=str,
        default="linear-mono-code-8-top-digit-rot-add.jsonl",
        help="Path to output .jsonl file",
    )
    parser.add_argument(
        "--init_state",
        type=str,
        default="12345678",
        help="Initial state as a string of digits (e.g., '12345678'). Length must be >= 1.",
    )
    args = parser.parse_args()

    init_state = str(args.init_state)
    if not init_state.isdigit():
        raise ValueError("init_state must be a string of digits '0'..'9'.")

    dataset = []

    updated_state = None
    for i in range(args.num_step):
        step = i + 1  # N iterations
        if i == 0:
            updated_state = update_digit_rot_add(init_state, i)
        else:
            updated_state = update_digit_rot_add(updated_state, i)

        ANSWER = updated_state  # final string after 'step' iterations
        print(ANSWER)

        task_text = f"""You are given runnable Python 3.10 code. Execute it exactly as-is in a clean environment (no extra imports).
This is a Code Execution task: run the program; do not rewrite or translate it.
Indexing is 0-based for both the iteration counter t and string positions.

Return only the value of ANSWER (no other text, no formatting).

Code:
'''python
# Task (Code Execution)
# Language: Python 3.10
# Run this code exactly as-is. Do NOT import anything.
# Evaluate the final value assigned to ANSWER and return it with no extra text.

N = {step}  # number of iterations (non-negative integer)
s = {init_state!r}  # initial digit string, e.g., "12345678"

def f(s: str, t: int) -> str:
    s = s[1:] + s[:1]
    out = []
    for j, ch in enumerate(s):
        d = (ord(ch) - 48 + (t + j)) % 10
        out.append(chr(48 + d))
    return "".join(out)

for t in range(N):  # t is 0-based: 0,1,...,N-1
    s = f(s, t)

ANSWER = s
'''
Return ANSWER exactly as produced by the program above as the final answer wrapped in \\boxed{{}}: \\boxed{{ANSWER}}.
"""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": ANSWER,  # final string after N steps
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
