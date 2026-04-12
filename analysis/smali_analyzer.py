#!/usr/bin/env python3
"""
Android APK Reverse Engineering Analysis & Patching Script
Adaptif terhadap obfuscation - tidak bergantung pada nama class/method

Script ini menganalisis file smali hasil decompile APK untuk menemukan:
1. Method dengan return type integer (I) - untuk energy, coin, progress, dll
2. Method dengan return type boolean (Z) - untuk validasi akses, unlock fitur, dll

Target: Bunpo APK 3.8.0+ dengan obfuscation
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class MethodInfo:
    """Informasi tentang method yang ditemukan"""
    file_path: str
    class_name: str
    method_name: str
    return_type: str
    access_flags: List[str]
    line_number: int
    has_getter_pattern: bool
    has_sget_pattern: bool
    has_iget_pattern: bool
    suspicious_strings: List[str]
    
class SmaliAnalyzer:
    """Analyzer untuk file smali"""
    
    # Pattern untuk mendeteksi return type
    RETURN_TYPE_INT = 'I'
    RETURN_TYPE_BOOL = 'Z'
    
    # Pattern regex untuk analisa
    METHOD_PATTERN = re.compile(
        r'\.method\s+(?P<access>[^\s]+(?:\s+[^\s]+)*)\s+(?P<name>[^\(]+)\((?P<params>[^\)]*)\)(?P<return>L[^;]*|.)'
    )
    
    FIELD_GET_PATTERN = re.compile(r'(iget|sget|aget)[^-]+->(?P<field>[^\s:]+):(?P<type>[^\s]+)')
    INVOKE_PATTERN = re.compile(r'invoke-(?:virtual|direct|static|interface)')
    
    # String yang mencurigakan untuk feature checking
    SUSPICIOUS_STRINGS = [
        'premium', 'vip', 'unlock', 'subscribe', 'license',
        'energy', 'coin', 'gem', 'diamond', 'gold', 'score',
        'point', 'count', 'limit', 'max', 'remaining',
        'available', 'enabled', 'allowed', 'permitted',
        'valid', 'active', 'status', 'state', 'flag'
    ]
    
    def __init__(self, smali_dir: str):
        self.smali_dir = Path(smali_dir)
        self.int_methods: List[MethodInfo] = []
        self.bool_methods: List[MethodInfo] = []
        self.all_classes: Dict[str, List[MethodInfo]] = defaultdict(list)
        
    def analyze(self):
        """Mulai analisis semua file smali"""
        print(f"[*] Menganalisis direktori: {self.smali_dir}")
        
        smali_files = list(self.smali_dir.rglob("*.smali"))
        print(f"[*] Ditemukan {len(smali_files)} file smali")
        
        for i, smali_file in enumerate(smali_files):
            if i % 1000 == 0:
                print(f"    Progress: {i}/{len(smali_files)}")
            self._analyze_file(smali_file)
            
        print(f"\n[*] Analisis selesai!")
        print(f"    - Method integer ditemukan: {len(self.int_methods)}")
        print(f"    - Method boolean ditemukan: {len(self.bool_methods)}")
        
    def _analyze_file(self, file_path: Path):
        """Analisis satu file smali"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return
            
        # Ekstrak class name
        class_match = re.search(r'\.class\s+(?:[^\s]+\s+)*L([^;]+);', content)
        if not class_match:
            return
        class_name = class_match.group(1)
        
        # Cari semua method
        for match in self.METHOD_PATTERN.finditer(content):
            method_info = self._process_method_match(match, file_path, class_name, content)
            if method_info:
                self.all_classes[class_name].append(method_info)
                
                if method_info.return_type == self.RETURN_TYPE_INT:
                    self.int_methods.append(method_info)
                elif method_info.return_type == self.RETURN_TYPE_BOOL:
                    self.bool_methods.append(method_info)
    
    def _process_method_match(self, match, file_path: Path, class_name: str, content: str) -> Optional[MethodInfo]:
        """Proses satu method match"""
        access_str = match.group('access')
        method_name = match.group('name').strip()
        params = match.group('params')
        return_type = match.group('return')
        
        # Hanya ambil method tanpa parameter atau dengan sedikit parameter (getter pattern)
        param_count = len([p for p in params.split(';') if p]) if params else 0
        
        # Filter: method dengan return I atau Z
        if return_type not in [self.RETURN_TYPE_INT, self.RETURN_TYPE_BOOL]:
            return None
            
        # Skip constructor dan method khusus
        if method_name in ['<init>', '<clinit>']:
            return None
            
        # Hitung line number
        line_num = content[:match.start()].count('\n') + 1
        
        # Cek pola akses
        method_block = self._extract_method_block(content, match.start())
        has_getter = bool(self.FIELD_GET_PATTERN.search(method_block))
        has_sget = 'sget' in method_block
        has_iget = 'iget' in method_block
        
        # Cek string mencurigakan
        suspicious = []
        for s in self.SUSPICIOUS_STRINGS:
            if s.lower() in method_block.lower():
                suspicious.append(s)
        
        access_flags = access_str.split()
        
        return MethodInfo(
            file_path=str(file_path),
            class_name=class_name,
            method_name=method_name,
            return_type=return_type,
            access_flags=access_flags,
            line_number=line_num,
            has_getter_pattern=has_getter,
            has_sget_pattern=has_sget,
            has_iget_pattern=has_iget,
            suspicious_strings=suspicious
        )
    
    def _extract_method_block(self, content: str, start_pos: int) -> str:
        """Ekstrak blok method dari posisi start hingga .end method"""
        end_match = re.search(r'\.end method', content[start_pos:])
        if end_match:
            return content[start_pos:start_pos + end_match.end()]
        return content[start_pos:start_pos + 2000]  # Fallback
    
    def get_priority_methods(self, min_score: int = 2) -> List[MethodInfo]:
        """Dapatkan method dengan prioritas tinggi untuk patching"""
        priority = []
        
        for method in self.int_methods + self.bool_methods:
            score = 0
            
            # Score berdasarkan pola getter
            if method.has_getter_pattern:
                score += 2
            if method.has_sget_pattern or method.has_iget_pattern:
                score += 1
                
            # Score berdasarkan string mencurigakan
            score += len(method.suspicious_strings)
            
            # Score berdasarkan access flags (public/static lebih mungkin)
            if 'public' in method.access_flags:
                score += 1
            if 'static' in method.access_flags:
                score += 1
                
            if score >= min_score:
                method.priority_score = score
                priority.append(method)
                
        return sorted(priority, key=lambda m: getattr(m, 'priority_score', 0), reverse=True)
    
    def print_report(self, top_n: int = 50):
        """Cetak laporan analisis"""
        print("\n" + "="*80)
        print("LAPORAN ANALISIS SMALI - METHOD POTENSIAL UNTUK PATCHING")
        print("="*80)
        
        priority_methods = self.get_priority_methods()
        
        print(f"\n[+] TOP {top_n} METHOD DENGAN SKOR PRIORITAS TERTINGGI:\n")
        
        for i, method in enumerate(priority_methods[:top_n], 1):
            print(f"{i}. Class: L{method.class_name};")
            print(f"   Method: {method.method_name}(){method.return_type}")
            print(f"   File: {method.file_path}")
            print(f"   Line: {method.line_number}")
            print(f"   Access: {' '.join(method.access_flags)}")
            print(f"   Patterns: getter={method.has_getter_pattern}, sget={method.has_sget_pattern}, iget={method.has_iget_pattern}")
            if method.suspicious_strings:
                print(f"   Suspicious: {', '.join(method.suspicious_strings)}")
            print(f"   Priority Score: {getattr(method, 'priority_score', 0)}")
            print()


class SmaliPatcher:
    """Patcher untuk memodifikasi file smali"""
    
    @staticmethod
    def patch_int_return(file_path: str, method_name: str, new_value: int = 9999) -> bool:
        """
        Patch method dengan return integer untuk mengembalikan nilai tetap
        
        Contoh patch:
        Sebelum: return v0  (di mana v0 berisi nilai dari field)
        Sesudah: const/4 v0, 0x10  (atau const v0, 9999)
                 return v0
        """
        try:
            content = Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            print(f"[!] Error membaca file: {e}")
            return False
            
        # Cari method
        method_pattern = re.compile(
            rf'(\.method\s+[^\n]*{re.escape(method_name)}\([^\)]*\)I[^\.]*?)(\.end method)',
            re.DOTALL
        )
        
        match = method_pattern.search(content)
        if not match:
            print(f"[!] Method {method_name} tidak ditemukan di {file_path}")
            return False
            
        method_block = match.group(1)
        
        # Cari instruksi return terakhir dalam method
        # Ganti dengan const + return nilai baru
        lines = method_block.split('\n')
        new_lines = []
        in_method = False
        patched = False
        
        for line in lines:
            stripped = line.strip()
            
            # Deteksi akhir method (sebelum .end method)
            if stripped.startswith('.end method'):
                break
                
            # Jika ada return vx, ganti dengan const + return
            if not patched and re.match(r'return\s+vx?$', stripped):
                # Tambahkan const instruction sebelum return
                if new_value <= 15:
                    new_lines.append(f"        const/4 v0, 0x{new_value:x}")
                else:
                    new_lines.append(f"        const v0, {new_value}")
                new_lines.append("        return v0")
                patched = True
            else:
                new_lines.append(line)
                
        if not patched:
            # Jika tidak ada return yang ditemukan, tambahkan di akhir
            new_lines.append(f"        const v0, {new_value}")
            new_lines.append("        return v0")
            patched = True
            
        # Rekonstruksi method block
        new_method_block = '\n'.join(new_lines) + '\n    .end method'
        
        # Replace di content
        new_content = content.replace(match.group(0), new_method_block)
        
        # Tulis kembali
        try:
            Path(file_path).write_text(new_content, encoding='utf-8')
            print(f"[+] Berhasil patch {method_name} di {file_path}")
            return True
        except Exception as e:
            print(f"[!] Error menulis file: {e}")
            return False
    
    @staticmethod
    def patch_bool_return(file_path: str, method_name: str, return_true: bool = True) -> bool:
        """
        Patch method dengan return boolean untuk selalu return true/false
        
        Contoh patch:
        Sebelum: return v0  (di mana v0 berisi hasil validasi)
        Sesudah: const/4 v0, 0x1  (true) atau const/4 v0, 0x0 (false)
                 return v0
        """
        try:
            content = Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            print(f"[!] Error membaca file: {e}")
            return False
            
        method_pattern = re.compile(
            rf'(\.method\s+[^\n]*{re.escape(method_name)}\([^\)]*\)Z[^\.]*?)(\.end method)',
            re.DOTALL
        )
        
        match = method_pattern.search(content)
        if not match:
            print(f"[!] Method {method_name} tidak ditemukan di {file_path}")
            return False
            
        method_block = match.group(1)
        lines = method_block.split('\n')
        new_lines = []
        patched = False
        
        return_value = 0x1 if return_true else 0x0
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('.end method'):
                break
                
            if not patched and re.match(r'return\s+vx?$', stripped):
                new_lines.append(f"        const/4 v0, 0x{return_value:x}")
                new_lines.append("        return v0")
                patched = True
            else:
                new_lines.append(line)
                
        if not patched:
            new_lines.append(f"        const/4 v0, 0x{return_value:x}")
            new_lines.append("        return v0")
            patched = True
            
        new_method_block = '\n'.join(new_lines) + '\n    .end method'
        new_content = content.replace(match.group(0), new_method_block)
        
        try:
            Path(file_path).write_text(new_content, encoding='utf-8')
            print(f"[+] Berhasil patch {method_name} di {file_path} (return={'true' if return_true else 'false'})")
            return True
        except Exception as e:
            print(f"[!] Error menulis file: {e}")
            return False
    
    @staticmethod
    def generate_patch_example(method: MethodInfo, patch_type: str = 'auto') -> str:
        """Generate contoh patch untuk sebuah method"""
        examples = []
        examples.append(f"\n# Contoh Patch untuk: L{method.class_name};->{method.method_name}(){method.return_type}")
        examples.append(f"# File: {method.file_path}")
        examples.append(f"# Line: {method.line_number}\n")
        
        if method.return_type == 'I':
            examples.append("""
# === PATCH INTEGER RETURN (Set nilai maksimum) ===
# Cari method dan modifikasi bagian return:

    .method public abstract methodName()I
        .registers 2
        
        # ... kode asli ...
        
        # GANTI BAGIAN INI:
        # return v0
        
        # DENGAN:
        const v0, 99999      # Set nilai maksimum
        return v0
        
    .end method
""")
        elif method.return_type == 'Z':
            examples.append("""
# === PATCH BOOLEAN RETURN (Force true) ===
# Cari method dan modifikasi bagian return:

    .method public abstract methodName()Z
        .registers 2
        
        # ... kode asli ...
        
        # GANTI BAGIAN INI:
        # return v0
        
        # DENGAN:
        const/4 v0, 0x1      # Force return true
        return v0
        
    .end method
""")
        
        return '\n'.join(examples)


def main():
    """Fungsi utama"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Android APK Smali Analyzer & Patcher (Anti-Obfuscation)'
    )
    parser.add_argument(
        'smali_dir',
        help='Direktori berisi file smali hasil decompile'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Tampilkan laporan analisis'
    )
    parser.add_argument(
        '--top', '-t',
        type=int,
        default=50,
        help='Jumlah method teratas untuk ditampilkan (default: 50)'
    )
    parser.add_argument(
        '--patch-int',
        nargs=2,
        metavar=('FILE', 'METHOD'),
        help='Patch method integer (contoh: --patch-int file.smali methodName)'
    )
    parser.add_argument(
        '--patch-bool',
        nargs=2,
        metavar=('FILE', 'METHOD'),
        help='Patch method boolean (contoh: --patch-bool file.smali methodName)'
    )
    parser.add_argument(
        '--int-value',
        type=int,
        default=9999,
        help='Nilai integer untuk patch (default: 9999)'
    )
    parser.add_argument(
        '--bool-value',
        choices=['true', 'false'],
        default='true',
        help='Nilai boolean untuk patch (default: true)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Simpan laporan ke file'
    )
    
    args = parser.parse_args()
    
    # Validasi direktori
    if not os.path.isdir(args.smali_dir):
        print(f"[!] Error: Direktori tidak ditemukan: {args.smali_dir}")
        sys.exit(1)
    
    # Analisis
    analyzer = SmaliAnalyzer(args.smali_dir)
    analyzer.analyze()
    
    # Generate report
    if args.report or not (args.patch_int or args.patch_bool):
        analyzer.print_report(args.top)
        
        # Simpan ke file jika diminta
        if args.output:
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                analyzer.print_report(args.top)
            
            Path(args.output).write_text(f.getvalue(), encoding='utf-8')
            print(f"\n[+] Laporan disimpan ke: {args.output}")
    
    # Patching
    patcher = SmaliPatcher()
    
    if args.patch_int:
        file_path, method_name = args.patch_int
        patcher.patch_int_return(file_path, method_name, args.int_value)
        
    if args.patch_bool:
        file_path, method_name = args.patch_bool
        patcher.patch_bool_return(
            file_path, 
            method_name, 
            return_true=(args.bool_value == 'true')
        )


if __name__ == '__main__':
    main()
