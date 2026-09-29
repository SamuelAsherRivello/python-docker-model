## Why

Workflow steps are functional, but their cards do not yet share a clear visual hierarchy or a consistent content layout. Users need to understand step order, identify the currently interactive step, and scan each step's value without learning a different presentation for every step type.

## What Changes

- Standardize every workflow `StepCard` with a horizontal title bar and body row.
- Number cards from one according to their position in the selected workflow.
- Display the step name beside its number and show one of three statuses on the right: `Unstarted`, `Active`, or `Complete`.
- Guarantee that zero or one card is `Active` at a time; inactive cards remain visible, greyed out, and non-interactive.
- Render the Query card as one horizontal `Input Text | text area | Submit` row, with Enter submitting and Shift+Enter inserting a newline.
- Preserve every card's final value after it completes; advancing the workflow updates the card status and disables its controls without clearing or replacing its content.
- Render the LLM card as `Response | generated text | empty action slot`.
- Render the Output card as `Output | final text | empty action slot`, preserving red error output.
- Add automated coverage for numbering, statuses, layouts, disabled states, and query submission behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workflow-step-pipelines`: Refine the presentation and interaction contract for workflow step cards without changing workflow configuration or execution semantics.

## Impact

- Primary implementation area: `Python/src/ui/layout/body.py` and its StepCard rendering helpers/styles.
- Tests: workflow UI rendering and interaction tests.
- No changes to workflow JSON, step processing contracts, model discovery, or Docker LLM behavior.
- The exact Enter and Shift+Enter behavior requires browser-level verification against the installed Streamlit version.
