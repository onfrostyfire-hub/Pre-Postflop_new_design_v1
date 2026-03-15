import streamlit as st
import random
from datetime import datetime
import utils

def show():
    st.markdown("""
    <style>
        .stApp { background-color: #212529; color: #e9ecef; }
        .block-container { padding-top: 4rem; }
        .game-area { position: relative; width: 100%; max-width: 700px; height: 400px; margin: 0 auto; background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); border: 15px solid #4a1c1c; border-radius: 200px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: box-shadow 0.3s, border-color 0.3s; }
        
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
        
        .table-info { position: absolute; top: 20%; width: 100%; text-align: center; pointer-events: none; }
        .info-spot { font-size: 24px; font-weight: 800; color: rgba(255,255,255,0.2); }
        .seat { position: absolute; width: 65px; height: 65px; background: #343a40; border: 2px solid #495057; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 11px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 4px; }
        .seat-active { border-color: #ffc107; background: #343a40; }
        .seat-folded { opacity: 0.4; border-color: #212529; }
        .opp-cards { position: absolute; top: -12px; width: 34px; height: 48px; background: #fff; border-radius: 4px; border: 1px solid #ccc; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); z-index: 20; box-shadow: 1px 1px 4px rgba(0,0,0,0.8); }
        .chip-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; pointer-events: none; }
        .poker-chip { width: 22px; height: 22px; background: #222; border: 3px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.7); }
        .chip-3bet { width: 24px; height: 24px; background: #d32f2f; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.6); }
        .dealer-button { width: 24px; height: 24px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 11px; display: flex; justify-content: center; align-items: center; z-index: 15; position: absolute; border: 1px solid #bfa006; }
        .bet-txt { font-size: 12px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px #000; background: rgba(0,0,0,0.6); padding: 1px 4px; border-radius: 4px; margin-top: -5px; z-index: 20; }
        .hero-panel { position: absolute; bottom: -45px; left: 50%; transform: translateX(-50%); background: #212529; border: 2px solid #ffc107; border-radius: 12px; padding: 6px 18px; display: flex; gap: 8px; z-index: 30; align-items: center; }
        .card { width: 50px; height: 70px; background: white; border-radius: 5px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .tl { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 16px; line-height: 1.1; }
        .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #212529; } .suit-green { color: #198754; }
        .rng-desktop { position: absolute; right: -50px; top: 15px; width: 40px; height: 40px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 16px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.6); }
        .rng-hint-box { text-align: center; color: #888; font-size: 13px; font-family: monospace; margin-top: 60px; margin-bottom: 10px; background: #2b2b2b; padding: 5px; border-radius: 6px; border: 1px solid #444; width: 100%; }
        div.stButton > button { width: 100%; height: 60px !important; font-size: 18px !important; font-weight: 700; border-radius: 8px; text-transform: uppercase; transition: all 0.2s; }
        .fold-btn button { background: #495057 !important; color: #adb5bd !important; border: 1px solid #6c757d !important; }
        .call-btn button { background: #28a745 !important; color: white !important; box-shadow: 0 4px 0 #1e7e34 !important; }
        .raise-btn button { background: #d63384 !important; color: white !important; box-shadow: 0 4px 0 #a02561 !important; }
        .open-raise-btn button { background: #2e7d32 !important; color: white !important; box-shadow: 0 4px 0 #1b5e20 !important; }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("База ренджей пуста. Проверь папку spots_data."); return
    
    is_leak_mode = st.session_state.get("leak_mode_active", False)

    if is_leak_mode:
        st.markdown('<div style="background:#dc3545; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:15px; box-shadow: 0 4px 10px rgba(220,53,69,0.4); border:2px solid #ffc107;">🔥 АКТИВЕН РЕЖИМ ОТРАБОТКИ ХРОНИЧЕСКИХ ОШИБОК 🔥</div>', unsafe_allow_html=True)
        if st.button("❌ ВЫЙТИ ИЗ РЕЖИМА ДЫР", use_container_width=True):
            st.session_state.leak_mode_active = False
            st.session_state.hand = None
            st.rerun()
            
        target_spot = st.session_state.get("leak_spot")
        full_key = None
        for src, sc_dict in ranges_db.items():
            for sc, sp_dict in sc_dict.items():
                if target_spot in sp_dict:
                    full_key = f"{src}|{sc}|{target_spot}"
                    break
        
        if not full_key:
            st.error("Спот не найден. Отключение режима.")
            st.session_state.leak_mode_active = False
            st.stop()
            
        pool = [full_key]
        
    else:
        scenario_map = {}
        for src, sc_dict in ranges_db.items():
            for sc, sp_dict in sc_dict.items():
                mapped_sc = sc
                sc_lower = sc.lower()
                if "3bet" in sc_lower: mapped_sc = "Def vs 3bet"
                elif "pfr" in sc_lower or "bbvsbu" in sc_lower or "bb def" in sc_lower: mapped_sc = "BB def vs PFR"
                elif "open raise" in sc_lower: mapped_sc = "Open Raise"
                
                if mapped_sc not in scenario_map: scenario_map[mapped_sc] = []
                for sp in sp_dict.keys():
                    scenario_map[mapped_sc].append((sp, f"{src}|{sc}|{sp}"))
        
        all_scenarios = ["Open Raise", "BB def vs PFR", "Def vs 3bet"]
        all_scenarios = [s for s in all_scenarios if s in scenario_map]

        with st.sidebar:
            st.header("⚙️ Фильтры")
            saved = utils.load_user_settings()
            
            saved_sc = [s for s in saved.get("scenarios", []) if s in all_scenarios]
            sel_sc = st.multiselect("Сценарий", all_scenarios, default=saved_sc if saved_sc else (all_scenarios[:1] if all_scenarios else []))
            
            sel_spots_keys = []
            if sel_sc:
                st.markdown("**Споты для тренировки:**")
                saved_spots = saved.get("spots", [])
                for sc in sel_sc:
                    st.markdown(f"<div style='color:#ffc107; font-size:14px; font-weight:bold; margin-top:8px;'>{sc}</div>", unsafe_allow_html=True)
                    for sp_name, sp_key in scenario_map[sc]:
                        is_checked = (sp_key in saved_spots) if "spots" in saved else True
                        if st.checkbox(sp_name, value=is_checked, key=f"d_chk_{sp_key}"):
                            sel_spots_keys.append(sp_key)
            
            if st.button("🚀 Применить настройки", use_container_width=True):
                utils.save_user_settings({"scenarios": sel_sc, "spots": sel_spots_keys})
                st.session_state.hand = None
                st.rerun()

        pool = sel_spots_keys
        if not pool:
            st.warning("⚠️ Не выбран ни один спот. Отметь галочки в меню слева.")
            st.stop()

    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'rng' not in st.session_state: st.session_state.rng = 0
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    if 'current_spot_key' not in st.session_state: st.session_state.current_spot_key = None
    
    if st.session_state.hand is None or st.session_state.current_spot_key is None or st.session_state.current_spot_key not in pool:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        r_data = data.get("ranges", data)
        
        if is_leak_mode:
            poss = st.session_state.get("leak_hands", [])
        else:
            t_range = r_data.get("training", r_data.get("source", r_data.get("full", "")))
            poss = utils.parse_range_to_list(t_range)
            
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        
        if sum(w) == 0: w = [100]*len(poss)
            
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.rng = random.randint(0, 99)
        ps = ['♠','♥','♦','♣']; s1 = random.choice(ps)
        st.session_state.suits = [s1, s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])]
        st.session_state.srs_mode = False

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
        if w > 0: correct_act = "RAISE"

    h_val = st.session_state.hand; s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-green" if s1 in '♣' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-green" if s2 in '♣' else "suit-black"

    col_center, col_right = st.columns([2, 1])
    
    with col_center:
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
            return {0: "bottom: 10%; left: 60%;", 1: "bottom: 25%; left: 16%;", 2: "top: 10%; left: 16%;",
                    3: "top: 10%; left: 60%;", 4: "top: 10%; right: 16%;", 5: "bottom: 25%; right: 16%;"}.get(idx, "")

        opp_html = ""; chips_html = ""

        for i in range(1, 6):
            p = rot[i]
            has_cards = False
            if is_defense:
                if p == villain_pos: has_cards = True
            else:
                if order.index(p) > order.index(hero_pos): has_cards = True
                
            cls = "seat-active" if has_cards else "seat-folded"
            cards = '<div class="opp-cards"></div>' if has_cards else ""
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

        html = f"""
        <div class="game-area">
            <div class="table-info"><div class="info-src">{sc}</div><div class="info-spot">{sp}</div></div>
            {opp_html} {chips_html}
            <div class="hero-panel">
                <div style="display:flex;flex-direction:column;align-items:center;"><span style="color:#ffc107;font-weight:bold;font-size:12px;">HERO</span></div>
                <div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>
                <div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>
                <div class="rng-desktop">{rng}</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        if is_defense: st.markdown('<div class="rng-hint-box">📉 0..Freq → Action | 📈 Freq..100 → Fold</div>', unsafe_allow_html=True)
        else: st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

        def handle_action(action):
            corr = (correct_act == action)
            st.session_state.last_error = not corr
            if corr:
                st.session_state.msg = f"✅ Correct"
            else:
                st.session_state.msg = f"❌ Err! RNG {rng} -> {correct_act}"
                
            utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), "CorrectAction": correct_act})
            st.session_state.srs_mode = True
            st.rerun()

        if not st.session_state.srs_mode:
            if is_defense:
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("FOLD"): handle_action("FOLD")
                    st.markdown("""<script>parent.document.querySelectorAll('div[data-testid="column"] button')[0].classList.add("fold-btn");</script>""", unsafe_allow_html=True)
                with c2:
                    if st.button("CALL"): handle_action("CALL")
                    st.markdown("""<script>parent.document.querySelectorAll('div[data-testid="column"] button')[1].classList.add("call-btn");</script>""", unsafe_allow_html=True)
                with c3:
                    if st.button("RAISE"): handle_action("RAISE")
                    st.markdown("""<script>parent.document.querySelectorAll('div[data-testid="column"] button')[2].classList.add("raise-btn");</script>""", unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("FOLD"): handle_action("FOLD")
                    st.markdown("""<script>parent.document.querySelectorAll('div[data-testid="column"] button')[0].classList.add("fold-btn");</script>""", unsafe_allow_html=True)
                with c2:
                    if st.button("RAISE"): handle_action("RAISE")
                    st.markdown("""<script>parent.document.querySelectorAll('div[data-testid="column"] button')[1].classList.add("open-raise-btn");</script>""", unsafe_allow_html=True)
        else:
            if st.session_state.last_error: st.error(st.session_state.msg)
            else: st.success(st.session_state.msg)
            
            s1, s2, s3 = st.columns(3)
            k = f"{src}_{sc}_{sp}".replace(" ","_")
            if s1.button("HARD", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
            if s2.button("NORM", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
            if s3.button("EASY", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

    with col_right:
        if st.session_state.srs_mode:
            st.markdown(f"**{sp}** Range ({correct_act})")
            st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:center;font-weight:bold;margin-bottom:10px;'>{sp}</div>", unsafe_allow_html=True)
            with st.expander("🫣 Подсмотреть Рендж", expanded=False):
                st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
