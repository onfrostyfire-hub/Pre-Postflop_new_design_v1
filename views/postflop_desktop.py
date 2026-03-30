import streamlit as st
import random
from datetime import datetime
import poker_utils as utils

ACTION_COLORS = ["#28a745", "#d63384", "#0dcaf0", "#ffc107", "#6f42c1"]

def map_suit(s):
    mapping = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
    return mapping.get(s.lower(), '♠')

def get_suit_color_class(s):
    if s == '♥': return "suit-red"
    if s == '♦': return "suit-blue"
    if s == '♣': return "suit-green"
    return "suit-black"

def show():
    st.markdown("""
    <style>
        .stApp { background-color: #1a1c20; color: #e9ecef; }
        .game-area { position: relative; width: 100%; max-width: 700px; height: 420px; margin: 0 auto; background: radial-gradient(ellipse at center, #1e5e2f 0%, #0d3b1a 100%); border: 12px solid #2c1a1a; border-radius: 180px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); transition: box-shadow 0.3s, border-color 0.3s; }
        .mastery-glow { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: inherit; pointer-events: none; z-index: 1; transition: box-shadow 0.5s ease; }
        .mastery-badge { font-size: 11px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 2px 10px; border-radius: 12px; display: inline-flex; align-items: center; gap: 5px; margin-top: 6px; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.1); z-index: 30; }
        .rusty-True { filter: grayscale(100%) opacity(0.6); }
        .mastery-bar-bg { width: 100px; height: 3px; background: #111; border-radius: 2px; margin: 4px auto 0 auto; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.8); z-index: 30; }
        .mastery-bar-fill { height: 100%; transition: width 0.3s; }
        .crest-left { position: absolute; left: 30px; top: 50%; transform: translateY(-50%); width: 140px; height: 140px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        .crest-right { position: absolute; right: 30px; top: 50%; transform: translateY(-50%); width: 140px; height: 140px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        .table-info { position: absolute; top: 12%; width: 100%; text-align: center; pointer-events: none; z-index: 15; }
        .info-spot { font-size: 20px; font-weight: 800; color: rgba(255,255,255,0.2); z-index: 30; position: relative;}
        .info-src { font-size: 12px; color: #aaa; z-index: 30; position: relative; }
        
        .board-container { position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%); display: flex; gap: 6px; z-index: 20; background: rgba(0,0,0,0.3); padding: 8px 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
        .board-card { width: 42px; height: 60px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); font-family: sans-serif; }
        .bc-tl { position: absolute; top: 2px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1; }
        .bc-c { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 22px; }
        
        .pot-badge { position: absolute; top: 65%; left: 50%; transform: translateX(-50%); background: #111; color: #ffc107; font-weight: bold; font-size: 14px; padding: 4px 12px; border-radius: 20px; border: 1px solid #ffc107; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 20; }
        .villain-action { position: absolute; top: 28%; left: 50%; transform: translateX(-50%); background: #dc3545; color: #fff; font-weight: bold; font-size: 12px; padding: 3px 10px; border-radius: 6px; border: 1px solid #ffaaaa; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 20; text-transform: uppercase; }
        .onenote-link { position: absolute; top: 25px; right: 40px; background: #6f42c1; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 16px; text-decoration: none; border: 2px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.6); z-index: 50; transition: transform 0.2s; }
        .onenote-link:hover { transform: scale(1.1); color: white; }

        .seat { position: absolute; width: 65px; height: 65px; background: #343a40; border: 2px solid #495057; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 11px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 4px; }
        .seat-active { border-color: #ffc107; background: #343a40; }
        .seat-folded { opacity: 0.4; border-color: #212529; }
        .opp-cards-desk { position: absolute; top: -15px; display: flex; z-index: 20; }
        .opp-card-desk { width: 22px; height: 32px; background: #fff; border-radius: 3px; border: 1px solid #777; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 1px 1px 3px rgba(0,0,0,0.8); }
        .opp-card-desk.right { margin-left: -8px; transform: rotate(12deg) translateY(2px); }

        .hero-panel { position: absolute; bottom: -35px; left: 50%; transform: translateX(-50%); background: #212529; border: 2px solid #ffc107; border-radius: 12px; padding: 6px 18px; display: flex; gap: 8px; z-index: 30; align-items: center; }
        .card { width: 50px; height: 70px; background: white; border-radius: 5px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.3); font-family: sans-serif; }
        .tl { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 16px; line-height: 1.1; }
        .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #212529; } .suit-green { color: #198754; }
        .rng-desktop { position: absolute; right: -50px; top: 15px; width: 40px; height: 40px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 16px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.6); }
        
        .combo-glow-5 { border-color: #0dcaf0 !important; box-shadow: 0 0 10px rgba(13, 202, 240, 0.4), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-10 { border-color: #ffc107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.5), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-25 { border-color: #fd7e14 !important; box-shadow: 0 0 20px rgba(253, 126, 20, 0.6), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-50 { border-color: #dc3545 !important; box-shadow: 0 0 30px rgba(220, 53, 69, 0.7), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-100 { border-color: #6f42c1 !important; box-shadow: 0 0 40px rgba(111, 66, 193, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; }
        
        div.stButton > button { height: 60px !important; font-size: 16px !important; font-weight: 800; border-radius: 8px; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.1); background: #343a40; color: #fff; transition: all 0.2s; box-shadow: 0 4px 0 #1d2124; }
        div.stButton > button:active { transform: translateY(4px); box-shadow: 0 0 0 transparent; }
    </style>
    """, unsafe_allow_html=True)

    pf_db = utils.load_postflop_ranges()
    if not pf_db: st.error("База постфлопа пуста."); return

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

    with st.sidebar:
        st.header("⚙️ Postflop Filters")
        dv_btn = st.radio("Interface Mode", ["📱 Mobile", "💻 Desktop"], index=1)
        if dv_btn != st.session_state.actual_view_type:
            st.session_state.actual_view_type = dv_btn
            st.rerun()
            
        st.markdown("---")
        saved = utils.load_user_settings(is_postflop=True)
        
        sel_spot = st.selectbox("1. Spot", sorted(list(tree.keys())), index=0 if tree else None)
        sel_hero, sel_street, sel_branch = None, None, None
        sel_spots_keys = []
        
        if sel_spot:
            sel_hero = st.selectbox("2. Position", sorted(list(tree[sel_spot].keys())), index=0 if tree[sel_spot] else None)
        if sel_hero:
            sel_street = st.selectbox("3. Street", sorted(list(tree[sel_spot][sel_hero].keys())), index=0 if tree[sel_spot][sel_hero] else None)
        if sel_street:
            sel_branch = st.selectbox("4. Branch", sorted(list(tree[sel_spot][sel_hero][sel_street].keys())), index=0 if tree[sel_spot][sel_hero][sel_street] else None)
            
        if sel_branch:
            st.markdown("**5. Boards for training:**")
            saved_spots = saved.get("pf_spots", [])
            for board_name, full_key in tree[sel_spot][sel_hero][sel_street][sel_branch]:
                is_checked = (full_key in saved_spots) if "pf_spots" in saved else True
                if st.checkbox(board_name, value=is_checked, key=f"pf_chk_{full_key}"):
                    sel_spots_keys.append(full_key)
        
        if st.button("🚀 Apply Filters", use_container_width=True):
            saved["pf_spots"] = sel_spots_keys
            utils.save_user_settings(saved, is_postflop=True)
            st.session_state.pf_hand = None
            st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ Выбери фильтры и борды в меню слева.")
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
        poss = utils.parse_range_to_list(t_range)
        srs = utils.load_srs_data(is_postflop=True)
        w = [srs.get(f"{chosen_key}_{h}".replace(" ","_"), 100) for h in poss]
        
        if sum(w) == 0: w = [100]*len(poss)
        st.session_state.pf_hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.pf_rng = random.randint(0, 99)
        
        ps = ['♠','♥','♦','♣']
        s1 = random.choice(ps)
        st.session_state.pf_suits = [s1, s1 if 's' in st.session_state.pf_hand else random.choice([x for x in ps if x!=s1])]

    chosen_key = st.session_state.pf_current_spot_key
    data = pf_db[chosen_key]
    parts = [p.strip() for p in chosen_key.split('|')]
    
    hero_pos = data.get("hero_pos", "BTN")
    active_players = data.get("active_players", ["BTN", "BB"])
    board_raw = data.get("board_cards", [])
    pot_size = data.get("pot_size", 0)
    villain_act = data.get("villain_action", "")
    info_link = data.get("info_link", "")
    actions = data.get("actions", ["Check"])
    ranges = data.get("ranges", {})

    h_val = st.session_state.pf_hand
    action_weights = {act: utils.get_weight(h_val, ranges.get(act, "")) for act in actions}
    
    correct_act = actions[0]
    cumulative = 0
    for act in actions:
        if st.session_state.pf_rng < cumulative + action_weights[act]:
            correct_act = act
            break
        cumulative += action_weights[act]

    s1, s2 = st.session_state.pf_suits
    c1, c2 = get_suit_color_class(s1), get_suit_color_class(s2)

    stats_data = utils.load_user_stats(is_postflop=True)
    rank_name, next_xp = utils.get_rank_info(stats_data["xp"])
    c = st.session_state.pf_combo
    progress_pct = int((stats_data["xp"] / next_xp) * 100) if next_xp != "MAX" else 100
    
    glow_color = '#00ff00' if c >= 1000 else '#ff00ff' if c >= 500 else '#00e5ff' if c >= 200 else '#6f42c1' if c >= 100 else '#dc3545' if c >= 50 else '#fd7e14' if c >= 25 else '#ffc107' if c >= 10 else '#0dcaf0' if c >= 5 else '#888'
    combo_cls = f"combo-glow-{max([v for v in [5,10,25,50,100] if c >= v] + [0])}" if c >= 5 else ""

    try: mastery = utils.get_spot_mastery_info(stats_data.get("spot_mastery", {}).get(chosen_key, {}))
    except: mastery = {"rank": 0, "name": "Sandbox", "icon": "⚪", "color": "#6c757d", "is_rusty": False, "prog_pct": 0, "svg": ""}

    # Логика рассадки 6-max
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    try: hero_idx = order.index(hero_pos)
    except ValueError: hero_idx = 0
    rot = order[hero_idx:] + order[:hero_idx]

    def get_seat_style(idx):
        return {0: "bottom: -20px; left: 50%; transform: translateX(-50%);", 1: "bottom: 15%; left: 0%;", 2: "top: 15%; left: 0%;", 
                3: "top: -20px; left: 50%; transform: translateX(-50%);", 4: "top: 15%; right: 0%;", 5: "bottom: 15%; right: 0%;"}.get(idx, "")

    opp_html = ""
    for i in range(1, 6):
        p = rot[i]
        has_cards = (p in active_players)
        cls = "seat-active" if has_cards else "seat-folded"
        cards = '<div class="opp-cards-desk"><div class="opp-card-desk"></div><div class="opp-card-desk right"></div></div>' if has_cards else ""
        ss = get_seat_style(i)
        opp_html += f'<div class="seat {cls}" style="{ss}">{cards}<span class="seat-label">{p}</span></div>'

    st.markdown(f'<div style="background:#111; border-radius:12px; margin-bottom:20px; border:1px solid #333; max-width:700px; margin: 0 auto 20px auto; padding:10px 20px; display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:15px; font-weight:bold; color:#ffc107;">{rank_name}</div><div style="background:#333; height:6px; border-radius:3px; margin-top:4px; width:80%;"><div style="background:#28a745; height:100%; width:{progress_pct}%; border-radius:3px;"></div></div><div style="font-size:11px; color:#aaa; margin-top:2px;">{stats_data["xp"]} XP</div></div><div style="flex:1; text-align:center;"><span style="font-size:22px; font-weight:900; color:{glow_color}; text-shadow: 0 0 {10 if c>=5 else 0}px {glow_color};">🔥 {c}</span></div><div style="flex:1; text-align:right;"><div style="font-size:16px; font-weight:bold; color:#17a2b8;">📅 {stats_data.get("streak", 1)} Days</div><div style="font-size:11px; color:#aaa;">Hands: {st.session_state.pf_session_hands}</div></div></div>', unsafe_allow_html=True)
    
    board_html = ""
    for card in board_raw:
        rank = card[:-1].upper()
        suit = map_suit(card[-1])
        sc = get_suit_color_class(suit)
        board_html += f'<div class="board-card"><div class="bc-tl {sc}">{rank}<br>{suit}</div><div class="bc-c {sc}">{suit}</div></div>'
        
    villain_html = f'<div class="villain-action">{villain_act}</div>' if villain_act else ""
    link_html = f'<a href="{info_link}" target="_blank" class="onenote-link" title="Open Strategy in OneNote">ℹ️</a>' if info_link else ""

    html = f'<div class="game-area {combo_cls}"><div class="crest-left">{mastery.get("svg","")}</div><div class="crest-right">{mastery.get("svg","")}</div><div class="mastery-glow" style="box-shadow: inset 0 0 35px {mastery.get("color","#888")};"></div>{link_html}<div class="table-info"><div class="info-src">{parts[0]} | {parts[1]} | {parts[2]}</div><div class="info-spot">{parts[3]}</div><div class="mastery-badge rusty-{mastery.get("is_rusty",False)}" style="color:{mastery.get("color")}; border-color:{mastery.get("color")};">{mastery.get("icon")} {mastery.get("name")}</div><div class="mastery-bar-bg"><div class="mastery-bar-fill" style="width:{mastery.get("prog_pct",0)}%; background:{mastery.get("color")};"></div></div></div>{villain_html}<div class="board-container">{board_html}</div><div class="pot-badge">Pot: {pot_size} bb</div>{opp_html}<div class="hero-panel"><div style="display:flex;flex-direction:column;align-items:center;"><span style="color:#ffc107;font-weight:bold;font-size:12px;">HERO</span></div><div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div><div class="rng-desktop">{st.session_state.pf_rng}</div></div></div>'
    
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

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
            st.session_state.msg = f"❌ ОШИБКА! Ты нажал {action}, но правильный экшен: {correct_act}"
            
        try:
            alerts = utils.process_gamification(corr, st.session_state.pf_combo, st.session_state.pf_session_hands, chosen_key, is_postflop=True)
            if alerts: st.session_state.pf_toast_msgs.extend(alerts)
        except: pass
        st.rerun()

    if st.session_state.pf_last_error:
        st.markdown(f'<div style="background:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:15px; font-size:16px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
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
