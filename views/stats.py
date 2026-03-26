import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import poker_utils as utils

def show():
    st.markdown("## 📊 Statistics Hub")
    
    df = utils.load_history()
    
    if df.empty or "Date" not in df.columns or "Result" not in df.columns:
        st.info("History is empty. Go train, Boss!")
        return

    # Подмена старых названий спотов на новые (на лету, без насилия над базой данных)
    rename_map = {
        "BUvsCO": "3bet BUvsCO",
        "SBvsCO": "3bet SBvsCO",
        "SBvsBU": "3bet SBvsBU",
        "BBvsCO": "3bet BBvsCO",
        "BBvsBU": "3bet BBvsBU",
        "BBvsSB": "3bet BBvsSB"
    }
    df["Spot"] = df["Spot"].replace(rename_map)

    # Очистка и форматирование
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)
    
    if df.empty:
        st.info("History is empty. Go train, Boss!")
        return

    st.markdown("### 📈 Performance")
    total_hands = len(df)
    total_correct = df["Result"].sum()
    winrate = (total_correct / total_hands * 100) if total_hands > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Hands", total_hands)
    c2.metric("Correct", total_correct)
    c3.metric("Accuracy", f"{winrate:.1f}%")

    st.markdown("### 🎯 Spots Mastery")
    stats = df.groupby("Spot")["Result"].agg(["count", "sum", "mean"]).reset_index()
    stats["Errors"] = stats["count"] - stats["sum"]
    stats["Accuracy"] = (stats["mean"] * 100).astype(int).astype(str) + "%"
    all_spots = stats.sort_values(by="count", ascending=False)
    st.dataframe(all_spots[["Spot", "Errors", "Accuracy", "count"]].rename(columns={"count": "Total"}), use_container_width=True, hide_index=True)

    with st.expander("📜 Raw History Log (click to expand)"):
        d = df.copy()
        d["Result"] = d["Result"].apply(lambda x: "✅" if x==1 else "❌")
        d = d.sort_values("Date", ascending=False)
        d["Date"] = d["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        cols_to_show = ["Date", "Spot", "Hand", "CorrectAction", "UserAction", "Result"] if "UserAction" in d.columns else ["Date", "Spot", "Hand", "CorrectAction", "Result"]
        st.dataframe(d[cols_to_show], use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("### 🚑 Data Recovery")
    with st.expander("Recover Spot Mastery from History", expanded=False):
        st.markdown("If your progress got reset, this will recalculate your experience, streak, and Spot Mastery from raw history.")
        
        if st.button("🔧 RECOVER SPOT MASTERY", use_container_width=True):
            df_hist = df.copy().sort_values("Date")
            new_mastery = {}
            total_correct = df_hist["Result"].sum()
            
            # Собираем уникальные даты для подсчета стрика
            unique_dates = sorted(df_hist["Date"].dt.date.unique())
            streak = 1
            if unique_dates:
                current_streak = 1
                for i in range(1, len(unique_dates)):
                    if (unique_dates[i] - unique_dates[i-1]).days == 1:
                        current_streak += 1
                    else:
                        current_streak = 1
                streak = current_streak

            # Восстанавливаем Spot Mastery
            ranges_db = utils.load_ranges()
            sp_to_full_key = {}
            for src, sc_dict in ranges_db.items():
                for sc, sp_dict in sc_dict.items():
                    for sp in sp_dict.keys():
                        sp_to_full_key[sp] = f"{src}|{sc}|{sp}"

            for _, row in df_hist.iterrows():
                sp = row["Spot"]
                if sp not in sp_to_full_key:
                    continue 
                    
                full_key = sp_to_full_key[sp]
                if full_key not in new_mastery:
                    new_mastery[full_key] = {"t": 0, "h": "", "d": ""}
                    
                new_mastery[full_key]["t"] += 1
                new_mastery[full_key]["h"] += "1" if row["Result"] == 1 else "0"
                if len(new_mastery[full_key]["h"]) > 100:
                    new_mastery[full_key]["h"] = new_mastery[full_key]["h"][-100:]
                new_mastery[full_key]["d"] = row["Date"].strftime("%Y-%m-%d")

            stats_dict = utils.load_user_stats()
            stats_dict["xp"] = int(total_correct * 10)
            stats_dict["total_hands"] = len(df_hist)
            stats_dict["streak"] = streak
            stats_dict["spot_mastery"] = new_mastery
            if unique_dates:
                stats_dict["last_date"] = unique_dates[-1].strftime("%Y-%m-%d")
                
            utils.save_user_stats(stats_dict)
            st.success("✅ Recovery complete! Refresh the page.")
            st.rerun()

    st.markdown("### 🗑️ Danger Zone")
    with st.expander("Clear History", expanded=False):
        d1, d2, d3, d4 = st.columns(4)
        if d1.button("Delete: 24 Hours", use_container_width=True):
            utils.delete_history(days=1); st.success("Done!"); st.rerun()
        if d2.button("Delete: 7 Days", use_container_width=True):
            utils.delete_history(days=7); st.success("Done!"); st.rerun()
        if d3.button("Delete: 30 Days", use_container_width=True):
            utils.delete_history(days=30); st.success("Done!"); st.rerun()
        if d4.button("NUKE ALL HISTORY", use_container_width=True):
            utils.delete_history(); st.success("Done!"); st.rerun()
