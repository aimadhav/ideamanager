import winreg
import os
import sys
from pathlib import Path

def add_to_startup():
    # Path to the run.bat in the root directory
    base_dir = Path(__file__).resolve().parent.parent
    bat_path = base_dir / "run.bat"
    
    if not bat_path.exists():
        print(f"Error: {bat_path} not found.")
        return

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        # Open the registry key
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        # Set the value (name, reserved, type, value)
        winreg.SetValueEx(key, "Ideamanager", 0, winreg.REG_SZ, f'"{str(bat_path)}"')
        winreg.CloseKey(key)
        print("Success: Ideamanager has been added to Windows Startup (Registry).")
        print("It will now start automatically when you log in.")
    except Exception as e:
        print(f"Failed to add to startup: {e}")

if __name__ == "__main__":
    add_to_startup()
