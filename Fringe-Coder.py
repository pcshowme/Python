"""
Fringe Glyph Substitution Cipher (5-bit)

Each Latin letter maps to a canonical Fringe base glyph
(Apple, Butterfly, Flower, Frog, Hand, Leaf, Seahorse, Smoke)
plus a distinct yellow-dot orientation/position.
"""

# Canonical Fringe Glyph alphabet mapping
# Format: CHAR -> (BASE_GLYPH, DOT_POSITION)
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

# Reverse lookup dictionary for decoding: (glyph, dot) -> char
REVERSE_LOOKUP = {v: k for k, v in FRINGE_ALPHABET.items()}


def encrypt_fringe(text: str) -> list[dict]:
    """
    Encrypt plain text into a structured Fringe glyph token stream.
    Preserves spaces and punctuation as raw literal tokens.
    """
    encoded_tokens = []
    for char in text.upper():
        if char in FRINGE_ALPHABET:
            glyph, dot = FRINGE_ALPHABET[char]
            encoded_tokens.append({
                "type": "glyph",
                "char": char,
                "glyph": glyph,
                "dot": dot,
                "token": f"{glyph}:{dot}"
            })
        elif char == ' ':
            encoded_tokens.append({"type": "separator", "token": " "})
        else:
            encoded_tokens.append({"type": "literal", "token": char})
    return encoded_tokens


def decrypt_fringe(tokens: list[dict]) -> str:
    """
    Decrypt a structured Fringe glyph token stream back into plain text.
    """
    decoded = []
    for token in tokens:
        if token["type"] == "glyph":
            key = (token["glyph"], token["dot"])
            decoded.append(REVERSE_LOOKUP.get(key, "?"))
        else:
            decoded.append(token["token"])
    return "".join(decoded)


def print_encoded_stream(tokens: list[dict]) -> None:
    for item in tokens:
        if item["type"] == "glyph":
            print(f"[{item['glyph']:<10} | Dot: {item['dot']:<15}] -> {item['char']}")
        elif item["type"] == "separator":
            print("--- [SPACE] ---")
        else:
            print(f"[LITERAL: {item['token']}]")


if __name__ == "__main__":
    plaintext = "OBSERVER"
    print(f"Original Text: {plaintext}\n")

    # Encrypt
    encrypted_stream = encrypt_fringe(plaintext)
    print("--- ENCRYPTED GLYPH STREAM ---")
    print_encoded_stream(encrypted_stream)

    # Decrypt
    decrypted_text = decrypt_fringe(encrypted_stream)
    print(f"\nDecrypted Output: {decrypted_text}")