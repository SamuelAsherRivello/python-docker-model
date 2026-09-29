from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any

import streamlit as st

from src.Workflows.workflow import (
    IStep,
    LlmPromptStep,
    OutputStep,
    QueryStep,
    StepMessage,
    WorkflowConfigurationError,
    WorkflowRunner,
    build_steps,
)
from src.llm.illm import ILLM


ACTIVE_STEP_KEY = "workflow_active_step"
FINGERPRINT_KEY = "workflow_fingerprint"
MESSAGES_KEY = "workflow_step_messages"
MODEL_KEY = "workflow_selected_model"
RUN_ID_KEY = "workflow_run_id"
WORKFLOW_KEY = "workflow_selected_name"
WORKFLOW_STATE_KEYS = {
    ACTIVE_STEP_KEY,
    FINGERPRINT_KEY,
    MESSAGES_KEY,
    MODEL_KEY,
    RUN_ID_KEY,
    WORKFLOW_KEY,
}
QUERY_WIDGET_PREFIX = "workflow-query-"


def reset_workflow_state(state: MutableMapping[str, Any]) -> None:
    """Remove only workflow-run and query-widget values from session state."""
    for key in tuple(state):
        if key in WORKFLOW_STATE_KEYS or str(key).startswith(QUERY_WIDGET_PREFIX):
            del state[key]


def sync_workflow_state(
    state: MutableMapping[str, Any],
    selected_model: str,
    selected_workflow: str,
    step_types: Sequence[str],
) -> bool:
    """Initialize or reset workflow state when its selection fingerprint changes."""
    fingerprint = (selected_model, selected_workflow, tuple(step_types))
    if state.get(FINGERPRINT_KEY) == fingerprint:
        return False

    state[FINGERPRINT_KEY] = fingerprint
    state[MODEL_KEY] = selected_model
    state[WORKFLOW_KEY] = selected_workflow
    state[ACTIVE_STEP_KEY] = 0
    state[MESSAGES_KEY] = {}
    state[RUN_ID_KEY] = int(state.get(RUN_ID_KEY, 0)) + 1
    return True


def render_body(
    selected_model: str | None,
    selected_workflow: str | None,
    workflows: Mapping[str, list[str]],
    llm: ILLM | None = None,
) -> None:
    """Render and advance the selected workflow pipeline."""
    if not selected_model or not selected_workflow:
        return
    step_types = workflows.get(selected_workflow)
    if not step_types:
        st.error(f"Workflow '{selected_workflow}' is not configured.")
        return

    try:
        steps = build_steps(step_types, model=selected_model, llm=llm)
    except WorkflowConfigurationError as exc:
        st.error(str(exc))
        return

    sync_workflow_state(
        st.session_state,
        selected_model=selected_model,
        selected_workflow=selected_workflow,
        step_types=step_types,
    )
    _render_step_card_styles()
    runner = WorkflowRunner(steps)

    for index, step in enumerate(steps):
        _render_step_card(index, step, runner, len(steps))


def _render_step_card(
    index: int,
    step: IStep,
    runner: WorkflowRunner,
    total_steps: int,
) -> None:
    messages: dict[int, StepMessage] = st.session_state[MESSAGES_KEY]
    active_index = st.session_state[ACTIVE_STEP_KEY]
    is_complete = index in messages
    is_active = index == active_index and not is_complete
    status = "complete" if is_complete else "active" if is_active else "unstarted"

    with st.container(
        border=True,
        key=f"workflow-step-{status}-{index}",
        gap="xsmall",
    ):
        with st.container(
            horizontal=True,
            horizontal_alignment="distribute",
            vertical_alignment="center",
            gap="small",
        ):
            st.subheader(f"Step {index + 1} · {step.label}")
            if is_complete:
                st.markdown(":green-badge[Complete]")
            elif is_active:
                st.markdown(":blue-badge[Active]")
            else:
                st.markdown(":gray-badge[Unstarted]")

        if isinstance(step, QueryStep):
            _render_query_step(index, runner, total_steps, is_active, is_complete)
        elif isinstance(step, LlmPromptStep):
            _render_llm_step(index, runner, total_steps, is_active, is_complete)
        elif isinstance(step, OutputStep):
            _render_output_step(index, runner, total_steps, is_active, is_complete)


def _render_query_step(
    index: int,
    runner: WorkflowRunner,
    total_steps: int,
    is_active: bool,
    is_complete: bool,
) -> None:
    run_id = st.session_state[RUN_ID_KEY]
    completed_message = st.session_state[MESSAGES_KEY].get(index)
    completed_value = completed_message["Message"] if is_complete else ""
    query_key = f"workflow-query-{run_id}"
    if is_complete:
        st.session_state[query_key] = completed_value
    elif query_key not in st.session_state:
        st.session_state[query_key] = ""

    with st.form(
        f"workflow-query-form-{run_id}",
        border=False,
        enter_to_submit=True,
    ):
        label_column, value_column, action_column = st.columns(
            [1.4, 6, 1.2],
            gap="small",
            vertical_alignment="center",
        )
        with label_column:
            st.markdown("**Input Text**")
        with value_column:
            prompt = st.text_area(
                "Input Text",
                placeholder="Enter a query for this workflow...",
                height=68,
                key=query_key,
                disabled=not is_active,
                label_visibility="collapsed",
            )
        with action_column:
            submitted = st.form_submit_button(
                "Submit",
                type="primary",
                icon=":material/send:",
                key=f"workflow-query-submit-{run_id}",
                disabled=not is_active,
                width="content",
            )

    if submitted and is_active:
        result = runner.process_step_sync(
            index,
            {"IsError": False, "Message": prompt or ""},
        )
        _record_step_result(index, result, total_steps)
        st.rerun()


def _render_llm_step(
    index: int,
    runner: WorkflowRunner,
    total_steps: int,
    is_active: bool,
    is_complete: bool,
) -> None:
    result = st.session_state[MESSAGES_KEY].get(index)
    if is_active and not is_complete:
        input_message = _previous_message(index)
        if input_message is None:
            st.error("The workflow cannot continue because the previous step has no message.")
            return

        with st.spinner("Processing with the selected model..."):
            result = runner.process_step_sync(index, input_message)
        _record_step_result(index, result, total_steps)
        st.rerun()

    _render_message_row("Response", result)


def _render_output_step(
    index: int,
    runner: WorkflowRunner,
    total_steps: int,
    is_active: bool,
    is_complete: bool,
) -> None:
    if is_active and not is_complete:
        input_message = _previous_message(index)
        if input_message is None:
            st.error("The workflow cannot continue because the previous step has no message.")
            return
        result = runner.process_step_sync(index, input_message)
        _record_step_result(index, result, total_steps)
        st.rerun()
    else:
        result = st.session_state[MESSAGES_KEY].get(index)

    _render_message_row("Output", result)


def _render_message_row(label: str, result: StepMessage | None) -> None:
    """Render a passive step body using the shared label/value/action grid."""
    label_column, value_column, action_column = st.columns(
        [1.4, 6, 1.2],
        gap="small",
        vertical_alignment="center",
    )
    with label_column:
        st.markdown(f"**{label}**")
    with value_column:
        if not result:
            st.caption("Waiting for the previous step.")
        elif result["IsError"]:
            st.error(result["Message"])
        else:
            st.markdown(result["Message"])
    with action_column:
        st.empty()


def _previous_message(index: int) -> StepMessage | None:
    if index <= 0:
        return {"IsError": False, "Message": ""}
    return st.session_state[MESSAGES_KEY].get(index - 1)


def _record_step_result(index: int, result: StepMessage, total_steps: int) -> None:
    messages = dict(st.session_state[MESSAGES_KEY])
    messages[index] = result
    st.session_state[MESSAGES_KEY] = messages
    st.session_state[ACTIVE_STEP_KEY] = min(index + 1, total_steps)


def _render_step_card_styles() -> None:
    st.html(
        """
        <style>
            [class*="st-key-workflow-step-unstarted-"] {
                opacity: 0.55;
                filter: grayscale(0.85);
                pointer-events: none;
            }

            [class*="st-key-workflow-step-complete-"] {
                opacity: 0.78;
                filter: grayscale(0.25);
                pointer-events: none;
            }
        </style>
        """
    )
