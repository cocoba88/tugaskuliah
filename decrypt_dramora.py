#!/usr/bin/env python3
"""
Decryptor untuk DramoraFlutterPatch.py
Script ini akan mengekstrak dan menampilkan kode asli yang di-obfuscate
"""

import re

# Mapping emoji ke digit angka
emoji_map = {
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

def decrypt_emoji_string(encrypted_string):
    """
    Decrypt string yang di-obfuscate dengan emoji
    Setiap grup emoji dipisahkan oleh double/triple space
    Setiap emoji dalam grup merepresentasikan digit angka
    Angka tersebut adalah kode ASCII dari karakter asli
    """
    decrypted_chars = []
    
    # Split oleh 2 atau lebih spasi untuk mendapatkan setiap grup emoji
    groups = re.split(r'\s{2,}', encrypted_string.strip())
    
    for group in groups:
        if not group.strip():
            continue
        
        # Untuk setiap grup emoji, konversi ke angka lalu ke karakter ASCII
        digits = ""
        emojis = group.strip().split()
        
        for emoji in emojis:
            if emoji in emoji_map:
                digits += str(emoji_map[emoji])
        
        if digits:
            try:
                char_code = int(digits)
                decrypted_chars.append(chr(char_code))
            except (ValueError, OverflowError):
                pass
    
    return "".join(decrypted_chars)


def extract_and_decrypt(filepath):
    """
    Extract string emoji dari file dan decrypt
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Temukan posisi awal string emoji (setelah exec(""))
    start_pattern = 'exec(""'.replace('"', '"')
    start_pos = content.find(start_pattern)
    
    if start_pos == -1:
        raise ValueError("Tidak dapat menemukan pattern exec()")
    
    # Cari kutip pembuka string emoji
    quote_start = content.find('"', start_pos)
    if quote_start == -1:
        raise ValueError("Tidak dapat menemukan awal string emoji")
    quote_start += 1
    
    # Cari akhir string emoji (sebelum .split())
    split_pattern = '.split("'
    split_pos = content.find(split_pattern, quote_start)
    
    if split_pos == -1:
        raise ValueError("Tidak dapat menemukan akhir string emoji")
    
    # Ekstrak string emoji (hapus backslash continuation dan newline)
    emoji_string = content[quote_start:split_pos]
    emoji_string = emoji_string.replace('\\\n', ' ').replace('\\\r\n', ' ')
    
    print("=" * 80)
    print("DECRYPTED CODE dari DramoraFlutterPatch.py")
    print("=" * 80)
    print()
    
    decrypted_code = decrypt_emoji_string(emoji_string)
    
    return decrypted_code


if __name__ == "__main__":
    try:
        decrypted_code = extract_and_decrypt('/workspace/DramoraFlutterPatch.py')
        print(decrypted_code)
        print()
        print("=" * 80)
        print("Decryption berhasil!")
        print("=" * 80)
        
        # Simpan hasil decrypt ke file baru
        with open('/workspace/decrypted_code.txt', 'w', encoding='utf-8') as f:
            f.write(decrypted_code)
        print("\nHasil decrypt disimpan ke: /workspace/decrypted_code.txt")
        
        # Juga buat versi executable Python
        with open('/workspace/DramoraFlutterPatch_decrypted.py', 'w', encoding='utf-8') as f:
            f.write("# Decrypted version of DramoraFlutterPatch.py\n")
            f.write("# Original file was obfuscated with emoji encoding\n\n")
            f.write(decrypted_code)
        print("Versi executable disimpan ke: /workspace/DramoraFlutterPatch_decrypted.py")
        
    except Exception as e:
        print(f"Error saat decrypt: {e}")
        import traceback
        traceback.print_exc()
