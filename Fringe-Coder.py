#!/usr/bin/env python3
"""
fringe_cipher.py - Encoder/decoder for the glyph cipher used in the TV show Fringe.

The show flashed one of eight glyphs (Apple, Butterfly, Flower, Frog, Hand, Leaf,
Seahorse, Smoke) before each commercial break. Each glyph appeared either in its
normal orientation or mirrored, with a glowing yellow dot in one of several
positions. Every (glyph, orientation, dot) combination maps to one letter - a
monoalphabetic substitution cipher.

Since a terminal can't draw the glyphs, each one is written as a token:

    GLYPH-ORIENT-DOT      e.g.  Leaf-N-D   Apple-M-A   Smoke-M-E

    GLYPH   Apple | Butterfly | Flower | Frog | Hand | Leaf | Seahorse | Smoke
    ORIENT  N = normal, M = mirrored
    DOT     dot-position code (A-F) from the Ars Technica transcription
            that first cracked the cipher

Letters are separated by spaces, words by " / ".

Key provenance: A-E, G-I, K-L, N-P, R-V come from the Sanchez/Sadun solution.
F, J, M, Q, W, Y follow the fan reconstruction; X and Z were never aired and are
placeholders. Edit KEY below (or supply a JSON key file) to correct any entry -
the program only requires that the table be one-to-one.

Usage:
    ./fringe_cipher.py                 interactive menu
    ./fringe_cipher.py --key my.json   use a custom key file
    ./fringe_cipher.py --dump-key      print the key as JSON (edit, then --key)
"""

import argparse
import json
import sys

GLYPHS = ("Apple", "Butterfly", "Flower", "Frog", "Hand", "Leaf", "Seahorse", "Smoke")
ORIENTS = {"N": "normal", "M": "mirrored"}
DOTS = ("A", "B", "C", "D", "E", "F")
WORD_SEP = " / "

# letter -> (glyph, orientation, dot, verified)
KEY = {
    "A": ("Leaf",      "N", "D", True),
    "B": ("Leaf",      "M", "A", True),
    "C": ("Apple",     "N", "A", True),
    "D": ("Apple",     "N", "D", True),
    "E": ("Apple",     "N", "C", True),
    "F": ("Apple",     "M", "A", False),
    "G": ("Leaf",      "N", "F", True),
    "H": ("Leaf",      "M", "C", True),
    "I": ("Flower",    "N", "A", True),
    "J": ("Flower",    "M", "A", False),
    "K": ("Flower",    "M", "F", True),
    "L": ("Flower",    "N", "C", True),
    "M": ("Seahorse",  "N", "F", False),
    "N": ("Seahorse",  "M", "F", True),
    "O": ("Butterfly", "M", "C", True),
    "P": ("Butterfly", "N", "F", True),
    "Q": ("Frog",      "M", "F", False),
    "R": ("Frog",      "N", "F", True),
    "S": ("Hand",      "N", "C", True),
    "T": ("Smoke",     "M", "E", True),
    "U": ("Hand",      "M", "F", True),
    "V": ("Hand",      "N", "B", True),
    "W": ("Hand",      "M", "B", False),
    "X": ("Smoke",     "N", "A", False),
    "Y": ("Smoke",     "N", "E", False),
    "Z": ("Smoke",     "M", "A", False),
}


# ---------------------------------------------------------------- key handling
def validate_key(key):
    """Raise ValueError if the key is malformed or not one-to-one."""
    seen = {}
    for letter, entry in key.items():
        glyph, orient, dot = entry[0], entry[1], entry[2]
        if glyph not in GLYPHS:
            raise ValueError(f"{letter}: unknown glyph '{glyph}'")
        if orient not in ORIENTS:
            raise ValueError(f"{letter}: orientation must be N or M, got '{orient}'")
        if dot not in DOTS:
            raise ValueError(f"{letter}: dot code must be one of {DOTS}, got '{dot}'")
        token = (glyph, orient, dot)
        if token in seen:
            raise ValueError(f"{letter} and {seen[token]} both map to {glyph}-{orient}-{dot}")
        seen[token] = letter


def load_key(path):
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    key = {}
    for letter, entry in raw.items():
        letter = letter.upper()
        if len(entry) == 3:
            entry = list(entry) + [True]
        key[letter] = (entry[0], entry[1].upper(), entry[2].upper(), bool(entry[3]))
    validate_key(key)
    return key


def dump_key(key):
    printable = {k: list(v) for k, v in sorted(key.items())}
    print(json.dumps(printable, indent=2))


# ---------------------------------------------------------------- cipher core
def token_of(entry):
    return f"{entry[0]}-{entry[1]}-{entry[2]}"


def build_reverse(key):
    return {token_of(v).upper(): k for k, v in key.items()}


def encode(text, key):
    """Return (ciphertext, dropped) where dropped lists characters skipped."""
    words, dropped = [], []
    for word in text.split():
        toks = []
        for ch in word:
            up = ch.upper()
            if up in key:
                toks.append(token_of(key[up]))
            else:
                dropped.append(ch)
        if toks:
            words.append(" ".join(toks))
    return WORD_SEP.join(words), dropped


def decode(cipher, key):
    """Return (plaintext, unknown) where unknown lists tokens not in the key."""
    rev = build_reverse(key)
    out_words, unknown = [], []
    for chunk in cipher.replace("|", "/").split("/"):
        letters = []
        for tok in chunk.split():
            hit = rev.get(tok.strip().upper())
            if hit:
                letters.append(hit)
            else:
                unknown.append(tok)
        if letters:
            out_words.append("".join(letters))
    return " ".join(out_words), unknown


# ---------------------------------------------------------------- UI helpers
BANNER = r"""
  ______ _____  _____ _   _  _____ ______
 |  ____|  __ \|_   _| \ | |/ ____|  ____|
 | |__  | |__) | | | |  \| | |  __| |__
 |  __| |  _  /  | | | . ` | | |_ |  __|
 | |    | | \ \ _| |_| |\  | |__| | |____
 |_|    |_|  \_\_____|_| \_|\_____|______|
            G L Y P H   C I P H E R
"""

MENU = """
  [1] Encode  - text to glyphs
  [2] Decode  - glyphs to text
  [3] Show key
  [4] Exit
"""


def show_key(key):
    print("\n Letter  Glyph      Orient    Dot   Status")
    print(" ------  ---------  --------  ---   --------")
    for letter in sorted(key):
        g, o, d, ok = key[letter]
        status = "verified" if ok else "unverified"
        print(f"   {letter}     {g:<9}  {ORIENTS[o]:<8}  {d}     {status}")
    print("\n Token form: GLYPH-ORIENT-DOT, e.g. " + token_of(key["A"]) + " = A")
    print(" Unverified entries were never aired or are fan reconstructions;")
    print(" use --dump-key, edit, and --key to override.\n")


def ask(prompt):
    """Single-line input; returns None on Ctrl-C / Ctrl-D so callers can bail."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def do_encode(key):
    text = ask("Text to encode: ")
    if text is None or not text.strip():
        print("Nothing to encode.")
        return
    cipher, dropped = encode(text, key)
    print("\nEncoded:\n" + cipher + "\n")
    if dropped:
        uniq = "".join(sorted(set(dropped)))
        print(f"Note: the cipher has letters only; skipped: {uniq!r}\n")


def do_decode(key):
    cipher = ask("Glyph tokens to decode (words separated by / ): ")
    if cipher is None or not cipher.strip():
        print("Nothing to decode.")
        return
    text, unknown = decode(cipher, key)
    print("\nDecoded:\n" + (text or "(no valid glyphs found)") + "\n")
    if unknown:
        print("Unrecognized tokens: " + ", ".join(unknown) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Fringe glyph cipher encoder/decoder")
    ap.add_argument("--key", metavar="FILE", help="JSON key file overriding the built-in key")
    ap.add_argument("--dump-key", action="store_true", help="print the key as JSON and exit")
    args = ap.parse_args()

    key = KEY
    try:
        validate_key(key)
        if args.key:
            key = load_key(args.key)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.exit(f"Key error: {exc}")

    if args.dump_key:
        dump_key(key)
        return

    print(BANNER)
    actions = {"1": do_encode, "2": do_decode, "3": show_key}
    while True:
        print(MENU)
        choice = ask("Select: ")
        if choice is None:
            print("Goodbye.")
            return
        choice = choice.strip().lower()
        if choice in ("4", "q", "x", "exit", "quit"):
            print("Goodbye.")
            return
        action = actions.get(choice)
        if action:
            action(key)
        else:
            print("Invalid choice - enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()