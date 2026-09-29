## Context

The Streamlit body currently renders all workflow steps and already tracks the active step and per-step messages. Cards expose their state, but their headers, labels, controls, and status vocabulary are inconsistent with the desired workflow presentation. This change is a focused UI refinement on top of the existing workflow runner.

## Goals / Non-Goals

**Goals:**

- Give every step card the same visual hierarchy.
- Make workflow order and current activity immediately visible.
- Keep only the active step interactive.
- Support keyboard-first query submission while retaining multiline entry.
- Preserve existing workflow execution, error propagation, and reset behavior.

**Non-Goals:**

- Changing the `IStep` or `StepMessage` contracts.
- Adding workflow or step types.
- Changing model discovery or Docker model invocation.
- Introducing new status states beyond `Unstarted`, `Active`, and `Complete`.
- Redesigning the footer selectors.

## Decisions

### Derive status from workflow position

Each rendered card receives its one-based position, display name, and a derived status:

- `Complete` when the step has finished processing, including processing that produced an error message.
- `Active` when the step is the current workflow step.
- `Unstarted` when the step has not yet become active.

The renderer must derive these values from the canonical workflow-run state rather than maintain a second status store. This prevents contradictory states and guarantees that no more than one card is active. A fully completed run has zero active cards and all cards are complete.

### Use one header contract

The header is a horizontal layout. Its left side renders `Step {number} · {name}` and its right side renders the textual status. Status must not be communicated by color alone.

### Use one three-column body contract

Every card body uses aligned label, value, and action regions. Column ratios may adapt at narrow widths, but the logical order stays label → value → action.

- Query: `Input Text` label, editable text area, Submit button on the same horizontal line.
- LLM prompt: `Response` label, generated response text, reserved empty action region.
- Output: `Output` label, final text, reserved empty action region.

Empty action regions remain structurally present so content aligns across cards. Unavailable values render as an unobtrusive empty or placeholder state rather than inventing workflow content.

After a step completes, the renderer keeps the value that was visible at completion. For the Query card, the submitted text remains in the text area and the text area and Submit button become disabled. The transition changes the status from `Active` to `Complete`; it does not replace the completed card with a summary or clear its widget value.

### Keep the query in a native form where possible

The Query card keeps the text area and submit button in one Streamlit form with form Enter submission enabled. The interaction contract is:

- Enter submits the current query.
- Shift+Enter inserts a newline without submitting.
- The click-based Submit action remains available.

This behavior must be verified in the browser with the installed Streamlit version. If the native form/text-area combination cannot meet both keyboard cases, implementation may add the smallest isolated keyboard-handling component needed to satisfy the contract without changing workflow processing.

### Separate semantic state from visual styling

The StepCard renderer assigns explicit classes or equivalent state markers for `unstarted`, `active`, and `complete`. Styling uses those markers to grey and disable inactive cards while preserving readable contrast. Only the active Query card exposes enabled controls; passive LLM and Output cards remain display-only in every state.

### Preserve error presentation

This change does not alter `StepMessage` propagation. The Output value region continues to render messages with `IsError=True` in red. A step that produced or propagated an error is still `Complete` after processing because status represents lifecycle, not success severity.

## Risks / Trade-offs

- Streamlit's generated DOM can make wrapper-level CSS selectors brittle. Keep selectors narrowly scoped and prefer stable containers or state markers already used by the app.
- Native Enter handling inside a multiline widget can vary by Streamlit release. Browser verification is required, with an isolated component fallback only if necessary.
- Horizontal columns may become cramped on small screens. Allow Streamlit's responsive stacking behavior while preserving semantic order.

## Migration Plan

1. Refactor the existing StepCard rendering path without changing workflow session-state keys.
2. Replace current status labels with the three-state vocabulary.
3. Update step-specific body renderers to use the shared layout.
4. Add interaction and rendering tests, then verify both default workflows in a browser.

The change is UI-only and requires no data migration or rollback procedure beyond reverting the renderer and styles.

## Open Questions

None. Browser verification determines implementation technique for keyboard handling but does not change the required behavior.
