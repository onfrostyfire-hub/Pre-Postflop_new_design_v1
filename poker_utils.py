import streamlit as st
import json
import pandas as pd
import os
import random
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

SPOTS_DIR = 'spots_data'
RANKS = 'AKQJT98765432'

# --- GOOGLE SHEETS CORE ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SPREADSHEET_ID = '15ouWJYZuQET1-sy7k5Wrn1fAzNUX6ssk5K8SOM9uYOc'

@st.cache_resource
def get_gspread_client():
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_JSON"])
        creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Google Sheets Connection Error: {e}")
        st.stop()

@st.cache_resource
def get_worksheets():
    client = get_gspread_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    return {
        "SRS": sh.worksheet("SRS"),
        "Settings": sh.worksheet("Settings"),
        "History": sh.worksheet("History")
    }

# --- LOAD RANGES ---
@st.cache_data
def load_ranges():
    ranges = {}
    if not os.path.exists(SPOTS_DIR):
        return ranges
    for file in os.listdir(SPOTS_DIR):
        if file.endswith('.json'):
            with open(os.path.join(SPOTS_DIR, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                ranges[data['source']] = ranges.get(data['source'], {})
                ranges[data['source']][data['scenario']] = data['spots']
    return ranges

# --- DB LOGIC & SYNC ---
def load_history():
    try:
        ws = get_worksheets()["History"]
        records = ws.get_all_records()
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()

def delete_history(days=1):
    ws = get_worksheets()["History"]
    df = load_history()
    if df.empty: return
    cutoff = datetime.now() - timedelta(days=days)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df_keep = df[df['Date'] > cutoff]
    
    data = [df_keep.columns.values.tolist()] + df_keep.values.tolist()
    try:
        ws.clear()
        try:
            ws.update(values=data, range_name="A1")
        except TypeError:
            ws.update("A1", data)
    except Exception as e:
        print(f"Delete history error: {e}")

def init_cloud_data():
    ws = get_worksheets()
    if "srs_data" not in st.session_state:
        try:
            records = ws["SRS"].get_all_records()
            st.session_state["srs_data"] = {str(r["Key"]): float(r["Weight"]) for r in records}
        except Exception:
            st.session_state["srs_data"] = {}

def force_sync():
    """Железобетонное сохранение весов без лагов и падений API"""
    ws = get_worksheets()
    srs_data = st.session_state.get("srs_data", {})
    if not srs_data:
        return

    # Пакуем данные для пакетной отправки
    data = [["Key", "Weight"]] + [[k, round(float(v), 2)] for k, v in srs_data.items()]
    
    try:
        ws["SRS"].clear()
        try:
            ws["SRS"].update(values=data, range_name="A1") # Для gspread v6+
        except TypeError:
            ws["SRS"].update("A1", data) # Fallback для старых версий
    except Exception as e:
        print(f"Critical SRS Sync Failure: {e}")

# --- SMART SRS ALGORITHM ---
def update_srs_weight(key, is_correct):
    srs_data = st.session_state.get("srs_data", {})
    current_w = srs_data.get(key, 100.0)

    if is_correct:
        new_w = max(10.0, current_w * 0.8)
    else:
        penalty = 20 if current_w < 50 else 50
        new_w = min(1000.0, (current_w * 1.5) + penalty)
        
    srs_data[key] = new_w
    st.session_state["srs_data"] = srs_data
    
    if "hands_played" not in st.session_state:
        st.session_state["hands_played"] = 0
    st.session_state["hands_played"] += 1
    
    # Синк каждые 5 раздач для разгрузки сети
    if st.session_state["hands_played"] % 5 == 0:
        force_sync()

def get_next_hand(spot_key, training_hands_str):
    """Выбор следующей руки на основе весов SRS"""
    srs_data = st.session_state.get("srs_data", {})
    hands = [h.strip() for h in training_hands_str.split(',') if h.strip()]
    weights = []
    
    for h in hands:
        k = f"{spot_key}_{h}".replace(" ", "_")
        weights.append(srs_data.get(k, 100.0))
        
    return random.choices(hands, weights=weights, k=1)[0]

def log_hand(spot, hand, result, correct_action, user_action):
    try:
        ws = get_worksheets()["History"]
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            spot,
            hand,
            int(result),
            correct_action,
            user_action
        ]
        ws.append_row(row)
    except Exception as e:
        print(f"Log hand error: {e}")

# --- UI HELPERS ---
def render_range(sp_name, target_hand=None):
    srs_data = st.session_state.get("srs_data", {})
    grid_html = '<div style="display:grid; grid-template-columns:repeat(13, 1fr); gap:2px; max-width:100%; margin:auto;">'
    
    for r1 in RANKS:
        for r2 in RANKS:
            if RANKS.index(r1) < RANKS.index(r2): h = f"{r1}{r2}s"
            elif RANKS.index(r1) > RANKS.index(r2): h = f"{r2}{r1}o"
            else: h = f"{r1}{r2}"
            
            key = f"{sp_name}_{h}".replace(" ", "_")
            w = srs_data.get(key, 100)
            
            if w <= 10: bg = "#0f5132" # Mastered
            elif w <= 50: bg = "#198754" # Good
            elif w <= 150: bg = "#2c3034" # Base
            elif w <= 500: bg = "#854000" # Warning
            elif w <= 1000: bg = "#fd7e14" # Danger
            else: bg = "#dc3545" # Leak
            
            style = f"aspect-ratio:1;display:flex;justify-content:center;align-items:center;font-size:8px;cursor:default;color:#fff;background:{bg};"
            if target_hand and h == target_hand: 
                style += "border:1.5px solid #ffc107;z-index:10;box-shadow: 0 0 4px #ffc107;"
                
            grid_html += f'<div style="{style}" title="{h} | Weight: {w:.1f}">{h}</div>'
            
    grid_html += '</div>'
    return grid_html
