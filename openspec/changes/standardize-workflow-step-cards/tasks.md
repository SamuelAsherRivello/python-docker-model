## 1. Shared StepCard presentation

- [ ] 1.1 Refactor the StepCard renderer to accept the one-based step number, display name, lifecycle status, and body content without changing workflow execution state.
- [ ] 1.2 Build the horizontal header with `Step {number} · {name}` on the left and the textual status on the right.
- [ ] 1.3 Replace the existing status vocabulary with `Unstarted`, `Active`, and `Complete`, derived from canonical workflow state so zero or one card is active.
- [ ] 1.4 Add scoped styles for active, unstarted, and complete cards with readable contrast and visible disabled treatment.

## 2. Consistent card bodies

- [ ] 2.1 Introduce the shared label, value, and action layout with responsive column behavior.
- [ ] 2.2 Render the Query card as one horizontal `Input Text | text area | Submit` row and enable controls only while the card is active.
- [ ] 2.3 Render the LLM prompt card as `Response | generated text | empty action slot`.
- [ ] 2.4 Render the Output card as `Output | final text | empty action slot`, preserving red rendering for error messages.

## 3. Query keyboard behavior

- [ ] 3.1 Configure the Query form so Enter submits through the existing workflow submission path.
- [ ] 3.2 Ensure Shift+Enter inserts a newline without submitting.
- [ ] 3.3 Verify that keyboard and button submission each process a query exactly once; add isolated keyboard handling only if native Streamlit behavior cannot satisfy both cases.
- [ ] 3.4 Preserve the submitted query in the completed Query card while disabling its text area and Submit button.

## 4. Automated verification

- [ ] 4.1 Update UI tests for one-based numbering, step names, and the three lifecycle statuses.
- [ ] 4.2 Add tests proving no more than one card is active and that completed runs have zero active cards.
- [ ] 4.3 Add tests for each step type's label, value, and action regions and for inactive-card disabled behavior.
- [ ] 4.3a Add a regression test proving a submitted query remains visible after the Query card becomes complete.
- [ ] 4.4 Preserve tests for error propagation and red error output.
- [ ] 4.5 Add interaction coverage for Enter submission, Shift+Enter newline insertion, and click submission.
- [ ] 4.6 Run the full automated test suite and strict OpenSpec validation.

## 5. Browser verification

- [ ] 5.1 Verify Workflow 1 and Workflow 2 visually at normal and narrow viewport widths.
- [ ] 5.2 Confirm card order, status transitions, disabled styling, keyboard behavior, generated response display, and red error output in the running Streamlit app.
