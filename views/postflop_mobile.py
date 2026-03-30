import streamlit as st
import random
from datetime import datetime
import poker_utils as utils

ACTION_COLORS = ["#28a745", "#d63384", "#0dcaf0", "#ffc107", "#6f42c1"]

def map_suit(s):
    mapping = {'h': '♥\ufe0e', 'd': '♦\ufe0e', 'c': '♣\ufe0e', 's': '♠\ufe0e'}
    return mapping.get(s.lower(), '♠\ufe0e')

def get_suit_color_class(s):
    if '♥' in s: return "suit-red"
    if '♦' in s: return "suit-blue"
    if '♣' in s: return "suit-green"
    return "suit-black"

def pf_parse_range(r_str):
    if not r_str: return []
    return [x.split(':')[0].strip() for x in r_str.split(',')]

def pf_get_weight(hand, r_str):
    if not r_str: return 0.0
    items = [x.strip() for x in r_str.split(',')]
    for item in items:
        if not item: continue
        parts = item.split(':')
        h = parts[0].strip()
        w = float(parts[1])*100 if len(parts)>1 and float(parts[1])<=1.0 else (float(parts[1]) if len(parts)>1 else 100.0)
        if h == hand: return w
    return 0.0

def show():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500;700;900&display=swap');

        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 100% !important; overflow-x: hidden !important; }
        [data-testid="stExpander"] { margin-top: -5px !important; margin-bottom: 5px !important; }
        
        div[data-testid="stHorizontalBlock"] { display: grid !important; grid-template-columns: repeat(auto-fit, minmax(10px, 1fr)) !important; gap: 8px !important; width: 100% !important; }
        div[data-testid="column"] { width: 100% !important; min-width: 0 !important; max-width: 100% !important; margin-bottom: 0 !important; }
        div[data-testid="stButton"] { width: 100% !important; }
        div[data-testid="stButton"] button { width: 100% !important; height: 50px !important; padding: 0 !important; border-radius: 12px !important; border: none !important; transition: transform 0.1s !important; background: #343a40 !important; color: #fff !important; box-shadow: 0 4px 0 #1d2124 !important; }
        div[data-testid="stButton"] button:active { transform: translateY(4px) !important; box-shadow: 0 0 0 transparent !important; }
        div[data-testid="stButton"] button p { font-family: 'Roboto', sans-serif !important; font-size: 15px !important; font-weight: 900 !important; margin: 0 !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; }

        .mobile-game-area { position: relative; width: 100%; height: 280px; margin: 35px auto 10px auto; background: radial-gradient(ellipse at center, #1b5e20 0%, #0a2e0b 100%); border: 6px solid #3e2723; border-radius: 125px; box-shadow: 0 4px 15px rgba(0,0,0,0.8); transition: box-shadow 0.3s, border-color 0.3s; }
        
        .mastery-glow { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: inherit; pointer-events: none; z-index: 1; transition: box-shadow 0.5s ease; }
        .crest-left-mob { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 75px; height: 75px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        .crest-right-mob { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); width: 75px; height: 75px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        
        .center-column-mob { position: absolute; top: 12%; left: 50%; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; gap: 4px; width: 100%; z-index: 20; }
        .mob-info-spot { font-size: 16px; font-weight: 900; color: rgba(255,255,255,0.3); text-transform: uppercase; line-height: 1; text-align: center; }
        .pot-badge-mob { background: #111; color: #ffc107; font-weight: bold; font-size: 11px; padding: 2px 10px; border-radius: 12px; border: 1px solid #ffc107; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .board-container-mob { display: flex; gap: 4px; background: rgba(0,0,0,0.4); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 2px 10px rgba(0,0,0,0.4); }
        .mastery-badge { font-size: 9px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 2px 8px; border-radius: 10px; display: inline-flex; align-items: center; gap: 4px; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.1); }
        .rusty-True { filter: grayscale(100%) opacity(0.6); }
        .mastery-bar-bg { width: 80px; height: 3px; background: #111; border-radius: 2px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.8); }
        .mastery-bar-fill { height: 100%; transition: width 0.3s; }
        .hands-left-mob { font-size: 8px; color: #aaa; text-transform: uppercase; font-weight: bold; margin-top: -2px; }

        .board-card-mob { width: 38px; height: 54px; background: white; border-radius: 3px; position: relative; color: black; box-shadow: 0 1px 3px rgba(0,0,0,0.5); font-family: Arial, sans-serif !important; }
        .bc-tl-mob { position: absolute; top: 2px; left: 3px; font-weight: bold; font-size: 12px; line-height: 1; }
        .bc-c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 20px; line-height: 1; }

        .seat { position: absolute; width: 44px; height: 44px; background: #222; border: 1px solid #444; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 9px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 2px; }
        .seat-active { border-color: #ffc107; background: #2a2a2a; }
        .seat-folded { opacity: 0.4; border-color: #333; }
        
        .opp-cards-mob { position: absolute; top: -14px; display: flex; z-index: 20; }
        .opp-card-mob { width: 18px; height: 26px; background: #fff; border-radius: 2px; border: 1px solid #777; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 1px 1px 3px rgba(0,0,0,0.8); }
        .opp-card-mob.right { margin-left: -8px; transform: rotate(12deg) translateY(2px); }

        .villain-act-badge-mob { position: absolute; background: #dc3545; color: #fff; font-weight: bold; font-size: 9px; padding: 1px 5px; border-radius: 4px; border: 1px solid #ffaaaa; box-shadow: 0 2px 3px rgba(0,0,0,0.5); z-index: 25; text-transform: uppercase; white-space: nowrap; left: 50%; transform: translateX(-50%); }
        .act-bottom-mob { bottom: -18px; } .act-top-mob { top: -18px; }

        .dealer-mob { width: 16px; height: 16px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 9px; display: flex; justify-content: center; align-items: center; border: 1px solid #bfa006; position: absolute; z-index: 15; box-shadow: 1px 1px 2px rgba(0,0,0,0.6); }
        
        .chip-container { position: absolute; z-index: 25; display: flex; flex-direction: column; align-items: center; pointer-events: none; }
        .chip-mob { width: 14px; height: 14px; background: #111; border: 2px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .bet-txt { font-size: 10px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px #000; background: rgba(0,0,0,0.6); padding: 1px 3px; border-radius: 4px; margin-top: -5px; z-index: 20; text-transform: lowercase;}

        .hero-mob { position: absolute; bottom: -15px; left: 50%; transform: translateX(-50%); display: flex; gap: 5px; z-index: 30; background: #222; padding: 4px 8px; border-radius: 12px; border: 1px solid #ffc107; }
        .card-mob { width: 38px; height: 54px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); font-family: Arial, sans-serif !important; }
        .tl-mob { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 12px; line-height: 1; }
        .c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 20px; line-height: 1; }
        
        .suit-red { color: #d32f2f !important; font-family: Arial, sans-serif !important; } 
        .suit-blue { color: #0056b3 !important; font-family: Arial, sans-serif !important; } 
        .suit-black { color: #111 !important; font-family: Arial, sans-serif !important; } 
        .suit-green { color: #198754 !important; font-family: Arial, sans-serif !important; }
        
        .rng-badge { position: absolute; top: 50%; right: -36px; transform: translateY(-50%); width: 28px; height: 28px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 11px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 40; }
        .info-badge-mob { position: absolute; top: 50%; left: -36px; transform: translateY(-50%); width: 28px; height: 28px; background: #17a2b8; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 14px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 40; text-decoration: none; }
        
        .combo-glow-5 { border-color: #0dcaf0 !important; box-shadow: 0 0 10px rgba(13, 202, 240, 0.4), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-10 { border-color: #ffc107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.5), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-25 { border-color: #fd7e14 !important; box-shadow: 0 0 20px rgba(253, 126, 20, 0.6), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-50 { border-color: #dc3545 !important; box-shadow: 0 0 30px rgba(220, 53, 69, 0.7), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-100 { border-color: #6f42c1 !important; box-shadow: 0 0 40px rgba(111, 66, 193, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; }
        </style>
    """, unsafe_allow_html=True)

    pf_db = utils.load_postflop_ranges()
    if not pf_db: st.error("База пуста"); return

    tree = {}
    for full_key in pf_db.keys():
        parts = [p.strip() for p in full_key.split('|')]
        if len(parts) != 5: continue
        spot, hero_pos_key, street, branch, board = parts
        if spot not in tree: tree[spot] = {}
        if hero_pos_key not in tree[spot]: tree[spot][hero_pos_key] = {}
        if street not in tree[spot][hero_pos_key]: tree[spot][hero_pos_key][street] = {}
        if branch not in tree[spot][hero_pos_key][street]: tree[spot][hero_pos_key][street][branch] = []
        tree[spot][hero_pos_key][street][branch].append((board, full_key))

    with st.expander("⚙️ PF Filters", expanded=False):
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            if st.button("📱 Mobile", key="mv_btn"): st.session_state.actual_view_type = "📱 Mobile"; st.rerun()
        with c_v2:
            if st.button("💻 Desktop", key="dv_btn"): st.session_state.actual_view_type = "💻 Desktop"; st.rerun()
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

        saved = utils.load_user_settings(is_postflop=True)
        
        all_spots = sorted(list(tree.keys()))
        sel_spots = st.multiselect("1. Spot(s)", all_spots, default=[x for x in saved.get("pf_sel_spots", []) if x in all_spots])
        
        avail_heroes = set()
        for sp in sel_spots: avail_heroes.update(tree[sp].keys())
        avail_heroes = sorted(list(avail_heroes))
        sel_heroes = st.multiselect("2. Position(s)", avail_heroes, default=[x for x in saved.get("pf_sel_heroes", []) if x in avail_heroes])
        
        avail_streets = set()
        for sp in sel_spots:
            for h in sel_heroes:
                if h in tree[sp]: avail_streets.update(tree[sp][h].keys())
        avail_streets = sorted(list(avail_streets))
        sel_streets = st.multiselect("3. Street(s)", avail_streets, default=[x for x in saved.get("pf_sel_streets", []) if x in avail_streets])
        
        avail_branches = set()
        for sp in sel_spots:
            for h in sel_heroes:
                if h in tree[sp]:
                    for st_ in sel_streets:
                        if st_ in tree[sp][h]: avail_branches.update(tree[sp][h][st_].keys())
        avail_branches = sorted(list(avail_branches))
        sel_branches = st.multiselect("4. Branch(es)", avail_branches, default=[x for x in saved.get("pf_sel_branches", []) if x in avail_branches])
        
        sel_spots_keys = []
        if sel_branches:
            st.markdown("**5. Boards:**")
            saved_boards = saved.get("pf_spots", [])
            
            matching_boards = []
            for sp in sel_spots:
                for h in sel_heroes:
                    if h in tree[sp]:
                        for st_ in sel_streets:
                            if st_ in tree[sp][h]:
                                for br in sel_branches:
                                    if br in tree[sp][h][st_]:
                                        matching_boards.extend(tree[sp][h][st_][br])
            
            for board_name, full_key in matching_boards:
                is_checked = (full_key in saved_boards) if "pf_spots" in saved else True
                parts = full_key.split('|')
                short_lbl = f"{board_name} ({parts[0].strip()} | {parts[3].strip()})"
                if st.checkbox(short_lbl, value=is_checked, key=f"pf_chk_m_{full_key}"):
                    sel_spots_keys.append(full_key)
        
        if st.button("🚀 Apply Filters", use_container_width=True):
            saved["pf_sel_spots"] = sel_spots
            saved["pf_sel_heroes"] = sel_heroes
            saved["pf_sel_streets"] = sel_streets
            saved["pf_sel_branches"] = sel_branches
            saved["pf_spots"] = sel_spots_keys
            utils.save_user_settings(saved, is_postflop=True)
            st.session_state.pf_hand = None
            st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ Выбери фильтры.")
        st.stop()

    for k in ['pf_combo', 'pf_session_hands', 'pf_session_correct', 'pf_rng']:
        if k not in st.session_state: st.session_state[k] = 0
    if 'pf_toast_msgs' not in st.session_state: st.session_state.pf_toast_msgs = []
    if st.session_state.pf_toast_msgs:
        for msg in st.session_state.pf_toast_msgs: st.toast(msg, icon="🔥" if "Combo" in msg else "🎯")
        st.session_state.pf_toast_msgs = []
    if 'pf_hand' not in st.session_state: st.session_state.pf_hand = None
    if 'pf_current_spot_key' not in st.session_state: st.session_state.pf_current_spot_key = None
    if 'pf_last_error' not in st.session_state: st.session_state.pf_last_error = False
    
    if st.session_state.pf_hand is None or st.session_state.pf_current_spot_key is None or st.session_state.pf_current_spot_key not in pool:
        chosen_key = random.choice(pool)
        st.session_state.pf_current_spot_key = chosen_key
        data = pf_db[chosen_key]
        t_range = data.get("ranges", {}).get("training", "")
        poss = pf_parse_range(t_range)
        srs = utils.load_srs_data(is_postflop=True)
        w = [srs.get(f"{chosen_key}_{h}".replace(" ","_"), 100) for h in poss]
        
        if sum(w) == 0: w = [100]*len(poss)
        st.session_state.pf_hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.pf_rng = random.randint(0, 99)

    chosen_key = st.session_state.pf_current_spot_key
    data = pf_db[chosen_key]
    parts = [p.strip() for p in chosen_key.split('|')]
    
    hero_pos = data.get("hero_pos", "BTN")
    villain_pos = data.get("villain_pos", "BB")
    btn_pos = data.get("btn_pos", "BTN")
    active_players = data.get("active_players", ["BTN", "BB"])
    board_raw = data.get("board_cards", [])
    pot_size = data.get("pot_size", 0)
    villain_act = data.get("villain_action", "")
    info_link = data.get("info_link", "")
    actions = data.get("actions", ["Check"])
    ranges = data.get("ranges", {})

    h_val = st.session_state.pf_hand
    action_weights = {act: pf_get_weight(h_val, ranges.get(act, "")) for act in actions}
    
    correct_act = actions[0]
    cumulative = 0
    for act in actions:
        if st.session_state.pf_rng < cumulative + action_weights[act]:
            correct_act = act
            break
        cumulative += action_weights[act]

    if len(h_val) == 4:
        r1, s1_raw, r2, s2_raw = h_val[0], h_val[1], h_val[2], h_val[3]
        s1, s2 = map_suit(s1_raw), map_suit(s2_raw)
    else:
        r1, r2 = h_val[0] if len(h_val)>0 else 'X', h_val[1] if len(h_val)>1 else 'X'
        s1, s2 = map_suit('s'), map_suit('s')
        
    c1, c2 = get_suit_color_class(s1), get_suit_color_class(s2)

    stats_data = utils.load_user_stats(is_postflop=True)
    rank_name, next_xp = utils.get_rank_info(stats_data["xp"])
    c = st.session_state.pf_combo
    progress_pct = int((stats_data["xp"] / next_xp) * 100) if next_xp != "MAX" else 100
    
    sh = st.session_state.pf_session_hands
    scorr = st.session_state.pf_session_correct
    wr = int((scorr / sh * 100)) if sh > 0 else 0
    wr_color = '#28a745' if wr >= 90 else '#ffc107' if wr >= 80 else '#dc3545'

    glow_color = '#00ff00' if c >= 1000 else '#ff00ff' if c >= 500 else '#00e5ff' if c >= 200 else '#6f42c1' if c >= 100 else '#dc3545' if c >= 50 else '#fd7e14' if c >= 25 else '#ffc107' if c >= 10 else '#0dcaf0' if c >= 5 else '#888'
    combo_cls = f"combo-glow-{max([v for v in [5,10,25,50,100] if c >= v] + [0])}" if c >= 5 else ""

    try: mastery = utils.get_spot_mastery_info(stats_data.get("spot_mastery", {}).get(chosen_key, {}))
    except: mastery = {"rank": 0, "name": "Sandbox", "icon": "⚪", "color": "#6c757d", "is_rusty": False, "prog_pct": 0, "total": 0, "next": 100, "svg": ""}

    m_total = mastery.get("total", 0)
    m_next = mastery.get("next", 100)
    if mastery.get("rank", 0) >= 5: hands_left_text = "MAX RANK"
    else: hands_left_text = f"Remaining: {max(0, m_next - m_total)} hands"

    multiplier = st.session_state.get("xp_multiplier", 1.0)
    mult_html = f'<span style="background: rgba(255,255,255,0.2); color:#fff; font-size:9px; font-weight:900; margin-left:4px; padding: 1px 4px; border-radius: 6px;">x{multiplier}</span>' if multiplier > 1.0 else ''
    combo_badge = f'<div style="flex:1; display:flex; justify-content:center; align-items:center;"><div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 20px; display: inline-flex; align-items: center; justify-content: center;"><span style="font-size:14px; font-weight:900; color:{glow_color};">🔥 {c}</span>{mult_html}</div></div>'

    header_html = f'<div style="background:#111; border-radius:10px; margin-bottom:5px; border:1px solid #333; overflow:hidden; font-family:sans-serif;"><div style="height: 3px; width: 100%; background: #222;"><div style="height: 100%; width: {wr if sh > 0 else 100}%; background: {wr_color if sh > 0 else "#444"}; transition: width 0.3s;"></div></div><div style="padding:6px 12px 0 12px; display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:13px; font-weight:bold; color:#ffc107;">{rank_name}</div><div style="background:#333; height:4px; border-radius:2px; margin-top:3px; width:100%;"><div style="background:#28a745; height:100%; width:{progress_pct}%; border-radius:2px;"></div></div></div><div style="font-size:10px; color:#aaa; margin-left:10px; font-weight:bold;">{stats_data["xp"]} / {next_xp} XP</div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:6px 12px;"><div style="flex:1;"><div style="font-size:11px; font-weight:bold; color:#aaa;">Winrate</div><div style="font-size:13px; font-weight:bold; color:{wr_color};">{wr}%</div></div>{combo_badge}<div style="flex:1; text-align:right;"><div style="font-size:11px; font-weight:bold; color:#aaa;">Hands</div><div style="font-size:13px; font-weight:bold; color:#fff;">{sh}</div></div></div></div>'
    st.markdown(header_html, unsafe_allow_html=True)

    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    try: hero_idx = order.index(hero_pos)
    except ValueError: hero_idx = 0
    rot = order[hero_idx:] + order[:hero_idx]

    def get_seat_style(idx):
        return {0: "bottom: -20px; left: 50%; transform: translateX(-50%);", 1: "bottom: 10%; left: -5%;", 2: "top: 10%; left: -5%;", 
                3: "top: -20px; left: 50%; transform: translateX(-50%);", 4: "top: 10%; right: -5%;", 5: "bottom: 10%; right: -5%;"}.get(idx, "")

    def get_btn_style(idx):
        return {0: "bottom: 25px; left: 60%;", 1: "bottom: 25%; left: 16%;", 2: "top: 10%; left: 16%;",
                3: "top: 10%; left: 60%;", 4: "top: 10%; right: 16%;", 5: "bottom: 25%; right: 16%;"}.get(idx, "")

    def get_chip_style(idx):
        return {
            0: "bottom: 75px; left: 50%; transform: translateX(-50%);", 
            1: "bottom: 20%; left: 10%;", 
            2: "top: 20%; left: 10%;",
            3: "top: 35px; left: 50%; transform: translateX(-50%);", 
            4: "top: 20%; right: 10%;", 
            5: "bottom: 20%; right: 10%;"
        }.get(idx, "")

    opp_html = ""; chips_html = ""

    for i in range(1, 6):
        p = rot[i]
        has_cards = (p in active_players)
        cls = "seat-active" if has_cards else "seat-folded"
        cards = '<div class="opp-cards-mob"><div class="opp-card-mob"></div><div class="opp-card-mob right"></div></div>' if has_cards else ""
        ss = get_seat_style(i)
        
        v_act_html = ""
        is_bet = villain_act and ("BET" in villain_act.upper() or "RAISE" in villain_act.upper())
        
        if p == villain_pos and villain_act:
            if not is_bet:
                pos_class = "act-bottom-mob" if i in [2, 3, 4] else "act-top-mob"
                v_act_html = f'<div class="villain-act-badge-mob {pos_class}">{villain_act}</div>'
            
        opp_html += f'<div class="seat {cls}" style="{ss}">{cards}<span class="seat-label">{p}</span>{v_act_html}</div>'

        if p == btn_pos:
            bs = get_btn_style(i)
            chips_html += f'<div class="dealer-mob" style="{bs}">D</div>'
            
        if p == villain_pos and is_bet:
            cs = get_chip_style(i)
            bet_amount_str = villain_act.upper().replace("BET", "").replace("RAISE", "").strip().lower()
            bet_txt = f'<div class="bet-txt">{bet_amount_str}</div>'
            chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div>{bet_txt}</div>'

    if rot[0] == btn_pos:
        hero_bs = get_btn_style(0)
        chips_html += f'<div class="dealer-mob" style="{hero_bs}">D</div>'
    
    board_html = ""
    for card in board_raw:
        rank = card[:-1].upper()
        suit = map_suit(card[-1])
        sc = get_suit_color_class(suit)
        board_html += f'<div class="board-card-mob"><div class="bc-tl-mob {sc}">{rank}</div><div class="bc-c-mob {sc}">{suit}</div></div>'
        
    mobile_link = info_link
    if mobile_link and mobile_link.startswith("https://"):
        mobile_link = "onenote:" + mobile_link
    
    link_html = f'<a href="{mobile_link}" target="_blank" class="info-badge-mob" title="Open in OneNote">ℹ️</a>' if info_link else ""

    html = f'''
    <div class="mobile-game-area {combo_cls}">
        <div class="crest-left-mob">{mastery.get("svg","")}</div><div class="crest-right-mob">{mastery.get("svg","")}</div>
        <div class="mastery-glow" style="box-shadow: inset 0 0 35px {mastery.get("color","#888")};"></div>
        <div class="center-column-mob">
            <div class="mob-info-spot">{parts[3]}</div>
            <div class="pot-badge-mob">Pot: {pot_size} bb</div>
            <div class="board-container-mob">{board_html}</div>
            <div class="mastery-badge rusty-{mastery.get("is_rusty",False)}" style="color:{mastery.get("color")}; border-color:{mastery.get("color")};">{mastery.get("icon")} {mastery.get("name")}</div>
            <div class="mastery-bar-bg"><div class="mastery-bar-fill" style="width:{mastery.get("prog_pct",0)}%; background:{mastery.get("color")};"></div></div>
            <div class="hands-left-mob">{hands_left_text}</div>
        </div>
        {opp_html}{chips_html}
        <div class="hero-mob">
            {link_html}
            <div class="card-mob"><div class="tl-mob {c1}">{r1}<br>{s1}</div><div class="c-mob {c1}">{s1}</div></div>
            <div class="card-mob"><div class="tl-mob {c2}">{r2}<br>{s2}</div><div class="c-mob {c2}">{s2}</div></div>
            <div class="rng-badge">{st.session_state.pf_rng}</div>
        </div>
    </div>
    '''
    
    st.markdown(html, unsafe_allow_html=True)

    def handle_action(action):
        corr = (correct_act == action)
        st.session_state.pf_session_hands += 1
        
        k = f"{chosen_key}_{h_val}".replace(" ","_")
        utils.update_srs_auto(k, h_val, corr, is_postflop=True)
        
        utils.save_to_history({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            "Spot": chosen_key, "Hand": f"{h_val}", "Result": int(corr), 
            "CorrectAction": correct_act, "UserAction": action
        }, is_postflop=True)
        
        if corr:
            st.session_state.pf_session_correct += 1
            st.session_state.pf_combo += 1
            st.session_state.pf_last_error = False
            st.session_state.pf_hand = None
        else:
            st.session_state.pf_combo = 0
            st.session_state.pf_last_error = True
            st.session_state.msg = f"❌ ОШИБКА! Правильно: {correct_act}"
            
        try:
            alerts = utils.process_gamification(corr, st.session_state.pf_combo, st.session_state.pf_session_hands, chosen_key, is_postflop=True)
            if alerts: st.session_state.pf_toast_msgs.extend(alerts)
        except: pass
        st.rerun()

    if st.session_state.pf_last_error:
        st.markdown(f'<div style="background:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:15px; font-size:14px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
        if st.button("ПОНЯТНО, ДАЛЬШЕ", type="primary", use_container_width=True):
            st.session_state.pf_last_error = False
            st.session_state.pf_hand = None
            st.rerun()
    else:
        btn_cols = st.columns(len(actions))
        for i, act in enumerate(actions):
            with btn_cols[i]:
                color = ACTION_COLORS[i % len(ACTION_COLORS)]
                st.markdown(f"""<style>div[data-testid="column"]:nth-of-type({i+1}) button {{ border-top: 3px solid {color} !important; }}</style>""", unsafe_allow_html=True)
                if st.button(act, key=f"pf_btn_{i}", use_container_width=True):
                    handle_action(act)
