import streamlit as st
import random
from datetime import datetime
import utils

def show():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@500;700;900&display=swap');

        /* Убиваем лишние отступы Streamlit для мобилок */
        .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
        
        /* Спрессовываем стопку колонок */
        [data-testid="column"] { margin-bottom: -12px !important; }

        /* Компактный 3D стиль для кнопок в стопке */
        div.stButton > button {
            width: 100%; height: 55px !important; font-family: 'Roboto', sans-serif; font-weight: 900 !important; font-size: 16px !important; 
            border-radius: 12px !important; border: none !important; text-transform: uppercase; transition: all 0.1s ease;
            position: relative; top: 0; padding: 0 4px !important; letter-spacing: 1px;
        }
        div.stButton > button:active { top: 4px; box-shadow: 0 2px 0 transparent !important; }

        .mobile-game-area { 
            position: relative; width: 100%; height: 250px; margin: 0 auto 10px auto; 
            background: radial-gradient(ellipse at center, #1b5e20 0%, #0a2e0b 100%); 
            border: 6px solid #3e2723; border-radius: 125px; box-shadow: 0 4px 15px rgba(0,0,0,0.8); 
        }

        .mob-info { position: absolute; top: 25%; width: 100%; text-align: center; pointer-events: none; }
        .mob-info-src { font-size: 10px; color: #888; text-transform: uppercase; }
        .mob-info-spot { font-size: 20px; font-weight: 900; color: rgba(255,255,255,0.15); }
        .seat { position: absolute; width: 44px; height: 44px; background: #222; border: 1px solid #444; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 9px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 2px; }
        .seat-active { border-color: #ffc107; background: #2a2a2a; }
        .seat-folded { opacity: 0.4; border-color: #333; }
        .chip-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; pointer-events: none; }
        .chip-mob { width: 14px; height: 14px; background: #111; border: 2px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .chip-3bet { width: 16px; height: 16px; background: #d32f2f; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.8); }
        .dealer-mob { width: 16px; height: 16px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 9px; display: flex; justify-content: center; align-items: center; border: 1px solid #bfa006; position: absolute; z-index: 11; }
        .bet-txt { font-size: 10px; font-weight: bold; color: #fff; text-shadow: 1px 1px 2px #000; background: rgba(0,0,0,0.6); padding: 1px 3px; border-radius: 4px; margin-top: -5px; z-index: 20; }
        
        .hero-mob { position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); display: flex; gap: 5px; z-index: 20; background: #222; padding: 5px 10px; border-radius: 12px; border: 1px solid #ffc107; }
        .card-mob { width: 45px; height: 64px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .tl-mob { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1; }
        .c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #111; } .suit-green { color: #198754; }
        .rng-badge { position: absolute; bottom: 50px; right: -15px; width: 30px; height: 30px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 12px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 40; }
        
        .rng-hint { text-align: center; color: #6c757d; font-size: 11px; font-family: 'Roboto', sans-serif; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("База ренджей пуста."); return

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
            st.error("Спот не найден.")
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

        with st.expander("⚙️ Настройки Фильтров", expanded=False):
            saved = utils.load_user_settings()
            sel_sc = st.multiselect("Сценарий", all_scenarios, default=[s for s in saved.get("scenarios", []) if s in all_scenarios])
            
            sel_spots_keys = []
            if sel_sc:
                st.markdown("**Споты для тренировки:**")
                saved_spots = saved.get("spots", [])
                for sc in sel_sc:
                    st.markdown(f"<div style='color:#ffc107; font-size:14px; font-weight:bold; margin-top:8px;'>{sc}</div>", unsafe_allow_html=True)
                    for sp_name, sp_key in scenario_map[sc]:
                        is_checked = (sp_key in saved_spots) if "spots" in saved else True
                        if st.checkbox(sp_name, value=is_checked, key=f"m_chk_{sp_key}"):
                            sel_spots_keys.append(sp_key)
            
            if st.button("🚀 Применить", use_container_width=True):
                utils.save_user_settings({"scenarios": sel_sc, "spots": sel_spots_keys})
                st.session_state.hand = None; st.rerun()

        pool = sel_spots_keys
        if not pool:
            st.warning("⚠️ Не выбран ни один спот.")
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
    c1 = "suit-red" if s1 == '♥' else "suit-blue" if s1 == '♦' else "suit-green" if s1 == '♣' else "suit-black"
    c2 = "suit-red" if s2 == '♥' else "suit-blue" if s2 == '♦' else "suit-green" if s2 == '♣' else "suit-black"

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
        cards = '<div class="opp-cards-mob"></div>' if has_cards else ""
        ss = get_seat_style(i)
        opp_html += f'<div class="seat {cls}" style="{ss}">{cards}<span class="seat-label">{p}</span></div>'
        
        cs = get_chip_style(i)
        if is_defense and p == villain_pos and display_villain_bet:
            bet_txt = f'<div class="bet-txt">{display_villain_bet}bb</div>'
            if is_3bet_pot:
                chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-12px;"></div>{bet_txt}</div>'
            else:
                chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-5px;"></div>{bet_txt}</div>'
        elif p in ["SB", "BB"]:
            if not (is_defense and p == villain_pos):
                chips_html += f'<div class="chip-container" style="{cs}"><div class="chip-mob"></div></div>'
        
        if p == btn_pos:
            bs = get_btn_style(i)
            chips_html += f'<div class="dealer-mob" style="{bs}">D</div>'

    hero_cs = get_chip_style(0)
    if is_defense and display_hero_bet: 
        bet_txt = f'<div class="bet-txt">{display_hero_bet}bb</div>'
        if display_hero_bet == 1.0:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div>{bet_txt}</div>'
        else:
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-5px;"></div>{bet_txt}</div>'
    else:
        if hero_pos in ["SB", "BB"]: 
            chips_html += f'<div class="chip-container" style="{hero_cs}"><div class="chip-mob"></div></div>'
        
    if rot[0] == btn_pos:
        hero_bs = get_btn_style(0)
        chips_html += f'<div class="dealer-mob" style="{hero_bs}">D</div>'

    html = f"""
    <div class="mobile-game-area">
        <div class="mob-info"><div class="mob-info-src">{sc}</div><div class="mob-info-spot">{sp}</div></div>
        {opp_html} {chips_html}
        <div class="hero-mob">
            <div class="card-mob"><div class="tl-mob {c1}">{h_val[0]}<br>{s1}</div><div class="c-mob {c1}">{s1}</div></div>
            <div class="card-mob"><div class="tl-mob {c2}">{h_val[1]}<br>{s2}</div><div class="c-mob {c2}">{s2}</div></div>
            <div class="rng-badge">{rng}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    if is_defense:
        st.markdown('<div class="rng-hint">RNG 0-Freq: ACTION &nbsp;|&nbsp; Freq-100: FOLD</div>', unsafe_allow_html=True)

    # БЛОК РЕНДЕРИНГА КНОПОК В СТОПКУ С ЦВЕТАМИ
    if not st.session_state.srs_mode:
        if is_defense:
            st.markdown("""<style>
                div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(180deg, #495057, #343a40) !important; color: #adb5bd !important; box-shadow: 0 5px 0 #1d2124, 0 6px 10px rgba(0,0,0,0.3) !important; }
                div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(180deg, #20c997, #198754) !important; color: #fff !important; box-shadow: 0 5px 0 #0f5132, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
                div[data-testid="column"]:nth-of-type(3) button { background: linear-gradient(180deg, #e83e8c, #d63384) !important; color: #fff !important; box-shadow: 0 5px 0 #a02561, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
            </style>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("FOLD", key="f", use_container_width=True):
                    corr = (correct_act == "FOLD")
                    st.session_state.last_error = not corr
                    st.session_state.msg = f"✅ Correct" if corr else f"❌ Err! RNG {rng} -> {correct_act}"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), "CorrectAction": correct_act})
                    st.session_state.srs_mode = True; st.rerun()
            with c2:
                if st.button("CALL", key="c", use_container_width=True):
                    corr = (correct_act == "CALL")
                    st.session_state.last_error = not corr
                    st.session_state.msg = f"✅ Correct" if corr else f"❌ Err! RNG {rng} -> {correct_act}"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), "CorrectAction": correct_act})
                    st.session_state.srs_mode = True; st.rerun()
            with c3:
                if st.button("RAISE", key="r", use_container_width=True):
                    corr = (correct_act == "RAISE")
                    st.session_state.last_error = not corr
                    st.session_state.msg = f"✅ Correct" if corr else f"❌ Err! RNG {rng} -> {correct_act}"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), "CorrectAction": correct_act})
                    st.session_state.srs_mode = True; st.rerun()
        else:
            st.markdown("""<style>
                div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(180deg, #495057, #343a40) !important; color: #adb5bd !important; box-shadow: 0 5px 0 #1d2124, 0 6px 10px rgba(0,0,0,0.3) !important; }
                div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(180deg, #e83e8c, #d63384) !important; color: #fff !important; box-shadow: 0 5px 0 #a02561, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
            </style>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("FOLD", key="f", use_container_width=True):
                    corr = (correct_act == "FOLD")
                    st.session_state.last_error = not corr
                    st.session_state.msg = "✅ Correct" if corr else "❌ Err"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), "CorrectAction": correct_act})
                    st.session_state.srs_mode = True; st.rerun()
            with c2:
                if st.button("RAISE", key="r", use_container_width=True):
                    corr = (correct_act == "RAISE")
                    st.session_state.last_error = not corr
                    st.session_state.msg = "✅ Correct" if corr else "❌ Err"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(corr), "CorrectAction": correct_act})
                    st.session_state.srs_mode = True; st.rerun()
    else:
        st.markdown("""<style>
            div[data-testid="column"]:nth-of-type(1) button { background: linear-gradient(180deg, #fd7e14, #e85d04) !important; color: #fff !important; box-shadow: 0 5px 0 #a13d00, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
            div[data-testid="column"]:nth-of-type(2) button { background: linear-gradient(180deg, #0dcaf0, #0aa2c0) !important; color: #fff !important; box-shadow: 0 5px 0 #057085, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
            div[data-testid="column"]:nth-of-type(3) button { background: linear-gradient(180deg, #6f42c1, #59339d) !important; color: #fff !important; box-shadow: 0 5px 0 #3a1e6d, 0 6px 10px rgba(0,0,0,0.3) !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4); }
        </style>""", unsafe_allow_html=True)
        
        if st.session_state.last_error:
            st.markdown(f'<div style="background:#dc3545; color:white; padding:8px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:8px; font-size:14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#28a745; color:white; padding:8px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:8px; font-size:14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">{st.session_state.msg}</div>', unsafe_allow_html=True)
            
        with st.expander(f"🔍 Смотреть рендж ({correct_act})", expanded=st.session_state.last_error):
            st.markdown(utils.render_range_matrix(data, st.session_state.hand), unsafe_allow_html=True)
        
        s1, s2, s3 = st.columns(3)
        k = f"{src}_{sc}_{sp}".replace(" ","_")
        with s1:
            if st.button("HARD", use_container_width=True): 
                utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        with s2:
            if st.button("NORM", use_container_width=True): 
                utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        with s3:
            if st.button("EASY", use_container_width=True): 
                utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()
