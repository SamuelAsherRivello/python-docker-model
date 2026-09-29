"""Docker Model Runner implementation of the LLM interface."""

import json
import subprocess
from typing import Any

from src.llm.illm import ILLM


class DockerLLM(ILLM):
    """Stateless LLM provider backed by Docker Model Runner CLI commands."""

    def list_models(self) -> tuple[list[str], str | None]:
        try:
            result = subprocess.run(
                ["docker", "model", "list", "--json"],
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
            payload: Any = json.loads(result.stdout)
            rows = payload.get("models", payload) if isinstance(payload, dict) else payload
            models = {
                tag
                for row in rows if isinstance(row, dict)
                for tag in _model_references(row)
            }
            return sorted(models), None
        except FileNotFoundError:
            return [], "Docker CLI was not found. Install Docker Desktop and ensure `docker` is on PATH."
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            detail = getattr(exc, "stderr", "") or str(exc)
            return [], f"Could not run `docker model list --json`: {detail.strip()}"

    def call(self, model: str, prompt: str) -> tuple[str | None, str | None]:
        try:
            result = subprocess.run(
                ["docker", "model", "run", model, prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=300,
            )
            return result.stdout.strip(), None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
            detail = getattr(exc, "stderr", "") or str(exc)
            return None, detail.strip() or str(exc)


def _model_references(row: dict[str, Any]) -> list[str]:
    """Docker's ID is a digest; its tags are runnable model names."""
    normalized = {str(key).lower(): value for key, value in row.items()}
    tags = normalized.get("tags")
    if isinstance(tags, list):
        return [_short_reference(tag) for tag in tags if isinstance(tag, str) and tag and not tag.startswith("sha256:")]
    for key in ("name", "model", "model_name", "reference", "repository", "repo"):
        value = normalized.get(key)
        if isinstance(value, str) and value and not value.startswith("sha256:"):
            return [_short_reference(value)]
    return []


def _short_reference(reference: str) -> str:
    if reference.startswith("docker.io/"):
        reference = reference[len("docker.io/"):]
    if reference.endswith(":latest"):
        reference = reference[:-len(":latest")]
    return reference
