import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils

def show():
    st.markdown("## 📊 Statistics Hub")
    
    df = utils.load_history()
    
    if df.empty or "Date" not in df.columns or "Result" not in df.columns:
        st.info("История пуста. Иди тренируйся, Начальник!")
        return

    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)
    
    if df.empty:
        st.info("История пуста. Иди тренируйся, Начальник!")
        return

    with st.expander("🔍 Фильтры", expanded=True):
        c1, c2, c3 = st.columns(3)
        time_filter = c1.selectbox("Период", ["All Time", "24 Hours", "7 Days", "30 Days", "1 Year"])
        unique_spots = df["Spot"].unique().tolist()
        spot_filter = c2.multiselect("Споты", unique_spots, default=unique_spots)
        res_filter = c3.selectbox("Результат", ["Все", "Только Ошибки", "Только Верные"])

    now = datetime.now()
    if time_filter == "24 Hours": df = df[df["Date"] >= now - timedelta(days=1)]
    elif time_filter == "7 Days": df = df[df["Date"] >= now - timedelta(days=7)]
    elif time_filter == "30 Days": df = df[df["Date"] >= now - timedelta(days=30)]
    elif time_filter == "1 Year": df = df[df["Date"] >= now - timedelta(days=365)]
        
    if spot_filter: df = df[df["Spot"].isin(spot_filter)]
    if res_filter == "Только Ошибки": df = df[df["Result"] == 0]
    elif res_filter == "Только Верные": df = df[df["Result"] == 1]

    if df.empty:
        st.warning("Нет данных по выбранным фильтрам.")
        return

    total_hands = len(df)
    correct_hands = df["Result"].sum()
    accuracy = int((correct_hands / total_hands) * 100) if total_hands > 0 else 0

    st.markdown("### Общая сводка")
    k1, k2, k3 = st.columns(3)
    k1.metric("Всего рук", total_hands)
    k2.metric("Точность", f"{accuracy}%")
    k3.metric("Ошибок", total_hands - correct_hands)

    st.divider()

    # --- БЛОК ЛИКФАЙНДЕРА (ТЕПЛОВАЯ КАРТА ДЫР) ---
    st.markdown("### 🔥 Leak Finder (Тепловая карта ошибок)")
    st.markdown("Скрипт анализирует хронические дыры. Показывает только те руки, где ты ошибся **минимум 2 раза** и процент ошибок **≥ 30%**.")
    
    unique_spots_all = df["Spot"].unique().tolist()
    target_spot = st.selectbox("Выбери спот для анализа дыр", unique_spots_all, index=0 if unique_spots_all else None)
    
    if target_spot:
        df_spot = df[df["Spot"] == target_spot]
        
        hand_stats = df_spot.groupby("Hand").agg(
            total=("Result", "count"),
            errors=("Result", lambda x: (x == 0).sum()),
            correct_action=("CorrectAction", lambda x: x.mode()[0] if not x.mode().empty else "FOLD")
        ).reset_index()
        
        # Жесткий фильтр: отсекаем случайные ошибки (нужно >=2 ошибок и винрейт с рукой <=70%)
        leaks = hand_stats[(hand_stats["errors"] >= 2) & (hand_stats["errors"] / hand_stats["total"] >= 0.3)]
        
        if leaks.empty:
            st.success(f"В споте '{target_spot}' у тебя нет хронических дыр. Так держать, машина!")
        else:
            lc1, lc2 = st.columns([2, 1])
            leaks_dict = {row['Hand']: {'errors': row['errors'], 'total': row['total'], 'correct_action': row['correct_action']} for _, row in leaks.iterrows()}
            
            with lc1:
                st.markdown(utils.render_leak_matrix(leaks_dict), unsafe_allow_html=True)
            
            with lc2:
                st.warning(f"Найдено дырявых рук: **{len(leaks)}**")
                
                overplays = leaks[leaks["correct_action"] == "FOLD"]["errors"].sum()
                underplays = leaks[leaks["correct_action"] == "RAISE"]["errors"].sum()
                passive_fails = leaks[leaks["correct_action"] == "CALL"]["errors"].sum()
                
                st.markdown("#### Твой диагноз:")
                if overplays > 0: 
                    st.markdown(f"- 🗑️ **Мусоришь (Overplay)**: {overplays} ошибок. Ты играешь (открываешь/коллишь/3-бетишь) то, что по GTO уходит в пас.")
                if underplays > 0: 
                    st.markdown(f"- 🐔 **Нитуешь (Underplay)**: {underplays} ошибок. Сбрасываешь или пассивно коллишь то, что нужно жестко рейзить.")
                if passive_fails > 0: 
                    st.markdown(f"- 🛡️ **Дыры защиты**: {passive_fails} ошибок. Оверфолдишь на стилы/3-беты, не тащишь по шансам.")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("⚔️ ТРЕНИРОВАТЬ ЭТИ ДЫРЫ", use_container_width=True):
                    st.session_state.leak_mode_active = True
                    st.session_state.leak_spot = target_spot
                    st.session_state.leak_hands = leaks["Hand"].tolist()
                    st.session_state.app_mode = "🎮 Trainer"
                    st.rerun()

    st.divider()

    st.markdown("### 📉 Худшие споты (Топ-10)")
    if not df.empty:
        stats = df.groupby("Spot")["Result"].agg(['count', 'sum', 'mean']).reset_index()
        stats["Errors"] = stats["count"] - stats["sum"]
        stats["Accuracy"] = (stats["mean"] * 100).astype(int)
        worst = stats.sort_values(by="Errors", ascending=False).head(10)
        st.dataframe(worst[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}), use_container_width=True, hide_index=True)

    with st.expander("📜 Полный лог (нажми, чтобы открыть)"):
        d = df.copy()
        d["Result"] = d["Result"].apply(lambda x: "✅" if x==1 else "❌")
        d = d.sort_values("Date", ascending=False)
        d["Date"] = d["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(d[["Date", "Spot", "Hand", "CorrectAction", "Result"]], use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("### 🗑️ Очистка истории")
    with st.expander("⚠️ Опасная зона", expanded=False):
        d1, d2, d3, d4 = st.columns(4)
        if d1.button("Стереть: 24 Часа", use_container_width=True):
            utils.delete_history(days=1); st.success("Готово!"); st.rerun()
        if d2.button("Стереть: Неделю", use_container_width=True):
            utils.delete_history(days=7); st.success("Готово!"); st.rerun()
        if d3.button("Стереть: Месяц", use_container_width=True):
            utils.delete_history(days=30); st.success("Готово!"); st.rerun()
        if d4.button("Стереть: Год", use_container_width=True):
            utils.delete_history(days=365); st.success("Готово!"); st.rerun()
