"""
Generate the CV-rotation (phonological iterator) data: vowel/consonant wheels with synchronous updates
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

TASK_TYPE = "phonology-cv-rotation"
CURRENT_PATH = Path(__file__).parent
DATA_SAVE_DIR = CURRENT_PATH.parent / "data"

def build_cycle_map(cycle: str):
    """
    Build a wrap-around mapping dict for a cycle string.
    Example: "aeiou" -> {'a':'e','e':'i','i':'o','o':'u','u':'a'}
    """
    m = {}
    for i, ch in enumerate(cycle):
        m[ch] = cycle[(i + 1) % len(cycle)]
    return m

def update_word_once(word: str, rotV: dict, rotC: dict) -> str:
    """
    Apply one synchronous CV-rotation step to the given word.

    Rules:
      - Vowels rotate on the vowel wheel (rotV).
      - Consonants rotate on the consonant wheel (rotC).
      - Case is preserved (A -> E, b -> c, etc.).
      - Non-letters (digits, hyphens, spaces, punctuation) are left unchanged.
      - Update is synchronous: every character is replaced based on the *original* w_t.
    """
    out_chars = []
    for ch in word:
        low = ch.lower()
        if low in rotV:
            nxt = rotV[low]
            out_chars.append(nxt.upper() if ch.isupper() else nxt)
        elif low in rotC:
            nxt = rotC[low]
            out_chars.append(nxt.upper() if ch.isupper() else nxt)
        else:
            out_chars.append(ch)  # leave non-letters or out-of-inventory chars as-is
    return "".join(out_chars)

def main():
    parser = argparse.ArgumentParser(description="Run CV-rotation (vowel/consonant wheels) for phonological iteration")
    parser.add_argument("--num_step", type=int, default=30,
                        help="Number of steps to generate (each record uses n = step from 1..num_step; default: 30)")
    parser.add_argument("--out_path", type=str, default="linear-mono-language-phonology-cv-rotation.jsonl",
                        help="Path to output .jsonl file (default: phonology-cv-rotation.jsonl)")
    args = parser.parse_args()

    # Inventory & cycles (ASCII English letters; 'y' treated as a consonant)
    V_CYCLE = "aeiou"
    C_CYCLE = "bcdfghjklmnpqrstvwxyz"

    rotV = build_cycle_map(V_CYCLE)
    rotC = build_cycle_map(C_CYCLE)

    # Initial spelling to iterate from (feel free to change)
    init_word = "bougainvillea"

    dataset = []
    updated_word = None

    for i in range(args.num_step):
        step = i + 1

        # Iteratively update from w0 to w_step
        if i == 0:
            updated_word = update_word_once(init_word, rotV, rotC)
        else:
            updated_word = update_word_once(updated_word, rotV, rotC)

        print(updated_word)

        task_text = f"""Given an integer n={step}, perform a vowel/consonant rotation sound change on the spelling w0="{init_word}" for exactly n steps.

What this task means (plain language):
- We split letters into two wheels and rotate them forward.
- Vowels are the five English vowels a, e, i, o, u (here, 'y' counts as a consonant).
- Consonants are all other letters a–z.

Rotation wheels (both loop back to the start):
- Vowel wheel: a → e → i → o → u → a
- Consonant wheel: b → c → d → f → g → h → j → k → l → m → n → p → q → r → s → t → v → w → x → y → z → b

How to update (do this n times):
1) Look at every character in the current spelling w_t at the same time (synchronous update).
2) If a character is a vowel, replace it with the next vowel on the vowel wheel.
3) If a character is a consonant, replace it with the next consonant on the consonant wheel.
4) Preserve lettercase (A→E, b→c). Characters that are not letters (digits, hyphens, spaces, punctuation) stay exactly as they are.
5) This produces the next spelling w_(t+1). Repeat until you have applied exactly n={step} {"steps" if step > 1 else "step"}.

Output:
Return the final spelling w_{step} only (just the string, no quotes or extra text)."""

        data_line = {
            "idx": step,
            "type": TASK_TYPE,
            "task": task_text,
            "gt_ans": updated_word
        }
        dataset.append(deepcopy(data_line))

    # Save all data_line records to a .jsonl file
    DATA_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_SAVE_DIR / args.out_path, "w", encoding="utf-8") as f:
        for rec in dataset:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dataset)} records to {args.out_path}")

if __name__ == "__main__":
    main()
