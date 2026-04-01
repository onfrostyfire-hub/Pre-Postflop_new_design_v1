import streamlit as st
import random
from datetime import datetime
import poker_utils as utils

def show():
    st.markdown("""
    <style>
        .stApp { background-color: #212529; color: #e9ecef; }
        .block-container { padding-top: 4.5rem !important; }
        .game-area { position: relative; width: 100%; max-width: 700px; height: 400px; margin: 0 auto 50px auto; background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); border: 15px solid #4a1c1c; border-radius: 200px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: box-shadow 0.3s, border-color 0.3s; }
        
        .mastery-glow { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: inherit; pointer-events: none; z-index: 1; transition: box-shadow 0.5s ease; }
        .mastery-badge { font-size: 11px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 2px 10px; border-radius: 12px; display: inline-flex; align-items: center; gap: 5px; margin-top: 6px; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.1); z-index: 30; }
        .rusty-True { filter: grayscale(100%) opacity(0.6); }
        .mastery-bar-bg { width: 100px; height: 3px; background: #111; border-radius: 2px; margin: 4px auto 0 auto; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.8); z-index: 30; }
        .mastery-bar-fill { height: 100%; transition: width 0.3s; }
        .hands-left { font-size: 10px; color: #aaa; text-transform: uppercase; font-weight: bold; margin-top: 3px; }
        
        .crest-left { position: absolute; left: 30px; top: 50%; transform: translateY(-50%); width: 140px; height: 140px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        .crest-right { position: absolute; right: 30px; top: 50%; transform: translateY(-50%); width: 140px; height: 140px; z-index: 1; pointer-events: none; display: flex; justify-content: center; align-items: center; }
        
        .combo-glow-5 { border-color: #0dcaf0 !important; box-shadow: 0 0 10px rgba(13, 202, 240, 0.4), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-10 { border-color: #ffc107 !important; box-shadow: 0 0 15px rgba(255, 193, 7, 0.5), 0 4px 15px rgba(0,0,0,0.8) !important; }
        .combo-glow-25 { border-color: #fd7e14 !important; box-shadow: 0 0 20px rgba(253, 126, 20, 0.6), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-slow 2s infinite; }
        .combo-glow-50 { border-color: #dc3545 !important; box-shadow: 0 0 30px rgba(220, 53, 69, 0.7), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-menace 1.5s infinite; }
        .combo-glow-100 { border-color: #6f42c1 !important; box-shadow: 0 0 40px rgba(111, 66, 193, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-neon 1s infinite; }
        .combo-glow-200 { border-color: #00e5ff !important; box-shadow: 0 0 50px rgba(0, 229, 255, 0.8), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-plasma 1s infinite alternate; }
        .combo-glow-500 { border-color: #ff00ff !important; box-shadow: 0 0 60px rgba(255, 0, 255, 0.9), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-matrix 0.8s infinite alternate; }
        .combo-glow-1000 { border-color: #00ff00 !important; box-shadow: 0 0 80px rgba(0, 255, 0, 1.0), 0 4px 15px rgba(0,0,0,0.8) !important; animation: pulse-god 0.5s infinite alternate; }
        
        @keyframes pulse-slow { 0% { box-shadow: 0 0 15px rgba(253, 126, 20, 0.4); } 50% { box-shadow: 0 0 25px rgba(253, 126, 20, 0.7); } 100% { box-shadow: 0 0 15px rgba(253, 126, 20, 0.4); } }
        @keyframes pulse-menace { 0% { box-shadow: 0 0 20px rgba(220, 53, 69, 0.5); } 50% { box-shadow: 0 0 40px rgba(220, 53, 69, 0.9); } 100% { box-shadow: 0 0 20px rgba(220, 53, 69, 0.5); } }
        @keyframes pulse-neon { 0% { box-shadow: 0 0 30px rgba(111, 66, 193, 0.6); } 50% { box-shadow: 0 0 60px rgba(111, 66, 193, 1.0); } 100% { box-shadow: 0 0 30px rgba(111, 66, 193, 0.6); } }
        @keyframes pulse-plasma { 0% { box-shadow: 0 0 30px rgba(0, 229, 255, 0.6); } 100% { box-shadow: 0 0 70px rgba(0, 229, 255, 1.0); } }
        @keyframes pulse-matrix { 0% { box-shadow: 0 0 40px rgba(255, 0, 255, 0.7); } 100% { box-shadow: 0 0 90px rgba(255, 0, 255, 1.0); } }
        @keyframes pulse-god { 0% { box-shadow: 0 0 50px rgba(0, 255, 0, 0.8); } 100% { box-shadow: 0 0 120px rgba(0, 255, 0, 1.0); } }

        .table-info { position: absolute; top: 16%; width: 100%; text-align: center; pointer-events: none; z-index: 15; }
        .info-spot { font-size: 24px; font-weight: 800; color: rgba(255,255,255,0.2); z-index: 30; position: relative;}
        .info-src { z-index: 30; position: relative; }
        .seat { position: absolute; width: 65px; height: 65px; background: #343a40; border: 2px solid #495057; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 11px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 4px; }
        .seat-active { border-color: #ffc107; background: #343a40; }
        .seat-folded { opacity: 0.4; border-color: #212529; }
        
        .opp-cards-desk { position: absolute; top: -15px; display: flex; z-index: 20; }
        .opp-card-desk { width: 22px; height: 32px; background: #fff; border-radius: 3px; border: 1px solid #777; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 1px 1px 3px rgba(0,0,0,0.8); }
        .opp-card-desk.right { margin-left: -8px; transform: rotate(12deg) translateY(2px); }

        .chip-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; pointer-events: none; }
        .poker-chip { width: 22px; height: 22px; background: #222; border: 3px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.7); }
        .chip-3bet { width: 24px; height: 24px; background: #d32f2f; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.6); }
        .dealer-button { width: 24px; height: 24px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 11px; display: flex; justify-content: center; align-items: center; z-index: 15; position: absolute; border: 1px solid #bfa006; }
        .bet-txt { font-size: 12px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px #000; background: rgba(0,0,0,0.6); padding: 1px 4px; border-radius: 4px; margin-top: -5px; z-index: 20; }
        
        .hero-panel { position: absolute; bottom: -60px; left: 50%; transform: translateX(-50%); background: #212529; border: 2px solid #ffc107; border-radius: 12px; padding: 6px 18px; display: flex; gap: 8px; z-index: 30; align-items: center; }
        .card { width: 50px; height: 70px; background: white; border-radius: 5px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .tl { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 16px; line-height: 1.1; }
        .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #212529; } .suit-green { color: #198754; }
        .rng-desktop { position: absolute; right: -50px; top: 15px; width: 40px; height: 40px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 16px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.6); }
        .rng-hint-box { text-align: center; color: #888; font-size: 13px; font-family: monospace; margin-top: 60px; margin-bottom: 10px; background: #2b2b2b; padding: 5px; border-radius: 6px; border: 1px solid #444; width: 100%; }
        
        .floating-reward { position: absolute; top: -30px; left: 50%; transform: translateX(-50%); font-size: 26px; font-weight: 900; text-shadow: 0px 2px 5px rgba(0,0,0,0.9), 0px 0px 2px #000; z-index: 100; pointer-events: none; animation: floatUpFade 1.2s ease-out forwards; }
        @keyframes floatUpFade { 0% { opacity: 1; transform: translate(-50%, 0) scale(0.5); } 20% { opacity: 1; transform: translate(-50%, -15px) scale(1.2); } 100% { opacity: 0; transform: translate(-50%, -80px) scale(1); } }
        
        .rage-bar-container { width: 100%; max-width: 700px; margin: 0 auto 15px auto; background: rgba(0,0,0,0.6); border: 2px solid #333; border-radius: 20px; padding: 4px; display: flex; align-items: center; position: relative; box-shadow: inset 0 2px 10px rgba(0,0,0,0.8); height: 32px; }
        .rage-bar-fill { height: 100%; border-radius: 16px; transition: width 0.3s ease-out; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(255,255,255,0.3), inset 0 -2px 5px rgba(0,0,0,0.4); }
        
        .rage-bar-fill::before, .rage-bar-fill::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 2px), radial-gradient(circle, rgba(255,255,255,0.5) 2px, transparent 3px), radial-gradient(circle, rgba(255,255,255,0.4) 1px, transparent 2px); z-index: 1; pointer-events: none; }
        .rage-bar-fill::before { background-size: 20px 25px, 35px 40px, 15px 20px; animation: bubbleRise1 1.2s infinite linear; }
        .rage-bar-fill::after { background-size: 25px 30px, 45px 50px, 22px 28px; animation: bubbleRise2 1.7s infinite linear; opacity: 0.6; }
        @keyframes bubbleRise1 { 0% { background-position: 0px 25px, 0px 40px, 0px 20px; } 50% { background-position: 5px 12.5px, -5px 20px, 3px 10px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }
        @keyframes bubbleRise2 { 0% { background-position: 0px 30px, 0px 50px, 0px 28px; } 50% { background-position: -6px 15px, 6px 25px, -4px 14px; } 100% { background-position: 0px 0px, 0px 0px, 0px 0px; } }

        .rage-labels { position: absolute; width: 100%; display: flex; justify-content: space-between; padding: 0 15px; font-weight: 900; font-size: 14px; color: #fff; text-shadow: 0 1px 3px #000, 0 0 5px #000; pointer-events: none; z-index: 2; top: 50%; transform: translateY(-50%); }
        .rage-pulse { animation: ragePulse 0.4s infinite alternate; }
        @keyframes ragePulse { 0% { filter: brightness(1); box-shadow: 0 0 5px #dc3545; } 100% { filter: brightness(1.3); box-shadow: 0 0 25px #dc3545, inset 0 0 10px #fff; } }
        .rage-flash { animation: whiteFlash 0.6s ease-out; }
        @keyframes whiteFlash { 0% { box-shadow: 0 0 50px #fff, inset 0 0 50px #fff; background: #fff; border-color: #fff; } 100% { box-shadow: 0 0 0 transparent; } }

        .glass-shatter { position: absolute; top:0; left:0; right:0; bottom:0; z-index:999; pointer-events: none; background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.2) 10px, rgba(255,255,255,0.2) 12px), repeating-linear-gradient(-45deg, transparent, transparent 15px, rgba(255,255,255,0.3) 15px, rgba(255,255,255,0.3) 18px); animation: shatterAnim 0.8s ease-out forwards; }
        @keyframes shatterAnim { 0% {opacity:1; transform: scale(1);} 100% {opacity:0; transform: scale(1.1);} }

        div.stButton > button { width: 100%; height: 60px !important; font-size: 18px !important; font-weight: 700; border-radius: 8px; text-transform: uppercase; transition: all 0.2s; }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("Ranges database is empty."); return
    
    scenario_map = {}
    for src, sc_dict in ranges_db.items():
        for sc, sp_dict in sc_dict.items():
            if sc not in scenario_map: scenario_map[sc] = []
            for sp in sp_dict.keys():
                scenario_map[sc].append((sp, f"{src}|{sc}|{sp}"))
    
    all_scenarios = sorted(list(scenario_map.keys()))

    with st.sidebar:
        st.header("⚙️ Settings")
        dv_btn = st.radio("Interface Mode", ["📱 Mobile", "💻 Desktop"], index=0 if st.session_state.actual_view_type=="📱 Mobile" else 1)
        if dv_btn != st.session_state.actual_view_type:
            st.session_state.actual_view_type = dv_btn
            st.rerun()
            
        st.markdown("---")
        saved = utils.load_user_settings()
        
        saved_sc = [s for s in saved.get("scenarios", []) if s in all_scenarios]
        sel_sc = st.multiselect("Scenario", all_scenarios, default=saved_sc if saved_sc else (all_scenarios[:1] if all_scenarios else []))
        
        sel_spots_keys = []
        if sel_sc:
            st.markdown("**Spots for training:**")
            saved_spots = saved.get("spots", [])
            for sc in sel_sc:
                st.markdown(f"<div style='color:#ffc107; font-size:14px; font-weight:bold; margin-top:8px;'>{sc}</div>", unsafe_allow_html=True)
                for sp_name, sp_key in scenario_map[sc]:
                    is_checked = (sp_key in saved_spots) if "spots" in saved else True
                    if st.checkbox(sp_name, value=is_checked, key=f"d_chk_{sp_key}"):
                        sel_spots_keys.append(sp_key)
        
        if st.button("🚀 Apply Settings", use_container_width=True):
            saved["scenarios"] = sel_sc
            saved["spots"] = sel_spots_keys
            utils.save_user_settings(saved)
            st.session_state.hand = None
            st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ No spots selected. Check menu on the left.")
        st.stop()

    if 'combo' not in st.session_state: st.session_state.combo = 0
    if 'shields' not in st.session_state: st.session_state.shields = 0
    if 'shield_break_anim' not in st.session_state: st.session_state.shield_break_anim = False
    if 'session_hands' not in st.session_state: st.session_state.session_hands = 0
    if 'session_correct' not in st.session_state: st.session_state.session_correct = 0
    
    if 'toast_msgs' not in st.session_state: st.session_state.toast_msgs = []
    if st.session_state.toast_msgs:
        for msg in st.session_state.toast_msgs:
            msg_str = str(msg)
            st.toast(msg_str, icon="🔥" if "Combo" in msg_str else "🎯")
        st.session_state.toast_msgs = []

    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'rng' not in st.session_state: st.session_state.rng = 0
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'current_spot_key' not in st.session_state: st.session_state.current_spot_key = None
    if 'last_error' not in st.session_state: st.session_state.last_error = False
    
    if st.session_state.hand is None or st.session_state.current_spot_key is None or st.session_state.current_spot_key not in pool:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        r_data = data.get("ranges", data)
        t_range = r_data.get("training", r_data.get("source", r_data.get("full", "")))
        poss = utils.parse_range_to_list(t_range)
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        
        if sum(w) == 0: w = [100]*len(poss)
            
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.rng = random.randint(0, 99)
        ps = ['♠','♥','♦','♣']; s1 = random.choice(ps)
        st.session_state.suits = [s1, s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])]

    src, sc, sp = st.session_state.current_spot_key.split('|')
    data = ranges_db[src][sc][sp]
    r_data = data.get("ranges", data)
    
    setup = data.get("setup", {})
    hero_pos = setup.get("hero_pos", "EP")
    villain_pos = setup.get("villain_pos")
    btn_pos = setup.get("btn_pos", "BTN")
    cards_in_play = setup.get("active_players", [])
    bets_on_table = setup.get("table_bets", {})
    display_hero_bet = setup.get("hero_bet")
    is_3bet_pot = setup.get("is_3bet_pot", False)

    is_defense = bool(villain_pos is not None or "call" in r_data or "Call" in r_data)

    rng = st.session_state.rng
    correct_act = "FOLD"
    r_call = r_data.get("call", r_data.get("Call", ""))
    r_raise = r_data.get("4bet", r_data.get("3bet", r_data.get("Raise", "")))
    r_full = r_data.get("full", r_data.get("Full", ""))

    if is_defense:
        w_c = utils.get_weight(st.session_state.hand, r_call)
        w_raise_val = utils.get_weight(st.session_state.hand, r_raise)
        if rng < w_raise_val: correct_act = "RAISE"
        elif rng < (w_raise_val + w_c): correct_act = "CALL"
    else:
        w = utils.get_weight(st.session_state.hand, r_full)
        if rng < w: correct_act = "RAISE"

    h_val = st.session_state.hand; s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 == '♥' else "suit-blue" if s1 == '♦' else "suit-green" if s1 == '♣' else "suit-black"
    c2 = "suit-red" if s2 == '♥' else "suit-blue" if s2 == '♦' else "suit-green" if s2 == '♣' else "suit-black"

    stats_data = utils.load_user_stats()
    rank_name, next_xp = utils.get_rank_info(stats_data["xp"])
    c = st.session_state.combo
    progress_pct = int((stats_data["xp"] / next_xp) * 100) if next_xp != "MAX" else 100
    
    sh = st.session_state.session_hands
    scorr = st.session_state.session_correct
    wr = int((scorr / sh * 100)) if sh > 0 else 0
    wr_color = '#28a745' if wr >= 90 else '#ffc107' if wr >= 80 else '#dc3545'

    try:
        mastery = utils.get_spot_mastery_info(stats_data.get("spot_mastery", {}).get(st.session_state.current_spot_key, {}))
    except Exception as e:
        mastery = {"rank": 0, "name": "Sandbox", "icon": "⚪", "color": "#6c757d", "is_rusty": False, "prog_pct": 0, "total": 0, "next": 100, "svg": ""}
        
    m_color = mastery['color']
    m_svg = mastery.get("svg", "")
    m_rust = mastery.get("is_rusty", False)
    m_icon = mastery.get("icon", "")
    m_name = mastery.get("name", "")
    m_pct = mastery.get("prog_pct", 0)
    m_total = mastery.get("total", 0)
    m_next = mastery.get("next", 100)
    m_rank = mastery.get("rank", 0)
    
    if m_rank >= 5: hands_left_text = "MAX RANK"
    else: hands_left_text = f"Remaining: {max(0, m_next - m_total)} hands"

    combo_cls = ""
    if c >= 1000: combo_cls = "combo-glow-1000"
    elif c >= 500: combo_cls = "combo-glow-500"
    elif c >= 200: combo_cls = "combo-glow-200"
    elif c >= 100: combo_cls = "combo-glow-100"
    elif c >= 50: combo_cls = "combo-glow-50"
    elif c >= 25: combo_cls = "combo-glow-25"
    elif c >= 10: combo_cls = "combo-glow-10"
    elif c >= 5: combo_cls = "combo-glow-5"

    tiers = [(0, 1.0), (10, 1.5), (25, 2.0), (50, 3.0), (100, 4.0), (250, 5.0), (500, 10.0)]
    curr_mult = 1.0; next_mult = 1.5; prev_req = 0; next_req = 10
    for i in range(len(tiers)):
        if c >= tiers[i][0]:
            curr_mult = tiers[i][1]
            prev_req = tiers[i][0]
            if i + 1 < len(tiers):
                next_req = tiers[i+1][0]
                next_mult = tiers[i+1][1]
            else:
                next_req = c 
                next_mult = "MAX"
                
    if next_mult == "MAX":
        rage_pct = 100
        lbl_left = f"x{curr_mult}"; lbl_right = "MAX"
    else:
        rage_pct = int((c - prev_req) / (next_req - prev_req) * 100)
        lbl_left = f"x{curr_mult}"; lbl_right = f"x{next_mult}"

    is_pulsing = "rage-pulse" if rage_pct >= 95 and next_mult != "MAX" else ""
    is_flashing = "rage-flash" if st.session_state.pop("just_leveled_up", False) else ""
    
    if curr_mult == 1.0: grad = "linear-gradient(90deg, #17a2b8, #0dcaf0)"
    elif curr_mult == 1.5: grad = "linear-gradient(90deg, #0dcaf0, #28a745)"
    elif curr_mult == 2.0: grad = "linear-gradient(90deg, #28a745, #ffc107)"
    elif curr_mult == 3.0: grad = "linear-gradient(90deg, #ffc107, #fd7e14)"
    elif curr_mult == 4.0: grad = "linear-gradient(90deg, #fd7e14, #dc3545)"
    elif curr_mult == 5.0: grad = "linear-gradient(90deg, #dc3545, #6f42c1)"
    else: grad = "linear-gradient(90deg, #6f42c1, #ff00ff)"

    shield_display = f'<span style="font-size:14px; margin-left:8px; filter:drop-shadow(0 0 5px #0dcaf0); display:{"inline-flex" if st.session_state.shields > 0 else "none"};">🛡️x{st.session_state.shields}</span>'
    combo_badge = f'<div style="flex:1; display:flex; justify-content:center; align-items:center;"><div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 20px; display: inline-flex; align-items: center; justify-content: center;"><span style="font-size:18px; font-weight:900; color:#fff;">🔥 {c}</span>{shield_display}</div></div>'

    header_html = f'<div style="background:#111; border-radius:12px; margin-bottom:10px; border:1px solid #333; max-width:700px; margin-left:auto; margin-right:auto; overflow:hidden;"><div style="height: 4px; width: 100%; background: #222;"><div style="height: 100%; width: {wr if sh > 0 else 100}%; background: {wr_color if sh > 0 else "#444"}; transition: width 0.3s;"></div></div><div style="display:flex; justify-content:space-between; align-items:center; padding:10px 20px;"><div style="flex:1;"><div style="font-size:15px; font-weight:bold; color:#ffc107;">{rank_name}</div><div style="font-size:11px; color:#aaa; margin-top:2px;">${stats_data["xp"]} / ${next_xp}</div></div>{combo_badge}<div style="flex:1; text-align:right;"><div style="font-size:16px; font-weight:bold; color:#17a2b8;">📅 {stats_data.get("streak", 1)} Days</div><div style="font-size:11px; color:#aaa;">Winrate: {wr}% | Hands: {sh}</div></div></div></div>'
    
    rage_bar_html = f'''
    <div class="rage-bar-container {is_flashing}">
        <div class="rage-bar-fill {is_pulsing}" style="width: {rage_pct}%; background: {grad};"></div>
        <div class="rage-labels">
            <span>{lbl_left}</span>
            <span>{lbl_right}</span>
        </div>
    </div>
    '''

    anim_html = ""
    anim_reward = st.session_state.pop("anim_reward", None)
    if anim_reward is not None:
        if anim_reward > 0: a_color = "#00ff00"; a_text = f"+${anim_reward}"
        elif anim_reward < 0: a_color = "#ff0000"; a_text = f"-${abs(anim_reward)}"
        else: a_color = "#888"; a_text = "$0"
        anim_html = f'<div class="floating-reward" style="color: {a_color}">{a_text}</div>'
        
    shatter_html = ""
    if st.session_state.pop("shield_break_anim", False):
        shatter_html = '<div class="glass-shatter"></div>'

    col_center, col_right = st.columns([2, 1])
    
    with col_center:
        st.markdown(header_html, unsafe_allow_html=True)
        st.markdown(rage_bar_html, unsafe_allow_html=True)
        
        order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
        try: hero_idx = order.index(hero_pos)
        except ValueError: hero_idx = 0
        rot = order[hero_idx:] + order[:hero_idx]

        def get_seat_style(idx):
            return {0: "bottom: -20px; left: 50%; transform: translateX(-50%);", 1: "bottom: 15%; left: 0%;", 2: "top: 15%; left: 0%;", 
                    3: "top: -20px; left: 50%; transform: translateX(-50%);", 4: "top: 15%; right: 0%;", 5: "bottom: 15%; right: 0%;"}.get(idx, "")

        def get_chip_style(idx):
            return {0: "bottom: 25%; left: 50%; transform: translateX(-50%);", 1: "bottom: 22%; left: 22%;", 2: "top: 22%; left: 22%;",
                    3: "top: 25%; left: 50%; transform: translateX(-50%);", 4: "top: 22%; right: 22%;", 5: "bottom: 22%; right: 22%;"}.get(idx, "")

        def get_btn_style(idx):
            return {0: "bottom: -15px; left: 50%; margin-left: -90px; z-index: 35;", 1: "bottom: 25%; left: 16%;", 2: "top: 10%; left: 16%;",
                    3: "top: 10%; left: 60%;", 4: "top: 10%; right: 16%;", 5: "bottom: 25%; right: 16%;"}.get(idx, "")

        opp_html = ""; chips_html = ""

        for i in range(1, 6):
            p = rot[i]
            
            has_cards = (p in cards_in_play)
            cls = "seat-active" if has_cards else "seat-folded"
            cards = '<div class="opp-cards-desk"><div class="opp-card-desk"></div><div class="opp-card-desk right"></div></div>' if has_cards else ""
            ss = get_seat_style(i)
            opp_html += f'<div class="seat {cls}" style="{ss}">{cards}<span class="seat-label">{p}</span></div>'
            
            cs = get_chip_style(i)
            bet_amount = bets_on_table.get(p)
            
            if bet_amount is not None:
                bet_txt = f'<div class="bet-txt">{bet_amount}bb</div>'
                if bet_amount <= 1.0:
                    if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div>{bet_txt}</div>'
                    else: chips_html += f'<div class="chip-container" style="{cs}"><div class="poker-chip"></div>{bet_txt}</div>'
                else:
                    if is_3bet_pot: chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-15px;"></div>{bet_txt}</div>'
                    else: chips_html += f'<div class="chip-container" style="{cs}"><div class="poker-chip"></div><div class="poker-chip" style="margin-top:-10px;"></div>{bet_txt}</div>'
            
            if p == btn_pos:
                bs = get_btn_style(i)
                chips_html += f'<div class="dealer-button" style="{bs}">D</div>'

        hero_cs = get_chip_style(0)
        if display_hero_bet is not None: 
            bet_txt = f'<div class="bet-txt">{display_hero_bet}bb</div>'
            if display_hero_bet <= 1.0:
                chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="poker-chip"></div>{bet_txt}</div>'
            else:
                chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="poker-chip"></div><div class="poker-chip" style="margin-top:-10px"></div>{bet_txt}</div>'
            
        if rot[0] == btn_pos:
            hero_bs = get_btn_style(0)
            chips_html += f'<div class="dealer-button" style="{hero_bs}">D</div>'

        html = f'<div class="game-area {combo_cls}">{shatter_html}<div class="crest-left">{m_svg}</div><div class="crest-right">{m_svg}</div><div class="mastery-glow" style="box-shadow: inset 0 0 35px {m_color};"></div><div class="table-info"><div class="info-src">{sc}</div><div class="info-spot">{sp}</div><div class="mastery-badge rusty-{m_rust}" style="color: {m_color}; border-color: {m_color};">{m_icon} {m_name}</div><div class="mastery-bar-bg"><div class="mastery-bar-fill" style="width: {m_pct}%; background: {m_color};"></div></div><div class="hands-left">{hands_left_text}</div></div>{opp_html}{chips_html}<div class="hero-panel">{anim_html}<div style="display:flex;flex-direction:column;align-items:center;"><span style="color:#ffc107;font-weight:bold;font-size:12px;">HERO</span></div><div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div><div class="rng-desktop">{rng}</div></div></div>'
        
        st.markdown(html, unsafe_allow_html=True)
        
        if not st.session_state.last_error:
            if is_defense: st.markdown('<div class="rng-hint-box">📉 0..Freq → Action | 📈 Freq..100 → Fold</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="rng-hint-box">📉 0..Freq → Raise | 📈 Freq..100 → Fold</div>', unsafe_allow_html=True)

        def handle_action(action):
            corr = (correct_act == action)
            st.session_state.session_hands += 1
            
            k = f"{src}_{sc}_{sp}".replace(" ","_")
            utils.update_srs_auto(k, st.session_state.hand, corr)
            
            utils.save_to_history({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), 
                "CorrectAction": correct_act, "UserAction": action
            })
            
            shield_used = False
            if corr:
                st.session_state.session_correct += 1
                st.session_state.combo += 1
                
                if st.session_state.combo in [100, 250, 500, 1000]:
                    st.session_state.shields += 1
                    
                st.session_state.last_error = False
                st.session_state.hand = None
            else:
                if st.session_state.shields > 0:
                    st.session_state.shields -= 1
                    st.session_state.shield_break_anim = True
                    st.session_state.last_error = True
                    shield_used = True
                    st.session_state.msg = f"🛡️ ЩИТ СЛОМАН! Защита от мисклика. GTO: {correct_act}"
                else:
                    st.session_state.combo = 0
                    st.session_state.last_error = True
                    st.session_state.msg = f"❌ WRONG! You chose {action}, but GTO is {correct_act}"
                
            try:
                import inspect
                sig = inspect.signature(utils.process_gamification)
                if 'shield_used' in sig.parameters:
                    res = utils.process_gamification(corr, st.session_state.combo, st.session_state.session_hands, st.session_state.current_spot_key, shield_used=shield_used)
                else:
                    res = utils.process_gamification(corr, st.session_state.combo, st.session_state.session_hands, st.session_state.current_spot_key)
                
                if isinstance(res, tuple):
                    alerts = res[0]
                    st.session_state.anim_reward = res[1]
                else:
                    alerts = res
                    
                if alerts: st.session_state.toast_msgs.extend(alerts)
            except Exception: pass
            
            st.rerun()

        if st.session_state.last_error:
            st.markdown(f'<div style="background:#dc3545; color:white; padding:12px; border-radius:12px; text-align:center; font-weight:bold; margin-bottom:15px; font-size:16px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🎯 Correct Range", "🧠 SRS Matrix"])
            with tab1:
                st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
            with tab2:
                st.markdown(utils.render_srs_matrix(data, src, sc, sp, utils.load_srs_data(), st.session_state.hand), unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("UNDERSTOOD, NEXT", type="primary", use_container_width=True):
                st.session_state.last_error = False
                st.session_state.hand = None
                st.session_state.shield_break_anim = False
                st.rerun()

        else:
            if is_defense:
                st.markdown("""<style>
                    div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(180deg, #495057, #343a40) !important; color: #adb5bd !important; box-shadow: 0 4px 0 #1d2124, 0 6px 10px rgba(0,0,0,0.3) !important; }
                    div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(180deg, #20c997, #198754) !important; color: #fff !important; box-shadow: 0 4px 0 #0f5132, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
                    div[data-testid="column"]:nth-of-type(3) button { background: linear-gradient(180deg, #e83e8c, #d63384) !important; color: #fff !important; box-shadow: 0 4px 0 #a02561, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
                </style>""", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("FOLD", key="f", use_container_width=True): handle_action("FOLD")
                with c2:
                    if st.button("CALL", key="c", use_container_width=True): handle_action("CALL")
                with c3:
                    if st.button("RAISE", key="r", use_container_width=True): handle_action("RAISE")
            else:
                st.markdown("""<style>
                    div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(180deg, #495057, #343a40) !important; color: #adb5bd !important; box-shadow: 0 4px 0 #1d2124, 0 6px 10px rgba(0,0,0,0.3) !important; }
                    div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(180deg, #e83e8c, #d63384) !important; color: #fff !important; box-shadow: 0 4px 0 #a02561, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
                </style>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("FOLD", key="f", use_container_width=True): handle_action("FOLD")
                with c2:
                    if st.button("RAISE", key="r", use_container_width=True): handle_action("RAISE")

    with col_right:
        if not st.session_state.last_error:
            st.markdown(f"<div style='text-align:center;font-weight:bold;margin-bottom:10px;'>{sp}</div>", unsafe_allow_html=True)
            with st.expander("🫣 Peek Range", expanded=False):
                st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
