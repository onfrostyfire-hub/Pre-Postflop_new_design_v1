import streamlit as st
from views import mobile, desktop, compare, stats

st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def main():
    # Скрываем черную шапку Стримлита, убираем боковое меню и наводим красоту
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent !important; }
        .block-container { padding-top: 3rem !important; }
        
        /* Секретный маркер для стилизации только конкретных радио-кнопок */
        .compact-tabs { display: none; }
        
        /* Превращаем радио-кнопки в компактные вкладки */
        .compact-tabs + div[role="radiogroup"] {
            display: inline-flex !important;
            background: #1a1c20 !important;
            padding: 4px !important;
            border-radius: 10px !important;
            border: 1px solid #333 !important;
            gap: 2px !important;
        }
        .compact-tabs + div[role="radiogroup"] label {
            padding: 6px 14px !important;
            background: transparent !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            margin: 0 !important;
            border: none !important;
        }
        /* Прячем сами кружочки радио */
        .compact-tabs + div[role="radiogroup"] label div:first-child {
            display: none !important;
        }
        /* Текст неактивной вкладки */
        .compact-tabs + div[role="radiogroup"] label p {
            color: #888 !important;
            font-size: 13px !important;
            font-weight: bold !important;
            margin: 0 !important;
        }
        /* Текст и фон АКТИВНОЙ вкладки */
        .compact-tabs + div[role="radiogroup"] label[data-checked="true"],
        .compact-tabs + div[role="radiogroup"] label:has(input:checked) {
            background: #ffc107 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.4) !important;
        }
        .compact-tabs + div[role="radiogroup"] label[data-checked="true"] p,
        .compact-tabs + div[role="radiogroup"] label:has(input:checked) p {
            color: #000 !important;
            font-weight: 900 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Неубиваемый стейт, чтобы ничего не слетало при перезагрузках
    if "actual_app_mode" not in st.session_state:
        st.session_state.actual_app_mode = "🎮 Trainer"
    if "actual_view_type" not in st.session_state:
        st.session_state.actual_view_type = "📱 Mobile"

    # --- КОМПАКТНЫЕ ВКЛАДКИ ГЛАВНОГО МЕНЮ ---
    st.markdown('<div class="compact-tabs"></div>', unsafe_allow_html=True)
    nav_mode = st.radio(
        "Nav", 
        ["🎮 Trainer", "🔬 Range Lab", "📊 Stats"], 
        index=["🎮 Trainer", "🔬 Range Lab", "📊 Stats"].index(st.session_state.actual_app_mode),
        horizontal=True, 
        label_visibility="collapsed"
    )
    if nav_mode != st.session_state.actual_app_mode:
        st.session_state.actual_app_mode = nav_mode
        st.rerun()

    # --- КОМПАКТНЫЕ ВКЛАДКИ ВЫБОРА УСТРОЙСТВА (ТОЛЬКО В ТРЕНАЖЕРЕ) ---
    if st.session_state.actual_app_mode == "🎮 Trainer":
        st.markdown('<div class="compact-tabs"></div>', unsafe_allow_html=True)
        v_mode = st.radio(
            "View", 
            ["📱 Mobile", "💻 Desktop"], 
            index=["📱 Mobile", "💻 Desktop"].index(st.session_state.actual_view_type),
            horizontal=True, 
            label_visibility="collapsed"
        )
        if v_mode != st.session_state.actual_view_type:
            st.session_state.actual_view_type = v_mode
            st.rerun()
        
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # --- РОУТИНГ ПО ЭКРАНАМ ---
    if st.session_state.actual_app_mode == "🔬 Range Lab":
        compare.show()
    elif st.session_state.actual_app_mode == "📊 Stats":
        stats.show()
    else:
        if st.session_state.actual_view_type == "📱 Mobile":
            mobile.show()
        else:
            desktop.show()

if __name__ == "__main__":
    main()
