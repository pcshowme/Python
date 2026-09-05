"""
Fringe Cipher CLI: Interactive Encoder/Decoder
Encodes text into portable 'Glyph:Dot' strings and decodes them back.
"""

# Canonical Fringe Glyph alphabet mapping
FRINGE_ALPHABET = {
    'A': ('Apple', 'External-Right'),
    'B': ('Apple', 'Top'),
    'C': ('Butterfly', 'Wing-Left'),
    'D': ('Butterfly', 'Wing-Right'),
    'E': ('Flower', 'Petal-Top'),
    'F': ('Flower', 'Stem-Base'),
    'G': ('Frog', 'Back-Left'),
    'H': ('Frog', 'Spine'),
    'I': ('Hand', 'Palm'),
    'J': ('Hand', 'Thumb'),
    'K': ('Leaf', 'Tip'),
    'L': ('Leaf', 'Stem'),
    'M': ('Seahorse', 'Tail'),
    'N': ('Seahorse', 'Crown'),
    'O': ('Smoke', 'Top-Left'),
    'P': ('Smoke', 'Center'),
    'Q': ('Apple', 'Stem'),
    'R': ('Butterfly', 'Center'),
    'S': ('Flower', 'Center'),
    'T': ('Frog', 'Head'),
    'U': ('Hand', 'Wrist'),
    'V': ('Leaf', 'Center'),
    'W': ('Seahorse', 'Belly'),
    'X': ('Smoke', 'Bottom'),
    'Y': ('Hand', 'Pinky'),
    'Z': ('Frog', 'Eye'),
}

# Reverse lookup dictionary for decoding: "glyph:dot" (lowercased) -> char
REVERSE_LOOKUP = {
    f"{glyph.lower()}:{dot.lower()}": char
    for char, (glyph, dot) in FRINGE_ALPHABET.items()
}


def encode_message(text: str) -> str:
    """Encodes plain text into space-separated Glyph:Dot tokens."""
    tokens = []
    for word in text.upper().split(' '):
        word_tokens = []
        for char in word:
            if char in FRINGE_ALPHABET:
                glyph, dot = FRINGE_ALPHABET[char]
                word_tokens.append(f"{glyph}:{dot}")
            else:
                word_tokens.append(char)
        tokens.append(" ".join(word_tokens))
    return " / ".join(tokens)


def decode_message(cipher_text: str) -> str:
    """Decodes space-separated Glyph:Dot tokens back into text."""
    decoded_words = []
    raw_words = cipher_text.strip().split(" / ")

    for word in raw_words:
        chars = []
        tokens = word.strip().split()
        for token in tokens:
            cleaned_token = token.strip().lower()
            if cleaned_token in REVERSE_LOOKUP:
                chars.append(REVERSE_LOOKUP[cleaned_token])
            else:
                chars.append(token)
        decoded_words.append("".join(chars))

    return " ".join(decoded_words)


def main():
    while True:
        print("\n=== FRINGE CIPHER INTERFACE ===")
        print("1. Encode (Plain Text -> Fringe Glyphs)")
        print("2. Decode (Fringe Glyphs -> Plain Text)")
        print("3. Exit")
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            msg = input("\nEnter message to ENCODE: ")
            encoded = encode_message(msg)
            print(f"\nCiphertext:\n{encoded}\n")
        elif choice == "2":
            print("\nEnter token string (e.g., 'Smoke:Top-Left Butterfly:Center / Apple:Top'):")
            cipher = input("Enter message to DECODE: ")
            decoded = decode_message(cipher)
            print(f"\nDecoded Text:\n{decoded}\n")
        elif choice == "3":
            print("Shutting down interface.")
            break
        else:
            print("Invalid selection. Enter 1, 2, or 3.")


if __name__ == "__main__":
    main()