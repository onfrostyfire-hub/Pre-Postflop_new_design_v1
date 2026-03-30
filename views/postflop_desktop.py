import streamlit as st
import poker_utils as utils

def show():
    pf_db = utils.load_postflop_ranges()
    if not pf_db: 
        st.warning("⚠️ База постфлопа пуста. Добавь JSON в папку postflop_data/")
        return

    # Строим дерево фильтров из ключей
    tree = {}
    for full_key in pf_db.keys():
        parts = [p.strip() for p in full_key.split('|')]
        if len(parts) != 5: continue
        spot, hero_pos, street, branch, board = parts
        
        if spot not in tree: tree[spot] = {}
        if hero_pos not in tree[spot]: tree[spot][hero_pos] = {}
        if street not in tree[spot][hero_pos]: tree[spot][hero_pos][street] = {}
        if branch not in tree[spot][hero_pos][street]: tree[spot][hero_pos][street][branch] = []
        
        tree[spot][hero_pos][street][branch].append((board, full_key))

    with st.sidebar:
        st.header("⚙️ Postflop Filters")
        dv_btn = st.radio("Interface Mode", ["📱 Mobile", "💻 Desktop"], index=1)
        if dv_btn != st.session_state.actual_view_type:
            st.session_state.actual_view_type = dv_btn
            st.rerun()
            
        st.markdown("---")
        saved = utils.load_user_settings(is_postflop=True)
        
        spots_list = sorted(list(tree.keys()))
        sel_spot = st.selectbox("1. Spot", spots_list, index=0 if spots_list else None)
        
        sel_hero, sel_street, sel_branch = None, None, None
        sel_spots_keys = []
        
        if sel_spot:
            hero_list = sorted(list(tree[sel_spot].keys()))
            sel_hero = st.selectbox("2. Position", hero_list, index=0 if hero_list else None)
            
        if sel_hero:
            street_list = sorted(list(tree[sel_spot][sel_hero].keys()))
            sel_street = st.selectbox("3. Street", street_list, index=0 if street_list else None)
            
        if sel_street:
            branch_list = sorted(list(tree[sel_spot][sel_hero][sel_street].keys()))
            sel_branch = st.selectbox("4. Branch (Action)", branch_list, index=0 if branch_list else None)
            
        if sel_branch:
            st.markdown("**5. Boards for training:**")
            saved_spots = saved.get("pf_spots", [])
            
            boards = tree[sel_spot][sel_hero][sel_street][sel_branch]
            for board_name, full_key in boards:
                is_checked = (full_key in saved_spots) if "pf_spots" in saved else True
                if st.checkbox(board_name, value=is_checked, key=f"pf_chk_{full_key}"):
                    sel_spots_keys.append(full_key)
        
        if st.button("🚀 Apply Postflop Settings", use_container_width=True):
            saved["pf_spots"] = sel_spots_keys
            utils.save_user_settings(saved, is_postflop=True)
            st.session_state.pf_hand = None
            st.rerun()

    pool = sel_spots_keys
    if not pool:
        st.warning("⚠️ Выбери фильтры и борды в меню слева.")
        st.stop()
        
    st.success(f"Выбрано бордов для тренировки: {len(pool)}")
    st.info("Архитектура каскадных фильтров готова. Ядро настроено на изоляцию. Жду отмашки на Этап 3 (Отрисовка стола).")
