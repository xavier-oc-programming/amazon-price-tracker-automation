import os
import sys
import subprocess
from pathlib import Path
from art import LOGO

ROOT = Path(__file__).parent

clear = True
while True:
    if clear:
        os.system("cls" if os.name == "nt" else "clear")
    clear = True

    print(LOGO)
    print("1. Original build  (course version)")
    print("2. Advanced build  (OOP, config.py, modular)")
    print("3. Schedule daily check  (install cron job)")
    print("q. Quit")
    print()

    choice = input("Select an option: ").strip().lower()

    if choice == "1":
        path = ROOT / "original" / "main.py"
        subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        input("\nPress Enter to return to menu...")
    elif choice == "2":
        path = ROOT / "advanced" / "main.py"
        subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        input("\nPress Enter to return to menu...")
    elif choice == "3":
        subprocess.run(["bash", str(ROOT / "setup_cron.sh")], cwd=str(ROOT))
        input("\nPress Enter to return to menu...")
    elif choice == "q":
        break
    else:
        print("Invalid choice. Try again.")
        clear = False
