# Tasks

## 1. Model availability state

- [x] 1.1 Expand `DockerLLM.list_models()` tests for a missing Docker executable, failed command, timeout, malformed JSON, and a successful empty model list, and verify each case returns no models without raising an exception.
- [x] 1.2 Replace the footer's combined error tuple with a typed state that distinguishes unavailable models from workflow configuration failures, and verify footer AppTest coverage for available, unavailable, and invalid-workflow states.
- [x] 1.3 Ensure unavailable discovery details are not rendered as primary user-facing command diagnostics while fatal workflow configuration errors remain visible, and verify both paths with focused UI tests.

## 2. Graceful unavailable-model experience

- [x] 2.1 Add a focused workflow-session reset helper that removes active run messages and query widget state without clearing unrelated session values, and verify it with unit tests.
- [x] 2.2 Add the dedicated unavailable-model body state with the exact warning “Docker Models not accessible. App designed to run locally, not yet online.” and scoped centering styles, and verify the warning text and keyed container with AppTest.
- [x] 2.3 Wire the unavailable state into `render_app()` so `render_body()` and Docker inference cannot run without a model, and verify a refresh remains exception-free with a disabled empty model selector and no partial workflow state.
- [x] 2.4 Preserve the normal local path when models are returned, and verify model selection, both configured workflows, no-LLM Workflow 1 behavior, LLM Workflow 2 behavior, and workflow reset regressions remain green.

## 3. Deployment readiness and automated verification

- [x] 3.1 Verify `Python/main.py`, `Python/requirements.txt`, and `Python/.streamlit/config.toml` form a deployable Streamlit Community Cloud project and confirm the app starts successfully in a no-Docker test environment.
- [x] 3.2 Run the complete unit/AppTest suite and `openspec validate add-demo-live --strict`, and verify all checks pass before deployment.
- [ ] 3.3 Commit and push the implementation to `main`, then verify the GitHub Actions Python test workflow succeeds for that commit.

## 4. Public release and documentation

- [ ] 4.1 Create the Streamlit Community Cloud app from `SamuelAsherRivello/python-docker-model`, branch `main`, entry point `Python/main.py`, and verify the assigned public URL reaches a healthy application.
- [ ] 4.2 Verify the deployed warning is centered at normal and narrow viewport widths, the exact message is visible, selectors cannot initiate model work, refresh is stable, and no raw Docker diagnostics or uncaught exceptions appear.
- [ ] 4.3 Replace the README's localhost-only Live Demo entry with the verified public URL and explain that hosted model inference is unavailable while local Docker Model Runner remains supported; verify the rendered links and wording.
- [ ] 4.4 Commit and push the deployment documentation, verify the public README and live demo from an unauthenticated browser session, and record the final GitHub and Streamlit URLs in the completion report.
