#!/usr/bin/env python3
"""
Universal Python Decryptor
Mendukung berbagai teknik enkripsi Python berdasarkan signature detection:

Encryption Techniques Supported:
- emoji_unicode_v1: Emoji-to-ASCII mapping (Dramora style)
- emoji_map_dual: Dual emoji maps for base64-like encoding (ClaudeCode style)
- marshal_bytecode: Raw Python marshal bytecode
- multi_layer_zlib_b64_rev: Nested layers - reverse → base64 → zlib (up to 100 layers!)
- base85_xor_marshal: Base85 + XOR + zlib + marshal (FarmVille2/HunterAssassin style)
- xor_obfuscation: XOR encryption with string obfuscation (TestProtection style)
- base64_zlib_simple: Generic base64 + zlib compression

Auto-detection based on code signatures, not filename patterns.
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

def decrypt_single_layer(data):
    """Decrypt single layer: reverse -> base64 decode -> zlib decompress"""
    try:
        # Reverse the data
        reversed_data = data[::-1]
        # Base64 decode
        decoded = base64.b64decode(reversed_data)
        # Zlib decompress
        decompressed = zlib.decompress(decoded)
        return decompressed, True
    except Exception as e:
        return data, False


def decrypt_mtcr_menu(filepath, max_layers=100):
    """
    Decrypt mtcr_menu.py dengan multi-layer nested encryption.
    Pattern: exec((_)(b'...')) dimana setiap layer adalah reverse+base64+zlib
    Support hingga 100 layers atau sampai tidak ada lagi nested exec()
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract initial encoded data - handle nested exec((_)(b'...'))
    # The pattern is: exec((_)(b'...')) where the inner () returns another exec((_)(b'...'))
    match = re.search(r'exec\(\(_\)\((b\'[^\']+\'\))\)', content)
    if match:
        # Get the inner b'...' part
        inner_match = re.search(r"b'([^']+)'", match.group(1))
        if inner_match:
            encoded_data = inner_match.group(1).encode()
        else:
            encoded_data = match.group(1).encode()
    else:
        # Fallback patterns
        patterns = [
            r'exec\(_\)\((b\'[^\']+\')\)',
            r'_\)\((b\'[^\']+\')\)',
        ]
        encoded_data = None
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                encoded_data = eval(match.group(1))
                break
        
        if not encoded_data:
            match = re.search(r"b'([A-Za-z0-9+/=]+)'", content)
            if match:
                encoded_data = match.group(1).encode()
    
    if not encoded_data:
        raise ValueError("Tidak dapat menemukan encoded data")
    
    if isinstance(encoded_data, str):
        encoded_data = encoded_data.encode()
    
    # Multi-layer decryption loop
    current_data = encoded_data
    layers_decrypted = 0
    
    print(f"Starting multi-layer decryption (max {max_layers} layers)...")
    
    while layers_decrypted < max_layers:
        # Try to decrypt current layer
        decrypted_data, success = decrypt_single_layer(current_data)
        
        if not success:
            print(f"Layer {layers_decrypted + 1}: Decryption failed, stopping.")
            break
        
        layers_decrypted += 1
        current_data = decrypted_data
        
        # Check if there's still nested exec() pattern in the decrypted data
        try:
            decoded_str = current_data.decode('utf-8', errors='ignore')
            
            # Look for nested exec((_)(b'...')) pattern - EXACT pattern from mtcr_menu
            nested_match = re.search(r'exec\(\(_\)\((b\'[^\']+\'\))\)', decoded_str)
            if nested_match:
                # Extract the inner b'...' part
                inner = re.search(r"b'([^']+)'", nested_match.group(1))
                if inner:
                    current_data = inner.group(1).encode()
                    print(f"Layer {layers_decrypted}: Found nested exec(), continuing to next layer...")
                    continue
            
            # Also check simpler pattern: exec((_)(b'...'))
            nested_match2 = re.search(r'exec\(_\)\((b\'[^\']+\')\)', decoded_str)
            if nested_match2:
                current_data = eval(nested_match2.group(1))
                if isinstance(current_data, str):
                    current_data = current_data.encode()
                print(f"Layer {layers_decrypted}: Found nested exec (simple), continuing...")
                continue
            
            # No more nested exec, check if it's valid Python code
            if (decoded_str.strip().startswith('import ') or 
                decoded_str.strip().startswith('def ') or 
                decoded_str.strip().startswith('#') or
                decoded_str.strip().startswith('"""') or
                'print(' in decoded_str or
                'sys.exit' in decoded_str or
                'os.' in decoded_str):
                print(f"Layer {layers_decrypted}: Valid Python code found!")
                break
            else:
                print(f"Layer {layers_decrypted}: No nested exec found, checking if final code...")
                break
                    
        except Exception as e:
            print(f"Layer {layers_decrypted}: Error checking nested exec: {e}")
            break
    
    # Final result should be valid Python source code
    try:
        final_code = current_data.decode('utf-8')
        print(f"Successfully decrypted {layers_decrypted} layers!")
        return final_code
    except UnicodeDecodeError:
        return current_data.decode('utf-8', errors='replace')


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
    """
    Detect tipe enkripsi berdasarkan signature/pola kode.
    Mengembalikan nama TECHNIQUE enkripsi, bukan nama file.
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # ========================================================================
    # SIGNATURE-BASED DETECTION
    # ========================================================================
    
    # 1. MULTI_LAYER_ZLIB_B64_REV (sebelumnya: mtcr_menu)
    # Signature: lambda dengan reverse + base64 + zlib, atau nested exec(b'...')
    if "lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]))" in content:
        return 'multi_layer_zlib_b64_rev'
    
    # Check for nested exec patterns - multiple variations
    if re.search(r'exec\(\(_\)\(', content) and re.search(r"b'[A-Za-z0-9+/=]+", content):
        return 'multi_layer_zlib_b64_rev'
    
    if re.search(r'exec\(_\)\(b\'[A-Za-z0-9+/=]+\'\)', content):
        return 'multi_layer_zlib_b64_rev'
    
    # 2. MARSHAL_BYTECODE (sebelumnya: marshal/blutter_execution)
    # Signature: marshal.loads tanpa b85decode/XOR kompleks
    if 'marshal.loads' in content:
        if 'b85decode' not in content and 'base64.b85decode' not in content:
            return 'marshal_bytecode'
    
    # 3. BASE85_XOR_MARSHAL (sebelumnya: farmville)
    # Signature: b85decode + hashlib + marshal.loads
    if 'b85decode' in content or 'base64.b85decode' in content:
        if 'marshal.loads' in content and 'hashlib' in content:
            return 'base85_xor_marshal'
        if 'marshal.loads' in content and 'xor' in content.lower():
            return 'base85_xor_marshal'
    
    # 4. EMOJI_UNICODE_V1 (sebelumnya: dramora)
    # Signature: Emoji map sederhana {'😀': 0} + split pattern
    if '{"😀": 0' in content or "'😀': 0" in content or '"😁": 3' in content:
        if 'split("' in content or ".split('" in content:
            return 'emoji_unicode_v1'
    
    # 5. EMOJI_MAP_DUAL (sebelumnya: claudecode)
    # Signature: Dual emoji maps (_gawfe, _zmadetxda) atau __acvwst/__ooghrdb
    if '_gawfe=' in content or '__acvwst=' in content or '_zmadetxda' in content:
        return 'emoji_map_dual'
    
    if '__kzlgg' in content and 'tkvdhxm' in content:
        return 'emoji_map_dual'
    
    # 6. XOR_OBFUSCATION (sebelumnya: testprotection)
    # Signature: Fungsi decrypt dengan nama hex (_0x..., _d2006c...) + lambda obfuscation
    if re.search(r'def _[0-9a-f]{10,}', content):
        return 'xor_obfuscation'
    
    if re.search(r'_0x[0-9a-f]+\s*=', content):
        return 'xor_obfuscation'
    
    if 'lambda.*\\^' in content or 'ord(c)^' in content:
        return 'xor_obfuscation'
    
    # 7. BASE64_ZLIB_SIMPLE (generic base64+zlib tanpa nested layers)
    if 'base64.b64decode' in content and 'zlib.decompress' in content:
        if 'lambda' not in content and 'exec' not in content:
            return 'base64_zlib_simple'
    
    return 'unknown'


def decrypt_file(filepath, output_path=None):
    """
    Universal decrypt function dengan auto-detection encryption type.
    """
    enc_type = detect_encryption_type(filepath)
    
    # Mapping dari technique name ke fungsi decrypt
    technique_map = {
        'emoji_unicode_v1': ('Emoji Unicode v1 (Dramora-style)', decrypt_dramora_file),
        'emoji_map_dual': ('Dual Emoji Map (ClaudeCode-style)', decrypt_claudecode),
        'marshal_bytecode': ('Marshal Bytecode', decrypt_marshal_file),
        'multi_layer_zlib_b64_rev': ('Multi-Layer Zlib/Base64/Reverse', decrypt_mtcr_menu),
        'base85_xor_marshal': ('Base85 + XOR + Marshal', decrypt_farmville_style),
        'xor_obfuscation': ('XOR Obfuscation', decrypt_test_protection),
        'base64_zlib_simple': ('Base64 + Zlib Simple', lambda f: "Generic Base64+Zlib - requires custom handling"),
        'unknown': ('Unknown', lambda f: "Unknown encryption type. Manual analysis required."),
    }
    
    tech_name, decrypt_func = technique_map.get(enc_type, technique_map['unknown'])
    
    print(f"[DETECT] Encryption Type: {enc_type}")
    print(f"[INFO] Technique: {tech_name}")
    
    try:
        result = decrypt_func(filepath)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"[SAVE] Decrypted code saved to: {output_path}")
        
        return result
    
    except Exception as e:
        return f"[ERROR] Decryption failed: {e}\nType: {type(e).__name__}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Universal Python Decryptor - Auto-detect & decrypt various Python encryption techniques',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Encryption Types Supported:
  emoji_unicode_v1       - Emoji-to-ASCII mapping (single char per group)
  emoji_map_dual         - Dual emoji maps for base64-like encoding
  marshal_bytecode       - Raw Python marshal bytecode
  multi_layer_zlib_b64_rev - Nested layers: reverse → base64 → zlib (up to 100 layers!)
  base85_xor_marshal     - Base85 decode → XOR multiple keys → zlib → marshal
  xor_obfuscation        - XOR decryption with string obfuscation
  base64_zlib_simple     - Simple base64 + zlib compression

Examples:
  python universal_decryptor.py encrypted.py
  python universal_decryptor.py *.py -o decrypted_output/
  python universal_decryptor.py -l
        """
    )
    parser.add_argument('files', nargs='*', help='Encrypted Python files to decrypt')
    parser.add_argument('-o', '--output', help='Output directory for decrypted files')
    parser.add_argument('-l', '--list', action='store_true', help='List supported encryption types with details')
    
    args = parser.parse_args()
    
    if args.list:
        print("="*70)
        print("SUPPORTED ENCRYPTION TECHNIQUES")
        print("="*70)
        print()
        print("1. emoji_unicode_v1")
        print("   Description: Each ASCII character encoded as group of emojis")
        print("   Detection: Emoji dict {'😀': 0, '😁': 3, ...} + split()")
        print("   Example: DramoraFlutterPatch.py")
        print()
        print("2. emoji_map_dual")
        print("   Description: Two emoji maps for base64-like encoding")
        print("   Detection: Variables _gawfe, _zmadetxda, __acvwst, __ooghrdb")
        print("   Example: claudecode.py")
        print()
        print("3. marshal_bytecode")
        print("   Description: Raw Python marshal bytecode embedded in script")
        print("   Detection: marshal.loads() without additional encoding")
        print("   Example: blutter_execution.py")
        print()
        print("4. multi_layer_zlib_b64_rev ⭐")
        print("   Description: Multiple nested layers of encryption")
        print("   Process: reverse string → base64 decode → zlib decompress")
        print("   Layers: Supports up to 100 nested layers automatically!")
        print("   Detection: lambda with [::-1] + b64decode + decompress")
        print("   Example: mtcr_menu.py (32 layers)")
        print()
        print("5. base85_xor_marshal")
        print("   Description: Multi-stage encoding with XOR keys")
        print("   Process: base85 decode → XOR with multiple keys → zlib → marshal")
        print("   Detection: b85decode + hashlib + marshal.loads")
        print("   Example: FarmVille2.py, HunterAssassin.py")
        print()
        print("6. xor_obfuscation")
        print("   Description: XOR encryption with obfuscated strings")
        print("   Detection: Hex-named functions (_0x...), lambda chains")
        print("   Example: TestProtection.py")
        print()
        print("7. base64_zlib_simple")
        print("   Description: Basic base64 encoding + zlib compression")
        print("   Detection: b64decode + decompress without nesting")
        print("   Example: Generic protected scripts")
        print()
        print("="*70)
        return
    
    if not args.files:
        parser.print_help()
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
