"""Phase 0 smoke tests: the skeleton is in place and settings load."""
from pathlib import Path

from config import settings

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_FOLDERS = [
    "config", "assets", "game", "algorithms", "reasoning", "knowledge_base",
    "agents", "frameworks", "learning", "evaluation", "ethics", "dashboard",
    "tests", "docs",
]
EXPECTED_FILES = [
    "README.md", "PROJECT_PROGRESS.md", "requirements.txt",
    ".gitignore", ".env.example", "main.py",
]


def test_folders_exist():
    for name in EXPECTED_FOLDERS:
        assert (ROOT / name).is_dir(), f"missing folder: {name}"


def test_files_exist():
    for name in EXPECTED_FILES:
        assert (ROOT / name).is_file(), f"missing file: {name}"


def test_settings_defaults():
    assert settings.GRID_ROWS > 0 and settings.GRID_COLS > 0
    assert settings.RANDOM_SEED == 42


def test_basic_mode_needs_no_api_key():
    # With no .env configured, LLM mode must be off so the project works offline.
    assert settings.llm_available() is False
