# Tasks

## 1. Workflow configuration and core contracts

- [x] 1.1 Add `Python/src/Workflows/workflow.json` with the two default ordered workflows and verify both definitions load from the project checkout
- [x] 1.2 Add workflow message, step, loader, and factory abstractions in `Python/src/Workflows/workflow.py`, including validation for unknown step types, and verify valid configurations instantiate the expected step sequence
- [x] 1.3 Implement `QueryStep`, `LlmPromptStep`, and `OutputStep` processing with the shared message contract and verify success and error propagation with unit tests
- [x] 1.4 Add the synchronous Streamlit runner bridge for async step processing and verify each step is processed once per workflow run

## 2. Streamlit workflow UI and state

- [x] 2.1 Add workflow selection beside model selection in the footer and verify the JSON-defined workflow names appear with existing model discovery
- [x] 2.2 Replace the fixed body flow with visible `StepCard` rendering for every selected step, enabling only the active step and verifying inactive steps are greyed out and non-interactive
- [x] 2.3 Implement session-state tracking for selected model, selected workflow, active step, step messages, and run fingerprints, verifying successful steps advance automatically
- [x] 2.4 Implement model, workflow, and new-session reset behavior, verifying stale messages and active-step state are cleared
- [x] 2.5 Ensure query-only workflows never call `DockerLLM.call()` and LLM workflows call it only when `llm-prompt-step` is present, verified with mocked adapter tests
- [x] 2.6 Render successful final output normally and propagated errors in red, verified through UI-facing behavior or component tests

## 3. Regression coverage

- [x] 3.1 Add tests for workflow JSON loading, step ordering, invalid step configuration, and message contract behavior, verifying the full core workflow test suite passes
- [x] 3.2 Add integration tests for both default workflows, selector/reset behavior, progression, no-LLM execution, model failures, and final error rendering, verifying existing Docker LLM tests still pass
- [x] 3.3 Run the project test command and verify the application imports successfully without changing existing Docker model discovery behavior
