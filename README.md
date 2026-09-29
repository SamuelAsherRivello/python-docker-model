# Python Docker Model

Python Docker Model is a Streamlit application for running configurable query workflows against local models exposed by Docker Model Runner. Workflows can pass input directly to output or send it through a selected model while the interface presents each stage as a numbered status card.

## Images

### Screenshots

<a href="documentation/layout-qa.png"><img src="documentation/layout-qa.png" width="400" alt="Python Docker Model Streamlit interface" /></a>

## Live Demo

- Hosted demo: [Open Python Docker Model on Streamlit Community Cloud](https://samuelasherrivello-python-docker-model-pythonmain-bk0iq4.streamlit.app/).
- Hosted model inference is unavailable because Streamlit Community Cloud cannot access Docker Model Runner. Run the project locally with Docker Desktop and Docker Model Runner to use model-backed workflows.
- Local development server: [http://localhost:8501](http://localhost:8501) after following the setup and run instructions below.

## Table of Contents

1. [Images](#images)
2. [Live Demo](#live-demo)
3. [Getting Started](#getting-started)
4. [Project Details](#project-details)
5. [Credits](#credits)

## Getting Started

The application requires Windows, Python 3.10 or newer, Docker Desktop with Docker Model Runner enabled, and at least one locally available model. Repository-level guidance and specifications stay at the root; all buildable application files live in `Python/`.

### 🛠 Build Project

1. From the repository root, pull or confirm a Docker model:
   ```powershell
   docker model pull ai/smollm2
   docker model list
   ```
2. Change to the buildable project root with `cd Python`.
3. Run `.\setup.bat` to create or update `Python/.venv` and install the required packages.

### 🛠 Run Project

1. From `Python/`, run `.\run.bat`.
2. Open [http://localhost:8501](http://localhost:8501).
3. Run `.\run.bat` again at any time to reuse the existing listener. The launcher runs Streamlit in the background without leaving a persistent command window and writes logs to `Python/.run/`.
4. To run in the foreground instead, use `.\.venv\Scripts\python.exe -m streamlit run main.py` from `Python/`.

### 🛠 Release Version

1. From `Python/`, run `.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`.
2. Create an annotated version tag with `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push the tag with `git push origin vX.Y.Z`, then create the corresponding GitHub release.

## Project Details

Workflows are declared in `Python/src/Workflows/workflow.json`. Workflow 1 passes the query directly to output, while Workflow 2 sends the query through the selected Docker model first. Changing the model or workflow resets the current run.

### 📝 Structure

- `Python/main.py` provides the Streamlit entry point.
- `Python/src/Workflows/` contains workflow configuration, loading, and step implementations.
- `Python/src/ui/` contains the application shell and workflow step-card interface.
- `Python/src/llm/` contains the Docker Model Runner adapter.
- `Python/tests/` contains the automated test suite.
- `documentation/` contains README images and supporting project documentation.

### 📦 AI

- `AGENTS.md` contains repository-specific AI agent guidance.
- `.codex/project-identity.md` records the repository and buildable project boundaries.
- [openspec](openspec/) contains the repository's specification workflow configuration and change artifacts.
- `.agents/skills/` contains project-local OpenSpec skills.

### 📦 Packages

- [Streamlit](https://streamlit.io/) provides the application interface and session state.
- [Docker Model Runner](https://docs.docker.com/ai/model-runner/) provides local model discovery and inference through the Docker CLI.
- Python's built-in `unittest` framework provides the automated test runner.

## Credits

### 💡 Contributors

- Samuel Asher Rivello - Over 25 years of game development XP (2026)

### 💡 Contact

- [LinkedIn.com/in/SamuelAsherRivello](https://Linkedin.com/in/SamuelAsherRivello) ⭐
- [GitHub.com/SamuelAsherRivello](https://github.com/SamuelAsherRivello/)
- [Twitter.com/srivello](https://twitter.com/srivello/)
- Resume / Portfolio: [SamuelAsherRivello.com](http://www.SamuelAsherRivello.com)

### 💡 License

- Provided as-is under the [MIT License](LICENSE).
- Copyright © 2026 Samuel Asher Rivello.
