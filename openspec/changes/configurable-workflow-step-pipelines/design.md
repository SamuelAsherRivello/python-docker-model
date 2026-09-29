# Design

## Context

The current application renders a single prompt form in `Python/src/ui/layout/body.py`, discovers models in `Python/src/ui/layout/footer.py`, and invokes the synchronous `DockerLLM` adapter directly. The new behavior crosses the app shell, footer, body, workflow configuration, step processing, and tests.

## Goals / Non-Goals

**Goals:**

- Make workflow composition data-driven through a project-local JSON file.
- Keep a stable message contract across query, model, and output processing.
- Preserve the existing Docker model discovery and invocation interfaces.
- Make progression and reset behavior deterministic across Streamlit reruns.

**Non-Goals:**

- Adding new Docker Model Runner APIs or changing model discovery semantics.
- Supporting arbitrary third-party step plugins or user-authored Python configuration.
- Adding persistence beyond the current Streamlit session.

## Decisions

1. **Use a workflow loader plus a step factory.** The loader reads `Python/src/Workflows/workflow.json`, validates named ordered step lists, and maps known names to step implementations. This keeps configuration declarative while making unknown step names fail clearly instead of silently producing an incomplete UI.

2. **Use a shared `StepMessage` structure.** Steps exchange a small dictionary-compatible message with `IsError` and `Message`. This avoids coupling the UI to individual step types and allows errors to flow to the final output step unchanged.

3. **Keep the public step contract asynchronous, bridge it at the Streamlit boundary.** Step implementations expose `async process(...)`; the runner invokes each step during a Streamlit interaction and awaits it through a small synchronous bridge. This satisfies the workflow contract without changing the existing synchronous Docker adapter or introducing a new dependency.

4. **Represent progress in `st.session_state`.** Store the selected model/workflow fingerprints, active step index, and messages by step. A change in either selector clears the run before rendering the new workflow. Streamlit session recreation naturally starts a fresh run.

5. **Make the query step interactive, model steps automatic, and output passive.** The query card owns the form submission. When activated, the LLM step processes the prior message without another user prompt. The output card only renders the final message. Errors advance to output so they are always visible.

6. **Keep all cards visible.** The body renders the complete selected pipeline every rerun, applying disabled/grey styling and disabling controls for steps after the active index. This makes the configured flow understandable without allowing out-of-order interaction.

## Risks / Trade-offs

- [Async bridge complexity] Streamlit reruns are synchronous while the contract is async -> Keep the bridge isolated in the runner and test it independently.
- [Configuration drift] A malformed or unknown step name can prevent a workflow from loading -> Validate configuration at load time and surface a clear application error.
- [Automatic model processing] Activating an LLM step can cause repeated calls across reruns -> Persist completed step messages and only process a step when its input or run identity changes.
- [Session-state edge cases] Selector changes and reruns can leave stale messages -> Use explicit run fingerprints and clear all step state whenever the model or workflow changes.

## Migration Plan

1. Add the workflow configuration and workflow modules.
2. Integrate selector and body state handling while retaining the existing Docker adapter.
3. Add unit and UI-facing tests for default workflows, progression, reset, no-LLM behavior, and errors.
4. Roll back by removing the workflow integration and restoring the existing direct body call; no data migration is required.

## Open Questions

- Exact visual styling for inactive `StepCard` containers can be finalized during implementation without changing the behavior contract.
