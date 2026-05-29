#!/usr/bin/env python3
"""
DramoraFlutterPatch Decryptor
Decrypts emoji-encoded Python code
"""

import re

# Emoji mapping dari file encrypted
EMOJI_MAP = {
    '😀': 0, 
    '😁': 3, 
    '😂': 6, 
    '😃': 1, 
    '😄': 2, 
    '😅': 4, 
    '😉': 7, 
    '😊': 8, 
    '😛': 9, 
    '🤣': 5
}

def extract_emoji_content(filepath):
    """Extract emoji string from exec statement"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The format is: exec("".join(map(chr,[int("".join(str({...}[i]) for i in x.split())) for x in
    # "emoji_string"))))
    # Find where emoji data starts (after "for x in\n")
    idx = content.find('for x in\n"')
    if idx == -1:
        raise ValueError("Cannot find 'for x in' statement")
    
    # Start of emoji string
    start_idx = idx + len('for x in\n"')
    
    # Find the end - look for the closing quote followed by newlines and parentheses
    # The pattern is: ...emojis..."\n)))))
    lines = content[start_idx:].split('\n')
    emoji_lines = []
    for line in lines:
        stripped = line.strip()
        # Remove trailing backslash
        if stripped.endswith('\\'):
            stripped = stripped[:-1]
        # Check if this is the end line (contains only ")" or quotes)
        if stripped.startswith(')') or stripped.startswith('"]'):
            break
        # Only keep emoji characters and spaces
        clean_line = ''
        for char in stripped:
            if char in EMOJI_MAP or char == ' ':
                clean_line += char
        if clean_line.strip():
            emoji_lines.append(clean_line.strip())
    
    emoji_text = ' '.join(emoji_lines)
    return emoji_text

def emoji_to_digits(emoji_text):
    """Convert emoji sequence to digit string"""
    numbers = []
    for emoji in emoji_text.split():
        if emoji in EMOJI_MAP:
            numbers.append(EMOJI_MAP[emoji])
        else:
            print(f"Warning: Unknown emoji '{emoji}'")
    return ''.join(str(n) for n in numbers)

def decrypt_digit_string(digit_str):
    """
    Decrypt digit string using smart variable-length parsing
    ASCII values can be 2 or 3 digits (32-126)
    Priority: try 3-digit first, then 2-digit
    """
    result = []
    i = 0
    while i < len(digit_str):
        # Try 3-digit first (for values 100-126)
        if i + 3 <= len(digit_str):
            val3 = int(digit_str[i:i+3])
            if 32 <= val3 <= 126:
                result.append(chr(val3))
                i += 3
                continue
        
        # Try 2-digit (for values 32-99)
        if i + 2 <= len(digit_str):
            val2 = int(digit_str[i:i+2])
            if 32 <= val2 <= 126:
                result.append(chr(val2))
                i += 2
                continue
        
        # Skip invalid
        i += 1
    
    return ''.join(result)

def main():
    input_file = '/workspace/DramoraFlutterPatch.py'
    output_file = '/workspace/DramoraFlutterPatch_DECRYPTED.py'
    
    print("=" * 60)
    print("DramoraFlutterPatch Decryptor")
    print("=" * 60)
    
    # Step 1: Extract emoji content
    print("\n[1/4] Extracting emoji content...")
    emoji_text = extract_emoji_content(input_file)
    print(f"      Extracted {len(emoji_text)} characters of emoji text")
    
    # Step 2: Convert emoji to digits
    print("\n[2/4] Converting emoji to digits...")
    digit_str = emoji_to_digits(emoji_text)
    print(f"      Converted to {len(digit_str)} digits")
    print(f"      First 100 digits: {digit_str[:100]}")
    
    # Step 3: Decrypt digit string to ASCII
    print("\n[3/4] Decrypting to ASCII code...")
    decrypted_code = decrypt_digit_string(digit_str)
    print(f"      Decrypted {len(decrypted_code)} characters")
    
    # Step 4: Save result
    print(f"\n[4/4] Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decrypted_code)
    
    print("\n" + "=" * 60)
    print("DECRYPTION COMPLETE!")
    print("=" * 60)
    print(f"\nFirst 500 characters of decrypted code:")
    print("-" * 60)
    print(decrypted_code[:500])
    print("-" * 60)
    print(f"\nFull code saved to: {output_file}")

if __name__ == '__main__':
    main()
