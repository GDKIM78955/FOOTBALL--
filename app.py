import streamlit as st
import pandas as pd
import re
import time
from database import load_sheet_data, get_gspread_client
from infographics import generate_naver_injury_infographic, render_clipboard_component

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="축구 결장자 & 징계 관리 전용 앱",
    page_icon="🚑",
    layout="wide"
)

# ---------------------------------------------------------
# ⚙️ 설정: 구글 시트 ID 입력 (기존 앱과 동일한 시트 ID 사용)
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ 데이터베이스 설정")
spreadsheet_id = st.sidebar.text_input(
    "구글 시트 Spreadsheet ID",
    value="1-b-QusmoSnsvMhToNFe1B1IK7dJUKjjANs89y5ZekAQ",
    type="default"
)

st.sidebar.info("💡 기존에 쓰시던 구글 시트 ID가 입력되어 있으며, '부상자명단'과 '경기내용' 시트를 연동하여 가볍고 빠르게 작동합니다.")

# 메인 타이틀
st.title("🚑 팀별 부상자/결장자 명단 및 카드 리포트 (결장자 전용 경량 모듈)")
st.markdown("---")

if not spreadsheet_id:
    st.warning("⚠️ 왼쪽 사이드바에 구글 시트의 Spreadsheet ID를 입력해 주세요!")
    st.stop()

# 시트 데이터 로딩
injury_sheet_name = "부상자명단"
stats_sheet_name = "경기내용"

with st.spinner("구글 시트에서 결장자 및 경기 데이터를 불러오는 중..."):
    df_injuries = load_sheet_data(injury_sheet_name, spreadsheet_id)
    df_stats_red = load_sheet_data(stats_sheet_name, spreadsheet_id)

def extract_month_day(date_str):
    if not date_str or not str(date_str).strip():
        return None
    s = str(date_str).strip()
    digits = re.findall(r"\d+", s)
    if len(digits) >= 3:
        m = int(digits[1])
        d = int(digits[2])
        return m * 100 + d
    elif len(digits) == 2:
        m = int(digits[0])
        d = int(digits[1])
        return m * 100 + d
    return None

# 1. 퇴장 발생 경기 자동 추적 레이더
with st.expander("🚨 [기간 및 리그별 퇴장 발생 경기 자동 추적 레이더] (놓친 징계 선수 찾기)", expanded=True):
    st.caption("10번 '경기내용' 시트에 기록된 경기 중 퇴장(레드카드)이 발생한 매치업을 기간 및 리그별로 자동 추출합니다.")
    
    date_col_name = None
    if not df_stats_red.empty:
        for c_cand in ["경기날짜", "날짜", "일자", "경기일자", "Date"]:
            if c_cand in df_stats_red.columns:
                date_col_name = c_cand
                break
        if date_col_name is None and len(df_stats_red.columns) > 2:
            date_col_name = df_stats_red.columns[2]

    lg_col_name = "리그명" if "리그명" in df_stats_red.columns else (df_stats_red.columns[1] if len(df_stats_red.columns) > 1 else "리그명")

    all_stat_leagues = ["전체 리그"]
    if not df_stats_red.empty and lg_col_name in df_stats_red.columns:
        all_stat_leagues += sorted([str(x).strip() for x in df_stats_red[lg_col_name].dropna().unique().tolist() if str(x).strip()])
    
    c_rc1, c_rc2, c_rc3 = st.columns([1, 1, 1])
    sel_rc_league = c_rc1.selectbox("조회할 리그", all_stat_leagues, key="rc_filter_league")
    
    rc_date_from = c_rc2.text_input("시작 날짜 필터 (포함)", placeholder="예: 08.21 또는 25.08.21", key="rc_date_from")
    rc_date_to = c_rc3.text_input("종료 날짜 필터 (포함)", placeholder="예: 08.29 또는 25.08.29", key="rc_date_to")

    val_from = extract_month_day(rc_date_from)
    val_to = extract_month_day(rc_date_to)

    if not df_stats_red.empty and "퇴장_홈" in df_stats_red.columns and "퇴장_원" in df_stats_red.columns:
        def to_num_rc(val):
            try:
                return float(str(val).replace("%", "").strip())
            except:
                return 0.0

        red_card_records = []
        for _, r in df_stats_red.iterrows():
            r_league = str(r.get(lg_col_name, "")).strip()
            r_date_raw = str(r.get(date_col_name, "")).strip() if date_col_name else ""
            r_date_val = extract_month_day(r_date_raw)
            
            r_home = str(r.get("홈팀", "")).strip()
            r_away = str(r.get("원정팀", "")).strip()
            
            rc_h = to_num_rc(r.get("퇴장_홈", 0))
            rc_a = to_num_rc(r.get("퇴장_원", 0))

            if sel_rc_league != "전체 리그" and r_league.upper() != sel_rc_league.upper():
                continue

            if val_from is not None and r_date_val is not None:
                if r_date_val < val_from:
                    continue
            elif rc_date_from.strip():
                if r_date_raw < rc_date_from.strip():
                    continue

            if val_to is not None and r_date_val is not None:
                if r_date_val > val_to:
                    continue
            elif rc_date_to.strip():
                if r_date_raw > rc_date_to.strip():
                    continue

            if rc_h > 0 or rc_a > 0:
                red_teams = []
                if rc_h > 0: red_teams.append(f"🔴 홈팀 [{r_home}] ({int(rc_h)}명 퇴장)")
                if rc_a > 0: red_teams.append(f"🔴 원정팀 [{r_away}] ({int(rc_a)}명 퇴장)")

                red_card_records.append({
                    "경기날짜": r_date_raw if r_date_raw else "-",
                    "리그": r_league, "매치업": f"{r_home} vs {r_away}",
                    "🚨 퇴장 발생 팀": " / ".join(red_teams),
                    "홈 퇴장": int(rc_h), "원정 퇴장": int(rc_a)
                })

        if red_card_records:
            st.error(f"🚨 선택하신 조건에서 **총 {len(red_card_records)}건의 퇴장 발생 경기**가 발견되었습니다! 해당 팀의 선수를 아래 결장 명단에 등록하세요.")
            st.dataframe(pd.DataFrame(red_card_records), use_container_width=True, hide_index=True)
        else:
            st.success("✅ 선택하신 기간 및 리그 조건에서 퇴장(레드카드)이 발생한 경기가 없습니다.")
    else:
        st.info("💡 '경기내용' 시트에 퇴장 기록 데이터가 없습니다.")

st.markdown("---")

# 시트 내 팀명 및 리그명 컬럼 자동 인식
team_col_name = "팀명" if not df_injuries.empty and "팀명" in df_injuries.columns else (df_injuries.columns[2] if not df_injuries.empty and len(df_injuries.columns) > 2 else None)
league_col_name = "리그명" if not df_injuries.empty and "리그명" in df_injuries.columns else (df_injuries.columns[1] if not df_injuries.empty and len(df_injuries.columns) > 1 else None)

all_known_teams = set()
if not df_injuries.empty and team_col_name:
    all_known_teams.update(df_injuries[team_col_name].dropna().unique())

if not df_stats_red.empty:
    for col_cand in ["홈팀", "Home"]:
        if col_cand in df_stats_red.columns:
            all_known_teams.update(df_stats_red[col_cand].dropna().unique())
            break
    for col_cand in ["원정팀", "Away"]:
        if col_cand in df_stats_red.columns:
            all_known_teams.update(df_stats_red[col_cand].dropna().unique())
            break

fallback_teams = ["웨스트햄", "리버풀", "맨체스터시티", "아스날", "첼시", "토트넘", "맨체스터유나이티드", "뉴캐슬", "아스톤빌라", "브라이튼"]
all_known_teams.update(fallback_teams)

team_options = sorted([str(t).strip() for t in all_known_teams if str(t).strip() and str(t).strip() != "nan"])

# =========================================================
# 🎯 팀 & 대회(리그/챔스 등) 멀티 필터 영역
# =========================================================
c_s1, c_s2, c_s3 = st.columns([1.2, 1, 1.3])
default_inj_idx = 0
if "selected_scan_match" in st.session_state and st.session_state.selected_scan_match:
    sm = st.session_state.selected_scan_match
    if sm["home"] in team_options:
        default_inj_idx = team_options.index(sm["home"])

selected_team = c_s1.selectbox("1️⃣ 조회할 팀명 선택", team_options, index=default_inj_idx, key="inj_filter_team")

# 선택한 팀에 등록된 대회(리그명) 목록 추출 + 기본 대회 옵션 제공
base_competitions = ["PL", "UCL", "UEL", "UECL", "LaLiga", "SerieA", "Bundesliga", "Ligue1", "컵대회"]
team_competitions = []
if not df_injuries.empty and team_col_name and league_col_name:
    team_rows = df_injuries[df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()]
    team_competitions = [str(x).strip() for x in team_rows[league_col_name].dropna().unique() if str(x).strip()]

comp_options = []
for c in team_competitions + base_competitions:
    if c not in comp_options:
        comp_options.append(c)
comp_options.append("전체 보기 (통합)")

selected_comp = c_s2.selectbox(
    "2️⃣ 대회/리그 기준 선택 (스탯 분리)",
    comp_options,
    index=0,
    help="같은 팀이라도 리그용(PL)과 챔스용(UCL) 스탯을 분리해서 관리하고 조회할 수 있습니다."
)

# 대회 선택 시 인포그래픽 상단 기준 표기 자동 추천
auto_title_map = {
    "PL": "잉글랜드 1부리그 기록",
    "UCL": "UEFA 챔피언스리그 기록",
    "UEL": "UEFA 유로파리그 기록",
    "UECL": "UEFA 컨퍼런스리그 기록",
    "LaLiga": "스페인 라리가 기록",
    "SerieA": "이탈리아 세리에A 기록",
    "Bundesliga": "독일 분데스리가 기록",
    "Ligue1": "프랑스 리그1 기록",
    "컵대회": "자국 컵대회 기록",
    "전체 보기 (통합)": "시즌 통합 기록"
}
default_title_val = auto_title_map.get(selected_comp, f"{selected_comp} 기록")
inj_league_title = c_s3.text_input("3️⃣ 카드 리포트 기준 표기", value=default_title_val)

# 역할 프리셋 목록 (요청사항 1번: 드롭다운 선택형)
ROLE_OPTIONS = ["주전", "핵심 주전", "로테이션", "백업", "유망주", "기타"]

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

# 2. 새로운 결장 선수 추가
with col_btn1:
    with st.expander("➕ 결장 선수 추가", expanded=False):
        f_s1, f_s2, f_s3 = st.columns(3)
        add_season = f_s1.text_input("시즌", value="25-26", key="add_inj_season")
        default_add_comp = "PL" if selected_comp == "전체 보기 (통합)" else selected_comp
        add_league = f_s2.text_input("대회/리그명", value=default_add_comp, key="add_inj_league")
        add_team = f_s3.text_input("팀명", value=selected_team, key="add_inj_team")

        f1, f2, f3 = st.columns(3)
        p_name_en = f1.text_input("선수 영문명", placeholder="예: Lucas Paquetá", key="p_name_en")
        p_name_kr = f2.text_input("선수 한글명", placeholder="예: 루카스 파케타", key="p_name_kr")
        p_pos = f3.selectbox("포지션", ["FW", "MF", "DF", "GK"], key="p_pos")

        f4, f5, f6, f7 = st.columns(4)
        p_start = f4.number_input("선발 출전", min_value=0, value=0, key="p_start")
        p_sub = f5.number_input("교체 출전", min_value=0, value=0, key="p_sub")
        p_goals = f6.number_input("골", min_value=0, value=0, key="p_goals")
        p_assists = f7.number_input("도움", min_value=0, value=0, key="p_assists")

        f8, f9, f10 = st.columns(3)
        # 요청사항 1번: 팀 내 역할을 Selectbox로 선택
        p_role = f8.selectbox("팀 내 역할", ROLE_OPTIONS, index=0, key="p_role")
        p_reason = f9.selectbox("결장 사유", ["부상", "결장의심", "징계/퇴장", "기타"], key="p_reason")
        p_note = f10.text_input("특이사항", value="-", placeholder="예: 복귀 예정 10월", key="p_note")

        if st.button("💾 구글 시트에 저장", type="primary", use_container_width=True):
            if p_name_en.strip() or p_name_kr.strip():
                client = get_gspread_client()
                if client:
                    try:
                        spreadsheet = client.open_by_key(spreadsheet_id)
                        ws_inj = spreadsheet.worksheet(injury_sheet_name)
                        new_row = [
                            add_season.strip(), add_league.strip(), add_team.strip(),
                            p_name_en.strip(), p_name_kr.strip(),
                            p_pos, p_start, p_sub, p_goals, p_assists,
                            p_role,
                            p_reason,
                            p_note.strip() if p_note.strip() else "-"
                        ]
                        ws_inj.append_row(new_row, value_input_option="USER_ENTERED")
                        time.sleep(0.3)
                        st.cache_data.clear()
                        st.success(f"🎉 [{add_team} - {add_league}] {p_name_kr or p_name_en} 선수가 저장되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"저장 실패: {e}")
                else:
                    st.warning("구글 시트 클라이언트 연결 실패. Secrets 설정을 확인하세요.")
            else:
                st.warning("선수 이름을 입력해 주세요.")

# 3. 부상 선수 정보 수정하기 (현재 선택된 팀 + 대회 기준)
with col_btn2:
    with st.expander("✏️ 선수 정보/스탯 수정", expanded=False):
        if not df_injuries.empty and team_col_name:
            filtered_df_edit = df_injuries[df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()]
            if selected_comp != "전체 보기 (통합)" and league_col_name:
                filtered_df_edit = filtered_df_edit[filtered_df_edit[league_col_name].astype(str).str.strip() == str(selected_comp).strip()]

            if not filtered_df_edit.empty:
                edit_player_ids = []
                edit_player_labels = {}
                for idx, row in filtered_df_edit.iterrows():
                    lg_tag = row.get(league_col_name, "") if league_col_name else ""
                    kr = row.get("선수한글명", row.get(df_injuries.columns[4], ""))
                    en = row.get("선수영문명", row.get(df_injuries.columns[3], ""))
                    disp_name = f"[{lg_tag}] {kr} ({en})" if kr and en else f"[{lg_tag}] {kr or en}"
                    edit_player_ids.append(idx)
                    edit_player_labels[idx] = disp_name

                if "edit_selected_idx" not in st.session_state or st.session_state.edit_selected_idx not in edit_player_ids:
                    st.session_state.edit_selected_idx = edit_player_ids[0]

                sel_idx = st.selectbox(
                    "수정할 선수 선택", 
                    edit_player_ids, 
                    format_func=lambda x: edit_player_labels[x], 
                    key="edit_selected_idx"
                )
                
                target_row_data = filtered_df_edit.loc[sel_idx]

                e_col1, e_col2 = st.columns(2)
                curr_lg_val = str(target_row_data.get(league_col_name, "PL")) if league_col_name else "PL"
                e_league = e_col1.text_input("대회/리그명 수정", value=curr_lg_val, key=f"edit_lg_{sel_idx}")
                
                pos_list = ["FW", "MF", "DF", "GK"]
                curr_pos = str(target_row_data.get("포지션", target_row_data.get(df_injuries.columns[5], "MF")))
                pos_idx = pos_list.index(curr_pos) if curr_pos in pos_list else 1
                e_pos = e_col2.selectbox("포지션 수정", pos_list, index=pos_idx, key=f"edit_pos_{sel_idx}")

                e_kr = st.text_input("선수 한글명 수정", value=str(target_row_data.get("선수한글명", target_row_data.get(df_injuries.columns[4], ""))), key=f"edit_kr_{sel_idx}")
                e_en = st.text_input("선수 영문명 수정", value=str(target_row_data.get("선수영문명", target_row_data.get(df_injuries.columns[3], ""))), key=f"edit_en_{sel_idx}")

                e1, e2, e3, e4 = st.columns(4)
                e_start = e1.number_input("선발", min_value=0, value=int(target_row_data.get("선발", target_row_data.get(df_injuries.columns[6], 0)) or 0), key=f"edit_start_{sel_idx}")
                e_sub = e2.number_input("교체", min_value=0, value=int(target_row_data.get("교체", target_row_data.get(df_injuries.columns[7], 0)) or 0), key=f"edit_sub_{sel_idx}")
                e_goals = e3.number_input("골", min_value=0, value=int(target_row_data.get("골", target_row_data.get(df_injuries.columns[8], 0)) or 0), key=f"edit_goals_{sel_idx}")
                e_assists = e4.number_input("도움", min_value=0, value=int(target_row_data.get("도움", target_row_data.get(df_injuries.columns[9], 0)) or 0), key=f"edit_assists_{sel_idx}")

                # 요청사항 1번: 수정 시에도 팀 내 역할을 Selectbox로 선택 (기존 텍스트 호환)
                curr_role = str(target_row_data.get("역할", target_row_data.get(df_injuries.columns[10], "주전"))).strip()
                dynamic_role_options = ROLE_OPTIONS if curr_role in ROLE_OPTIONS else [curr_role] + ROLE_OPTIONS
                e_role = st.selectbox("팀 내 역할 수정", dynamic_role_options, index=dynamic_role_options.index(curr_role), key=f"edit_role_{sel_idx}")
                
                reason_list = ["부상", "결장의심", "징계/퇴장", "기타"]
                curr_reason = str(target_row_data.get("결장사유", target_row_data.get("사유", target_row_data.get(df_injuries.columns[11], "부상"))))
                reason_idx = reason_list.index(curr_reason) if curr_reason in reason_list else 0
                e_reason = st.selectbox("결장 사유 수정", reason_list, index=reason_idx, key=f"edit_reason_{sel_idx}")
                
                e_note = st.text_input("특이사항 수정", value=str(target_row_data.get("특이사항", target_row_data.get(df_injuries.columns[12], "-"))), key=f"edit_note_{sel_idx}")

                if st.button("🔄 정보 갱신하기", type="primary", use_container_width=True):
                    client = get_gspread_client()
                    if client:
                        try:
                            spreadsheet = client.open_by_key(spreadsheet_id)
                            ws_inj = spreadsheet.worksheet(injury_sheet_name)
                            
                            updated_row_values = [
                                str(target_row_data.get("시즌", "25-26")),
                                e_league.strip(),
                                str(selected_team),
                                e_en.strip(),
                                e_kr.strip(),
                                e_pos,
                                e_start,
                                e_sub,
                                e_goals,
                                e_assists,
                                e_role,
                                e_reason,
                                e_note.strip() if e_note.strip() else "-"
                            ]
                            ws_inj.update(f"A{sel_idx + 2}:M{sel_idx + 2}", [updated_row_values], value_input_option="USER_ENTERED")
                            time.sleep(0.3)
                            st.cache_data.clear()
                            st.success(f"🎉 [{e_kr or e_en}] 선수의 정보가 수정되었습니다!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"수정 실패: {e}")
            else:
                st.info(f"현재 [{selected_team} - {selected_comp}]에 수정할 선수가 없습니다.")
        else:
            st.info("시트에 등록된 선수 데이터가 없습니다.")

# 4. 요청사항 2번: 타 대회용(예: PL -> UCL) 결장 명단 일괄 복제 기능
with col_btn3:
    with st.expander("⚡ 타 대회용 명단 복제", expanded=False):
        st.caption("다친 선수는 동일한데 챔스/컵대회 스탯만 다르게 써야 할 때, 기존 대회 명단을 새 대회용으로 1초 만에 복사합니다.")
        if not df_injuries.empty and team_col_name and league_col_name and team_competitions:
            src_comp = st.selectbox("가져올 원본 대회", team_competitions, key="clone_src_comp")
            dst_comp = st.selectbox("생성할 대상 대회", ["UCL", "UEL", "UECL", "PL", "컵대회", "직접입력"], key="clone_dst_comp")
            if dst_comp == "직접입력":
                dst_comp = st.text_input("대상 대회명 직접 입력", value="FA컵", key="clone_dst_custom")
            reset_stats = st.checkbox("출전/골/도움 스탯 0으로 초기화해서 복사", value=True, help="체크하면 새 대회 스탯을 0선발 0교체 0골 0도움으로 깔끔하게 비워서 생성합니다.")

            if st.button("🚀 명단 일괄 복제하기", type="primary", use_container_width=True):
                if src_comp == dst_comp:
                    st.warning("원본 대회와 대상 대회가 같습니다.")
                else:
                    src_rows = df_injuries[
                        (df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()) &
                        (df_injuries[league_col_name].astype(str).str.strip() == str(src_comp).strip())
                    ]
                    if not src_rows.empty:
                        client = get_gspread_client()
                        if client:
                            try:
                                spreadsheet = client.open_by_key(spreadsheet_id)
                                ws_inj = spreadsheet.worksheet(injury_sheet_name)
                                new_rows_to_append = []
                                for _, r in src_rows.iterrows():
                                    new_rows_to_append.append([
                                        str(r.get("시즌", "25-26")),
                                        dst_comp.strip(),
                                        str(selected_team),
                                        str(r.get("선수영문명", r.get(df_injuries.columns[3], ""))),
                                        str(r.get("선수한글명", r.get(df_injuries.columns[4], ""))),
                                        str(r.get("포지션", r.get(df_injuries.columns[5], "MF"))),
                                        0 if reset_stats else int(r.get("선발", 0) or 0),
                                        0 if reset_stats else int(r.get("교체", 0) or 0),
                                        0 if reset_stats else int(r.get("골", 0) or 0),
                                        0 if reset_stats else int(r.get("도움", 0) or 0),
                                        str(r.get("역할", r.get(df_injuries.columns[10], "주전"))),
                                        str(r.get("결장사유", r.get("사유", r.get(df_injuries.columns[11], "부상")))),
                                        str(r.get("특이사항", r.get(df_injuries.columns[12], "-")))
                                    ])
                                ws_inj.append_rows(new_rows_to_append, value_input_option="USER_ENTERED")
                                time.sleep(0.3)
                                st.cache_data.clear()
                                st.success(f"🎉 [{src_comp}] 명단 {len(new_rows_to_append)}명이 [{dst_comp}] 대회용으로 복제되었습니다! 상단에서 [{dst_comp}]를 선택해 스탯만 수정하세요.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"복제 실패: {e}")
        else:
            st.info(f"[{selected_team}]에 먼저 기본 대회 결장자를 1명 이상 등록해 주세요.")

# 5. 복귀 선수 제외 (삭제 - 모든 대회 동시 복귀 옵션 포함)
with col_btn4:
    with st.expander("🗑️ 복귀 선수 제외", expanded=False):
        if not df_injuries.empty and team_col_name:
            filtered_df_rm = df_injuries[df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()]
            if selected_comp != "전체 보기 (통합)" and league_col_name:
                filtered_df_rm = filtered_df_rm[filtered_df_rm[league_col_name].astype(str).str.strip() == str(selected_comp).strip()]

            if not filtered_df_rm.empty:
                player_options = []
                for idx, row in filtered_df_rm.iterrows():
                    lg_tag = row.get(league_col_name, "") if league_col_name else ""
                    kr = row.get("선수한글명", "")
                    en = row.get("선수영문명", "")
                    name_display = f"[{lg_tag}] {kr} ({en})" if kr and en else f"[{lg_tag}] {kr or en}"
                    player_options.append((idx, name_display, kr, en))
                
                sel_player_to_remove = st.selectbox("복귀한 선수 선택", player_options, format_func=lambda x: x[1], key="sel_remove_player")
                del_all_comps = st.checkbox("이 선수를 모든 대회(리그+챔스 등)에서 한 번에 복귀(삭제) 처리", value=True)
                
                if st.button("🚀 복귀 완료 (삭제)", type="secondary", use_container_width=True):
                    client = get_gspread_client()
                    if client:
                        with st.spinner("삭제 중..."):
                            try:
                                spreadsheet = client.open_by_key(spreadsheet_id)
                                ws_inj = spreadsheet.worksheet(injury_sheet_name)
                                
                                if del_all_comps:
                                    # 같은 팀 내 동일 이름 선수 행 모두 찾아서 역순 삭제 (행 밀림 방지)
                                    target_kr, target_en = sel_player_to_remove[2], sel_player_to_remove[3]
                                    team_all_rows = df_injuries[df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()]
                                    rows_to_del = []
                                    for r_idx, r_val in team_all_rows.iterrows():
                                        r_kr = str(r_val.get("선수한글명", "")).strip()
                                        r_en = str(r_val.get("선수영문명", "")).strip()
                                        if (target_kr and r_kr == target_kr) or (target_en and r_en == target_en):
                                            rows_to_del.append(r_idx + 2)
                                    for sheet_row in sorted(rows_to_del, reverse=True):
                                        ws_inj.delete_rows(sheet_row)
                                else:
                                    target_row_index = sel_player_to_remove[0] + 2
                                    ws_inj.delete_rows(target_row_index)

                                time.sleep(0.3)
                                st.cache_data.clear()
                                st.success(f"🎉 [{sel_player_to_remove[1]}] 선수가 제외되었습니다!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"삭제 실패: {e}")
            else:
                st.info(f"현재 [{selected_team} - {selected_comp}]에 등록된 선수가 없습니다.")
        else:
            st.info("시트에 등록된 데이터가 없습니다.")

st.markdown("---")

# =========================================================
# 📊 선택된 팀 & 선택된 대회 기준 결장자 필터링 및 카드 출력
# =========================================================
filtered_df = pd.DataFrame()
if not df_injuries.empty and team_col_name:
    filtered_df = df_injuries[df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()]
    if selected_comp != "전체 보기 (통합)" and league_col_name:
        filtered_df = filtered_df[filtered_df[league_col_name].astype(str).str.strip() == str(selected_comp).strip()]

reason_col = None
if not filtered_df.empty:
    for c in filtered_df.columns:
        if any(k in c for k in ["결장사유", "사유", "비고"]):
            reason_col = c
            break
    if reason_col is None and len(filtered_df.columns) > 11:
        reason_col = filtered_df.columns[11]

confirmed_players = []
doubt_players = []

if not filtered_df.empty and reason_col and reason_col in filtered_df.columns:
    for _, p_row in filtered_df.iterrows():
        p_dict = p_row.to_dict()
        val_reason = str(p_dict.get(reason_col, "")).strip()
        if "의심" in val_reason or "GTD" in val_reason:
            doubt_players.append(p_dict)
        else:
            confirmed_players.append(p_dict)
elif not filtered_df.empty:
    confirmed_players = filtered_df.to_dict("records")

st.subheader(f"📋 [{selected_team}] ({selected_comp}) 결장자 현황 (총 {len(filtered_df)}명)")

with st.expander("📊 / 📋 네이버 블로그/카페용 결장자 인포그래픽 도표 복사 (추천 ⭐)", expanded=True):
    st.markdown(f"##### 🌟 [네이버 블로그/카페 전용] [{selected_team}] 결장자 리포트 카드 ({selected_comp})")
    st.caption("초록색 버튼을 1번만 클릭하면 네이버 블로그 서식으로 복사됩니다. 블로그 글쓰기에서 Ctrl+V를 누르세요!")

    naver_inj_html = generate_naver_injury_infographic(
        selected_team, inj_league_title, confirmed_players, doubt_players
    )
    render_clipboard_component(naver_inj_html, "t5_clip", height=520)

with st.expander("🔍 시트에 저장된 원본 데이터 표 보기"):
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"💡 [{selected_team}]의 [{selected_comp}] 대회에 등록된 부상/결장 선수 데이터가 없습니다. (다른 대회 명단이 있다면 '⚡ 타 대회용 명단 복제'를 눌러 생성해 보세요!)")
