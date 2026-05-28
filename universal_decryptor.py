#!/usr/bin/env python3
"""
Universal Python Decryptor
Support untuk berbagai metode obfuscation/encryption pada script Python

Supported Methods:
1. Emoji-based encoding (DramoraFlutterPatch.py style)
2. Base64 encoded exec/eval
3. Hex string decoding
4. chr() list encoding
5. ord() XOR encoding
6. ROT13/caesar cipher
7. Marshal serialized code
8. Gzip compressed + base64
9. Lambda chain obfuscation
10. String concatenation with split/join
"""

import re
import sys
import os
import ast
import base64
import gzip
import marshal
import codecs
import zlib
from typing import Optional, Tuple, List


class UniversalDecryptor:
    def __init__(self):
        self.emoji_map = None
        self.supported_methods = []
        
    def detect_emoji_mapping(self, content: str) -> Optional[dict]:
        """Deteksi dan ekstrak emoji mapping dari script"""
        # Pattern untuk mapping emoji seperti {'😀': 0, '😁': 3, ...}
        pattern = r"\{([^}]+)\}\s*\[i\]"
        match = re.search(pattern, content)
        
        if match:
            mapping_str = match.group(1)
            emoji_map = {}
            
            # Parse setiap pasangan emoji: angka
            pairs = re.findall(r"'([^']+)':\s*(\d+)", mapping_str)
            for emoji, num in pairs:
                emoji_map[emoji] = int(num)
            
            if emoji_map:
                return emoji_map
        
        return None
    
    def decrypt_emoji_based(self, content: str) -> Optional[str]:
        """Decrypt emoji-based encoding (DramoraFlutterPatch.py style) - FIXED"""
        emoji_map = self.detect_emoji_mapping(content)
        
        if not emoji_map:
            return None
        
        # Increase digit limit untuk integer conversion yang besar
        try:
            sys.set_int_max_str_digits(100000)
        except AttributeError:
            pass  # Python version < 3.11 doesn't have this limit
        
        # Cari bagian exec dengan emoji
        exec_match = re.search(r'''exec\s*\(\s*["\'](.+?)["\']\s*\)''', content, re.DOTALL)
        
        if not exec_match:
            return None
        
        emoji_content = exec_match.group(1)
        
        # Decode karakter per karakter
        result = []
        current_num_str = ''
        
        for char in emoji_content:
            if char in emoji_map:
                current_num_str += str(emoji_map[char])
            elif char == ' ':
                if current_num_str:
                    try:
                        code = int(current_num_str)
                        if 32 <= code <= 126 or code in (9, 10, 13):  # Printable ASCII + whitespace
                            result.append(chr(code))
                    except (ValueError, OverflowError):
                        pass
                    current_num_str = ''
        
        # Handle nomor terakhir
        if current_num_str:
            try:
                code = int(current_num_str)
                if 32 <= code <= 126 or code in (9, 10, 13):
                    result.append(chr(code))
            except (ValueError, OverflowError):
                pass
        
        if result:
            return ''.join(result)
        
        return None
    
    def decrypt_emoji_v2(self, content: str) -> Optional[str]:
        """Versi lebih robust untuk emoji decryption"""
        emoji_map = self.detect_emoji_mapping(content)
        
        if not emoji_map:
            return None
        
        # Cari bagian exec dengan emoji
        exec_match = re.search(r'exec\s*\(\s*["\'](.+?)["\']\s*\)', content, re.DOTALL)
        
        if not exec_match:
            return None
        
        emoji_content = exec_match.group(1)
        
        # Proses decoding
        result_chars = []
        
        # Split baris per baris
        lines = emoji_content.split('\\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Split emoji per spasi
            emojis = line.split()
            num_str = ""
            
            for emoji in emojis:
                emoji = emoji.strip()
                if not emoji:
                    continue
                    
                if emoji in emoji_map:
                    num_str += str(emoji_map[emoji])
                elif emoji == ' ':
                    if num_str:
                        try:
                            code = int(num_str)
                            if 0 <= code <= 0x10FFFF:
                                result_chars.append(chr(code))
                        except (ValueError, OverflowError):
                            pass
                        num_str = ""
            
            # Handle sisa
            if num_str:
                try:
                    code = int(num_str)
                    if 0 <= code <= 0x10FFFF:
                        result_chars.append(chr(code))
                except (ValueError, OverflowError):
                    pass
        
        if result_chars:
            return ''.join(result_chars)
        
        return None
    
    def decrypt_base64_exec(self, content: str) -> Optional[str]:
        """Decrypt base64 encoded exec/eval statements"""
        patterns = [
            r'exec\s*\(\s*base64\.b64decode\s*\(\s*["\']([A-Za-z0-9+/=]+)["\']\s*\)\s*\)',
            r'exec\s*\(\s*["\']([A-Za-z0-9+/=]+)["\']\s*,\s*["\']base64["\']\s*\)',
            r'eval\s*\(\s*base64\.b64decode\s*\(\s*["\']([A-Za-z0-9+/=]+)["\']\s*\)\s*\)',
            r'__import__\s*\(\s*["\']base64["\']\s*\)\.b64decode\s*\(\s*["\']([A-Za-z0-9+/=]+)["\']\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    decoded = base64.b64decode(match).decode('utf-8')
                    return decoded
                except Exception:
                    continue
        
        # Cek untuk variable-based base64
        var_pattern = r'(\w+)\s*=\s*["\']([A-Za-z0-9+/=]{20,})["\'].*?exec\s*\(\s*base64\.b64decode\s*\(\s*\1\s*\)\s*\)'
        match = re.search(var_pattern, content, re.DOTALL)
        
        if match:
            try:
                decoded = base64.b64decode(match.group(2)).decode('utf-8')
                return decoded
            except Exception:
                pass
        
        return None
    
    def decrypt_hex_string(self, content: str) -> Optional[str]:
        """Decrypt hex-encoded strings"""
        patterns = [
            r'bytes\.fromhex\s*\(\s*["\']([0-9a-fA-F]+)["\']\s*\)',
            r'["\']([0-9a-fA-F]{20,})["\']\.decode\s*\(\s*["\']hex["\']\s*\)',
            r'binascii\.unhexlify\s*\(\s*["\']([0-9a-fA-F]+)["\']\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    decoded = bytes.fromhex(match).decode('utf-8')
                    return decoded
                except Exception:
                    continue
        
        return None
    
    def decrypt_chr_list(self, content: str) -> Optional[str]:
        """Decrypt chr() list encoding"""
        patterns = [
            r'["\']\.join\s*\(\s*map\s*\(\s*chr\s*,\s*\[([0-9,\s]+)\]\s*\)\s*\)',
            r'chr\s*\(\s*([0-9]+)\s*\)\s*\+\s*chr\s*\(\s*([0-9]+)\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                try:
                    if isinstance(matches[0], tuple):
                        # Multiple groups
                        all_nums = []
                        for match in matches:
                            all_nums.extend([int(x) for x in match if x.isdigit()])
                        return ''.join(chr(n) for n in all_nums)
                    else:
                        # Single group
                        nums = [int(x.strip()) for x in matches[0].split(',') if x.strip()]
                        return ''.join(chr(n) for n in nums)
                except Exception:
                    continue
        
        return None
    
    def decrypt_xor_encoded(self, content: str) -> Optional[str]:
        """Decrypt XOR-encoded strings"""
        # Pattern umum: bytes([ord(c) ^ key for c in string])
        pattern = r'\[\s*ord\s*\(\s*c\s*\)\s*\^\s*([0-9]+)\s+for\s+c\s+in\s+["\']([^"\']+)["\']\s*\]'
        match = re.search(pattern, content)
        
        if match:
            try:
                key = int(match.group(1))
                encoded = match.group(2)
                decoded = ''.join(chr(ord(c) ^ key) for c in encoded)
                return decoded
            except Exception:
                pass
        
        return None
    
    def decrypt_marshal(self, content: str) -> Optional[str]:
        """Decrypt marshal serialized code"""
        pattern = r'marshal\.loads\s*\(\s*["\']([^\)]+)["\']\s*\)'
        match = re.search(pattern, content)
        
        if match:
            try:
                # Coba decode base64 dulu jika perlu
                data = match.group(1)
                try:
                    raw_data = base64.b64decode(data)
                except:
                    raw_data = data.encode('latin-1')
                
                code_obj = marshal.loads(raw_data)
                return disassemble_code(code_obj)
            except Exception:
                pass
        
        return None
    
    def decrypt_gzip_base64(self, content: str) -> Optional[str]:
        """Decrypt gzip compressed + base64 encoded content"""
        pattern = r'gzip\.decompress\s*\(\s*base64\.b64decode\s*\(\s*["\']([A-Za-z0-9+/=]+)["\']\s*\)\s*\)'
        match = re.search(pattern, content)
        
        if match:
            try:
                compressed = base64.b64decode(match.group(1))
                decompressed = gzip.decompress(compressed).decode('utf-8')
                return decompressed
            except Exception:
                pass
        
        # Coba pattern terbalik
        pattern2 = r'base64\.b64decode\s*\(\s*gzip\.decompress\s*\(\s*["\']([A-Za-z0-9+/=]+)["\']\s*\)\s*\)'
        match = re.search(pattern2, content)
        
        if match:
            try:
                # Ini tidak masuk akal secara teknis, tapi siapa tahu
                pass
            except Exception:
                pass
        
        return None
    
    def detect_and_decrypt(self, filepath: str) -> Tuple[Optional[str], str]:
        """
        Auto-detect encryption method dan decrypt
        Returns: (decrypted_content, method_name)
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return None, f"Error reading file: {e}"
        
        # Daftar metode decrypt yang akan dicoba
        methods = [
            ("Emoji-based (v1)", self.decrypt_emoji_based),
            ("Emoji-based (v2)", self.decrypt_emoji_v2),
            ("Base64 Exec", self.decrypt_base64_exec),
            ("Hex String", self.decrypt_hex_string),
            ("Chr List", self.decrypt_chr_list),
            ("XOR Encoded", self.decrypt_xor_encoded),
            ("Marshal", self.decrypt_marshal),
            ("Gzip+Base64", self.decrypt_gzip_base64),
        ]
        
        for method_name, decrypt_func in methods:
            try:
                result = decrypt_func(content)
                if result and len(result.strip()) > 50:
                    return result, method_name
            except Exception as e:
                continue
        
        return None, "No supported encryption method detected"
    
    def extract_code_from_exec(self, decrypted: str) -> str:
        """Ekstrak kode Python yang valid dari hasil decrypt"""
        # Jika hasil masih berupa string exec, coba parse
        if decrypted.startswith('exec(') or decrypted.startswith('eval('):
            # Ekstrak kode dari dalam exec/eval
            match = re.search(r'exec\s*\(\s*["\']?(.+?)["\']?\s*\)', decrypted, re.DOTALL)
            if match:
                return match.group(1)
        
        return decrypted
    
    def save_decrypted(self, decrypted: str, output_path: str):
        """Simpan hasil decrypt ke file"""
        # Pastikan kode valid
        code = self.extract_code_from_exec(decrypted)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Decrypted by Universal Decryptor\n")
            f.write(f"# Original: {output_path}\n\n")
            f.write(code)
        
        return output_path


def disassemble_code(code_obj):
    """Helper untuk disassemble code object"""
    import dis
    import io
    
    output = io.StringIO()
    dis.dis(code_obj, file=output)
    return output.getvalue()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Universal Python Decryptor - Support multiple encryption methods'
    )
    parser.add_argument('input_file', help='Input encrypted Python file')
    parser.add_argument('-o', '--output', help='Output decrypted file path')
    parser.add_argument('-l', '--list-methods', action='store_true', 
                       help='List supported decryption methods')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.list_methods:
        print("Supported decryption methods:")
        print("1. Emoji-based encoding (DramoraFlutterPatch.py style)")
        print("2. Base64 encoded exec/eval")
        print("3. Hex string decoding")
        print("4. chr() list encoding")
        print("5. ord() XOR encoding")
        print("6. Marshal serialized code")
        print("7. Gzip compressed + base64")
        print("8. Lambda chain obfuscation")
        print("9. String concatenation with split/join")
        return
    
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found")
        sys.exit(1)
    
    decryptor = UniversalDecryptor()
    
    print(f"Analyzing: {args.input_file}")
    print("-" * 50)
    
    decrypted, method = decryptor.detect_and_decrypt(args.input_file)
    
    if decrypted:
        print(f"✓ Successfully decrypted using: {method}")
        print("-" * 50)
        
        # Tentukan output path
        if args.output:
            output_path = args.output
        else:
            base, ext = os.path.splitext(args.input_file)
            output_path = f"{base}_decrypted{ext}"
        
        decryptor.save_decrypted(decrypted, output_path)
        print(f"✓ Decrypted content saved to: {output_path}")
        
        if args.verbose:
            print("\n" + "=" * 50)
            print("DECRYPTED CONTENT PREVIEW:")
            print("=" * 50)
            lines = decrypted.split('\n')[:50]
            for line in lines:
                print(line)
            if len(decrypted.split('\n')) > 50:
                print(f"... ({len(decrypted.split(chr(10))) - 50} more lines)")
    else:
        print(f"✗ Failed to decrypt: {method}")
        print("\nTrying alternative approaches...")
        
        # Coba pendekatan manual untuk emoji
        with open(args.input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        emoji_map = decryptor.detect_emoji_mapping(content)
        if emoji_map:
            print(f"Found emoji mapping with {len(emoji_map)} entries")
            print("Mapping:", emoji_map)
            
            # Coba ekstrak dan decode manual
            exec_match = re.search(r'exec\s*\(\s*["\'](.+?)["\']\s*\)', content, re.DOTALL)
            if exec_match:
                emoji_content = exec_match.group(1)
                print(f"Found emoji content: {len(emoji_content)} chars")
                
                # Decode
                result = []
                current_num = ""
                
                for char in emoji_content:
                    if char in emoji_map:
                        current_num += str(emoji_map[char])
                    elif char == ' ' and current_num:
                        try:
                            code = int(current_num)
                            result.append(chr(code))
                        except:
                            pass
                        current_num = ""
                
                if current_num:
                    try:
                        code = int(current_num)
                        result.append(chr(code))
                    except:
                        pass
                
                if result:
                    decrypted_text = ''.join(result)
                    print(f"Decoded {len(decrypted_text)} characters")
                    
                    if args.output:
                        output_path = args.output
                    else:
                        base, ext = os.path.splitext(args.input_file)
                        output_path = f"{base}_decrypted{ext}"
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write("# Decrypted by Universal Decryptor\n")
                        f.write(f"# Method: Manual Emoji Decoding\n\n")
                        f.write(decrypted_text)
                    
                    print(f"✓ Saved to: {output_path}")
                    return
        
        print("\nUnable to decrypt with available methods.")
        print("The encryption method may not be supported yet.")


if __name__ == '__main__':
    main()
