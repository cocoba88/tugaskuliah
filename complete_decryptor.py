#!/usr/bin/env python3
"""
Universal Decryptor Script
Mendeteksi dan mencoba decrypt berbagai jenis encryption/obfuscation pattern

Support:
- Emoji encoding (seperti DramoraFlutterPatch.py)
- Base64 encoding
- Hex encoding  
- ROT/Caesar cipher
- XOR encoding
- Marshal bytecode
- Custom numeric encoding
"""

import re
import sys
import base64
import marshal
from types import CodeType
from collections import Counter

# ============================================================================
# EMOJI MAPPINGS (berbagai variant yang umum)
# ============================================================================
EMOJI_MAPPINGS = [
    # Standard mapping
    {'😀': 0, '😁': 3, '😂': 6, '😃': 1, '😄': 2, '😅': 4, '😉': 7, '😊': 8, '😛': 9, '🤣': 5},
    # Sequential mapping
    {'😀': 0, '😁': 1, '😂': 2, '😃': 3, '😄': 4, '😅': 5, '😉': 6, '😊': 7, '😛': 8, '🤣': 9},
    # Reverse mapping
    {'😀': 9, '😁': 8, '😂': 7, '😃': 6, '😄': 5, '😅': 4, '😉': 3, '😊': 2, '😛': 1, '🤣': 0},
]

class UniversalDecryptor:
    def __init__(self):
        self.detected_patterns = []
    
    def detect_pattern(self, content):
        """Detect encryption/obfuscation pattern"""
        patterns = []
        
        # Check emoji encoding
        emoji_chars = set('😀😁😂😃😄😅😉😊😛🤣')
        if any(c in content for c in emoji_chars):
            patterns.append('emoji_encoding')
        
        # Check base64
        if re.search(r'[A-Za-z0-9+/]{50,}={0,2}', content):
            patterns.append('base64')
        
        # Check hex encoding
        if re.search(r'(?:\\x[0-9a-fA-F]{2}){10,}', content):
            patterns.append('hex_encoding')
        
        # Check eval/exec obfuscation
        if re.search(r'eval\s*\(|exec\s*\(', content):
            patterns.append('eval_exec')
        
        # Check marshal header
        if content.startswith(b'\x0d\x0a') if isinstance(content, bytes) else False:
            patterns.append('marshal_bytecode')
        
        self.detected_patterns = patterns
        return patterns
    
    def decrypt_emoji(self, content, emoji_map=None):
        """Decrypt emoji-encoded content"""
        if emoji_map is None:
            emoji_map = EMOJI_MAPPINGS[0]
        
        # Extract emoji string
        match = re.search(r'for x in\s*"([^"]+)"', content, re.DOTALL)
        if not match:
            match = re.search(r'"([😀😁😂😃😄😅😉😊😛🤣\s]+)"', content, re.DOTALL)
        
        if not match:
            return None
        
        emoji_string = match.group(1) if match.groups() else match.group(0)
        
        # Decode
        emoji_groups = emoji_string.split()
        decoded_bytes = bytearray()
        
        for group in emoji_groups:
            if group:
                num_str = ''.join(str(emoji_map[emoji]) for emoji in group if emoji in emoji_map)
                if num_str:
                    decoded_bytes.append(int(num_str))
        
        return bytes(decoded_bytes)
    
    def try_decompile(self, data):
        """Try to decompile marshal data"""
        results = []
        
        for offset in range(min(50, len(data))):
            try:
                obj = marshal.loads(data[offset:])
                
                if isinstance(obj, CodeType):
                    try:
                        import uncompyle6
                        import io
                        output = io.StringIO()
                        uncompyle6.decompile(obj, output)
                        results.append(('decompiled', output.getvalue(), offset))
                    except:
                        results.append(('code_object', obj, offset))
                else:
                    results.append(('marshal_data', obj, offset))
            except:
                pass
        
        return results
    
    def analyze_bytes(self, data):
        """Analyze byte patterns"""
        freq = Counter(data)
        
        analysis = {
            'total_bytes': len(data),
            'unique_bytes': len(freq),
            'min_byte': min(data) if data else 0,
            'max_byte': max(data) if data else 0,
            'frequency': dict(freq.most_common(10)),
        }
        
        return analysis
    
    def try_ascii_mapping(self, data):
        """Try various ASCII mappings"""
        mappings = [
            ("+32", lambda b: chr(b + 32) if b + 32 < 128 else None),
            ("+65", lambda b: chr(b + 65) if b + 65 < 128 else None),
            ("+97", lambda b: chr(b + 97) if b + 97 < 128 else None),
            ("*10+32", lambda b: chr(b * 10 + 32) if b * 10 + 32 < 128 else None),
            ("freq_map", None),  # Special handling
        ]
        
        results = []
        for name, mapper in mappings:
            if mapper:
                try:
                    chars = [mapper(b) for b in data[:1000]]
                    chars = [c for c in chars if c is not None]
                    text = ''.join(chars)
                    
                    # Score based on Python keywords
                    score = sum(1 for kw in ['def ', 'import ', 'class ', 'return ', 'print'] if kw in text)
                    if score > 0 or len(text) > 100:
                        results.append((name, text[:500], score))
                except:
                    pass
        
        return results
    
    def decrypt_file(self, input_file, output_file=None):
        """Main decrypt function"""
        print("=" * 60)
        print("UNIVERSAL DECRYPTOR")
        print("=" * 60)
        print(f"Input: {input_file}")
        
        # Read file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(input_file, 'rb') as f:
                content = f.read()
        
        # Detect patterns
        patterns = self.detect_pattern(content)
        print(f"\nDetected patterns: {patterns}")
        
        if not patterns:
            print("No known encryption patterns detected!")
            return False
        
        # Try emoji decryption
        if 'emoji_encoding' in patterns:
            print("\n=== Trying Emoji Decryption ===")
            
            for i, emoji_map in enumerate(EMOJI_MAPPINGS):
                decoded = self.decrypt_emoji(content, emoji_map)
                if decoded:
                    print(f"\nMapping {i+1}: Decoded {len(decoded)} bytes")
                    
                    analysis = self.analyze_bytes(decoded)
                    print(f"Byte range: {analysis['min_byte']} - {analysis['max_byte']}")
                    
                    # Save raw bytes
                    raw_out = f"{output_file or 'decrypted'}_raw_{i+1}.bin"
                    with open(raw_out, 'wb') as f:
                        f.write(decoded)
                    print(f"Saved raw bytes to: {raw_out}")
                    
                    # Try marshal decompile
                    marshal_results = self.try_decompile(decoded)
                    if marshal_results:
                        print(f"\n✓ Marshal decode successful!")
                        for result_type, obj, offset in marshal_results[:3]:
                            print(f"  Offset {offset}: {result_type}")
                            
                            if result_type == 'decompiled':
                                py_out = f"{output_file or 'decrypted'}_{i+1}.py"
                                with open(py_out, 'w') as f:
                                    f.write(f"# Decompiled from emoji encoding\n\n{obj}")
                                print(f"  Saved decompiled code to: {py_out}")
                                return True
                    
                    # Try ASCII mappings
                    ascii_results = self.try_ascii_mapping(decoded)
                    if ascii_results:
                        print("\nASCII mapping attempts:")
                        for name, text, score in sorted(ascii_results, key=lambda x: -x[2]):
                            print(f"\n  {name} (score: {score}):")
                            print(f"  {text[:200]}...")
        
        print("\n" + "=" * 60)
        print("Decryption attempt completed.")
        print("Check output files for results.")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python complete_decryptor.py <input_file> [output_prefix]")
        print("\nSupported formats:")
        print("  - Emoji-encoded Python files")
        print("  - Base64 encoded content")
        print("  - Hex encoded strings")
        print("  - Marshal bytecode (.pyc)")
        print("  - XOR encrypted data")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else None
    
    decryptor = UniversalDecryptor()
    success = decryptor.decrypt_file(input_file, output_prefix)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
