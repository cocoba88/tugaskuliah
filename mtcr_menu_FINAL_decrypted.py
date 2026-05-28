import os
import sys
import subprocess
import shutil
import secrets
import string
from pathlib import Path

# MTCR Apply Script
# Author / Credit: @issmali

JAR_NAME = "mtcr-apply.jar"


def clear_screen():
    os.system("clear")


def banner():
    print(r"""
███╗   ███╗████████╗ ██████╗██████╗ 
████╗ ████║╚══██╔══╝██╔════╝██╔══██╗
██╔████╔██║   ██║   ██║     ██████╔╝
██║╚██╔╝██║   ██║   ██║     ██╔══██╗
██║ ╚═╝ ██║   ██║   ╚██████╗██║  ██║
╚═╝     ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝

   MTCR APPLY TOOL (TERMUX)
--------------------------------
 Author : @issmali
 Version: 1.0
--------------------------------
""")


def exit_message(code=0):
    print("\n[*] Thanks for using MTCR Apply Tool")
    print("[*] Session ended")
    sys.exit(code)


def check_java():
    if shutil.which("java"):
        print("[+] Java detected")
        return True

    print("[!] Java not found")
    choice = input("[?] Install Java (openjdk-17)? [y/N]: ").lower()
    if choice != "y":
        print("[!] Java installation skipped")
        return False

    try:
        print("[*] Updating package repository...")
        subprocess.run(["pkg", "update", "-y"], check=True)

        print("[*] Installing openjdk-17...")
        subprocess.run(["pkg", "install", "-y", "openjdk-17"], check=True)

        print("[+] Java installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("[!] Failed to install Java")
        return False


def list_files(ext):
    return sorted([f.name for f in Path.cwd().glob(f"*{ext}")])


def pick_file(files, title):
    if not files:
        print(f"[!] No {title} files found")
        return None

    while True:
        print(f"\n[*] Select {title}:")
        for i, f in enumerate(files, 1):
            print(f" {i}) {f}")

        choice = input("[?] Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice) - 1]

        print("[!] Invalid selection, try again")


def auto_output_name():
    chars = string.ascii_lowercase + string.digits
    while True:
        rand = "".join(secrets.choice(chars) for _ in range(6))
        output = f"patched-{rand}.apk"
        if not Path(output).exists():
            return output


def run_cmd(cmd):
    print("\n[*] Executing command:")
    print("    " + " ".join(cmd))
    print()

    try:
        subprocess.run(cmd, check=True)
        print("[+] Operation completed successfully")
    except subprocess.CalledProcessError:
        print("[!] mtcr-apply execution failed")


def apply_patch(reverse=False):
    if not Path(JAR_NAME).exists():
        print(f"[!] {JAR_NAME} not found in current directory")
        return

    apk = pick_file(list_files(".apk"), "APK file")
    if not apk:
        return

    mtcr = pick_file(list_files(".mtcr"), "MTCR patch")
    if not mtcr:
        return

    output = input(
        "[?] Output APK name (leave empty for random name): "
    ).strip()

    if not output:
        output = auto_output_name()
        print(f"[*] Auto output name: {output}")

    cmd = ["java", "-jar", JAR_NAME]
    if reverse:
        cmd.append("-r")

    cmd += ["-i", apk, "-p", mtcr, "-o", output]

    run_cmd(cmd)


def menu():
    while True:
        clear_screen()
        banner()
        print("""
 1) Apply patch
 2) Reverse patch
 3) Exit
""")
        choice = input("[?] Select option: ").strip()

        if choice == "1":
            apply_patch(False)
        elif choice == "2":
            apply_patch(True)
        elif choice == "3":
            exit_message(0)
        else:
            print("[!] Invalid menu option")

        input("\n[*] Press Enter to return to menu...")


if __name__ == "__main__":
    try:
        clear_screen()
        banner()
        if not check_java():
            print("[!] Java is required to run this tool")
            exit_message(1)
        menu()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        exit_message(0)