import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from src.Workflows.workflow import (
    IStep,
    LlmPromptStep,
    OutputStep,
    QueryStep,
    WorkflowConfigurationError,
    WorkflowRunner,
    build_steps,
    load_workflows,
)


class WorkflowTests(unittest.TestCase):
    def test_default_workflows_load_from_project_checkout(self):
        workflows = load_workflows()

        self.assertEqual(
            workflows,
            {
                "Workflow 1": ["query-step", "output-step"],
                "Workflow 2": ["query-step", "llm-prompt-step", "output-step"],
            },
        )

    def test_loader_rejects_unknown_step_type(self):
        with TemporaryDirectory() as directory:
            config = Path(directory) / "workflow.json"
            config.write_text(
                json.dumps({"workflows": {"Broken": ["query-step", "missing-step"]}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(WorkflowConfigurationError, "missing-step"):
                load_workflows(config)

    def test_factory_builds_steps_in_configured_order(self):
        llm = Mock()

        steps = build_steps(
            ["query-step", "llm-prompt-step", "output-step"],
            model="ai/test",
            llm=llm,
        )

        self.assertEqual([type(step) for step in steps], [QueryStep, LlmPromptStep, OutputStep])
        self.assertIs(steps[1].llm, llm)

    def test_query_step_returns_success_and_validation_error(self):
        runner = WorkflowRunner([QueryStep()])

        self.assertEqual(
            runner.process_step_sync(0, {"IsError": False, "Message": "  hello  "}),
            {"IsError": False, "Message": "hello"},
        )
        self.assertEqual(
            runner.process_step_sync(0, {"IsError": False, "Message": "   "}),
            {"IsError": True, "Message": "Enter a query first."},
        )

    def test_llm_step_calls_model_and_returns_response(self):
        llm = Mock()
        llm.call.return_value = ("model answer", None)
        runner = WorkflowRunner([LlmPromptStep("ai/test", llm=llm)])

        result = runner.process_step_sync(0, {"IsError": False, "Message": "hello"})

        self.assertEqual(result, {"IsError": False, "Message": "model answer"})
        llm.call.assert_called_once_with("ai/test", "hello")

    def test_error_propagates_without_calling_model(self):
        llm = Mock()
        runner = WorkflowRunner([LlmPromptStep("ai/test", llm=llm), OutputStep()])
        error = {"IsError": True, "Message": "query failed"}

        messages = runner.process_all_sync(error)

        self.assertEqual(messages, [error, error])
        llm.call.assert_not_called()

    def test_model_error_is_preserved_by_output_step(self):
        llm = Mock()
        llm.call.return_value = (None, "runner unavailable")
        runner = WorkflowRunner([LlmPromptStep("ai/test", llm=llm), OutputStep()])

        messages = runner.process_all_sync({"IsError": False, "Message": "hello"})

        self.assertEqual(
            messages[-1],
            {
                "IsError": True,
                "Message": "The model request failed: runner unavailable",
            },
        )

    def test_runner_processes_each_step_once(self):
        calls: list[str] = []

        class CountingStep(IStep):
            step_type = "counting-step"
            label = "Counting"

            def __init__(self, name: str) -> None:
                self.name = name

            async def process(self, input):
                calls.append(self.name)
                return input

        runner = WorkflowRunner([CountingStep("first"), CountingStep("second")])

        runner.process_all_sync({"IsError": False, "Message": "hello"})

        self.assertEqual(calls, ["first", "second"])


if __name__ == "__main__":
    unittest.main()
