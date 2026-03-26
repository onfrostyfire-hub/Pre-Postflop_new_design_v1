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

    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    df["Result"] = pd.to_numeric(df["Result"], errors='coerce').fillna(0).astype(int)
    
    if df.empty:
        st.info("History is empty. Go train, Boss!")
        return

    st.markdown("### 🚑 Data Recovery")
    with st.expander("Recover Spot Mastery & SRS from History", expanded=False):
        st.markdown("If your progress or hand weights got reset, this will recalculate everything from raw history.")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔧 RECOVER SPOT MASTERY", use_container_width=True):
                df_hist = df.copy().sort_values("Date")
                new_mastery = {}
                total_correct = 0
                unique_dates = set()
                
                ranges_db = utils.load_ranges()
                sp_to_full_key = {}
                for src, sc_dict in ranges_db.items():
                    for sc, sp_dict in sc_dict.items():
                        for sp in sp_dict.keys():
                            sp_to_full_key[sp] = f"{src}|{sc}|{sp}"
                
                for _, row in df_hist.iterrows():
                    short_spot = str(row["Spot"])
                    res_int = int(row["Result"])
                    res_str = str(res_int)
                    date_obj = row["Date"].date()
                    date_str = date_obj.strftime("%Y-%m-%d")
                    
                    unique_dates.add(date_obj)
                    if res_int == 1: total_correct += 1
                    
                    full_key = sp_to_full_key.get(short_spot, short_spot)
                    if full_key not in new_mastery: new_mastery[full_key] = {"t": 0, "h": "", "d": ""}
                    
                    new_mastery[full_key]["t"] += 1
                    new_mastery[full_key]["d"] = date_str
                    new_mastery[full_key]["h"] += res_str
                    
                    if len(new_mastery[full_key]["h"]) > 100:
                        new_mastery[full_key]["h"] = new_mastery[full_key]["h"][-100:]
                
                sorted_dates = sorted(list(unique_dates), reverse=True)
                streak = 1 if sorted_dates else 0
                if sorted_dates:
                    curr_d = sorted_dates[0]
                    for d in sorted_dates[1:]:
                        if (curr_d - d).days == 1:
                            streak += 1
                            curr_d = d
                        else: break
                            
                stats = utils.load_user_stats()
                stats["spot_mastery"] = new_mastery
                stats["total_hands"] = len(df_hist)
                stats["xp"] = total_correct * 10
                stats["streak"] = streak
                if sorted_dates: stats["last_date"] = sorted_dates[0].strftime("%Y-%m-%d")
                    
                utils.save_user_stats(stats)
                utils.force_sync()
                st.success("✅ Spot Mastery recovered! Refresh the page.")

        with c2:
            if st.button("🧠 REBUILD SRS FROM HISTORY", type="primary", use_container_width=True):
                utils.rebuild_srs_from_history()
                st.success("✅ Neural weights (SRS) rebuilt for all hands! Check the Google Sheet.")

    with st.expander("🔍 Filters", expanded=False):
        c1, c2, c3 = st.columns(3)
        time_filter = c1.selectbox("Timeframe", ["All Time", "24 Hours", "7 Days", "30 Days", "1 Year"])
        unique_spots = df["Spot"].unique().tolist()
        spot_filter = c2.multiselect("Spots", unique_spots, default=unique_spots)
        res_filter = c3.selectbox("Result", ["All", "Errors Only", "Correct Only"])

    now = datetime.now()
    if time_filter == "24 Hours": df = df[df["Date"] >= now - timedelta(days=1)]
    elif time_filter == "7 Days": df = df[df["Date"] >= now - timedelta(days=7)]
    elif time_filter == "30 Days": df = df[df["Date"] >= now - timedelta(days=30)]
    elif time_filter == "1 Year": df = df[df["Date"] >= now - timedelta(days=365)]
        
    if spot_filter: df = df[df["Spot"].isin(spot_filter)]
    if res_filter == "Errors Only": df = df[df["Result"] == 0]
    elif res_filter == "Correct Only": df = df[df["Result"] == 1]

    if df.empty:
        st.warning("No data found for these filters.")
        return

    total_hands = len(df)
    correct_hands = df["Result"].sum()
    accuracy = int((correct_hands / total_hands) * 100) if total_hands > 0 else 0

    st.markdown("### Overall Summary")
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Hands", total_hands)
    k2.metric("Accuracy", f"{accuracy}%")
    k3.metric("Errors", total_hands - correct_hands)

    st.divider()

    st.markdown("### 📉 Spots Breakdown")
    if not df.empty:
        stats = df.groupby("Spot")["Result"].agg(['count', 'sum', 'mean']).reset_index()
        stats["Errors"] = stats["count"] - stats["sum"]
        stats["Accuracy"] = (stats["mean"] * 100).astype(int)
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

    st.markdown("### 🗑️ Danger Zone")
    with st.expander("Clear History", expanded=False):
        d1, d2, d3, d4 = st.columns(4)
        if d1.button("Delete: 24 Hours", use_container_width=True):
            utils.delete_history(days=1); st.success("Done!"); st.rerun()
        if d2.button("Delete: 7 Days", use_container_width=True):
            utils.delete_history(days=7); st.success("Done!"); st.rerun()
        if d3.button("Delete: 30 Days", use_container_width=True):
            utils.delete_history(days=30); st.success("Done!"); st.rerun()
        if d4.button("Delete: 1 Year", use_container_width=True):
            utils.delete_history(days=365); st.success("Done!"); st.rerun()
