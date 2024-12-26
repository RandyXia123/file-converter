import sys
import subprocess

def install_package():
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "pdfplumber"
        ])
        print("Successfully installed pdfplumber")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_package()