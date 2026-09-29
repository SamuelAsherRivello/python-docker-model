from src.ui.app import render_app
import streamlit as st


if __name__ == "__main__":
    if st.runtime.exists():
        render_app()
    else:
        print("This is a Streamlit app. Start it with: streamlit run main.py")
