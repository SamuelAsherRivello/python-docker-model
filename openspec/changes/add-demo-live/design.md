# Design

## Context

The Streamlit app discovers models synchronously through `docker model list --json` during each render. `DockerLLM.list_models()` already converts a missing executable, failed process, timeout, or malformed response into an empty list plus an error string. `render_footer()` currently combines model-discovery and workflow-configuration failures into one error, and `render_app()` displays that text with a local setup hint before returning.

The public repository keeps the deployable entry point and dependency file under `Python/`. Streamlit Community Cloud can launch `Python/main.py`, but its managed runtime cannot access a user's local Docker Desktop or Docker Model Runner. See `proposal.md` for motivation and `specs/hosted-demo/spec.md` for the observable behavior.

## Goals / Non-Goals

**Goals:**

- Make model availability an explicit UI state rather than a fatal application error.
- Keep workflow-configuration errors distinguishable from expected Docker unavailability.
- Present the unavailable state as a centered, polished warning that is stable across reruns.
- Ensure no stale workflow state or Docker inference can continue while no model is selected.
- Deploy and verify the public app from `Python/main.py` on Streamlit Community Cloud.

**Non-Goals:**

- Provide remote model inference, bundled model weights, Docker-in-Docker, or a simulated model response.
- Change workflow definitions, step contracts, or successful local inference behavior.
- Add user accounts, secrets, persistent storage, analytics, or a custom domain.
- Hide genuine workflow configuration errors behind the hosted-demo warning.

## Decisions

### 1. Deploy through Streamlit Community Cloud

Configure a public Streamlit Community Cloud app using repository `SamuelAsherRivello/python-docker-model`, branch `main`, and entry point `Python/main.py`. The existing `Python/requirements.txt` and `Python/.streamlit/config.toml` remain colocated with the application.

This is preferred over GitHub Pages because Streamlit requires a Python server runtime. A custom container host was considered but would add deployment infrastructure without making local Docker Model Runner available.

### 2. Separate expected model unavailability from fatal application errors

Represent footer output as a typed state containing selected values, loaded workflows, model availability, and any fatal workflow-configuration error. Missing Docker, command failures, malformed model output, and an empty model list all map to the same expected unavailable state for users. Workflow JSON failures remain explicit application errors.

This avoids parsing user-facing strings in `render_app()` and prevents hosted infrastructure details or command stderr from becoming the primary page content. Reusing the current combined `footer_error` string was considered but cannot reliably distinguish an expected hosted limitation from a broken workflow configuration.

### 3. Render one centered warning state in the body

When model availability is false, `render_app()` will render a dedicated body-state helper and will not call `render_body()`. The helper will use a keyed container plus scoped CSS to center a warning panel both horizontally and vertically in the available body region. Its primary message will exactly match the specification; supporting text may point visitors to the repository's local setup instructions.

The header and footer remain visible so the hosted page still demonstrates the application shell. The empty model selector remains disabled. This is preferred over a modal because Streamlit reruns can repeatedly reopen modal dialogs and because the warning is the stable body content, not a transient interruption.

### 4. Reset workflow state before showing the unavailable state

Extract or add a focused workflow reset helper for the workflow session keys. Invoke it when model availability is lost before rendering the warning. Because `render_body()` is skipped, neither automatic steps nor an LLM prompt step can execute without a selected model.

Clearing all of `st.session_state` was considered but rejected because it can disrupt unrelated widget state and makes future extension harder. Only workflow-run keys and their query widget values should be reset.

### 5. Test availability behavior at adapter and app boundaries

Keep adapter tests for subprocess result normalization and add coverage for missing Docker, failed discovery, timeout or malformed output, and empty model lists where needed. Add Streamlit AppTest scenarios that inject unavailable and available model states, assert the exact warning, verify the warning container and disabled selector, prove `render_body()` or model inference is not entered while unavailable, and confirm normal local rendering remains unchanged.

The browser-level deployment check will verify the public URL and centered presentation because AppTest cannot prove hosted reachability or final viewport alignment.

### 6. Publish the verified deployment URL only after deployment succeeds

Create the Streamlit Community Cloud deployment, wait for a healthy page, and verify the fallback before replacing the README's localhost-only Live Demo entry with the actual public URL. The README will continue to explain local setup and will explicitly state that hosted model inference is unavailable.

## Risks / Trade-offs

- **[Streamlit Community Cloud slug is assigned or unavailable]** → Record the actual deployed URL after creation and use that verified URL in documentation.
- **[Docker errors are over-normalized]** → Normalize only model discovery failures; retain fatal workflow configuration errors and keep adapter details available to tests or logs rather than the primary warning.
- **[Local Docker temporarily fails and users lose an in-progress run]** → Reset only workflow state when availability is lost; this is safer than retaining a run that can no longer complete.
- **[Hosted sleep or cold-start delays appear as downtime]** → Verify the deployed page after wake-up and document that it is a Streamlit Community Cloud demo.
- **[CSS selectors change across Streamlit versions]** → Scope styling to a stable keyed container and verify at normal and narrow viewport widths.

## Migration Plan

1. Implement and test the explicit model-availability state and centered fallback locally.
2. Push the implementation to `main` and confirm GitHub Actions passes.
3. Create the Streamlit Community Cloud app from `Python/main.py` and verify its public unavailable-model experience.
4. Update the README Live Demo URL and limitation text with the verified deployment address, then push the documentation update.
5. Verify the public repository link and deployed app from an unauthenticated browser session.

Rollback consists of reverting the README live link and application fallback commit, then deleting or unpublishing the Streamlit Community Cloud app if the deployment is unhealthy. Local Docker behavior remains available from the preceding release.
