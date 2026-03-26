import streamlit as st
from views import mobile, desktop, compare, stats

st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def main():
    # Тотальная компрессия отступов
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { background: transparent !important; height: 0px !important; min-height: 0px !important; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        
        /* Секретный маркер для вкладок */
        .compact-tabs { display: none; }
        
        /* Обертка радио-кнопок */
        .compact-tabs + div[role="radiogroup"] {
            display: inline-flex !important;
            background: #1a1c20 !important;
            padding: 2px !important;
            border-radius: 8px !important;
            border: 1px solid #333 !important;
            gap: 2px !important;
            margin-top: -5px !important; /* Поднимаем вкладки выше */
            margin-bottom: -8px !important; /* Прижимаем к нижнему элементу */
        }
        .compact-tabs + div[role="radiogroup"] label {
            padding: 4px 8px !important;
            background: transparent !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            margin: 0 !important;
            border: none !important;
        }
        .compact-tabs + div[role="radiogroup"] label div:first-child { display: none !important; }
        .compact-tabs + div[role="radiogroup"] label p { 
            color: #888 !important; 
            font-size: 11px !important; 
            font-weight: bold !important; 
            margin: 0 !important; 
            text-transform: uppercase; 
        }
        
        /* Активное состояние */
        .compact-tabs + div[role="radiogroup"] label[data-checked="true"],
        .compact-tabs + div[role="radiogroup"] label:has(input:checked) {
            background: #ffc107 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.4) !important;
        }
        .compact-tabs + div[role="radiogroup"] label[data-checked="true"] p,
        .compact-tabs + div[role="radiogroup"] label:has(input:checked) p {
            color: #000 !important;
            font-weight: 900 !important;
        }
        
        /* Глобальное схлопывание пустот между блоками Стримлита */
        div[data-testid="stVerticalBlock"] > div { padding-bottom: 0 !important; margin-bottom: 0 !important; }
        div.element-container { margin-bottom: 2px !important; }
    </style>
    """, unsafe_allow_html=True)

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
