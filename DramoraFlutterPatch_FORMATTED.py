#!/usr/bin/env python3
import ose3[yo)?ree3[yo)?syse3[yo)?timee3[yo)?shutile3[yo)?zipfilee3[yo)?tempfilee3[yo)?hashlibe3[yo)?itertoolse3[yo)?threadinge3[yo)?atexiterom pathlib import Patherom datetime import datetime
APP_VERSION = "v1.14.13"l.:GET_LIB = "libapp.so"j:CH = "ARM64-v8a"j::/OR = "PhoenixMods a.k.a 0xdeadc0de"kb:0UT_DIR = f"Dramora_{APP_VERSION}"
R = "\033[1;31m"k = "\033[1;32m"l]= "\033[1;33m"j?= "\033[1;34m"jI= "\033[1;36m"kI= "\033[1;35m"lI= "\033[1;37m"lS= "\033[0m"
ANIMATION_SPEED = {
    "typing": 0.008,
    "title": 0.008,
    "spinner": 0.12,
    "progress": 0.08,
    "patch_delay": 0.04,
    "step_delay": 0.5e3lATCHES = {
    "Enabled Premium (Force True)": {
        "patch": "C2820091",
        "offsets": [
            0x73D080, 0x465C88, 0x465C8C, 0x55B4D4, 0x55BEE4,
            0x55BFA8, 0x55BFAC, 0x69EA6C, 0x69EAB0, 0x69EAD8,
            0x69EB00, 0x69EB28, 0x73DF3C, 0x73DF54, 0x73E09C,
            0x73E0BC, 0x73E18C, 0x73E1AC, 0x73E2C0, 0x73E2E0,
            0x73E3B8, 0x73E3D8,
        ]
    },
    "Disabled Ads (Force False)": {
        "patch": "01000014",
        "offsets": [
            0x5727F8, 0x572CD4, 0x572E60, 0x574A00, 0x5750F8,
            0x5753F8, 0x692370, 0x692E3C, 0x693140, 0x693378,
            0x693478, 0x693570, 0x761FBC,
        ]
    }e3e=n[_dirs = []
def cleanup_temp_dirs():
    for temp_dir in temp_dirs:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            passeatexit.register(cleanup_temp_dirs)
def clear():
    os.system("cls" if os.name == "nt" else "clear")
def terminal_width():
    try:
        return shutil.get_terminal_size(fallback=(120, 30)).columns
    except Exception:
        return 120
def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
def visible_length(text):
    return len(strip_ansi(text))
def center_text(text):
    width = terminal_width()
    visible = visible_length(text)
    padding = max((width - visible) // 2, 0)
    return (" " * padding) + text
def gradient_text(text):
    colors = ["\033[38;5;51m", "\033[38;5;45m", "\033[38;5;39m", "\033[38;5;33m", "\033[38;5;63m"]
    result = ""
    for i, char in enumerate(text):
        result += colors[i % len(colors)] + char
    return result + X
def typing(text, speed=None, centered=True):
    speed = speed or ANIMATION_SPEED["typing"]
    if centered:
        text = center_text(text)
    for char in text:
        print(char, end="", flush=True)
        time.sleep(speed)
    print()
def animated_title(text, speed=None):
    speed = speed or ANIMATION_SPEED["title"]
    width = terminal_width()
    for i in range(len(text) + 1):
        raw_text = text[:i]
        current = gradient_text(raw_text)
        visible = len(raw_text)
        padding = max((width - visible) // 2, 0)
        sys.stdout.write("\r" + (" " * width))
        sys.stdout.write("\r" + (" " * padding) + current)
        sys.stdout.flush()
        time.sleep(speed)
    print("\n")
def cyberpunk_divider():
    line = f"{M}{'`]]* 6}{C}{'_4' * 58}{M}{'`]]* 6}{X}"
    print(center_text(line))
def glass_box(lines):
    visible_widths = [visible_length(x) for x in lines]
    width = max(visible_widths) + 6
    top = f"{C}_Q{'^H' * width}_R{X}"
    bottom = f"{C}_T{'^H' * width}_S{X}"
    print(center_text(top))
    for line in lines:
        visible = visible_length(line)
        padding = width - visible - 2
        content = f"{C}^J{X}  {line}{' ' * padding}{C}^J{X}"
        print(center_text(content))
    print(center_text(bottom))
def status_card(title, value, color=G):
    return f"{W}{title:<14}{X}: {color}{value}{X}"
def centered_status_card(title, value, color=G):
    text = f"{W}{title}{X}: {color}{value}{X}"
    return center_text(text)
def banner(package_path, output_dir):
    clear()
    cyberpunk_divider()
    print()
    animated_title("`H DRAMORA LIB PATCH `H")
    print(center_text(f"{Y}DRAMORA Advanced ARM64 Binary Patching Engine{X}"))
    print()
    cyberpunk_divider()
    print()
    
    status_lines = [
        centered_status_card("Version", APP_VERSION),
        centered_status_card("Target Lib", TARGET_LIB),
        centered_status_card("Architecture", ARCH),
        centered_status_card("Package", os.path.basename(package_path)),
        centered_status_card("Output Dir", output_dir),
        centered_status_card("Author", AUTHOR),
    ]
    
    for line in status_lines:
        print(line)
    
    print()
    cyberpunk_divider()
    print()
spinner_running = False
def spinner(text):
    global spinner_running
    spinner_running = True
    symbols = itertools.cycle(["f3", "fA", "fa", "f`", "g", "f\", "fN", "fO", "f/", "f7"])
    while spinner_running:
        sys.stdout.write(f"\r{center_text(f'{Y}[{next(symbols)}]{X} {text}')}    ")
        sys.stdout.flush()
        time.sleep(ANIMATION_SPEED["spinner"])
def start_spinner(text):
    thread = threading.Thread(target=spinner, args=(text,), daemon=True)
    thread.start()
    return thread
def stop_spinner():
    global spinner_running
    spinner_running = False
    time.sleep(0.2)
    sys.stdout.write("\r" + (" " * terminal_width()) + "\r")
    sys.stdout.flush()
def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)
def md5_file(path):
    md5 = hashlib.md5()
    with open(path, "rb") as file:
        while chunk := file.read(4096):
            md5.update(chunk)
    return md5.hexdigest()
def extract_package(package_path, extract_dir):
    try:
        with zipfile.ZipFile(package_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        return True
    except Exception as error:
        print(center_text(f"{R}[ERROR]{X} Extract failed"))
        print(center_text(str(error)))
        return False
def verify_arm64(lib_path):
    try:
        with open(lib_path, "rb") as file:
            elf = file.read(0x20)
        if elf[:4] != b"\x7fELF":
            return False
        return elf[4] == 2
    except Exception:
        return False
def find_arm64_lib(base_dir):
    arm64_keywords = ["arm64", "arm64_v8a", "arm64-v8a"]
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file != TARGET_LIB:
                continue
            full = os.path.join(root, file)
            lower = full.lower()
            if any(k in lower for k in arm64_keywords):
                if verify_arm64(full):
                    return full
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file != TARGET_LIB:
                continue
            full = os.path.join(root, file)
            try:
                if verify_arm64(full):
                    return full
            except Exception:
                pass
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            lower = file.lower()
            if not lower.endswith(".apk"):
                continue
            if not any(k in lower for k in arm64_keywords):
                continue
            split_apk = os.path.join(root, file)
            split_extract = os.path.join(root, f"split_extract_{abs(hash(file))}")
            os.makedirs(split_extract, exist_ok=True)
            try:
                with zipfile.ZipFile(split_apk, "r") as zip_ref:
                    zip_ref.extractall(split_extract)
            except Exception:
                continue
            for r, _, f in os.walk(split_extract):
                for x in f:
                    if x != TARGET_LIB:
                        continue
                    full = os.path.join(r, x)
                    try:
                        if verify_arm64(full):
                            return full
                    except Exception:
                        pass
    return None
def progress(current, total):
    percent = int((current / total) * 100)
    filled = int(percent / 4)
    bar = "`S+* filled
    empty = "`I+* (25 - filled)
    text = f"{C}[{bar}{empty}]{X} {G}{percent}%{X} {Y}({current}/{total}){X}"
    sys.stdout.write(f"\r{center_text(text)}")
    sys.stdout.flush()
def animate_step(message, duration=1.2):
    dots = ["   ", ".  ", ".. ", "..."]
    steps = 30
    for i in range(steps):
        idx = i % len(dots)
        text = f"{Y}e({X} {message}{dots[idx]}"
        sys.stdout.write(f"\r{center_text(text)}    ")
        sys.stdout.flush()
        time.sleep(duration / steps)
    sys.stdout.write("\r" + (" " * terminal_width()) + "\r")
    sys.stdout.flush()
def patch_offset(data, offset, patch_bytes):
    if offset >= len(data):
        return False
    old = data[offset:offset + len(patch_bytes)]
    if old == patch_bytes:
        return False
    data[offset:offset + len(patch_bytes)] = patch_bytes
    return True
def centered_print(text, color=""):
    if color:
        text = f"{color}{text}{X}"
    print(center_text(text))
def main():
    if len(sys.argv) < 2:
        script_name = os.path.basename(sys.argv[0])
        centered_print("\n[USAGE]", R)
        centered_print(f"python3 {script_name} file.apk")
        centered_print(f"python3 {script_name} file.apks")
        centered_print(f"python3 {script_name} file.xapk")
        centered_print(f"python3 {script_name} file.apkm\n")
        sys.exit(1)
    
    package_path = sys.argv[1]
    
    if not os.path.exists(package_path):
        centered_print("[ERROR] File not found", R)
        sys.exit(1)
    
    ext = Path(package_path).suffix.lower()
    supported = [".apk", ".apks", ".xapk", ".apkm"]
    
    if ext not in supported:
        centered_print("[ERROR] Unsupported format", R)
        sys.exit(1)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    banner(package_path, OUTPUT_DIR)
    
    temp_dir = tempfile.mkdtemp(prefix="dramora_")
    temp_dirs.append(temp_dir)
    
    animate_step("Extracting package", 1.5)
    start_spinner("Extracting files")
    success = extract_package(package_path, temp_dir)
    stop_spinner()
    
    if not success:
        sys.exit(1)
    
    centered_print("[OK] Package extracted", G)
    
    animate_step("Searching ARM64 library", 1.2)
    start_spinner("Scanning directories")
    lib_path = find_arm64_lib(temp_dir)
    stop_spinner()
    
    if not lib_path:
        centered_print("[ERROR] ARM64 libapp.so not found", R)
        sys.exit(1)
    
    centered_print("[FOUND] ARM64 library detected", G)
    
    animate_step("Verifying ELF header", 1.0)
    
    if not verify_arm64(lib_path):
        centered_print("[ERROR] Invalid ARM64 ELF", R)
        sys.exit(1)
    
    centered_print("[OK] ARM64 ELF verified", G)
    
    animate_step("Calculating MD5 hash", 1.0)
    centered_print(f"[MD5] {md5_file(lib_path)}", C)
    
    animate_step("Exporting original library", 0.8)
    original_output = os.path.join(OUTPUT_DIR, "libapp_original.so")
    shutil.copy2(lib_path, original_output)
    centered_print("[EXPORT] Original lib exported", G)
    
    animate_step("Loading library into memory", 0.8)
    
    with open(lib_path, "rb") as file:
        data = bytearray(file.read())
    
    total_offsets = sum(len(v["offsets"]) for v in PATCHES.values())
    current = 0
    patched = 0
    
    print()
    
    for module, info in PATCHES.items():
        cyberpunk_divider()
        centered_print(f"[ MODULE ] {module}", Y)
        cyberpunk_divider()
        print()
        
        patch_bytes = hex_to_bytes(info["patch"])
        module_total = len(info["offsets"])
        module_patched = 0
        
        start_spinner("Injecting binary patch")
        
        for offset in info["offsets"]:
            current += 1
            success = patch_offset(data, offset, patch_bytes)
            progress(current, total_offsets)
            if success:
                patched += 1
                module_patched += 1
            time.sleep(ANIMATION_SPEED["patch_delay"])
        
        stop_spinner()
        print()
        centered_print("[SUCCESS] Binary patch injected successfully", G)
        centered_print(f"[INFO] {module_patched}/{module_total} memory regions modified", C)
        print()
    
    patched_output = os.path.join(OUTPUT_DIR, "libapp_patched.so")
    
    animate_step("Saving patched library", 1.2)
    start_spinner("Writing to disk")
    
    with open(patched_output, "wb") as file:
        file.write(data)
    
    stop_spinner()
    centered_print("[OK] Patched lib saved", G)
    
    animate_step("Generating patch log", 0.8)
    
    log_path = os.path.join(OUTPUT_DIR, "patch_log.txt")
    
    with open(log_path, "w") as log:
        log.write("====================================\n")
        log.write("DRAMORA PATCH LOG\n")
        log.write("====================================\n")
        log.write(f"Version      : {APP_VERSION}\n")
        log.write(f"Architecture : {ARCH}\n")
        log.write(f"Patched      : {patched}\n")
        log.write(f"Package      : {package_path}\n")
        log.write(f"Output Dir   : {OUTPUT_DIR}\n")
        log.write(f"Date         : {dat
    time.now()}\n")
        log.write("====================================\n")
    
    centered_print("[OK] Log saved", G)
    
    animate_step("Cleaning temporary files", 1.0)
    print()
    cyberpunk_divider()
    print()
    
    success_text = "d!PATCH COMPLETED SUCCESSFULLY d!)    print(center_text(gradient_text(success_text)))
    print()
    
    final_status = [
        centered_status_card("Patched", f"{patched} Offsets"),
        centered_status_card("Original Lib", original_output),
        centered_status_card("Patched Lib", patched_output),
        centered_status_card("Patch Log", log_path),
        centered_status_card("Temp Cleaned", "Yes"),
        centered_status_card("Status", "SUCCESS", G),
    ]
    
    for line in final_status:
        print(line)
    
    print()
    cyberpunk_divider()
    print()
    
    typing("Process completed! Press Enter to exit...", 0.005)
    input()
if __name__ == "__main__":
    main()