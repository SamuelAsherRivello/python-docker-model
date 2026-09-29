# Proposal

## Why

The public repository has no playable deployment, and the current app exposes technical Docker errors when started in a hosted environment that cannot access Docker Model Runner. A hosted demo should load cleanly and explain this limitation without crashing or presenting unusable model controls.

## What Changes

- Prepare the Streamlit project for deployment on Streamlit Community Cloud from the `Python/` project root.
- Detect when Docker Model Runner or its models are unavailable without treating the condition as an application failure.
- Replace raw hosted-runtime Docker errors with a centered warning prompt: “Docker Models not accessible. App designed to run locally, not yet online.”
- Disable model-dependent interaction while the warning is displayed and preserve normal local behavior when Docker models are available.
- Add automated coverage for the graceful unavailable state and retain existing Docker, workflow, and error-propagation behavior.
- Update repository documentation with the deployed Streamlit demo URL and accurate local-versus-hosted behavior.

## Capabilities

### New Capabilities

- `hosted-demo`: Covers deployment of the Streamlit application as a public live demo and its graceful, centered unavailable-model experience when Docker Model Runner cannot be reached.

### Modified Capabilities

None.

## Impact

- Primary implementation areas: `Python/src/ui/app.py`, `Python/src/ui/layout/footer.py`, and focused UI helpers or styles.
- Tests: Streamlit AppTest coverage for missing Docker, failed Docker commands, and empty model lists.
- Deployment and documentation: Streamlit Community Cloud configuration, root `README.md`, and the repository live-demo link.
- No changes to workflow JSON, step contracts, successful local Docker inference, or the rule that LLM calls occur only in workflows containing `llm-prompt-step`.
