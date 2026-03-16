import streamlit as st
from views import mobile, desktop, compare, stats

st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def main():
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🎮 Trainer"

    with st.sidebar:
        st.title("Poker Trainer")
        app_mode = st.radio("Menu", ["🎮 Trainer", "🔬 Range Lab", "📊 Statistics"], key="app_mode")
        st.markdown("---")
        
        view_type = "Mobile"
        if app_mode == "🎮 Trainer":
            view_type = st.radio("View Mode", ["Mobile", "Desktop"], index=0)

    if app_mode == "🔬 Range Lab":
        compare.show()
    elif app_mode == "📊 Statistics":
        stats.show()
    else:
        if view_type == "Mobile":
            mobile.show()
        else:
            desktop.show()

if __name__ == "__main__":
    main()
