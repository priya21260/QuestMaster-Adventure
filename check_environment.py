"""Checks that your computer is ready to run QuestMaster.

Run:  python check_environment.py
It only reports; it never installs or changes anything.
"""
import importlib
import shutil
import sys

# (import name, pip name, needed from which phase, required for basic mode?)
PACKAGES = [
    ("pygame", "pygame", "Phase 1 (game window)", True),
    ("networkx", "networkx", "Phase 1 (graphs)", True),
    ("numpy", "numpy", "Phase 1", True),
    ("matplotlib", "matplotlib", "Phase 1 (charts)", True),
    ("pandas", "pandas", "Phase 1 (tables)", True),
    ("dotenv", "python-dotenv", "Phase 0 (settings)", False),
    ("pytest", "pytest", "Testing", True),
    ("pyswip", "pyswip", "Phase 2 (Prolog bridge)", False),
    ("langchain", "langchain", "Phase 3 (RAG)", False),
    ("langgraph", "langgraph", "Phase 4 (main workflow)", False),
    ("autogen", "pyautogen", "Phase 4 (AutoGen)", False),
    ("crewai", "crewai", "Phase 4 (CrewAI)", False),
    ("streamlit", "streamlit", "Dashboard (optional)", False),
]


def main() -> int:
    print("QuestMaster environment check")
    print("=" * 40)
    ok_python = sys.version_info >= (3, 10)
    print(f"Python {sys.version.split()[0]}: {'OK' if ok_python else 'TOO OLD (need 3.10+)'}")

    missing_required = []
    for module, pip_name, phase, required in PACKAGES:
        try:
            importlib.import_module(module)
            print(f"  [OK]      {module}")
        except ImportError:
            tag = "MISSING " if required else "optional"
            print(f"  [{tag}] {module:<10} -> pip install {pip_name}   ({phase})")
            if required:
                missing_required.append(pip_name)

    swipl = shutil.which("swipl")
    print(f"  [{'OK' if swipl else 'optional'}] SWI-Prolog program: "
          f"{swipl or 'not found (a Python fallback reasoner will be used)'}")

    print("=" * 40)
    if missing_required:
        print("Missing required packages. Fix with:\n  pip install -r requirements.txt")
        return 1
    print("All required packages for the basic mode are installed.")
    return 0 if ok_python else 1


if __name__ == "__main__":
    sys.exit(main())
