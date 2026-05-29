#!/usr/bin/env python3
"""
Universal Emoji Decryptor
Mendeteksi dan mendecrypt file yang di-encrypt dengan emoji encoding
"""

import re
import sys
import marshal
from types import CodeType

# Mapping emoji ke angka (standard mapping yang umum digunakan)
EMOJI_MAP = {
    '😀': 0, '😁': 3, '😂': 6, '😃': 1, '😄': 2, 
    '😅': 4, '😉': 7, '😊': 8, '😛': 9, '🤣': 5
}

def extract_emoji_data(content):
    """Extract emoji-encoded string dari file Python"""
    # Cari pola exec("".join(map(chr,[int("".join(str({...}[i]) for i in x.split())) for x in "..."))
    patterns = [
        r'for x in\s*"([^"]+)"',
        r'exec\([^)]*"([^"]+)"',
        r'"([😀😁😂😃😄😅😉😊😛🤣\s]+)"'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1) if len(match.groups()) > 0 else match.group(0)
    return None

def decode_emoji_to_bytes(emoji_string):
    """Decode emoji string ke bytes"""
    emoji_groups = emoji_string.split()
    decoded_bytes = bytearray()
    
    for group in emoji_groups:
        if group:
            num_str = ''.join(str(EMOJI_MAP[emoji]) for emoji in group if emoji in EMOJI_MAP)
            if num_str:
                decoded_bytes.append(int(num_str))
    
    return bytes(decoded_bytes)

def try_marshal_decode(data):
    """Coba decode sebagai marshal data"""
    results = []
    
    # Coba berbagai offset
    for offset in range(min(50, len(data))):
        try:
            obj = marshal.loads(data[offset:])
            results.append((offset, obj))
        except:
            pass
    
    return results

def decompile_code_object(code_obj):
    """Decompile code object ke source code"""
    try:
        import uncompyle6
        import io
        output = io.StringIO()
        uncompyle6.decompile(code_obj, output)
        return output.getvalue()
    except Exception as e:
        return f"Decompile error: {e}"

def analyze_byte_patterns(data):
    """Analyze pola byte untuk menentukan tipe encoding"""
    from collections import Counter
    
    byte_counts = Counter(data)
    unique_bytes = len(byte_counts)
    
    print(f"\n=== Byte Analysis ===")
    print(f"Total bytes: {len(data)}")
    print(f"Unique byte values: {unique_bytes}")
    print(f"Byte range: {min(data)} - {max(data)}")
    
    # Cek distribusi
    print("\nTop 10 byte values:")
    for byte_val, count in byte_counts.most_common(10):
        pct = count / len(data) * 100
        print(f"  {byte_val:3d} (0x{byte_val:02x}): {count:6d} ({pct:.1f}%)")
    
    return byte_counts

def try_ascii_mapping(data):
    """Coba berbagai ASCII mapping"""
    mappings = [
        ("+32 offset", lambda b: chr(b + 32) if b + 32 < 128 else None),
        ("+65 offset", lambda b: chr(b + 65) if b + 65 < 128 else None),
        ("+97 offset", lambda b: chr(b + 97) if b + 97 < 128 else None),
        ("x10+32", lambda b: chr(b * 10 + 32) if b * 10 + 32 < 128 else None),
    ]
    
    results = []
    for name, mapper in mappings:
        try:
            chars = [mapper(b) for b in data[:500]]
            chars = [c for c in chars if c is not None]
            text = ''.join(chars)
            
            # Cek apakah mengandung keyword Python
            score = sum(1 for kw in ['def ', 'import ', 'class ', 'return ', 'print', 'if ', 'for '] if kw in text)
            if score > 0:
                results.append((name, text[:300], score))
        except:
            pass
    
    return results

def decrypt_file(input_file, output_file=None):
    """Main decrypt function"""
    print(f"=== Emoji Decryptor ===")
    print(f"Input file: {input_file}")
    
    # Baca file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract emoji data
    emoji_data = extract_emoji_data(content)
    if not emoji_data:
        print("❌ Tidak menemukan emoji-encoded data!")
        return False
    
    print(f"✓ Found emoji data: {len(emoji_data)} characters")
    
    # Decode ke bytes
    decoded_bytes = decode_emoji_to_bytes(emoji_data)
    print(f"✓ Decoded to: {len(decoded_bytes)} bytes")
    
    # Analyze byte patterns
    byte_counts = analyze_byte_patterns(decoded_bytes)
    
    # Jika hanya byte 0-9, ini adalah custom encoding
    if max(decoded_bytes) <= 9:
        print("\n⚠ Data menggunakan custom encoding (hanya byte 0-9)")
        print("Mencoba berbagai interpretasi...")
        
        # Simpan raw decoded bytes
        raw_output = output_file or "decoded_raw.bin"
        with open(raw_output, 'wb') as f:
            f.write(decoded_bytes)
        print(f"✓ Raw bytes saved to: {raw_output}")
        
        # Coba ASCII mappings
        ascii_results = try_ascii_mapping(decoded_bytes)
        if ascii_results:
            print("\n=== ASCII Mapping Results ===")
            for name, text, score in sorted(ascii_results, key=lambda x: -x[2]):
                print(f"\n{name} (score: {score}):")
                print(text[:200])
        
        # Coba marshal dengan berbagai prefix
        print("\n=== Trying Marshal Decode ===")
        marshal_results = try_marshal_decode(decoded_bytes)
        if marshal_results:
            for offset, obj in marshal_results[:3]:
                print(f"\nOffset {offset}: {type(obj)}")
                if isinstance(obj, CodeType):
                    print("  ✓ Code object found!")
                    decompiled = decompile_code_object(obj)
                    
                    py_output = output_file.replace('.bin', '.py') if output_file else "decompiled.py"
                    with open(py_output, 'w') as f:
                        f.write("# Decompiled code\n\n")
                        f.write(decompiled)
                    print(f"  ✓ Saved to: {py_output}")
                    return True
        else:
            print("  ❌ Marshal decode failed")
        
        return True
    
    # Data dengan byte range normal - coba langsung sebagai marshal/bytecode
    print("\n=== Standard Byte Range ===")
    
    # Coba marshal
    marshal_results = try_marshal_decode(decoded_bytes)
    if marshal_results:
        print("✓ Marshal decode successful!")
        for offset, obj in marshal_results[:3]:
            print(f"  Offset {offset}: {type(obj)}")
            if isinstance(obj, CodeType):
                decompiled = decompile_code_object(obj)
                py_output = output_file or "decompiled.py"
                with open(py_output, 'w') as f:
                    f.write(decompiled)
                print(f"  ✓ Saved to: {py_output}")
                return True
    
    # Simpan sebagai binary
    bin_output = output_file or "decoded.bin"
    with open(bin_output, 'wb') as f:
        f.write(decoded_bytes)
    print(f"✓ Saved raw bytes to: {bin_output}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python emoji_decryptor.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = decrypt_file(input_file, output_file)
    sys.exit(0 if success else 1)
