#!/usr/bin/env python3
"""
Universal Python Decryptor/Deobfuscator
Mendeteksi dan mendecrypt berbagai pattern enkripsi/obfuscation pada file Python
"""

import re
import ast
import sys
from pathlib import Path


class PatternDetector:
    """Mendeteksi pattern enkripsi/obfuscation"""
    
    @staticmethod
    def detect_emoji_encoding(content):
        """Deteksi emoji-based encoding"""
        patterns = [
            r'exec\(\s*["\']\.join\s*\(\s*map\s*\(\s*chr\s*,',
            r'map\s*\(\s*chr\s*,\s*\[int\(',
            r'\{[^}]*😀[^}]*😁[^}]*😂[^}]*\}',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    
    @staticmethod
    def detect_base64_encoding(content):
        """Deteksi base64 encoding"""
        patterns = [
            r'import\s+base64',
            r'base64\.b64decode',
            r'base64\.decodebytes',
            r'exec\s*\(\s*base64\.',
            r'eval\s*\(\s*base64\.',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_hex_encoding(content):
        """Deteksi hex encoding"""
        patterns = [
            r'\\x[0-9a-fA-F]{2}',
            r'bytes\.fromhex',
            r'\.decode\(\s*["\']hex["\']',
            r'exec\s*\(\s*["\'][0-9a-fA-F]+["\']',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    
    @staticmethod
    def detect_rot_encoding(content):
        """Deteksi ROT/Caesar cipher"""
        patterns = [
            r'rot_\d+',
            r'caesar',
            r'chr\s*\(\s*ord\s*\([^)]+\)\s*[+\-]\s*\d+',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_xor_encoding(content):
        """Deteksi XOR encoding"""
        patterns = [
            r'\^\s*0x[0-9a-fA-F]+',
            r'\^\s*\d+',
            r'xor',
            r'lambda\s*\w+\s*:\s*\w+\s*\^',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def detect_eval_exec(content):
        """Deteksi penggunaan eval/exec untuk obfuscation"""
        patterns = [
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'getattr\s*\(\s*__builtins__',
        ]
        
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            count += len(matches)
        
        return count > 0


class EmojiDecryptor:
    """Decryptor untuk emoji-based encoding"""
    
    def __init__(self, content):
        self.content = content
        self.emoji_map = None
        self.encoded_strings = []
    
    def extract_emoji_mapping(self):
        """Ekstrak mapping emoji ke angka"""
        # Cari dictionary mapping emoji
        pattern = r'\{([^}]*(?:😀|😁|😂|😃|😄|😅|😉|😊|😛|🤣)[^}]*)\}'
        match = re.search(pattern, self.content)
        
        if match:
            map_content = match.group(1)
            self.emoji_map = {}
            
            # Parse setiap mapping 'emoji': number
            emoji_pattern = r"'([😀-🙏]+)':\s*(\d+)"
            for emoji_match in re.finditer(emoji_pattern, map_content):
                emoji = emoji_match.group(1)
                number = int(emoji_match.group(2))
                self.emoji_map[emoji] = number
            
            return True
        return False
    
    def extract_encoded_data(self):
        """Ekstrak string emoji yang terenkripsi"""
        # Cari string emoji setelah mapping
        pattern = r'["\']([\s😀-🙏]+)["\']\s*\)'
        matches = re.findall(pattern, self.content)
        
        if matches:
            # Gabungkan semua string emoji yang ditemukan
            self.encoded_strings = matches
            return True
        
        # Alternatif: cari dalam format exec
        pattern = r'for\s+x\s+in\s*["\']([\s😀-🙏]+)["\']'
        match = re.search(pattern, self.content)
        
        if match:
            self.encoded_strings = [match.group(1)]
            return True
        
        return False
    
    def decode_emoji_string(self, emoji_string):
        """Decode string emoji menjadi teks asli"""
        if not self.emoji_map:
            return None
        
        decoded_chars = []
        
        # Split berdasarkan whitespace untuk mendapatkan setiap grup emoji
        emoji_groups = emoji_string.split()
        
        for group in emoji_groups:
            if not group.strip():
                continue
            
            # Konversi setiap grup emoji menjadi angka
            digit_str = ""
            i = 0
            while i < len(group):
                found = False
                # Coba match emoji dengan panjang berbeda (dari yang terpanjang)
                for length in range(min(4, len(group) - i), 0, -1):
                    emoji_candidate = group[i:i+length]
                    if emoji_candidate in self.emoji_map:
                        digit_str += str(self.emoji_map[emoji_candidate])
                        i += length
                        found = True
                        break
                
                if not found:
                    i += 1
            
            if digit_str:
                try:
                    char_code = int(digit_str)
                    if 0 <= char_code <= 0x10FFFF:
                        decoded_chars.append(chr(char_code))
                except (ValueError, OverflowError):
                    pass
        
        return ''.join(decoded_chars)
    
    def decrypt(self):
        """Proses decrypt lengkap"""
        if not self.extract_emoji_mapping():
            return None, "Gagal mengekstrak emoji mapping"
        
        if not self.extract_encoded_data():
            return None, "Gagal mengekstrak data terenkripsi"
        
        decoded_parts = []
        for encoded in self.encoded_strings:
            decoded = self.decode_emoji_string(encoded)
            if decoded:
                decoded_parts.append(decoded)
        
        if decoded_parts:
            full_decoded = ''.join(decoded_parts)
            return full_decoded, "Success"
        
        return None, "Gagal decoding"


class Base64Decryptor:
    """Decryptor untuk base64 encoding"""
    
    def __init__(self, content):
        self.content = content
    
    def decrypt(self):
        """Cari dan decode base64 strings"""
        import base64
        
        # Cari base64 encoded strings
        pattern = r'["\']([A-Za-z0-9+/=]{20,})["\']'
        matches = re.findall(pattern, self.content)
        
        decoded_parts = []
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if decoded.isprintable() or '\n' in decoded:
                    decoded_parts.append(decoded)
            except Exception:
                pass
        
        if decoded_parts:
            return '\n'.join(decoded_parts), "Success"
        
        return None, "No valid base64 found"


class HexDecryptor:
    """Decryptor untuk hex encoding"""
    
    def __init__(self, content):
        self.content = content
    
    def decrypt(self):
        """Cari dan decode hex strings"""
        # Cari hex strings
        pattern = r'(?:\\x[0-9a-fA-F]{2})+'
        matches = re.findall(pattern, self.content)
        
        if matches:
            try:
                decoded = ''.join([chr(int(x[2:], 16)) for x in matches[0].split('\\x')[1:]])
                return decoded, "Success"
            except Exception as e:
                return None, f"Hex decode error: {e}"
        
        # Cari format lain
        pattern = r'["\']([0-9a-fA-F]{20,})["\']'
        matches = re.findall(pattern, self.content)
        
        for match in matches:
            try:
                decoded = bytes.fromhex(match).decode('utf-8', errors='ignore')
                if decoded.isprintable():
                    return decoded, "Success"
            except Exception:
                pass
        
        return None, "No valid hex found"


class UniversalDecryptor:
    """Main decryptor class yang mendeteksi dan mendecrypt otomatis"""
    
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.content = None
        self.detected_patterns = []
    
    def load_file(self):
        """Load file content"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def detect_patterns(self):
        """Deteksi semua pattern enkripsi"""
        self.detected_patterns = []
        
        detectors = [
            ('Emoji Encoding', PatternDetector.detect_emoji_encoding),
            ('Base64 Encoding', PatternDetector.detect_base64_encoding),
            ('Hex Encoding', PatternDetector.detect_hex_encoding),
            ('ROT/Caesar Cipher', PatternDetector.detect_rot_encoding),
            ('XOR Encoding', PatternDetector.detect_xor_encoding),
            ('Eval/Exec Obfuscation', PatternDetector.detect_eval_exec),
        ]
        
        for name, detector_func in detectors:
            if detector_func(self.content):
                self.detected_patterns.append(name)
        
        return self.detected_patterns
    
    def decrypt(self):
        """Proses decrypt berdasarkan pattern yang terdeteksi"""
        if not self.content:
            if not self.load_file():
                return None, "Failed to load file"
        
        # Deteksi patterns
        patterns = self.detect_patterns()
        
        if not patterns:
            return self.content, "No encryption detected, returning original content"
        
        print(f"Detected patterns: {', '.join(patterns)}")
        
        # Coba decrypt berdasarkan pattern
        if 'Emoji Encoding' in patterns:
            print("\nAttempting emoji decryption...")
            decryptor = EmojiDecryptor(self.content)
            result, message = decryptor.decrypt()
            if result:
                return result, f"Emoji decryption successful: {message}"
        
        if 'Base64 Encoding' in patterns:
            print("\nAttempting base64 decryption...")
            decryptor = Base64Decryptor(self.content)
            result, message = decryptor.decrypt()
            if result:
                return result, f"Base64 decryption successful: {message}"
        
        if 'Hex Encoding' in patterns:
            print("\nAttempting hex decryption...")
            decryptor = HexDecryptor(self.content)
            result, message = decryptor.decrypt()
            if result:
                return result, f"Hex decryption successful: {message}"
        
        # Jika tidak ada yang berhasil
        return None, "Could not decrypt with available methods"
    
    def save_decrypted(self, output_path=None):
        """Save hasil decrypt ke file"""
        result, message = self.decrypt()
        
        if not result:
            print(f"Decryption failed: {message}")
            return False
        
        if output_path is None:
            output_path = self.file_path.parent / f"{self.file_path.stem}_decrypted{self.file_path.suffix}"
        else:
            output_path = Path(output_path)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n✓ Decrypted file saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python universal_decryptor.py <encrypted_file> [output_file]")
        print("\nSupported encryption types:")
        print("  - Emoji-based encoding")
        print("  - Base64 encoding")
        print("  - Hex encoding")
        print("  - ROT/Caesar cipher")
        print("  - XOR encoding")
        print("  - Eval/Exec obfuscation")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    print(f"Processing: {input_file}")
    print("=" * 60)
    
    decryptor = UniversalDecryptor(input_file)
    
    if decryptor.save_decrypted(output_file):
        print("\n✓ Decryption completed successfully!")
    else:
        print("\n✗ Decryption failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
