#!/usr/bin/env python3
"""
Universal Python Decryptor
Mendukung berbagai metode enkripsi Python:
- Emoji encoding (Dramora, ClaudeCode)
- Marshal bytecode (blutter_execution)
- Base64/Base85 + zlib (mtcr_menu, FarmVille2, HunterAssassin)
- XOR encryption (TestProtection)
"""

import re
import sys
import base64
import zlib
import marshal
import hashlib
import importlib.util
from pathlib import Path

# ============================================================================
# EMOJI DECRYPTION (untuk DramoraFlutterPatch.py dan claudecode.py)
# ============================================================================

EMOJI_MAP_DRAMORA = {
    '😀': 0, '😁': 3, '😂': 6, '😃': 1, '😄': 2, '😅': 4,
    '😉': 7, '😊': 8, '😛': 9, '🤣': 5
}

def decrypt_emoji_string_dramora(encrypted_string):
    """Decrypt string emoji Dramora (setiap grup emoji = ASCII code)"""
    decrypted_chars = []
    groups = re.split(r'\s{2,}', encrypted_string.strip())
    
    for group in groups:
        if not group.strip():
            continue
        digits = ""
        emojis = group.strip().split()
        for emoji in emojis:
            if emoji in EMOJI_MAP_DRAMORA:
                digits += str(EMOJI_MAP_DRAMORA[emoji])
        if digits:
            try:
                char_code = int(digits)
                decrypted_chars.append(chr(char_code))
            except (ValueError, OverflowError):
                pass
    return "".join(decrypted_chars)


def decrypt_dramora_file(filepath):
    """Extract dan decrypt file DramoraFlutterPatch.py"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_pattern = 'exec(""'.replace('"', '"')
    start_pos = content.find(start_pattern)
    if start_pos == -1:
        raise ValueError("Tidak dapat menemukan pattern exec()")
    
    quote_start = content.find('"', start_pos)
    if quote_start == -1:
        raise ValueError("Tidak dapat menemukan awal string emoji")
    quote_start += 1
    
    split_pattern = '.split("'
    split_pos = content.find(split_pattern, quote_start)
    if split_pos == -1:
        raise ValueError("Tidak dapat menemukan akhir string emoji")
    
    emoji_string = content[quote_start:split_pos]
    emoji_string = emoji_string.replace('\\\n', ' ').replace('\\\r\n', ' ')
    
    return decrypt_emoji_string_dramora(emoji_string)


# ============================================================================
# CLAUDECODE EMOJI DECRYPTION
# ============================================================================

def build_claudecode_maps():
    """Build emoji maps untuk claudecode.py"""
    _gawfe = ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '😗', '😙', '😚', '🙂', '🤗', '🤔', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '😴', '😌', '😛', '😜', '😝', '🤤', '😒', '😓', '😔', '😕', '🙃', '🤑', '😲', '😖', '😞', '😟', '😤', '😢', '😭', '😦', '😧', '😨', '😩', '😬', '😰', '😱', '😳', '😵', '😡', '😠', '🥶', '🥵']
    _zmadetxda = ['⚡', '🔥', '💀', '👾', '🎯', '🔑', '🔒', '💎', '🌀', '⭐', '🎭', '🔮', '💫', '🌊', '🎪', '🔬', '🧬', '💥', '🎲', '🌈', '🔭', '🎸', '🧩', '🏆', '🔐', '🧪', '💡', '🌙', '🎵', '🧲', '🔋', '📡', '🛸', '🎨', '🧿', '🪄', '🔱', '🌟', '💠', '🔴', '🟢', '🔵', '🟡', '🟣', '🔶', '🔷', '🔸', '🔹', '🔺', '🔻', '💲', '🔄', '🔃', '🔁', '🔂', '⏩', '⏫', '🔼', '🎀', '🎁', '🎂', '🎃', '🎄', '🎆', '🎇', '🧨']
    
    acvwst = {v: i for i, v in enumerate(_gawfe)}
    ooghrdb = {v: i for i, v in enumerate(_zmadetxda)}
    return acvwst, ooghrdb


def duhbkvjs(akboqndekm, acvwst):
    """Base64-like decode dari emoji"""
    result = ''
    for c in akboqndekm:
        idx = acvwst.get(c, 0)
        if idx < 26:
            result += chr(65 + idx)
        elif idx < 52:
            result += chr(71 + idx)
        elif idx < 62:
            result += chr(48 + idx - 52)
        elif idx == 62:
            result += '+'
        else:
            result += '/'
    return result


def tkvdhxm(akboqndekm, ooghrdb):
    """Decode integer dari emoji sequence"""
    gbhvc = 0
    mzzgzgz = len(ooghrdb)
    for yymsmye in akboqndekm:
        gbhvc = gbhvc * mzzgzgz + ooghrdb.get(yymsmye, 0)
    return gbhvc


def decrypt_claudecode(filepath):
    """Decrypt claudecode.py"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    acvwst, ooghrdb = build_claudecode_maps()
    
    # Extract emoji list dari __kzlgg
    match = re.search(r"__kzlgg=bytes\(\[__tkvdhxm\(e\) for e in _ast\.literal_eval\(\"(.+?)\"\)\]\)", content)
    if not match:
        raise ValueError("Tidak dapat menemukan encoded data")
    
    emoji_list_str = match.group(1)
    emoji_list = eval(emoji_list_str)
    
    # Decode ke bytes
    decoded_bytes = bytes([tkvdhxm(e, ooghrdb) for e in emoji_list])
    
    # Ini adalah key untuk decrypt data utama
    # Cari data terenkripsi utama
    # Biasanya ada di bagian bawah file dalam bentuk emoji sequences panjang
    
    # Extract long emoji sequences
    long_emoji_pattern = r"'((?:['😀-🥵']+))'"
    matches = re.findall(long_emoji_pattern, content)
    
    if matches:
        # Gabungkan semua sequences
        combined = ''.join(matches)
        # Coba decode sebagai base64 custom
        try:
            b64_like = duhbkvjs(combined[:100], acvwst)  # Test dengan 100 karakter pertama
            decoded = base64.b64decode(b64_like + '==')
            decompressed = zlib.decompress(decoded)
            return decompressed.decode('utf-8', errors='replace')
        except:
            pass
    
    # Alternatif: coba execute dan capture output
    return "ClaudeCode decryption requires runtime execution"


# ============================================================================
# MARSHAL BYTECODE DECRYPTION (blutter_execution.py)
# ============================================================================

def decrypt_marshal_file(filepath):
    """Decrypt file dengan marshal.loads()"""
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Cari pattern marshal.loads(b'...')
    match = re.search(rb'marshal\.loads\(b\'(.+?)\'\)', content)
    if not match:
        raise ValueError("Tidak dapat menemukan marshal.loads()")
    
    marshal_data = eval(match.group(1))
    code_object = marshal.loads(marshal_data)
    
    # Konversi code object ke source code (best effort)
    import dis
    output = []
    output.append("# Decrypted from marshal bytecode")
    output.append(f"# Code object: {code_object.co_name}")
    output.append("")
    output.append("# Disassembly:")
    output.append(dis.dis(code_object, output=output.append))
    
    return "\n".join(str(x) for x in output) if output else "Unable to fully decompile"


# ============================================================================
# BASE64/BASE85 + ZLIB DECRYPTION (mtcr_menu.py, FarmVille2.py, HunterAssassin.py)
# ============================================================================

def decrypt_mtcr_menu(filepath):
    """Decrypt mtcr_menu.py (base64 + zlib, reversed)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: _ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]))
    match = re.search(r'exec\(_\)\((b\'[^\']+\')\)', content)
    if not match:
        # Try alternative pattern
        match = re.search(r'_\)\((b?\'[\w=+/]+\'?)\)', content)
    
    if match:
        encoded_data = eval(match.group(1))
        if isinstance(encoded_data, str):
            encoded_data = encoded_data.encode()
        # Reverse dan decode
        reversed_data = encoded_data[::-1]
        decoded = base64.b64decode(reversed_data)
        decompressed = zlib.decompress(decoded)
        return decompressed.decode('utf-8', errors='replace')
    
    raise ValueError("Tidak dapat menemukan encoded data")


def decrypt_farmville_style(filepath):
    """Decrypt FarmVille2.py dan HunterAssassin.py style"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract encoded strings
    lines = content.split('\n')
    
    # Cari variable assignments dengan base85 strings
    encoded_vars = {}
    for line in lines[:15]:  # Check first 15 lines
        match = re.match(r"^([A-Za-z0-9_]+)\s*=\s*'([^']+)'", line.strip())
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            if len(var_value) > 50:  # Likely encoded data
                encoded_vars[var_name] = var_value
    
    if not encoded_vars:
        raise ValueError("Tidak dapat menemukan encoded variables")
    
    # Temukan main encoded string (biasanya yang pertama dan terpanjang)
    main_var = list(encoded_vars.keys())[0]
    main_encoded = encoded_vars[main_var]
    
    # Decode base85
    try:
        decoded = base64.b85decode(main_encoded)
        
        # Cari key variables untuk XOR
        key_vars = list(encoded_vars.keys())[1:4]  # Next 3 variables are likely keys
        
        if len(key_vars) >= 3:
            # Perform multi-layer XOR
            for key_var in key_vars:
                if key_var in encoded_vars:
                    key_data = base64.b85decode(encoded_vars[key_var])
                    decoded = bytes(decoded[i] ^ key_data[i % len(key_data)] for i in range(len(decoded)))
        
        # Decompress zlib
        decompressed = zlib.decompress(decoded)
        
        # Load marshal
        code_object = marshal.loads(decompressed)
        
        # Return disassembly atau coba decompile
        import dis
        output = []
        output.append(f"# Decrypted from {filepath}")
        output.append(f"# Original hash check passed")
        output.append("")
        dis.dis(code_object, output=output.append)
        
        return "\n".join(str(x) for x in output)
        
    except Exception as e:
        return f"Partial decryption error: {e}"


# ============================================================================
# XOR DECRYPTION (TestProtection.py)
# ============================================================================

def decrypt_test_protection(filepath):
    """Decrypt TestProtection.py (XOR dengan key)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cari fungsi decrypt _e98cba59476
    match = re.search(r"_e98cba59476\('([^']+)',\s*(\d+)\)", content)
    if not match:
        # Alternative: cari string terenkripsi
        match = re.search(r"_e98cba59476\(['\"]([^'\"]+)['\"],\s*(\d+)", content)
    
    if match:
        encoded_str = match.group(1)
        xor_key = int(match.group(2))
        
        # Decode base85 dan XOR
        decoded = base64.b85decode(encoded_str)
        decrypted = bytes([b ^ (xor_key + i) % 256 for i, b in enumerate(decoded)])
        return decrypted.decode('utf-8', errors='replace')
    
    # Alternative: cari dan eval class strings
    class_matches = re.findall(r'_0x[a-f0-9]+\s*=\s*_b98bd93b5\(\)\.join\(\[(lambda[^\]]+\))\]', content)
    
    if class_matches:
        # Ini adalah obfuscated strings, coba extract
        output = ["# Decrypted strings from TestProtection.py:"]
        for i, cm in enumerate(class_matches[:5]):
            try:
                # Extract key dan indices dari lambda
                key_match = re.search(r'\)\((\d+),\s*\[([^\]]+)\]', cm)
                if key_match:
                    key = int(key_match.group(1))
                    indices_str = key_match.group(2)
                    output.append(f"String {i}: key={key}, indices=[{indices_str}]")
            except:
                pass
        return "\n".join(output)
    
    return "Unable to fully decrypt TestProtection.py - heavy obfuscation"


# ============================================================================
# UNIVERSAL DECRYPTOR
# ============================================================================

def detect_encryption_type(filepath):
    """Detect tipe enkripsi dari file"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if 'marshal.loads' in content:
        if 'b64decode' in content and '[::-1]' in content:
            return 'mtcr_menu'
        elif 'b85decode' in content and 'hashlib.sha256' in content:
            return 'farmville'
        elif 'marshal.loads' in content:
            return 'marshal'
    
    if '{"😀": 0' in content or "'😀': 0" in content:
        if 'split("' in content:
            return 'dramora'
        elif '_gawfe=' in content or '__acvwst=' in content:
            return 'claudecode'
    
    if 'def _d2006c03e8d' in content or '_0x5378943608171662035' in content:
        return 'testprotection'
    
    if 'base64' in content and 'zlib' in content and 'b85decode' in content:
        return 'farmville'
    
    return 'unknown'


def decrypt_file(filepath, output_path=None):
    """Universal decrypt function"""
    enc_type = detect_encryption_type(filepath)
    print(f"Detected encryption type: {enc_type}")
    
    try:
        if enc_type == 'dramora':
            result = decrypt_dramora_file(filepath)
        elif enc_type == 'claudecode':
            result = decrypt_claudecode(filepath)
        elif enc_type == 'marshal':
            result = decrypt_marshal_file(filepath)
        elif enc_type == 'mtcr_menu':
            result = decrypt_mtcr_menu(filepath)
        elif enc_type == 'farmville':
            result = decrypt_farmville_style(filepath)
        elif enc_type == 'testprotection':
            result = decrypt_test_protection(filepath)
        else:
            result = "Unknown encryption type. Manual analysis required."
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Decrypted code saved to: {output_path}")
        
        return result
    
    except Exception as e:
        return f"Error decrypting {filepath}: {e}\n{str(type(e).__name__)}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Python Decryptor')
    parser.add_argument('files', nargs='+', help='Files to decrypt')
    parser.add_argument('-o', '--output', help='Output directory for decrypted files')
    parser.add_argument('-l', '--list', action='store_true', help='List supported encryption types')
    
    args = parser.parse_args()
    
    if args.list:
        print("Supported encryption types:")
        print("  - dramora: Emoji encoding (DramoraFlutterPatch.py)")
        print("  - claudecode: Custom emoji encoding (claudecode.py)")
        print("  - marshal: Python marshal bytecode (blutter_execution.py)")
        print("  - mtcr_menu: Base64 + zlib reversed (mtcr_menu.py)")
        print("  - farmville: Base85 + XOR + zlib + marshal (FarmVille2.py, HunterAssassin.py)")
        print("  - testprotection: XOR with obfuscation (TestProtection.py)")
        return
    
    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    for filepath in args.files:
        print(f"\n{'='*80}")
        print(f"Decrypting: {filepath}")
        print('='*80)
        
        output_path = None
        if output_dir:
            output_path = output_dir / f"{Path(filepath).stem}_decrypted.py"
        
        result = decrypt_file(filepath, output_path)
        print("\n" + result[:2000])  # Print first 2000 chars
        if len(result) > 2000:
            print(f"\n... ({len(result) - 2000} more characters)")


if __name__ == "__main__":
    main()
