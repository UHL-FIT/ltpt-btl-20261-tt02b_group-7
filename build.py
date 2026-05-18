"""
build.py
========
Script dong goi ung dung thanh file .exe cho Windows bang PyInstaller.

Cach dung:
    python build.py

Ket qua:
    dist/QuanLyDiem/QuanLyDiem.exe   (thu muc chua exe + data)
"""

import subprocess
import sys
import os
import shutil

# --- CAU HINH ---
TEN_APP = "SmartAttend"
FILE_MAIN = "main.py"
THU_MUC_DATA = "data"
THU_MUC_ASSETS = "assets"
ICON_FILE = r"assets\app_icon.ico"


def kiem_tra_pyinstaller():
    """Kiem tra PyInstaller da cai chua, neu chua thi cai."""
    try:
        import PyInstaller
        print(f"  [OK] PyInstaller {PyInstaller.__version__} da cai san")
    except ImportError:
        print("  [..] Dang cai dat PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("  [OK] Da cai dat PyInstaller")


def xoa_build_cu():
    """Xoa thu muc build cu."""
    for folder in ["build", "dist", f"{TEN_APP}.spec"]:
        if os.path.exists(folder):
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            else:
                os.remove(folder)
            print(f"  [DEL] Da xoa: {folder}")


def tao_installer():
    """Goi Inno Setup Compiler de tao file Setup_QuanLyDiem.exe"""
    print("\n  [4/4] Dang tao file cai dat (Installer)...")
    iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if not os.path.exists(iscc_path):
        print(f"  [WARN] Khong tim thay Inno Setup tai {iscc_path}")
        print("  [WARN] Vui long cai dat Inno Setup 6 de tao file install.")
        return False
        
    iss_file = "installer.iss"
    if not os.path.exists(iss_file):
        print(f"  [FAIL] Khong tim thay file cau hinh {iss_file}")
        return False
        
    cmd = [iscc_path, iss_file]
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("  [OK] TAO INSTALLER THANH CONG!")
        print(f"  File cai dat: dist\\Setup_{TEN_APP}.exe")
        print("=" * 50)
        return True
    else:
        print("\n  [FAIL] Tao installer that bai!")
        return False


def build():
    """Chay PyInstaller de dong goi."""
    print("\n" + "=" * 50)
    print("  DONG GOI UNG DUNG QUAN LY DIEM SINH VIEN")
    print("=" * 50)

    # 1. Kiem tra PyInstaller
    kiem_tra_pyinstaller()

    # 2. Xoa build cu
    print("\n  [1/4] Don dep build cu...")
    xoa_build_cu()

    # 3. Chay PyInstaller cho GUI
    print(f"\n  [2/4] Dang dong goi {FILE_MAIN} -> {TEN_APP}.exe (GUI mode)...")

    cmd_gui = [
        sys.executable, "-m", "PyInstaller",
        "--name", TEN_APP,
        "--noconfirm",          # Khong hoi ghi de
        "--windowed",           # An cua so Terminal (GUI mode)
        "--clean",              # Xoa cache cu
        # Them thu muc data vao bundle
        "--add-data", f"{THU_MUC_DATA};{THU_MUC_DATA}",
        "--add-data", f"{THU_MUC_ASSETS};{THU_MUC_ASSETS}",
        # Hidden imports cho pandas/numpy
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
    ]

    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd_gui.extend(["--icon", ICON_FILE])

    cmd_gui.append(FILE_MAIN)

    result = subprocess.run(cmd_gui, capture_output=False)

    if result.returncode != 0:
        print("\n  [FAIL] Build GUI that bai! Xem loi o tren.")
        return False

    # 4. Chay PyInstaller cho CLI
    print(f"\n  [3/4] Dang dong goi main_cli.py -> {TEN_APP}_CLI.exe (Console mode)...")
    
    cmd_cli = [
        sys.executable, "-m", "PyInstaller",
        "--name", f"{TEN_APP}_CLI",
        "--noconfirm",          # Khong hoi ghi de
        "--console",            # Hien cua so Terminal
        "--clean",              # Xoa cache cu
        # Them thu muc data vao bundle
        "--add-data", f"{THU_MUC_DATA};{THU_MUC_DATA}",
        "--add-data", f"{THU_MUC_ASSETS};{THU_MUC_ASSETS}",
        # Hidden imports cho pandas/numpy
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
    ]

    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd_cli.extend(["--icon", ICON_FILE])

    cmd_cli.append("main_cli.py")

    result_cli = subprocess.run(cmd_cli, capture_output=False)

    if result_cli.returncode != 0:
        print("\n  [FAIL] Build CLI that bai! Xem loi o tren.")
        return False

    # 5. Kiem tra ket qua va copy data
    print(f"\n  [4/4] Kiem tra ket qua...")
    exe_path = os.path.join("dist", TEN_APP, f"{TEN_APP}.exe")
    if os.path.exists(exe_path):
        # Copy thu muc data ra canh exe de doc/ghi CSV
        dest_data = os.path.join("dist", TEN_APP, "data")
        if os.path.exists(dest_data):
            shutil.rmtree(dest_data)
        shutil.copytree(THU_MUC_DATA, dest_data)
        print(f"  [OK] Da copy data/ -> dist/{TEN_APP}/data/")

        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n" + "=" * 50)
        print("  [OK] BUILD THANH CONG!")
        print(f"  File: {os.path.abspath(exe_path)}")
        print(f"  Size: {size_mb:.1f} MB")
        print("=" * 50)
        
        # Tao installer
        tao_installer()
        return True
    else:
        print("\n  [FAIL] Khong tim thay file exe sau khi build!")
        return False


if __name__ == "__main__":
    build()
