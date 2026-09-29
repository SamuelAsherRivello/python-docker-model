from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent


def test_expected_repository_folders_exist():
    assert (REPOSITORY_ROOT / "documentation").is_dir()
    assert (REPOSITORY_ROOT / "openspec").is_dir()


def test_expected_project_folders_exist():
    assert (PROJECT_ROOT / ".streamlit").is_dir()
    assert (PROJECT_ROOT / "src").is_dir()
    assert (PROJECT_ROOT / "tests").is_dir()


def test_project_entrypoints_exist():
    assert (PROJECT_ROOT / "main.py").is_file()
    assert (PROJECT_ROOT / "requirements.txt").is_file()
    assert (PROJECT_ROOT / "run.bat").is_file()
    assert (PROJECT_ROOT / "setup.bat").is_file()
