"""Central settings for QuestMaster.

Everything configurable lives here so other modules never hard-code values.
Reads optional values from a .env file; every setting has a safe default so
the project runs with no configuration at all.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Game window / grid (used from Phase 1) ---
GRID_ROWS = 20
GRID_COLS = 20
CELL_SIZE = 32
FPS = 30

# --- Reproducibility ---
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# --- Optional LLM features (used from Phase 3) ---
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def llm_available() -> bool:
    """True only if the user enabled LLM mode AND provided some way to reach a model."""
    return USE_LLM and bool(OPENAI_API_KEY or ANTHROPIC_API_KEY or OLLAMA_BASE_URL)
