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
        st.error(f"Ошибка подключения к Google Sheets: Проверь секреты в Streamlit! {e}")
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

def init_cloud_data():
    if "app_initialized" not in st.session_state:
        sheets = get_worksheets()
        try:
            srs_vals = sheets["SRS"].get_all_values()
            st.session_state["srs_data"] = {str(r[0]): int(r[1]) for r in srs_vals[1:]} if len(srs_vals) > 1 else {}
        except: st.session_state["srs_data"] = {}
        
        try:
            set_val = sheets["Settings"].acell('A1').value
            st.session_state["user_settings"] = json.loads(set_val) if set_val else {}
        except: st.session_state["user_settings"] = {}
            
        st.session_state["history_buffer"] = []
        st.session_state["unsaved_count"] = 0
        st.session_state["settings_changed"] = False
        st.session_state["app_initialized"] = True

# --- GAMIFICATION & MASTERY CORE ---
def load_user_stats():
    init_cloud_data()
    sets = st.session_state.get("user_settings", {})
    stats = sets.get("stats", {})
    if "xp" not in stats: stats["xp"] = 0
    if "streak" not in stats: stats["streak"] = 0
    if "last_date" not in stats: stats["last_date"] = ""
    if "max_combo" not in stats: stats["max_combo"] = 0
    if "total_hands" not in stats: stats["total_hands"] = 0
    if "dailies" not in stats: stats["dailies"] = {"date": "", "quests": []}
    if "spot_mastery" not in stats: stats["spot_mastery"] = {}
    return stats

def save_user_stats(stats):
    sets = st.session_state.get("user_settings", {})
    sets["stats"] = stats
    save_user_settings(sets)

def get_rank_info(xp):
    tiers = [
        (0, "🐟 Fish"), (2000, "🪨 Nit"), (7500, "🚶 Reg"),
        (20000, "⚔️ Grinder"), (50000, "🦈 Shark"), (100000, "🎩 High Roller"),
        (250000, "👑 Boss"), (500000, "🤖 GTO Machine")
    ]
    current_rank = tiers[0][1]
    next_xp = tiers[1][0]
    for i, (req_xp, name) in enumerate(tiers):
        if xp >= req_xp:
            current_rank = name
            next_xp = tiers[i+1][0] if i+1 < len(tiers) else "MAX"
    return current_rank, next_xp

def generate_dailies():
    return [
        {"id": "play", "desc": "Сыграть 100 рук", "target": 100, "progress": 0, "done": False, "xp": 500},
        {"id": "correct", "desc": "50 верных ответов", "target": 50, "progress": 0, "done": False, "xp": 500},
        {"id": "combo", "desc": "Комбо x15", "target": 15, "progress": 0, "done": False, "xp": 1000}
    ]

def process_gamification(is_correct, combo, session_total_hands):
    stats = load_user_stats()
    now_date = datetime.now().date()
    now_date_str = now_date.strftime("%Y-%m-%d")
    alerts = []
    
    if stats["last_date"]:
        try:
            last_date = datetime.strptime(stats["last_date"], "%Y-%m-%d").date()
            delta = (now_date - last_date).days
            if delta == 1: stats["streak"] += 1
            elif delta > 1: stats["streak"] = 1
        except: stats["streak"] = 1
    else: stats["streak"] = 1
    stats["last_date"] = now_date_str
    
    stats["total_hands"] += 1
    if is_correct: stats["xp"] += 10
    if combo > stats.get("max_combo", 0): stats["max_combo"] = combo
    
    if stats["dailies"].get("date") != now_date_str:
        stats["dailies"] = {"date": now_date_str, "quests": generate_dailies()}
        
    for q in stats["dailies"]["quests"]:
        if not q["done"]:
            if q["id"] == "play": q["progress"] += 1
            elif q["id"] == "correct" and is_correct: q["progress"] += 1
            elif q["id"] == "combo" and combo > q["progress"]: q["progress"] = combo
            
            if q["progress"] >= q["target"]:
                q["progress"] = q["target"]
                q["done"] = True
                stats["xp"] += q["xp"]
                alerts.append(f"🎯 Дейлик: {q['desc']} (+{q['xp']} XP)")

    save_user_stats(stats)
    return alerts

def update_spot_mastery(spot_key, is_correct):
    stats = load_user_stats()
    if "spot_mastery" not in stats: stats["spot_mastery"] = {}
    
    sm = stats["spot_mastery"].get(spot_key, {})
    total = sm.get("total", 0)
    hist = sm.get("hist", "")
    
    total += 1
    hist += "1" if is_correct else "0"
    if len(hist) > 100: hist = hist[-100:]
    last = datetime.now().strftime("%Y-%m-%d")
    
    stats["spot_mastery"][spot_key] = {"total": total, "hist": hist, "last": last}
    save_user_stats(stats)

def get_spot_mastery_info(spot_key):
    stats = load_user_stats()
    sm = stats.get("spot_mastery", {}).get(spot_key, {})
    total = sm.get("total", 0)
    hist = sm.get("hist", "")
    last = sm.get("last", "")

    form = hist.count("1") / len(hist) * 100 if hist else 0.0

    days_since = 0
    if last:
        try: days_since = (datetime.now().date() - datetime.strptime(last, "%Y-%m-%d").date()).days
        except: pass

    is_rusty = days_since > 7

    tiers = [
        (0, 0, "Sandbox"),
        (100, 75, "Basic"),
        (500, 82, "Solid"),
        (1500, 88, "Unexploitable"),
        (3000, 92, "Elite"),
        (5000, 95, "Solver")
    ]

    current_idx = 0
    for i in range(len(tiers) - 1, -1, -1):
        if total >= tiers[i][0] and form >= tiers[i][1]:
            current_idx = i
            break

    if days_since > 14 and current_idx > 0:
        current_idx -= 1

    tier_name = tiers[current_idx][2]
    
    if current_idx < len(tiers) - 1:
        next_total = tiers[current_idx + 1][0]
        next_form = tiers[current_idx + 1][1]
        progress = min(100, int((total / next_total) * 100)) if next_total else 100
        if total >= next_total and form < next_form:
            progress = 99
    else:
        progress = 100

    return {
        "tier_name": tier_name, "total": total, "form": int(form), 
        "rusty": is_rusty, "progress": progress
    }

def get_mastery_svg(tier_name):
    base = "position:absolute; width:120px; height:120px; top:50%; transform:translateY(-50%); opacity:0.08; color:rgba(255,255,255,1); pointer-events:none; z-index:1;"
    svg_l = f'<svg style="{base} left:10%;" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    svg_r = f'<svg style="{base} right:10%;" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    
    spade = '<path d="M50 25 C50 25 35 45 35 60 C35 70 45 75 50 65 L46 80 L54 80 L50 65 C55 75 65 70 65 60 C65 45 50 25 50 25 Z" fill="currentColor"/>'
    shield = '<path d="M25 20 L75 20 L75 55 C75 75 50 90 50 90 C50 90 25 75 25 55 Z" fill="none" stroke="currentColor" stroke-width="4"/>'
    swords = '<path d="M20 80 L80 20 M20 20 L80 80" stroke="currentColor" stroke-width="3"/><circle cx="20" cy="80" r="3" fill="currentColor"/><circle cx="80" cy="80" r="3" fill="currentColor"/><circle cx="20" cy="20" r="3" fill="currentColor"/><circle cx="80" cy="20" r="3" fill="currentColor"/>'
    crown = '<path d="M35 15 L40 5 L50 15 L60 5 L65 15 L65 20 L35 20 Z" fill="currentColor"/>'
    laurels = '<path d="M20 90 C0 60 10 20 25 10 M80 90 C100 60 90 20 75 10" fill="none" stroke="currentColor" stroke-width="3"/>'

    content = ""
    if tier_name == "Sandbox": return "", ""
    elif tier_name == "Basic": content = spade
    elif tier_name == "Solid": content = shield + spade
    elif tier_name == "Unexploitable": content = swords + shield + spade
    elif tier_name == "Elite": content = swords + shield + spade + crown
    elif tier_name == "Solver": content = laurels + swords + shield + spade + crown

    return svg_l + content + '</svg>', svg_r + content + '</svg>'

# --- SAVE & SYNC ---
def load_srs_data():
    init_cloud_data()
    return st.session_state.get("srs_data", {})

def update_srs_smart(spot_id, hand, rating):
    init_cloud_data()
    data = st.session_state["srs_data"]
    key = f"{spot_id}_{hand}"
    w = data.get(key, 100)
    
    if rating == 'hard': w *= 2.5
    elif rating == 'normal': w = w / 1.5 if w > 100 else w * 1.2
    elif rating == 'easy': w /= 4.0
    
    data[key] = int(max(1, min(w, 2000)))
    st.session_state["unsaved_count"] += 1
    check_auto_sync()

def load_user_settings():
    init_cloud_data()
    return st.session_state.get("user_settings", {})

def save_user_settings(settings):
    init_cloud_data()
    st.session_state["user_settings"] = settings
    st.session_state["settings_changed"] = True
    st.session_state["unsaved_count"] += 1
    check_auto_sync()

def save_to_history(record):
    init_cloud_data()
    row = [str(record.get("Date", "")), str(record.get("Spot", "")), str(record.get("Hand", "")), str(record.get("Result", "")), str(record.get("CorrectAction", ""))]
    st.session_state["history_buffer"].append(row)
    st.session_state["unsaved_count"] += 1
    check_auto_sync()

def check_auto_sync():
    if st.session_state["unsaved_count"] >= 5: force_sync()

def force_sync():
    if st.session_state.get("unsaved_count", 0) == 0: return
    sheets = get_worksheets()
    try:
        if "srs_data" in st.session_state:
            rows = [["Key", "Weight"]] + [[k, v] for k, v in st.session_state["srs_data"].items()]
            sheets["SRS"].update(values=rows, range_name="A1")
        if "history_buffer" in st.session_state and st.session_state["history_buffer"]:
            sheets["History"].append_rows(st.session_state["history_buffer"])
            st.session_state["history_buffer"] = []
        if st.session_state.get("settings_changed"):
            sheets["Settings"].update_acell('A1', json.dumps(st.session_state["user_settings"]))
            st.session_state["settings_changed"] = False
            
        st.session_state["unsaved_count"] = 0
    except: pass

@st.cache_data(ttl=60)
def load_history():
    try:
        vals = get_worksheets()["History"].get_all_values()
        if not vals or len(vals) < 2: return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction"])
        return pd.DataFrame(vals[1:], columns=vals[0])
    except: return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction"])

def delete_history(days=None):
    try:
        sheets = get_worksheets()
        if days is None:
            sheets["History"].clear()
            sheets["History"].append_row(["Date", "Spot", "Hand", "Result", "CorrectAction"])
        else:
            df = load_history()
            if df.empty: return
            df["Date"] = pd.to_datetime(df["Date"])
            now = datetime.now()
            cutoff = now - timedelta(days=days)
            df_new = df[df["Date"] >= cutoff] 
            sheets["History"].clear()
            rows = [["Date", "Spot", "Hand", "Result", "CorrectAction"]] + df_new.astype(str).values.tolist()
            sheets["History"].update(values=rows, range_name="A1")
        load_history.clear()
        if "history_buffer" in st.session_state: st.session_state["history_buffer"] = []
    except Exception as e: st.error(f"Ошибка удаления истории: {e}")

@st.cache_data(ttl=0)
def load_ranges():
    db = {}
    if not os.path.exists(SPOTS_DIR): return db
    for file in os.listdir(SPOTS_DIR):
        if file.endswith('.json'):
            with open(os.path.join(SPOTS_DIR, file), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    src = data.get("source", "Unknown")
                    sc = data.get("scenario", "Unknown")
                    if src not in db: db[src] = {}
                    if sc not in db[src]: db[src][sc] = {}
                    db[src][sc].update(data.get("spots", {}))
                except Exception as e: st.error(f"Ошибка чтения {file}: {e}")
    return db

ALL_HANDS = []
for i, r1 in enumerate(RANKS):
    for j, r2 in enumerate(RANKS):
        if i < j: ALL_HANDS.append(r1 + r2 + 's'); ALL_HANDS.append(r1 + r2 + 'o')
        elif i == j: ALL_HANDS.append(r1 + r2)

def get_weight(hand, range_str):
    if not range_str or not isinstance(range_str, str): return 0.0
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if ':' in item:
            h_part, w_part = item.split(':')
            try:
                weight = float(w_part)
                if weight <= 1.0: weight *= 100
            except: weight = 100.0
        else:
            h_part = item
            weight = 100.0
        if h_part == hand: return weight
        if len(h_part) == 2 and h_part[0] != h_part[1] and hand.startswith(h_part): return weight
    return 0.0

def parse_range_to_list(range_str):
    if not range_str or not isinstance(range_str, str) or "22+" in range_str or range_str == "ALL": return ALL_HANDS.copy()
    hand_list = []
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if not item: continue
        h = item.split(':')[0]
        if h in ALL_HANDS: hand_list.append(h)
        elif len(h) == 2:
            if h[0] == h[1]: hand_list.append(h)
            else: hand_list.extend([h+'s', h+'o'])
    if not hand_list: return ALL_HANDS.copy()
    return list(set(hand_list))

def render_range_matrix(spot_data, target_hand=None):
    ranges = spot_data.get("ranges", spot_data)
    r_call = ranges.get("call", ranges.get("Call", ""))
    r_raise = ranges.get("4bet", ranges.get("3bet", ranges.get("Raise", "")))
    r_full = ranges.get("full", ranges.get("Full", ""))
    
    grid_html = '<div style="display:grid;grid-template-columns:repeat(13,1fr);gap:1px;background:#111;padding:1px;border:1px solid #444;">'
    for r1 in RANKS:
        for r2 in RANKS:
            if RANKS.index(r1) == RANKS.index(r2): h = r1 + r2
            elif RANKS.index(r1) < RANKS.index(r2): h = r1 + r2 + 's'
            else: h = r2 + r1 + 'o'
            
            w_c = get_weight(h, r_call)
            w_4 = get_weight(h, r_raise)
            w_f = get_weight(h, r_full)
            
            raise_w = w_4 if w_4 > 0 else w_f
            call_w = w_c
            
            total_w = raise_w + call_w
            if total_w > 100:
                raise_w = (raise_w / total_w) * 100
                call_w = (call_w / total_w) * 100
            
            style = "aspect-ratio:1;display:flex;justify-content:center;align-items:center;font-size:7px;cursor:default;color:#fff;"
            
            if raise_w == 0 and call_w == 0:
                bg = "#2c3034"
                style += "color:#495057;"
            elif raise_w >= 100: bg = "#d63384"
            elif call_w >= 100: bg = "#28a745"
            else:
                stops = []
                curr_pct = 0.0
                if raise_w > 0:
                    stops.append(f"#d63384 {curr_pct}%")
                    curr_pct += raise_w
                    stops.append(f"#d63384 {curr_pct}%")
                if call_w > 0:
                    stops.append(f"#28a745 {curr_pct}%")
                    curr_pct += call_w
                    stops.append(f"#28a745 {curr_pct}%")
                if curr_pct < 100:
                    stops.append(f"#2c3034 {curr_pct}%")
                    stops.append(f"#2c3034 100%")
                bg = f"linear-gradient(to right, {', '.join(stops)})"
            
            style += f"background:{bg};"
            if target_hand and h == target_hand: style += "border:1.5px solid #ffc107;z-index:10;box-shadow: 0 0 4px #ffc107;"
            grid_html += f'<div style="{style}" title="{h} | Raise: {raise_w:.0f}%, Call: {call_w:.0f}%">{h}</div>'
    grid_html += '</div>'

    stats = spot_data.get("stats", {})
    if stats:
        stats_html = '<div style="display:flex; gap:8px; justify-content:center; margin-top:10px; flex-wrap:wrap; font-size:12px; font-weight:bold; font-family:sans-serif;">'
        for k, v in stats.items():
            kl = k.lower()
            if "raise" in kl or "3bet" in kl or "4bet" in kl or "pfr" in kl: color = "#d63384" 
            elif "call" in kl: color = "#28a745" 
            elif "fold" in kl: color = "#6c757d" 
            else: color = "#adb5bd" 
            stats_html += f'<div style="background:#222; border:1px solid {color}; color:{color}; padding:4px 10px; border-radius:6px; box-shadow: 0 2px 4px rgba(0,0,0,0.4);">{k} {v}</div>'
        stats_html += '</div>'
        grid_html += stats_html
    return grid_html

def render_leak_matrix(leaks_dict):
    grid_html = '<div style="display:grid;grid-template-columns:repeat(13,1fr);gap:1px;background:#111;padding:1px;border:1px solid #444;">'
    max_errors = max([v['errors'] for v in leaks_dict.values()]) if leaks_dict else 1
    
    for r1 in RANKS:
        for r2 in RANKS:
            if RANKS.index(r1) == RANKS.index(r2): h = r1 + r2
            elif RANKS.index(r1) < RANKS.index(r2): h = r1 + r2 + 's'
            else: h = r2 + r1 + 'o'
            
            style = "aspect-ratio:1;display:flex;justify-content:center;align-items:center;font-size:7px;cursor:default;color:#fff;"
            
            if h in leaks_dict:
                err = leaks_dict[h]['errors']
                tot = leaks_dict[h]['total']
                act = leaks_dict[h]['correct_action']
                
                intensity = 0.4 + 0.6 * (err / max_errors)
                bg = f"rgba(220, 53, 69, {intensity})"
                title = f"{h} | Ошибок: {err}/{tot} | GTO действие: {act}"
                
                border = "1px solid rgba(255,255,255,0.2)"
                style += f"background:{bg}; {border}; font-weight:bold;"
            else:
                bg = "#2c3034"
                title = f"{h} | Нет дыр"
                style += f"background:{bg}; color:#495057;"
            
            grid_html += f'<div style="{style}" title="{title}">{h}</div>'
    grid_html += '</div>'
    return grid_html
