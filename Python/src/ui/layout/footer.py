import streamlit as st

from src.Workflows.workflow import WorkflowConfigurationError, load_workflows
from src.llm.docker_llm import DockerLLM
from src.llm.illm import ILLM


def render_footer(
    llm: ILLM | None = None,
) -> tuple[str | None, str | None, dict[str, list[str]], str | None]:
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

    errors = [error for error in (model_error, workflow_error) if error]
    if not models and not model_error:
        errors.append("No local Docker models found. Pull one with `docker model pull <model>`.")
    return selected_model, selected_workflow, workflows, "\n\n".join(errors) or None
