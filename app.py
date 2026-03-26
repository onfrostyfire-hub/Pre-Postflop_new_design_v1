import streamlit as st
from views import mobile, desktop, compare, stats

st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def main():
    # --- ТОПОВЫЙ CSS ДЛЯ IOS-ВКЛАДОК НАВИГАЦИИ ---
    st.markdown("""
    <style>
        /* Прячем дефолтные кружочки радио-кнопок */
        div[role="radiogroup"] label div:first-child { display: none !important; }
        div[role="radiogroup"] label input { display: none !important; }
        
        /* Стилизуем контейнер (обертку) вкладок */
        div[role="radiogroup"] {
            flex-direction: row !important;
            background: #111 !important;
            padding: 4px !important;
            border-radius: 12px !important;
            border: 1px solid #333 !important;
            gap: 4px !important;
            margin-bottom: 10px !important;
            width: 100% !important;
        }
        
        /* Стилизуем сами вкладки */
        div[role="radiogroup"] label {
            background: transparent !important;
            padding: 8px 4px !important;
            border-radius: 8px !important;
            margin: 0 !important;
            flex: 1 !important;
            display: flex !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        
        /* Текст неактивной вкладки */
        div[role="radiogroup"] label p {
            color: #888 !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            margin: 0 !important;
            text-transform: uppercase !important;
        }
        
        /* Активная вкладка (вжигается желтым) */
        div[role="radiogroup"] label:has(input:checked) {
            background: #ffc107 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5) !important;
        }
        div[role="radiogroup"] label:has(input:checked) p {
            color: #000 !important;
            font-weight: 900 !important;
        }
        
        /* Прячем кнопку старого сайдбара на мобилках */
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* Урезаем отступ сверху, чтобы вкладки висели аккуратно */
        .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "🎮 Trainer"
    if "view_type" not in st.session_state:
        st.session_state.view_type = "Mobile"

    # Вкладки главного меню
    app_mode = st.radio(
        "Навигация", 
        ["🎮 Trainer", "🔬 Range Lab", "📊 Statistics"], 
        horizontal=True, 
        label_visibility="collapsed",
        key="app_mode"
    )

    # Переключатель Mobile/Desktop выводим только на экране тренажера
    if app_mode == "🎮 Trainer":
        view_type = st.radio("Режим", ["Mobile", "Desktop"], horizontal=True, label_visibility="collapsed", key="view_type")

    # Роутинг страниц
    if app_mode == "🔬 Range Lab":
        compare.show()
    elif app_mode == "📊 Statistics":
        stats.show()
    else:
        if st.session_state.view_type == "Mobile":
            mobile.show()
        else:
            desktop.show()

if __name__ == "__main__":
    main()
