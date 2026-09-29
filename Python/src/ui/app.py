import streamlit as st
from src.ui.layout.body import render_body, reset_workflow_state
from src.ui.layout.footer import render_footer
from src.ui.layout.header import render_header


MODEL_UNAVAILABLE_MESSAGE = (
    "Docker Models not accessible. App designed to run locally, not yet online."
)


def render_model_unavailable() -> None:
    """Render the stable hosted-demo state when no Docker model is usable."""
    st.html(
        """
        <style>
            .st-key-model-unavailable {
                min-height: calc(100% - 2rem);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
                box-sizing: border-box;
            }
            .st-key-model-unavailable > div {
                width: min(720px, 100%);
            }
            .st-key-model-unavailable [data-testid="stAlert"] {
                text-align: center;
            }
            .st-key-model-unavailable [data-testid="stCaptionContainer"] {
                text-align: center;
            }
        </style>
        """
    )
    with st.container(key="model-unavailable"):
        st.warning(MODEL_UNAVAILABLE_MESSAGE, icon=":material/cloud_off:")
        st.caption(
            "Run this project locally with Docker Desktop and Docker Model Runner "
            "to select a model and execute workflows."
        )


def render_app() -> None:
    st.set_page_config(page_title="Docker Model Runner Chat", page_icon="🐳", layout="wide")
    st.html("""
    <style>
        html, body, .stApp { width: 100%; height: 100%; overflow: hidden; }
        [data-testid="stHeader"], [data-testid="stToolbar"],
        .stDeployButton, #MainMenu, #stDecoration { display: none !important; }
        [data-testid="stMain"] {
            width: calc(100% - 10px);
            height: calc(100dvh - 10px);
            margin: 5px;
            overflow: hidden !important;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: none !important;
            width: 100% !important;
            height: calc(100dvh - 115px) !important;
            flex: 0 0 calc(100dvh - 115px) !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        [data-testid="stMainBlockContainer"] > .stVerticalBlock {
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 0 !important;
        }
        [data-testid="stMainBlockContainer"] > .stVerticalBlock > div:has(> .st-key-header) {
            flex: 0 0 105px !important;
        }
        [data-testid="stMainBlockContainer"] > .stVerticalBlock > div:has(> .st-key-body) {
            flex: 1 1 auto !important;
            min-height: 0 !important;
        }
        .st-key-header {
            height: 100px !important;
            min-height: 100px !important;
            margin: 0 0 5px 0 !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: var(--background-color);
            border-bottom: 1px solid var(--border-color);
        }
        .st-key-header > div { width: 100%; }
        .st-key-header h1 { margin: 0 !important; padding: 0 !important; font-size: 1.5rem !important; }
        .st-key-body {
            height: 100% !important;
            min-height: 0 !important;
            margin: 0 !important;
            overflow-y: scroll !important;
            scrollbar-gutter: stable;
            padding: 1rem 0 !important;
        }
        [data-testid="stBottom"], [data-testid="stBottom"] > div {
            height: 105px !important;
            min-height: 105px !important;
            flex: 0 0 105px !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stBottom"] > div > div {
            height: 105px !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .st-key-footer {
            height: 100px !important;
            min-height: 100px !important;
            margin: 5px 0 0 0 !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            border-top: 1px solid var(--border-color);
            background: var(--background-color);
        }
        .st-key-footer > div { width: 100%; }
        .st-key-footer [data-testid="stVerticalBlock"] { gap: 0 !important; }
    </style>
    """)
    with st.container(key="header"):
        render_header()
    with st.bottom:
        with st.container(key="footer"):
            footer_state = render_footer()
    if footer_state.fatal_error:
        with st.container(key="body"):
            st.error(footer_state.fatal_error)
        return
    if not footer_state.model_available:
        reset_workflow_state(st.session_state)
        with st.container(key="body"):
            render_model_unavailable()
        return
    with st.container(key="body"):
        render_body(
            footer_state.selected_model,
            footer_state.selected_workflow,
            footer_state.workflows,
        )
