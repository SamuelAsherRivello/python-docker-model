# Proposal

## Why

The Streamlit app currently hardcodes a single query-to-LLM-to-response flow, making it difficult to offer different user experiences without changing UI code. Configurable workflow pipelines will make the body experience declarative while preserving the existing Docker model discovery and invocation behavior.

## What Changes

- Add JSON-defined workflows composed of ordered step types.
- Add a workflow loader and sequential workflow runner using a shared `StepMessage` contract.
- Add query, optional LLM prompt, and output step implementations.
- Render every configured step as a visible `StepCard`, enabling interaction only for the active step.
- Add a workflow selector beside the model selector in the footer.
- Add session-state reset behavior when the model, workflow, or app session changes.
- Propagate errors through subsequent steps and render final errors in red.
- Preserve the existing Docker model discovery and model execution integration.

## Capabilities

### New Capabilities

- `configurable-workflow-pipelines`: Declarative workflow configuration, step processing, state progression, error propagation, and Streamlit workflow UI.

### Modified Capabilities

None.

## Impact

- Adds `Python/src/Workflows/workflow.json` and `Python/src/Workflows/workflow.py` plus supporting workflow/UI modules.
- Changes `Python/src/ui/app.py`, `Python/src/ui/layout/footer.py`, and `Python/src/ui/layout/body.py` to pass workflow selection and render pipeline steps.
- Adds or extends tests for workflow loading, step contracts, state transitions, error propagation, selector behavior, and the no-LLM path.
- No external API or Docker Model Runner contract changes are required.
