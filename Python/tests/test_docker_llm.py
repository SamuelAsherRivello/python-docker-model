import json
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
