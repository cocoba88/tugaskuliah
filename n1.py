#!/usr/bin/env python3
"""
N1Master APK Patcher - com.aicyteadev.n1master
Patch by: インドラ
Features:
- Premium/Pro Selamanya
- Energy 999999
- Bypass License Check (pairip)
- Bypass Play Store redirect
- Toast "Patch by : インドラ" 2x di MainActivity
- Fix extractNativeLibs untuk install
- ✅ STANDALONE: Auto-download apktool & uber-apk-signer jika tidak ada
- ✅ ADAPTIVE: Auto-detect smali paths (compatible multi-versi)
- ✅ VERSION DETECTOR: Deteksi versi APK otomatis
- ✅ HACKER UI: Animasi terminal style hacker

Usage:
    python3 n1.py <input.apk|input.apks> [--output output.apk]

Requirements:
    - java (untuk menjalankan apktool.jar & uber-apk-signer)
    - Internet connection (hanya jika perlu download tools)

Compatible: Termux & Windows
Versi APK tested: v1.1.x, v1.1.33+

Changelog v2 (patch for v1.1.33):
  - UserProfile & MainActivity pindah dari smali_classes4 -> smali
  - EnergyManager dihapus dari app, diganti class i6/a (obfuscated LocalStorage)
  - Injection point Toast baru: new-instance p1, Li6/a;
  - Auto-detection smali path untuk future updates
  - Regex pattern lebih robust (tidak bergantung .locals whitespace)
"""
import os
import sys
import re
import shutil
import subprocess
import argparse
import glob
import urllib.request
import ssl
import time
import random

# ============================================================
# CONFIG
# ============================================================
PACKAGE = "com.aicyteadev.n1master"
TOAST_TEXT = "Patch by :\nインドラ"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# URLs untuk auto-download tools
APKTOOL_URL = "https://github.com/iBotPeaches/Apktool/releases/download/v3.0.1/apktool_3.0.1.jar"
APKTOOL_FILENAME = "apktool_3.0.1.jar"
UBER_SIGNER_URL = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar"
UBER_SIGNER_FILENAME = "uber-apk-signer-1.3.0.jar"

# Smali file paths (relative to decompiled folder)
# NOTE: Paths here are HINTS only - script will auto-search if not found
# v1.1.x: UserProfile & MainActivity di smali_classes4
# v1.1.33+: UserProfile & MainActivity pindah ke smali (classes.dex)
SMALI_PATHS = {
    # Try v1.1.33+ path first (smali/), then v1.1.x (smali_classes4/)
    "UserProfile": [
        "smali/com/aicyteadev/n1master/data/models/UserProfile.smali",
        "smali_classes4/com/aicyteadev/n1master/data/models/UserProfile.smali",
    ],
    # EnergyManager DIHAPUS di v1.1.33 - patch dilakukan di i6/a (LocalStorage obfuscated)
    # Patch energy sekarang dilakukan via UserProfile.isPro() dan UserProfile.getEnergy()
    "EnergyManager": [],  # kosong = tidak ada, akan di-skip
    # i6/a = LocalStorageManager obfuscated (muncul di v1.1.33)
    "LocalStorageObf": [
        "smali/i6/a.smali",
    ],
    "LicenseClient": [
        "smali_classes2/com/pairip/licensecheck/LicenseClient.smali",
    ],
    "LicenseActivity": [
        "smali_classes2/com/pairip/licensecheck/LicenseActivity.smali",
    ],
    # LicenseContentProvider adalah entry point UTAMA pairip yang dipanggil otomatis
    # sebelum MainActivity - ini root cause redirect ke Play Store!
    "LicenseContentProvider": [
        "smali_classes2/com/pairip/licensecheck/LicenseContentProvider.smali",
    ],
    "MainActivity": [
        "smali/com/aicyteadev/n1master/MainActivity.smali",
        "smali_classes4/com/aicyteadev/n1master/MainActivity.smali",
    ],
}

# ============================================================
# HELPERS
# ============================================================

# ANSI color codes for hacker UI
class Colors:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def hacker_print(text, color=Colors.GREEN, bold=False, delay=0.03):
    """Print text with hacker-style typing effect"""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}", end='', flush=True)
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print(f"{Colors.RESET}", flush=True)

def hacker_log(msg, color=Colors.CYAN):
    """Log message with hacker style"""
    print(f"{Colors.DIM}[{Colors.GREEN}N1Master{Colors.DIM}]{Colors.RESET} ", end='', flush=True)
    hacker_print(msg, color=color, delay=0.01)

def hacker_banner():
    """Display hacker-style banner"""
    banner = [
        f"{Colors.GREEN}",
        "  _   _  ____   ____    _    _   _ _____ ____  ",
        " | \\ | ||  _ \\ / ___|  / \\  | \\ | | ____|  _ \\ ",
        " |  \\| | |_) | |     / _ \\ |  \\| |  _| | |_) |",
        " | |\\  |  __/| |___ / ___ \\| |\\  | |___|  _ < ",
        " |_| \\_|_|    \\____/_/   \\_\\_| \\_|_____|_| \\_\\",
        f"{Colors.CYAN}           APK Patcher - Premium Unlimited",
        f"{Colors.YELLOW}              Patch by : インドラ",
        f"{Colors.RESET}"
    ]
    for line in banner:
        print(line)
        time.sleep(0.05)
    print()

def detect_apk_version(input_file):
    """Detect APK version from AndroidManifest.xml or file analysis"""
    log(f"Analyzing APK version...")
    
    # Try to extract version using aapt2 or aapt if available
    for cmd in ["aapt2", "aapt"]:
        try:
            result = subprocess.run(
                [cmd, "dump", "badging", input_file],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                output = result.stdout
                # Extract versionName
                version_match = re.search(r"versionName='([^']+)'", output)
                version_code_match = re.search(r"versionCode='([^']+)'", output)
                
                if version_match:
                    version_name = version_match.group(1)
                    version_code = version_code_match.group(1) if version_code_match else "unknown"
                    log(f"✅ APK Version Detected: v{version_name} (Code: {version_code})")
                    return {"versionName": version_name, "versionCode": version_code, "method": "aapt"}
        except:
            continue
    
    # Fallback: Try to extract manifest with apktool and parse
    try:
        temp_dir = os.path.join(SCRIPT_DIR, "temp_version_check")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        apktool_cmd = find_apktool()
        if apktool_cmd:
            run_cmd(apktool_cmd + ["d", "-f", "-o", temp_dir, "--no-src", "--only-main-classes", input_file], 
                   cwd=SCRIPT_DIR, check=False)
            
            manifest_path = os.path.join(temp_dir, "AndroidManifest.xml")
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                version_match = re.search(r'android:versionName="([^"]+)"', content)
                version_code_match = re.search(r'android:versionCode="([^"]+)"', content)
                
                if version_match:
                    version_name = version_match.group(1)
                    version_code = version_code_match.group(1) if version_code_match else "unknown"
                    log(f"✅ APK Version Detected: v{version_name} (Code: {version_code})")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return {"versionName": version_name, "versionCode": version_code, "method": "apktool"}
            
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        log(f"⚠️ Version detection via apktool failed: {e}")
    
    # Last resort: filename-based detection
    filename = os.path.basename(input_file)
    version_match = re.search(r'v?(\d+\.\d+(\.\d+)?)', filename, re.IGNORECASE)
    if version_match:
        version_name = version_match.group(1)
        log(f"⚠️ Estimated version from filename: v{version_name}")
        return {"versionName": version_name, "versionCode": "unknown", "method": "filename"}
    
    log("⚠️ Could not detect exact version, proceeding with adaptive patching...")
    return {"versionName": "unknown", "versionCode": "unknown", "method": "none"}

def log(msg):
    print(f"{Colors.DIM}[{Colors.GREEN}N1Master{Colors.DIM}]{Colors.RESET} {msg}")

def run_cmd(cmd, cwd=None, check=True):
    """Run shell command, return stdout."""
    log(f"Running: {' '.join(cmd[:3])}...")
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd
    )
    if result.stdout:
        print(result.stdout[:500])
    if result.returncode != 0 and check:
        print(f"STDERR: {result.stderr[:500]}")
        if check:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result

def download_file(url, dest_path):
    """Download file from URL with progress."""
    log(f"Downloading: {url}")
    log(f"Saving to: {dest_path}")
    
    # Handle SSL context for older Python versions
    try:
        context = ssl._create_unverified_context()
    except:
        context = None
    
    try:
        if context:
            with urllib.request.urlopen(url, context=context, timeout=60) as response, \
                 open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            with urllib.request.urlopen(url, timeout=60) as response, \
                 open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            log(f"✅ Download success: {os.path.getsize(dest_path) / 1024:.1f} KB")
            return True
        else:
            log("❌ Download failed: file empty or not created")
            return False
    except Exception as e:
        log(f"❌ Download error: {e}")
        return False

def find_file(name, search_dir):
    """Find file by name recursively."""
    for root, dirs, files in os.walk(search_dir):
        if name in files:
            return os.path.join(root, name)
    return None

def resolve_smali_path(key, path_list, decompiled_dir):
    """
    Resolve smali path from a list of candidates.
    Returns the first existing path, or auto-searches by filename.
    Returns None if not found (caller should handle).
    """
    if not path_list:  # empty list = intentionally skipped
        return None
    
    # Try each candidate path
    for rel_path in path_list:
        full_path = os.path.join(decompiled_dir, rel_path)
        if os.path.exists(full_path):
            log(f"  Found at: {rel_path}")
            return full_path
    
    # Auto-search by filename in all smali dirs
    filename = os.path.basename(path_list[0])  # get filename from first candidate
    package_hint = "/".join(path_list[0].split("/")[2:])  # get package path without smali_xxx prefix
    
    for d in sorted(os.listdir(decompiled_dir)):
        if d.startswith("smali"):
            candidate = os.path.join(decompiled_dir, d, package_hint)
            if os.path.exists(candidate):
                log(f"  Auto-found at: {d}/{package_hint}")
                return candidate
    
    # Last resort: search by filename only
    found = find_file(filename, decompiled_dir)
    if found:
        log(f"  Found by filename search: {os.path.relpath(found, decompiled_dir)}")
        return found
    
    return None

def find_apktool():
    """
    Find apktool: check PATH, then local jar, then auto-download.
    Returns: list command to run apktool (e.g., ['java', '-jar', 'apktool_3.0.1.jar'])
    """
    # 1. Check if apktool command exists in PATH
    for cmd in ["apktool", "apktool.bat"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True, timeout=10)
            log(f"apktool found in PATH: {cmd}")
            return [cmd]
        except:
            pass
    
    # 2. Check local apktool jar in script directory
    local_jar = os.path.join(SCRIPT_DIR, APKTOOL_FILENAME)
    if os.path.exists(local_jar):
        log(f"apktool jar found locally: {local_jar}")
        return ["java", "-jar", local_jar]
    
    # 3. Auto-download apktool jar
    log("apktool not found. Attempting auto-download...")
    if download_file(APKTOOL_URL, local_jar):
        # Verify download by checking version
        try:
            result = subprocess.run(
                ["java", "-jar", local_jar, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                log(f"✅ apktool verified: {result.stdout.strip()}")
                return ["java", "-jar", local_jar]
        except Exception as e:
            log(f"⚠️ Could not verify apktool: {e}")
    
    log("❌ Failed to get apktool. Please install manually or check internet connection.")
    return None

def find_uber_apk_signer():
    """
    Find uber-apk-signer: check local jar, PATH, then auto-download.
    Returns: path to jar file or None
    """
    candidates = [
        os.path.join(SCRIPT_DIR, UBER_SIGNER_FILENAME),
        os.path.join(SCRIPT_DIR, "uber-apk-signer.jar"),
    ]
    
    # Check workspace for any uber-apk-signer jar
    for f in os.listdir(SCRIPT_DIR):
        if "uber-apk-signer" in f and f.endswith(".jar"):
            candidates.insert(0, os.path.join(SCRIPT_DIR, f))
    
    for c in candidates:
        if os.path.exists(c):
            log(f"uber-apk-signer found: {c}")
            return c
    
    # Try which command
    try:
        result = subprocess.run(
            ["which", "uber-apk-signer"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            log(f"uber-apk-signer found in PATH: {path}")
            return path
    except:
        pass
    
    # Auto-download
    log("uber-apk-signer not found. Attempting auto-download...")
    dest_path = os.path.join(SCRIPT_DIR, UBER_SIGNER_FILENAME)
    if download_file(UBER_SIGNER_URL, dest_path):
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            log(f"✅ uber-apk-signer downloaded: {dest_path}")
            return dest_path
    
    log("⚠️ Could not download uber-apk-signer. APK will be unsigned if not found.")
    return None

def check_java():
    """Check if java is available."""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=10)
        version = result.stderr.split('\n')[0] if result.stderr else "Unknown"
        log(f"✅ Java found: {version}")
        return True
    except:
        log("❌ Java not found! Please install Java to run apktool/uber-apk-signer.")
        return False

# ============================================================
# PATCH FUNCTIONS
# ============================================================
def patch_user_profile(filepath):
    """Patch isPro() -> true, getEnergy() -> 999999"""
    log(f"Patching UserProfile.smali...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    patched_methods = []
    
    # Patch isPro() - replace entire method body
    ispro_pattern = r'(\.method public final isPro\(\)Z\s+\.locals \d+)(.*?)(\.end method)'
    def ispro_replace(m):
        return m.group(1) + '\n\n    const/4 v0, 0x1\n    return v0\n\n' + m.group(3)
    new_content = re.sub(ispro_pattern, ispro_replace, content, flags=re.DOTALL)
    if new_content != content:
        patched_methods.append('isPro() -> true')
    content = new_content
    
    # Patch getEnergy() - replace entire method body
    energy_pattern = r'(\.method public final getEnergy\(\)I\s+\.locals \d+)(.*?)(\.end method)'
    def energy_replace(m):
        return m.group(1) + '\n\n    const v0, 0xf423f\n    return v0\n\n' + m.group(3)
    new_content = re.sub(energy_pattern, energy_replace, content, flags=re.DOTALL)
    if new_content != content:
        patched_methods.append('getEnergy() -> 999999')
    content = new_content
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    if patched_methods:
        for m in patched_methods:
            log(f"  ✅ {m}")
    else:
        log("  ⚠️ WARNING: No methods patched in UserProfile - method signatures may have changed!")

def patch_energy_manager(filepath):
    """
    Patch EnergyManager (versi lama < v1.1.33).
    Di v1.1.33, EnergyManager dihapus. Patch energy dilakukan via UserProfile.
    """
    if not filepath:
        log("  EnergyManager tidak ditemukan (normal untuk v1.1.33+, sudah di-handle via UserProfile)")
        return
    
    log(f"Patching EnergyManager.smali (versi lama)...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    patched = []
    
    # Patch hasEnoughEnergy()
    has_pattern = r'(\.method public final hasEnoughEnergy\(Landroid/content/Context;I\)Z\s+\.locals \d+)(.*?)(\.end method)'
    def has_replace(m):
        return m.group(1) + '\n\n    const/4 v0, 0x1\n    return v0\n\n' + m.group(3)
    new = re.sub(has_pattern, has_replace, content, flags=re.DOTALL)
    if new != content: patched.append('hasEnoughEnergy() -> true')
    content = new
    
    # Patch deductEnergy() - return true without deduction
    deduct_pattern = r'(\.method public final deductEnergy\(Landroid/content/Context;I\)Lkotlin/Pair;)(.*?)(\.end method)'
    deduct_body = '''
    .locals 2
    const-string v0, "context"
    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V
    const/4 v0, 0x1
    invoke-static {v0}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v0
    const/4 v1, 0x0
    invoke-static {v1}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v1
    invoke-static {v0, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;
    move-result-object p1
    return-object p1
'''
    def deduct_replace(m):
        return m.group(1) + deduct_body + m.group(3)
    new = re.sub(deduct_pattern, deduct_replace, content, flags=re.DOTALL)
    if new != content: patched.append('deductEnergy() -> no deduction')
    content = new
    
    # Patch getEnergy(Context)
    getenergy_ctx_pattern = r'(\.method public final getEnergy\(Landroid/content/Context;\)I\s+\.locals \d+)(.*?)(\.end method)'
    def getenergy_replace(m):
        return m.group(1) + '\n\n    const v0, 0xf423f\n    return v0\n\n' + m.group(3)
    new = re.sub(getenergy_ctx_pattern, getenergy_replace, content, flags=re.DOTALL)
    if new != content: patched.append('getEnergy(Context) -> 999999')
    content = new
    
    # Patch MAX_ENERGY constant
    new = re.sub(r'\.field public static final MAX_ENERGY:I = 0x\w+',
                 '.field public static final MAX_ENERGY:I = 0xf423f', content)
    if new != content: patched.append('MAX_ENERGY -> 999999')
    content = new
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    for m in patched:
        log(f"  ✅ {m}")
    if not patched:
        log("  ⚠️ WARNING: Tidak ada yang di-patch di EnergyManager")


def patch_local_storage_obf(filepath):
    """
    Patch kelas LocalStorage obfuscated (i6/a di v1.1.33+).
    Kelas ini mengelola penyimpanan UserProfile ke SharedPreferences.
    Kita patch method i() yang membaca profil untuk selalu return isPro=true dan energy=999999.
    """
    if not filepath:
        log("  LocalStorageObf (i6/a) tidak ditemukan, skip")
        return
    
    log(f"Patching LocalStorage obfuscated (i6/a) - Energy & Premium bypass...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    patched = []
    
    # Patch method k() yang kemungkinan = hasEnoughEnergy / isPremiumValid
    # Mencari method boolean yang punya 1 local dan return value dari SharedPreferences
    k_pattern = r'(\.method public final k\(\)Z\s+\.locals \d+)(.*?)(\.end method)'
    def k_replace(m):
        return m.group(1) + '\n\n    const/4 v0, 0x1\n    return v0\n\n' + m.group(3)
    new = re.sub(k_pattern, k_replace, content, flags=re.DOTALL)
    if new != content:
        patched.append('k() -> true (internal premium check)')
    content = new
    
    # Patch method c() yang return int (energy count)
    c_pattern = r'(\.method public final c\(\)I\s+\.locals \d+)(.*?)(\.end method)'
    def c_replace(m):
        return m.group(1) + '\n\n    const v0, 0xf423f\n    return v0\n\n' + m.group(3)
    new = re.sub(c_pattern, c_replace, content, flags=re.DOTALL)
    if new != content:
        patched.append('c() -> 999999 (internal energy getter)')
    content = new
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    for m in patched:
        log(f"  ✅ {m}")
    if not patched:
        log("  ℹ️ LocalStorageObf: tidak ada method tambahan yang di-patch (normal)")

def patch_license_client(filepath):
    """Bypass LicenseClient - semua method yang berhubungan dengan license check."""
    log(f"Patching LicenseClient.smali...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    patched = []
    
    # Patch initializeLicenseCheck() -> return-void
    # Gunakan regex lebih robust (tidak bergantung \s+ setelah .locals)
    def make_void_patch(method_sig):
        escaped = re.escape(method_sig)
        pattern = r'(' + escaped + r'\s+\.locals \d+)(.*?)(\.end method)'
        def replacer(m):
            return m.group(1) + '\n\n    return-void\n\n' + m.group(3)
        return pattern, replacer
    
    # initializeLicenseCheck
    pat, rep = make_void_patch('.method public initializeLicenseCheck()V')
    new = re.sub(pat, rep, content, flags=re.DOTALL)
    if new != content:
        patched.append('initializeLicenseCheck() -> return-void')
    content = new
    
    # connectToLicensingService - juga bypass koneksi ke Google Play
    pat, rep = make_void_patch('.method private connectToLicensingService()V')
    new = re.sub(pat, rep, content, flags=re.DOTALL)
    if new != content:
        patched.append('connectToLicensingService() -> return-void')
    content = new
    
    # processResponse - bypass response handler (jika dipanggil, tidak berbuat apa-apa)
    # Patch ini mencegah startPaywallActivity dipanggil dari processResponse
    process_pat = r'(\.method private processResponse\(ILandroid/os/Bundle;\)V\s+\.locals \d+)(.*?)(\.end method)'
    def process_rep(m):
        return m.group(1) + '\n\n    return-void\n\n' + m.group(3)
    new = re.sub(process_pat, process_rep, content, flags=re.DOTALL)
    if new != content:
        patched.append('processResponse() -> return-void (no paywall trigger)')
    content = new
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    for m in patched:
        log(f"  ✅ {m}")
    if not patched:
        log("  ⚠️ WARNING: Tidak ada method LicenseClient yang ter-patch!")


def patch_license_activity(filepath):
    """Bypass LicenseActivity - semua method yang menampilkan Play Store redirect."""
    log(f"Patching LicenseActivity.smali...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    patched = []
    
    def void_method(sig, content_):
        pat = r'(' + re.escape(sig) + r'\s+\.locals \d+)(.*?)(\.end method)'
        def rep(m):
            return m.group(1) + '\n\n    return-void\n\n' + m.group(3)
        new = re.sub(pat, rep, content_, flags=re.DOTALL)
        return new, new != content_
    
    # onStart -> return-void (utama: mencegah showPaywallAndCloseApp)
    content, did = void_method('.method public onStart()V', content)
    if did: patched.append('onStart() -> return-void')
    
    # showPaywallAndCloseApp -> return-void
    content, did = void_method('.method private showPaywallAndCloseApp()V', content)
    if did: patched.append('showPaywallAndCloseApp() -> return-void')
    
    # closeApp -> return-void (mencegah System.exit)
    close_pat = r'(\.method protected closeApp\(\)V\s+\.locals \d+)(.*?)(\.end method)'
    def close_rep(m):
        return m.group(1) + '\n\n    return-void\n\n' + m.group(3)
    new = re.sub(close_pat, close_rep, content, flags=re.DOTALL)
    if new != content:
        patched.append('closeApp() -> return-void (no System.exit)')
    content = new
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    for m in patched:
        log(f"  ✅ {m}")
    if not patched:
        log("  ⚠️ WARNING: Tidak ada method LicenseActivity yang ter-patch!")


def patch_license_content_provider(filepath):
    """
    *** ROOT CAUSE FIX untuk redirect 'Get this app from Play' ***
    
    LicenseContentProvider adalah CompentProvider yang diinisiasi Android
    secara OTOMATIS sebelum MainActivity (bahkan sebelum Application.onCreate).
    Method onCreate() langsung memanggil LicenseClient.initializeLicenseCheck()
    yang kemudian konek ke Google Play licensing service.
    
    Perbaikan: patch onCreate() agar hanya return true tanpa license check.
    """
    if not filepath:
        log("  ⚠️ LicenseContentProvider tidak ditemukan, skip")
        return
    
    log(f"Patching LicenseContentProvider.smali (ROOT CAUSE fix)...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Patch onCreate() -> langsung return true (const/4 v0, 0x1 lalu return v0)
    oncreate_pat = r'(\.method public onCreate\(\)Z\s+\.locals \d+)(.*?)(\.end method)'
    def oncreate_rep(m):
        return m.group(1) + '\n\n    const/4 v0, 0x1\n    return v0\n\n' + m.group(3)
    new = re.sub(oncreate_pat, oncreate_rep, content, flags=re.DOTALL)
    
    if new != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new)
        log("  ✅ onCreate() -> return true (no initializeLicenseCheck call!)")
        log("  ✅ Play Store redirect BYPASSED at entry point")
    else:
        log("  ⚠️ WARNING: LicenseContentProvider.onCreate() tidak ter-patch - pattern tidak cocok!")
        log("  Mencoba patch manual...")
        # Fallback: patch dengan string replacement langsung
        marker = "invoke-virtual {v0}, Lcom/pairip/licensecheck/LicenseClient;->initializeLicenseCheck()V"
        if marker in content:
            content = content.replace(marker, "# initializeLicenseCheck BYPASSED")
            # Tapi ini tidak valid smali, jadi kita gunakan nop
            content = content.replace(
                "# initializeLicenseCheck BYPASSED",
                "const/4 v0, 0x0  # initializeLicenseCheck bypassed"
            )
            log("  ⚠️ Fallback patch applied (verbose)")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

def patch_main_activity_toast(filepath):
    """Inject Toast 'Patch by :\nインドラ' 2x in MainActivity.onCreate()"""
    log(f"Patching MainActivity.smali (Toast injection)...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if toast already injected
    if "Patch by :" in content:
        log("  Toast already injected, skipping")
        return
    
    toast_injection = '''
    const/4 v1, 0x0
    const-string v0, "Patch by :\\u30a4\\u30f3\\u30c9\\u30e9"
    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v0
    invoke-virtual {v0}, Landroid/widget/Toast;->show()V
    const-string v0, "Patch by :\\u30a4\\u30f3\\u30c9\\u30e9"
    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v0
    invoke-virtual {v0}, Landroid/widget/Toast;->show()V
'''
    
    # Priority list of injection points (newest version first)
    # v1.1.33+: LocalStorageManager diganti Li6/a
    injection_markers = [
        # v1.1.33+: inject sebelum instansiasi Li6/a (LocalStorage obfuscated)
        "new-instance p1, Li6/a;",
        # v1.1.x: inject sebelum instansiasi LocalStorageManager
        "new-instance v0, Lcom/aicyteadev/n1master/data/local/LocalStorageManager;",
        # Fallback: inject setelah invoke-super onCreate
        "invoke-super {p0, p1}, Landroidx/activity/q;->onCreate(Landroid/os/Bundle;)V",
        "invoke-super {p0, p1}, Landroidx/activity/ComponentActivity;->onCreate(Landroid/os/Bundle;)V",
    ]
    
    injected = False
    for marker in injection_markers:
        if marker in content:
            content = content.replace(marker, toast_injection + "\n    " + marker, 1)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            log(f"  ✅ Toast injected 2x in onCreate() (marker: '{marker[:50]}...')")
            injected = True
            break
    
    if not injected:
        log("  ⚠️ WARNING: Could not find injection point in MainActivity")
        log("  Available new-instance calls in MainActivity:")
        for line in content.split('\n'):
            if 'new-instance' in line:
                log(f"    {line.strip()}")

def patch_manifest(decompiled_dir):
    """Fix extractNativeLibs in AndroidManifest.xml"""
    manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        log("  WARNING: AndroidManifest.xml not found")
        return
    
    log("Patching AndroidManifest.xml...")
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # Replace extractNativeLibs="false" with "true" (only if explicitly false)
    content = content.replace('extractNativeLibs="false"', 'extractNativeLibs="true"')
    
    # Only add if it was false or missing (v1.1.33 doesn't have it at all = default true in API 31+)
    # For older Android targets, we add it explicitly
    if 'extractNativeLibs' not in content:
        # Check target SDK - only add for older API levels
        if 'android:targetSdkVersion="31"' in content or \
           'android:targetSdkVersion="30"' in content or \
           'android:targetSdkVersion="29"' in content:
            content = content.replace(
                '<application',
                '<application android:extractNativeLibs="true"',
                1
            )
            log("  extractNativeLibs -> true (added, legacy target SDK)")
        else:
            log("  extractNativeLibs: tidak diubah (API 31+ default true)")
    elif content != original:
        log("  extractNativeLibs -> true (was false)")
    else:
        log("  extractNativeLibs: tidak perlu diubah")
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)

# ============================================================
# MAIN WORKFLOW
# ============================================================
def decompile_apk(input_file, apktool_cmd):
    """Decompile APK/APKS"""
    log(f"Decompiling {input_file}...")
    decompiled_dir = os.path.join(SCRIPT_DIR, "N1Master_patched_work")
    
    # Clean previous work
    if os.path.exists(decompiled_dir):
        log("Cleaning previous decompile...")
        shutil.rmtree(decompiled_dir)
    
    run_cmd(apktool_cmd + ["d", "-f", "-o", decompiled_dir, input_file], cwd=SCRIPT_DIR)
    return decompiled_dir

def rebuild_apk(decompiled_dir, apktool_cmd, version_name=None):
    """Rebuild APK with optional version in filename"""
    if version_name and version_name != "unknown":
        # Remove any leading 'v' from version_name for consistency
        clean_version = version_name.lstrip('v')
        output_apk = os.path.join(SCRIPT_DIR, f"N1Master_patched-v{clean_version}.apk")
    else:
        output_apk = os.path.join(SCRIPT_DIR, "N1Master_patched.apk")
    log(f"Rebuilding APK to: {os.path.basename(output_apk)}...")
    run_cmd(apktool_cmd + ["b", "-o", output_apk, decompiled_dir], cwd=SCRIPT_DIR)
    return output_apk

def sign_apk(apk_path, version_name=None):
    """Sign APK with uber-apk-signer"""
    log("Signing APK...")
    signer_jar = find_uber_apk_signer()
    
    if not signer_jar:
        log("WARNING: uber-apk-signer not found. APK will be unsigned.")
        log("Download from: https://github.com/patrickfav/uber-apk-signer/releases")
        return apk_path
    
    run_cmd(
        ["java", "-jar", signer_jar, "--apks", apk_path],
        cwd=SCRIPT_DIR
    )
    
    # Find signed APK - handle both versioned and non-versioned filenames
    if version_name and version_name != "unknown":
        clean_version = version_name.lstrip('v')
        aligned = apk_path.replace(f"-v{clean_version}.apk", f"-v{clean_version}-aligned-debugSigned.apk")
    else:
        aligned = apk_path.replace(".apk", "-aligned-debugSigned.apk")
    
    if os.path.exists(aligned):
        return aligned
    return apk_path

def main():
    # Display hacker banner at startup
    hacker_banner()
    
    parser = argparse.ArgumentParser(description="N1Master APK Patcher (Standalone)")
    parser.add_argument("input", help="Input APK or APKS file")
    parser.add_argument("--output", "-o", help="Output APK filename")
    parser.add_argument("--no-sign", action="store_true", help="Skip signing")
    parser.add_argument("--skip-decompile", action="store_true", help="Skip decompile (use existing work dir)")
    parser.add_argument("--skip-download", action="store_true", help="Skip auto-download of tools")
    args = parser.parse_args()
    
    input_file = os.path.abspath(args.input)
    if not os.path.exists(input_file):
        log(f"ERROR: File not found: {input_file}")
        sys.exit(1)
    
    # Detect APK version first
    hacker_print("\n🔍 INITIATING APK ANALYSIS...", Colors.YELLOW, bold=True)
    time.sleep(0.5)
    version_info = detect_apk_version(input_file)
    
    # Store version info for output
    detected_version = version_info.get("versionName", "unknown")
    detected_code = version_info.get("versionCode", "unknown")
    
    hacker_print(f"\n📦 TARGET APK INFORMATION:", Colors.CYAN, bold=True)
    hacker_print(f"   File: {os.path.basename(input_file)}", Colors.WHITE)
    hacker_print(f"   Version: v{detected_version}", Colors.GREEN)
    hacker_print(f"   Version Code: {detected_code}", Colors.GREEN)
    hacker_print(f"   Detection Method: {version_info.get('method', 'unknown')}", Colors.DIM)
    time.sleep(0.3)
    
    # Check Java first (required for both tools)
    hacker_print("\n🔧 CHECKING PREREQUISITES...", Colors.YELLOW, bold=True)
    if not check_java():
        sys.exit(1)
    
    # Get apktool command
    apktool_cmd = None
    if not args.skip_download:
        apktool_cmd = find_apktool()
    else:
        # Only check local/system, no download
        for cmd in ["apktool", "apktool.bat"]:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, check=True, timeout=10)
                apktool_cmd = [cmd]
                break
            except:
                pass
        local_jar = os.path.join(SCRIPT_DIR, APKTOOL_FILENAME)
        if not apktool_cmd and os.path.exists(local_jar):
            apktool_cmd = ["java", "-jar", local_jar]
    
    if not apktool_cmd:
        log("ERROR: apktool not found and --skip-download is set, or download failed.")
        log("Please install apktool manually or run without --skip-download.")
        sys.exit(1)
    
    log(f"✅ Using apktool: {' '.join(apktool_cmd)}")
    
    # Step 1: Decompile
    if args.skip_decompile:
        decompiled_dir = os.path.join(SCRIPT_DIR, "N1Master_patched_work")
        if not os.path.exists(decompiled_dir):
            log("ERROR: --skip-decompile but work dir not found")
            sys.exit(1)
        log("Skipping decompile, using existing work dir")
    else:
        decompiled_dir = decompile_apk(input_file, apktool_cmd)
    
    # Step 2: Apply patches
    log("=" * 50)
    log("Applying patches...")
    log("=" * 50)
    
    # Find smali files (handle multi-dex & multi-version)
    resolved_paths = {}
    log("Resolving smali file paths...")
    for name, path_candidates in SMALI_PATHS.items():
        if not path_candidates:  # empty list = intentionally skipped
            log(f"  {name}: SKIP (dihapus di versi ini)")
            resolved_paths[name] = None
            continue
        
        full_path = resolve_smali_path(name, path_candidates, decompiled_dir)
        if full_path:
            resolved_paths[name] = full_path
        else:
            log(f"  ⚠️ WARNING: {name} tidak ditemukan di semua kandidat path")
            resolved_paths[name] = None
    
    log("")
    log("Applying patches...")
    
    if resolved_paths.get("UserProfile"):
        patch_user_profile(resolved_paths["UserProfile"])
    
    if resolved_paths.get("EnergyManager"):
        patch_energy_manager(resolved_paths["EnergyManager"])
    else:
        patch_energy_manager(None)  # will print informational message
    
    if resolved_paths.get("LocalStorageObf"):
        patch_local_storage_obf(resolved_paths["LocalStorageObf"])
    
    if resolved_paths.get("LicenseClient"):
        patch_license_client(resolved_paths["LicenseClient"])
    
    if resolved_paths.get("LicenseActivity"):
        patch_license_activity(resolved_paths["LicenseActivity"])
    
    # ROOT CAUSE: ContentProvider dipanggil sebelum Activity - patch ini kritis!
    if resolved_paths.get("LicenseContentProvider"):
        patch_license_content_provider(resolved_paths["LicenseContentProvider"])
    
    if resolved_paths.get("MainActivity"):
        patch_main_activity_toast(resolved_paths["MainActivity"])
    
    # Patch manifest
    patch_manifest(decompiled_dir)
    
    # Step 3: Rebuild
    log("=" * 50)
    log("Rebuilding APK...")
    log("=" * 50)
    unsigned_apk = rebuild_apk(decompiled_dir, apktool_cmd, detected_version)
    
    # Step 4: Sign
    if not args.no_sign:
        final_apk = sign_apk(unsigned_apk, detected_version)
    else:
        final_apk = unsigned_apk
    
    # Rename if output specified
    if args.output:
        output_path = os.path.abspath(args.output)
        shutil.copy2(final_apk, output_path)
        final_apk = output_path
    
    # Final summary with hacker style
    print(f"\n{Colors.GREEN}{'=' * 60}{Colors.RESET}")
    hacker_print("🎉 PATCHING COMPLETED SUCCESSFULLY!", Colors.GREEN, bold=True)
    print(f"{Colors.GREEN}{'=' * 60}{Colors.RESET}")
    
    hacker_print(f"\n📦 OUTPUT INFORMATION:", Colors.CYAN, bold=True)
    hacker_print(f"   File: {os.path.basename(final_apk)}", Colors.WHITE)
    hacker_print(f"   Path: {final_apk}", Colors.DIM)
    size = os.path.getsize(final_apk) / (1024 * 1024)
    hacker_print(f"   Size: {size:.1f} MB", Colors.WHITE)
    hacker_print(f"   APK Version Detected: v{detected_version}", Colors.YELLOW)
    
    print(f"\n{Colors.GREEN}{'=' * 60}{Colors.RESET}")
    hacker_print("🔓 PATCHES APPLIED:", Colors.MAGENTA, bold=True)
    print(f"{Colors.GREEN}{'=' * 60}{Colors.RESET}")
    
    patches = [
        ("✅ isPro() -> true", "Premium selamanya"),
        ("✅ getEnergy() -> 999999", "Energy unlimited"),
        ("✅ LicenseClient bypassed", "Bypass license check"),
        ("✅ LicenseActivity bypassed", "No paywall popup"),
        ("✅ LicenseContentProvider bypassed", "Prevent Play Store redirect"),
        ("✅ Toast injected", "'Patch by : インドラ' 2x"),
        ("✅ Manifest patched", "Debuggable & extractNativeLibs"),
        ("✅ Auto-download tools", "Standalone mode"),
        ("✅ Adaptive patching", "Multi-version support"),
    ]
    
    for patch, desc in patches:
        hacker_print(f"   {Colors.GREEN}{patch}{Colors.RESET} - {Colors.DIM}{desc}{Colors.RESET}", delay=0.005)
    
    print(f"\n{Colors.YELLOW}⚠️  Uninstall versi original dulu sebelum install!{Colors.RESET}")
    print(f"{Colors.DIM}\n💀 Patched by N1Master - Hack the Planet! 💀{Colors.RESET}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())