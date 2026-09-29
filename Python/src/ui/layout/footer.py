from dataclasses import dataclass

import streamlit as st

from src.Workflows.workflow import WorkflowConfigurationError, load_workflows
from src.llm.docker_llm import DockerLLM
from src.llm.illm import ILLM


@dataclass(frozen=True)
class FooterState:
    """Selections and availability discovered while rendering the footer."""

    selected_model: str | None
    selected_workflow: str | None
    workflows: dict[str, list[str]]
    model_available: bool
    model_diagnostic: str | None = None
    fatal_error: str | None = None


def render_footer(
    llm: ILLM | None = None,
) -> FooterState:
    """Render model and workflow selectors and return their current values."""
    llm = llm or DockerLLM()
    models, model_error = llm.list_models()
    try:
        workflows = load_workflows()
        workflow_error = None
    except WorkflowConfigurationError as exc:
        workflows = {}
        workflow_error = str(exc)

    with st.container(horizontal=True, vertical_alignment="center", gap="small", wrap=False):
        st.markdown("Adapter: `docker_llm.py`")
        st.markdown("Model:")
        selected_model = st.selectbox(
            "Model",
            models,
            index=0 if models else None,
            key="selected_model",
            disabled=not models,
            label_visibility="collapsed",
            width=400,
        )
        st.markdown("Workflow:")
        selected_workflow = st.selectbox(
            "Workflow",
            list(workflows),
            index=0 if workflows else None,
            key="selected_workflow",
            disabled=not workflows,
            label_visibility="collapsed",
            width=260,
        )

    model_diagnostic = model_error
    if not models and not model_diagnostic:
        model_diagnostic = "No local Docker models were found."

    return FooterState(
        selected_model=selected_model,
        selected_workflow=selected_workflow,
        workflows=workflows,
        model_available=bool(models),
        model_diagnostic=model_diagnostic,
        fatal_error=workflow_error,
    )
