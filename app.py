import streamlit as st
from views import mobile, desktop, compare, stats

st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def main():
    # Убираем кнопку бокового меню, делаем шапку прозрачной и опускаем контент
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent !important; }
        .block-container { padding-top: 4.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

    # Инициализация состояний
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🎮 Trainer"
    if "view_type" not in st.session_state:
        st.session_state.view_type = "Mobile"

    # --- ВЕРХНИЕ ВКЛАДКИ НАВИГАЦИИ ---
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🎮 Trainer", type="primary" if st.session_state.app_mode == "🎮 Trainer" else "secondary", use_container_width=True):
            st.session_state.app_mode = "🎮 Trainer"
            st.rerun()
    with c2:
        if st.button("🔬 Range Lab", type="primary" if st.session_state.app_mode == "🔬 Range Lab" else "secondary", use_container_width=True):
            st.session_state.app_mode = "🔬 Range Lab"
            st.rerun()
    with c3:
        if st.button("📊 Stats", type="primary" if st.session_state.app_mode == "📊 Statistics" else "secondary", use_container_width=True):
            st.session_state.app_mode = "📊 Statistics"
            st.rerun()

    # --- ПОДМЕНЮ: ВЫБОР ПК / МОБАЙЛ (ТОЛЬКО В РАЗДЕЛЕ ТРЕНАЖЕРА) ---
    if st.session_state.app_mode == "🎮 Trainer":
        v1, v2 = st.columns(2)
        with v1:
            if st.button("📱 Mobile View", type="primary" if st.session_state.view_type == "Mobile" else "secondary", use_container_width=True):
                st.session_state.view_type = "Mobile"
                st.rerun()
        with v2:
            if st.button("💻 Desktop View", type="primary" if st.session_state.view_type == "Desktop" else "secondary", use_container_width=True):
                st.session_state.view_type = "Desktop"
                st.rerun()
        st.markdown("<hr style='margin: 5px 0 15px 0; border-color: #333;'>", unsafe_allow_html=True)

    # --- РОУТИНГ ПО ЭКРАНАМ ---
    if st.session_state.app_mode == "🔬 Range Lab":
        compare.show()
    elif st.session_state.app_mode == "📊 Statistics":
        stats.show()
    else:
        if st.session_state.view_type == "Mobile":
            mobile.show()
        else:
            desktop.show()

if __name__ == "__main__":
    main()
