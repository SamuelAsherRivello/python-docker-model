import json
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.llm.docker_llm import DockerLLM


class DockerLLMTests(unittest.TestCase):
    def test_model_list_uses_tags_instead_of_digests(self):
        payload = [
            {"id": "sha256:first", "tags": ["docker.io/ai/smollm2:latest"]},
            {"id": "sha256:second", "tags": ["docker.io/ai/qwen3.5:4b-q4_K_M"]},
        ]
        with patch("src.llm.docker_llm.subprocess.run", return_value=SimpleNamespace(stdout=json.dumps(payload))):
            models, error = DockerLLM().list_models()

        self.assertIsNone(error)
        self.assertEqual(models, ["ai/qwen3.5:4b-q4_K_M", "ai/smollm2"])

    def test_missing_docker_cli_returns_an_unavailable_result(self):
        with patch(
            "src.llm.docker_llm.subprocess.run",
            side_effect=FileNotFoundError("docker"),
        ):
            models, error = DockerLLM().list_models()

        self.assertEqual(models, [])
        self.assertIn("Docker CLI was not found", error or "")

    def test_failed_model_discovery_returns_an_unavailable_result(self):
        failure = subprocess.CalledProcessError(
            1,
            ["docker", "model", "list", "--json"],
            stderr="runner unavailable",
        )
        with patch(
            "src.llm.docker_llm.subprocess.run",
            side_effect=failure,
        ):
            models, error = DockerLLM().list_models()

        self.assertEqual(models, [])
        self.assertIn("runner unavailable", error or "")

    def test_timed_out_model_discovery_returns_an_unavailable_result(self):
        timeout = subprocess.TimeoutExpired(
            ["docker", "model", "list", "--json"],
            timeout=15,
        )
        with patch(
            "src.llm.docker_llm.subprocess.run",
            side_effect=timeout,
        ):
            models, error = DockerLLM().list_models()

        self.assertEqual(models, [])
        self.assertIn("Could not run", error or "")

    def test_malformed_model_json_returns_an_unavailable_result(self):
        with patch(
            "src.llm.docker_llm.subprocess.run",
            return_value=SimpleNamespace(stdout="not-json"),
        ):
            models, error = DockerLLM().list_models()

        self.assertEqual(models, [])
        self.assertIn("Could not run", error or "")

    def test_empty_model_list_is_not_an_adapter_error(self):
        with patch(
            "src.llm.docker_llm.subprocess.run",
            return_value=SimpleNamespace(stdout="[]"),
        ):
            models, error = DockerLLM().list_models()

        self.assertEqual(models, [])
        self.assertIsNone(error)
