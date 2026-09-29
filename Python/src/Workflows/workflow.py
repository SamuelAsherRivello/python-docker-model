"""Workflow loading, step contracts, implementations, and execution helpers."""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Mapping, Sequence
from pathlib import Path
from typing import TypeVar, TypedDict

from src.llm.docker_llm import DockerLLM
from src.llm.illm import ILLM


class StepMessage(TypedDict):
    """Shared message structure passed between every workflow step."""

    IsError: bool
    Message: str


class WorkflowConfigurationError(ValueError):
    """Raised when a workflow configuration cannot be loaded safely."""


class IStep(ABC):
    """Contract implemented by every workflow step."""

    step_type: str
    label: str

    @abstractmethod
    async def process(self, input: StepMessage) -> StepMessage:
        """Process and return the shared workflow message."""


class QueryStep(IStep):
    step_type = "query-step"
    label = "Query"

    async def process(self, input: StepMessage) -> StepMessage:
        message = _normalize_message(input)
        if message["IsError"]:
            return message

        query = message["Message"].strip()
        if not query:
            return {"IsError": True, "Message": "Enter a query first."}
        return {"IsError": False, "Message": query}


class LlmPromptStep(IStep):
    step_type = "llm-prompt-step"
    label = "LLM prompt"

    def __init__(self, model: str, llm: ILLM | None = None) -> None:
        self.model = model
        self.llm = llm or DockerLLM()

    async def process(self, input: StepMessage) -> StepMessage:
        message = _normalize_message(input)
        if message["IsError"]:
            return message

        answer, error = self.llm.call(self.model, message["Message"])
        if error:
            return {"IsError": True, "Message": f"The model request failed: {error}"}
        if answer is None:
            return {"IsError": True, "Message": "The model returned no response."}
        return {"IsError": False, "Message": answer}


class OutputStep(IStep):
    step_type = "output-step"
    label = "Output"

    async def process(self, input: StepMessage) -> StepMessage:
        return _normalize_message(input)


SUPPORTED_STEP_TYPES = frozenset(
    {QueryStep.step_type, LlmPromptStep.step_type, OutputStep.step_type}
)


def load_workflows(config_path: str | Path | None = None) -> dict[str, list[str]]:
    """Load and validate named workflow definitions from JSON."""
    path = Path(config_path) if config_path else Path(__file__).with_name("workflow.json")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowConfigurationError(f"Workflow configuration was not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowConfigurationError(
            f"Workflow configuration is not valid JSON: {exc.msg}"
        ) from exc

    workflows = payload.get("workflows") if isinstance(payload, Mapping) else None
    if not isinstance(workflows, Mapping) or not workflows:
        raise WorkflowConfigurationError(
            "Workflow configuration must contain a non-empty 'workflows' object."
        )

    validated: dict[str, list[str]] = {}
    for raw_name, raw_steps in workflows.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise WorkflowConfigurationError("Workflow names must be non-empty strings.")
        if not isinstance(raw_steps, list) or not raw_steps:
            raise WorkflowConfigurationError(
                f"Workflow '{raw_name}' must contain a non-empty list of steps."
            )
        if not all(isinstance(step_type, str) for step_type in raw_steps):
            raise WorkflowConfigurationError(
                f"Workflow '{raw_name}' contains a non-string step type."
            )

        unknown = [step_type for step_type in raw_steps if step_type not in SUPPORTED_STEP_TYPES]
        if unknown:
            raise WorkflowConfigurationError(
                f"Workflow '{raw_name}' contains unknown step type(s): {', '.join(unknown)}"
            )
        validated[raw_name] = list(raw_steps)

    return validated


def build_steps(
    step_types: Sequence[str],
    model: str,
    llm: ILLM | None = None,
) -> list[IStep]:
    """Map configured step names to concrete step implementations."""
    steps: list[IStep] = []
    for step_type in step_types:
        if step_type == QueryStep.step_type:
            steps.append(QueryStep())
        elif step_type == LlmPromptStep.step_type:
            steps.append(LlmPromptStep(model=model, llm=llm))
        elif step_type == OutputStep.step_type:
            steps.append(OutputStep())
        else:
            raise WorkflowConfigurationError(f"Unknown workflow step type: {step_type}")
    return steps


T = TypeVar("T")


def run_async(awaitable: Awaitable[T]) -> T:
    """Execute an async workflow operation from Streamlit's synchronous script."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)
    raise RuntimeError("Workflow sync execution cannot run inside an active event loop.")


class WorkflowRunner:
    """Process configured workflow steps sequentially or one step at a time."""

    def __init__(self, steps: Sequence[IStep]) -> None:
        self.steps = list(steps)

    async def process_step(self, index: int, input: StepMessage) -> StepMessage:
        return await self.steps[index].process(_normalize_message(input))

    def process_step_sync(self, index: int, input: StepMessage) -> StepMessage:
        return run_async(self.process_step(index, input))

    async def process_all(self, input: StepMessage) -> list[StepMessage]:
        messages: list[StepMessage] = []
        current = _normalize_message(input)
        for step in self.steps:
            current = await step.process(current)
            messages.append(current)
        return messages

    def process_all_sync(self, input: StepMessage) -> list[StepMessage]:
        return run_async(self.process_all(input))


def _normalize_message(input: StepMessage) -> StepMessage:
    return {
        "IsError": bool(input.get("IsError", False)),
        "Message": str(input.get("Message", "")),
    }
