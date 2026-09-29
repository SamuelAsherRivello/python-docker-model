import streamlit as st


def render_header() -> None:
    title_column, actions_column = st.columns([8, 1], vertical_alignment="center")
    with title_column:
        st.title("Docker Model Runner Chat")
    with actions_column:
        if st.button("Refresh", icon=":material/refresh:", key="refresh", width="stretch"):
            st.rerun()
