import argparse
import subprocess
import sys
from pathlib import Path

# --- Part A ---
def run_command(cmd: list[str], cwd: Path) -> int:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode

def setup():
    """Install requirements"""
    print("Setting up environment...")
    cmd = [sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"]
    sys.exit(run_command(cmd, Path(".")))

def test():
    """Run tests with coverage"""
    print("Running tests...")
    cmd = [sys.executable, "-m", "pytest", "backend/tests/", "-v", "--cov=backend/app", "--cov-report=term"]
    sys.exit(run_command(cmd, Path(".")))

def run():
    """Run the application"""
    print("Running application...")
    cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
    sys.exit(run_command(cmd, Path(".")))

def eval():
    """Run evaluation script (Part A)"""
    print("Running evaluation...")
    # To be implemented in A-M6
    print("Evaluation not yet implemented.")
    sys.exit(0)

def verify():
    """Run all verifications"""
    print("Running verification...")
    # To be implemented
    sys.exit(0)

# --- Part B ---
# Part B can add frontend setup tasks etc.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task runner")
    parser.add_argument("task", choices=["setup", "test", "run", "eval", "verify"], help="Task to run")
    args = parser.parse_args()

    tasks = {
        "setup": setup,
        "test": test,
        "run": run,
        "eval": eval,
        "verify": verify,
    }
    tasks[args.task]()
