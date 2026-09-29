# Repository guidance

## Project boundaries

- Treat the repository root as the home for documentation, OpenSpec artifacts, GitHub automation, and agent guidance.
- Treat `Python/` as the buildable and testable application root.
- Run Python, Streamlit, and test commands from `Python/` unless a command explicitly targets repository metadata.
- Keep OpenSpec under `openspec/` at the repository root and use `Python/`-prefixed source paths in new artifacts.

## Development

- Use the project-local interpreter at `Python/.venv/Scripts/python.exe` when available.
- Run tests with `Python/.venv/Scripts/python.exe -m unittest discover -s Python/tests -p "test*.py"` from the repository root, or the equivalent command from `Python/`.
- Preserve the workflow step message contract: `IsError: bool` and `Message: str`.
- Do not introduce an LLM call into workflows that omit `llm-prompt-step`.
- Keep model and workflow changes resetting the current run.

## Repository operations

- Do not commit, push, publish, or create a remote unless the user explicitly requests it.
- Do not add generated environments, caches, runtime logs, or Streamlit secrets to Git.
