#!/usr/bin/env python3
"""
DramoraFlutterPatch.py Decryptor
Khusus untuk mendecrypt file yang diobfuscate dengan emoji encoding
"""

import re


def decrypt_emoji_encoded(content):
    """
    Decrypt emoji-encoded content
    Format: exec("".join(map(chr,[int("".join(str(emoji_map[i]) for i in x.split())) for x in "emoji_string"])))
    """
    
    # Ekstrak emoji mapping dari baris 4
    map_pattern = r"\{([^}]*(?:😀|😁|😂|😃|😄|😅|😉|😊|😛|🤣)[^}]*)\}"
    map_match = re.search(map_pattern, content)
    
    if not map_match:
        print("❌ Tidak dapat menemukan emoji mapping")
        return None
    
    map_content = map_match.group(1)
    emoji_map = {}
    
    # Parse mapping: 'emoji': number
    emoji_pattern = r"'([😀-🙏]+)':\s*(\d+)"
    for match in re.finditer(emoji_pattern, map_content):
        emoji = match.group(1)
        number = int(match.group(2))
        emoji_map[emoji] = number
    
    # Tambahkan emoji yang mungkin missing (seperti 😄 yang tidak ada di mapping eksplisit)
    # Dari kode asli: {'😀': 0, '😁': 3, '😂': 6, '😃': 1, '😄': 2, '😅': 4, '😉': 7, '😊': 8, '😛': 9, '🤣': 5}
    # Mapping lengkap dari file original
    full_emoji_map = {
        '😀': 0,
        '😃': 1,
        '😄': 2,
        '😁': 3,
        '😅': 4,
        '🤣': 5,
        '😂': 6,
        '😉': 7,
        '😊': 8,
        '😛': 9,
    }
    
    # Override dengan yang ditemukan di file
    emoji_map.update(full_emoji_map)
    
    print(f"✓ Emoji mapping ditemukan: {len(emoji_map)} emojis")
    print(f"  Mapping: {emoji_map}")
    
    # Cari string emoji besar setelah "for x in"
    # Pattern: for x in "..." dimana ... adalah emoji string
    pattern = r'for\s+x\s+in\s*["\']([\s😀-🙏\\]+)["\']'
    match = re.search(pattern, content)
    
    if not match:
        print("❌ Tidak dapat menemukan encoded string dengan pattern utama")
        # Coba alternatif: cari semua emoji di line 5 dan seterusnya
        lines = content.split('\n')
        emoji_lines = []
        for i, line in enumerate(lines):
            if i >= 4 and i <= 300:  # Baris 5-301
                # Extract emoji dari line
                emoji_only = ''.join(c for c in line if ord(c) >= 0x1F600 or c in ' \\')
                if emoji_only.strip():
                    emoji_lines.append(emoji_only.strip())
        
        full_encoded = ' '.join(emoji_lines)
        print(f"✓ Menggunakan alternatif: {len(full_encoded)} chars dari {len(emoji_lines)} lines")
    else:
        full_encoded = match.group(1)
        print(f"✓ Encoded string ditemukan: {len(full_encoded)} chars")
    
    # Decode
    decoded_chars = []
    emoji_groups = full_encoded.split()
    
    for group in emoji_groups:
        if not group.strip():
            continue
        
        digit_str = ""
        i = 0
        while i < len(group):
            found = False
            # Coba match dari emoji terpanjang
            for length in range(min(4, len(group) - i), 0, -1):
                emoji_candidate = group[i:i+length]
                if emoji_candidate in emoji_map:
                    digit_str += str(emoji_map[emoji_candidate])
                    i += length
                    found = True
                    break
            
            if not found:
                i += 1
        
        if digit_str:
            try:
                char_code = int(digit_str)
                # Terima semua karakter ASCII (0-127) untuk kode Python
                if 0 <= char_code <= 127:
                    decoded_chars.append(chr(char_code))
            except (ValueError, OverflowError):
                pass
    
    decoded = ''.join(decoded_chars)
    print(f"✓ Decoded {len(decoded_chars)} characters")
    
    return decoded


def main():
    input_file = "/workspace/DramoraFlutterPatch.py"
    output_file = "/workspace/DramoraFlutterPatch_decrypted.py"
    
    print("=" * 60)
    print("DramoraFlutterPatch.py Decryptor")
    print("=" * 60)
    
    # Baca file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ File {input_file} berhasil dibaca")
    except Exception as e:
        print(f"❌ Error membaca file: {e}")
        return
    
    # Decrypt
    decrypted = decrypt_emoji_encoded(content)
    
    if not decrypted:
        print("\n❌ Decryption gagal")
        return
    
    # Simpan hasil
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(decrypted)
        print(f"\n✓ File decrypted berhasil disimpan ke: {output_file}")
        
        # Tampilkan preview
        print("\n" + "=" * 60)
        print("Preview (500 karakter pertama):")
        print("=" * 60)
        print(decrypted[:500])
        
    except Exception as e:
        print(f"❌ Error menyimpan file: {e}")


if __name__ == "__main__":
    main()
