import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
import time
import json
from database import (
    load_sheet_data,
    get_gspread_client,
    load_drive_logo_map,
    get_logo_base64_src
)
from infographics import (
    generate_naver_injury_infographic,
    render_clipboard_component
)

# =========================================================
# 🎨 [내장 함수] 카페/SNS용 다크 스카우팅 카드 & 이미지 복사기
# (infographics.py 버전에 상관없이 에러가 나지 않도록 직접 내장)
# =========================================================
def get_role_badge_html_dark(role):
    role_str = str(role).strip() if role else "-"
    if "핵심" in role_str:
        bg_color, border_color = "#7c3aed", "#a78bfa"
    elif "주전" in role_str:
        bg_color, border_color = "#ef4444", "#f87171"
    elif "로테이션" in role_str:
        bg_color, border_color = "#2563eb", "#60a5fa"
    elif "백업" in role_str:
        bg_color, border_color = "#475569", "#94a3b8"
    elif "유망주" in role_str:
        bg_color, border_color = "#10b981", "#34d399"
    else:
        bg_color, border_color = "#64748b", "#94a3b8"

    return (
        f"<span style='background-color: {bg_color}; color: #ffffff; "
        f"padding: 2px 7px; border-radius: 4px; font-size: 10px; "
        f"font-weight: bold; display: inline-block; margin-top: 3px; border: 1px solid {border_color};'>{role_str}</span>"
    )

def generate_cafe_dark_infographic(team_name, league_title, confirmed_list, doubt_list, logo_src=""):
    all_players = confirmed_list + doubt_list
    total_out = len(all_players)
    
    key_out = 0
    total_goals = 0
    total_assists = 0
    for p in all_players:
        r_str = str(p.get("역할", ""))
        if "주전" in r_str or "핵심" in r_str:
            key_out += 1
        try:
            total_goals += int(float(str(p.get("골", 0) or 0)))
        except Exception:
            pass
        try:
            total_assists += int(float(str(p.get("도움", 0) or 0)))
        except Exception:
            pass

    if logo_src:
        logo_box_html = f"""
        <div style="width: 68px; height: 68px; background: #ffffff; border: 2px solid #38bdf8; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(56, 189, 248, 0.25); padding: 6px; box-sizing: border-box; flex-shrink: 0;">
            <img src="{logo_src}" style="max-width: 54px; max-height: 54px; object-fit: contain; display: block;" />
        </div>
        """
    else:
        logo_box_html = """
        <div style="width: 68px; height: 68px; background: #1e293b; border: 2px solid #38bdf8; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 30px; flex-shrink: 0;">
            🛡️
        </div>
        """

    def get_pos_chip(pos):
        p_str = str(pos).strip().upper()
        if p_str == "FW":
            c = "#f43f5e"
        elif p_str == "MF":
            c = "#38bdf8"
        elif p_str == "DF":
            c = "#10b981"
        else:
            c = "#f59e0b"
        return f"<span style='background: rgba(15,23,42,0.8); color: {c}; border: 1px solid {c}; padding: 2px 7px; border-radius: 5px; font-size: 11px; font-weight: 800; letter-spacing: 0.5px;'>{p_str}</span>"

    html = f"""
    <div style="width: 100%; max-width: 650px; margin: 0 auto; background-color: #0b1120; background-image: radial-gradient(rgba(56, 189, 248, 0.08) 1px, transparent 1px); background-size: 18px 18px; border: 1px solid #1e293b; border-radius: 18px; padding: 22px; box-sizing: border-box; font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; color: #f8fafc; box-shadow: 0 12px 30px rgba(0,0,0,0.5);">
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div style="display: flex; gap: 8px; align-items: center;">
                <span style="background: linear-gradient(90deg, #dc2626, #ef4444); color: #ffffff; font-size: 11px; font-weight: 800; padding: 4px 12px; border-radius: 999px; letter-spacing: 0.5px;">SQUAD INJURY REPORT</span>
                <span style="background: #131c31; border: 1px solid #334155; color: #cbd5e1; font-size: 11px; font-weight: bold; padding: 4px 12px; border-radius: 999px;">{league_title}</span>
            </div>
            <div style="background: #131c31; border: 1px solid #1e293b; color: #38bdf8; font-size: 11px; font-weight: bold; padding: 4px 12px; border-radius: 999px;">
                ⚡ 전력 누수 분석
            </div>
        </div>

        <div style="background: linear-gradient(135deg, #111827 0%, #1e293b 100%); border: 1px solid #334155; border-radius: 14px; padding: 18px 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 16px;">
                {logo_box_html}
                <div>
                    <div style="font-size: 11px; font-weight: 800; color: #38bdf8; letter-spacing: 1.2px;">OFFICIAL ABSENCE & GTD STATUS</div>
                    <div style="font-size: 25px; font-weight: 900; color: #ffffff; margin-top: 2px; letter-spacing: -0.5px;">{team_name}</div>
                    <div style="display: flex; gap: 6px; margin-top: 6px;">
                        <span style="background: #0f172a; border: 1px solid #334155; color: #94a3b8; font-size: 11px; padding: 2px 8px; border-radius: 6px;">📋 기준: {league_title}</span>
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="width: 64px; height: 64px; border-radius: 50%; border: 4px solid {'#ef4444' if total_out > 0 else '#10b981'}; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #0b1120; box-shadow: 0 0 12px {'rgba(239,68,68,0.3)' if total_out > 0 else 'rgba(16,185,129,0.3)'};">
                    <div style="font-size: 18px; font-weight: 900; color: #ffffff; line-height: 1;">{total_out}명</div>
                    <div style="font-size: 9px; color: #94a3b8; margin-top: 3px; font-weight: bold;">결장/의심</div>
                </div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 18px;">
            <div style="background: #111827; border: 1px solid #1e293b; border-top: 2px solid #f8fafc; border-radius: 10px; padding: 10px 8px; text-align: center;">
                <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">총 이탈 인원</div>
                <div style="font-size: 18px; font-weight: 900; color: #ffffff; margin-top: 4px;">{total_out}명</div>
                <div style="font-size: 9px; color: #64748b; margin-top: 2px;">확정 {len(confirmed_list)} · 의심 {len(doubt_list)}</div>
            </div>
            <div style="background: #111827; border: 1px solid #1e293b; border-top: 2px solid #ef4444; border-radius: 10px; padding: 10px 8px; text-align: center;">
                <div style="font-size: 10px; color: #fca5a5; font-weight: bold;">핵심·주전 이탈</div>
                <div style="font-size: 18px; font-weight: 900; color: #ef4444; margin-top: 4px;">{key_out}명</div>
                <div style="font-size: 9px; color: #64748b; margin-top: 2px;">주전급 전력 누수</div>
            </div>
            <div style="background: #111827; border: 1px solid #1e293b; border-top: 2px solid #10b981; border-radius: 10px; padding: 10px 8px; text-align: center;">
                <div style="font-size: 10px; color: #6ee7b7; font-weight: bold;">결장자 합산 스탯</div>
                <div style="font-size: 16px; font-weight: 900; color: #10b981; margin-top: 5px;">{total_goals}골 {total_assists}도움</div>
                <div style="font-size: 9px; color: #64748b; margin-top: 2px;">공격포인트 공백</div>
            </div>
            <div style="background: #111827; border: 1px solid #1e293b; border-top: 2px solid #f59e0b; border-radius: 10px; padding: 10px 8px; text-align: center;">
                <div style="font-size: 10px; color: #fcd34d; font-weight: bold;">결장 의심 (GTD)</div>
                <div style="font-size: 18px; font-weight: 900; color: #f59e0b; margin-top: 4px;">{len(doubt_list)}명</div>
                <div style="font-size: 9px; color: #64748b; margin-top: 2px;">라인업 직전 확인</div>
            </div>
        </div>
    """

    if not confirmed_list and not doubt_list:
        html += """
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 24px; text-align: center;">
            <div style="font-size: 16px; font-weight: 800; color: #34d399;">✅ 현재 등록된 부상 및 징계 결장자가 없습니다.</div>
            <div style="font-size: 12px; color: #a7f3d0; margin-top: 6px;">스쿼드 100% 가동 가능 (Full Strength Squad 👑)</div>
        </div>
        """

    if confirmed_list:
        html += """
        <div style="background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 14px; margin-bottom: 14px;">
            <div style="font-size: 13px; font-weight: 800; color: #f87171; margin-bottom: 10px;">🔴 결장 확정 명단 (CONFIRMED OUT)</div>
        """
        for p in confirmed_list:
            kr = p.get("선수한글명", "")
            en = p.get("선수영문명", "")
            main_name = kr if kr else en
            sub_name = en if (kr and en) else ""
            pos = p.get("포지션", "MF")
            role = p.get("역할", "-")
            start = p.get("선발", 0)
            sub = p.get("교체", 0)
            goals = p.get("골", 0)
            assists = p.get("도움", 0)
            reason = p.get("결장사유", p.get("사유", "부상"))
            note = p.get("특이사항", "-")
            note_html = f"<div style='font-size: 10px; color: #94a3b8; margin-top: 3px;'>({note})</div>" if note != "-" else ""

            pos_chip = get_pos_chip(pos)
            role_badge = get_role_badge_html_dark(role)

            html += f"""
            <div style="background: #192338; border: 1px solid #263554; border-left: 4px solid #ef4444; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div style="flex: 1.3; min-width: 0; padding-right: 8px;">
                    <div style="font-size: 14px; font-weight: 800; color: #ffffff;">{main_name}</div>
                    <div style="font-size: 10px; color: #94a3b8; margin-top: 1px;">{sub_name}</div>
                </div>
                <div style="flex: 0.9; text-align: center;">
                    {pos_chip}<br>{role_badge}
                </div>
                <div style="flex: 1.2; text-align: center; background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 5px 6px; margin: 0 8px;">
                    <div style="font-size: 11px; color: #cbd5e1;">{start}선발 · {sub}교체</div>
                    <div style="font-size: 12px; font-weight: 800; color: #34d399; margin-top: 2px;">⚽ {goals}골 · 🎯 {assists}도움</div>
                </div>
                <div style="flex: 1.0; text-align: right;">
                    <span style="background: rgba(239, 68, 68, 0.18); border: 1px solid #ef4444; color: #fca5a5; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; display: inline-block;">🚨 {reason}</span>
                    {note_html}
                </div>
            </div>
            """
        html += "</div>"

    if doubt_list:
        html += """
        <div style="background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 14px;">
            <div style="font-size: 13px; font-weight: 800; color: #fbbf24; margin-bottom: 10px;">🟡 결장 의심 명단 (QUESTIONABLE / GTD)</div>
        """
        for p in doubt_list:
            kr = p.get("선수한글명", "")
            en = p.get("선수영문명", "")
            main_name = kr if kr else en
            sub_name = en if (kr and en) else ""
            pos = p.get("포지션", "MF")
            role = p.get("역할", "-")
            start = p.get("선발", 0)
            sub = p.get("교체", 0)
            goals = p.get("골", 0)
            assists = p.get("도움", 0)
            reason = p.get("결장사유", p.get("사유", "결장의심"))
            note = p.get("특이사항", "-")
            note_html = f"<div style='font-size: 10px; color: #94a3b8; margin-top: 3px;'>({note})</div>" if note != "-" else ""

            pos_chip = get_pos_chip(pos)
            role_badge = get_role_badge_html_dark(role)

            html += f"""
            <div style="background: #192338; border: 1px solid #263554; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div style="flex: 1.3; min-width: 0; padding-right: 8px;">
                    <div style="font-size: 14px; font-weight: 800; color: #ffffff;">{main_name}</div>
                    <div style="font-size: 10px; color: #94a3b8; margin-top: 1px;">{sub_name}</div>
                </div>
                <div style="flex: 0.9; text-align: center;">
                    {pos_chip}<br>{role_badge}
                </div>
                <div style="flex: 1.2; text-align: center; background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 5px 6px; margin: 0 8px;">
                    <div style="font-size: 11px; color: #cbd5e1;">{start}선발 · {sub}교체</div>
                    <div style="font-size: 12px; font-weight: 800; color: #34d399; margin-top: 2px;">⚽ {goals}골 · 🎯 {assists}도움</div>
                </div>
                <div style="flex: 1.0; text-align: right;">
                    <span style="background: rgba(245, 158, 11, 0.18); border: 1px solid #f59e0b; color: #fde68a; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; display: inline-block;">⚠️ {reason}</span>
                    {note_html}
                </div>
            </div>
            """
        html += "</div>"

    html += "</div>"
    return html

def render_cafe_image_component(html_content, component_id, height=680, team_name="팀"):
    safe_team_name = json.dumps(f"{team_name}_결장자리포트_다크.png")
    wrapper_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{ margin: 0; padding: 10px; font-family: 'Malgun Gothic', sans-serif; background-color: transparent; }}
            .btn-group {{ display: flex; gap: 10px; margin-bottom: 14px; }}
            .action-btn {{ flex: 1; color: #ffffff; font-size: 15px; font-weight: bold; padding: 13px 12px; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.15); }}
            .btn-img-copy {{ background: linear-gradient(90deg, #2563eb, #3b82f6); }}
            .btn-img-copy:hover {{ background: linear-gradient(90deg, #1d4ed8, #2563eb); }}
            .btn-img-down {{ flex: 0.35; background-color: #334155; }}
            .btn-img-down:hover {{ background-color: #1e293b; }}
            .preview-box {{ background-color: #060911; border: 1px solid #1e293b; border-radius: 14px; padding: 18px; overflow-x: auto; display: flex; justify-content: center; }}
            #cafe-capture-area {{ display: inline-block; width: 100%; max-width: 650px; }}
        </style>
    </head>
    <body>
        <div class="btn-group">
            <button class="action-btn btn-img-copy" id="cafeImgCopyBtn" onclick="copyCafeImage()">
                📸 [카페/SNS 전용] 고화질 다크 이미지 카드로 원클릭 복사 (클릭 후 Ctrl+V)
            </button>
            <button class="action-btn btn-img-down" onclick="downloadCafeImage()">
                📥 PNG 파일 저장
            </button>
        </div>
        <div class="preview-box">
            <div id="cafe-capture-area">{html_content}</div>
        </div>
        <script>
            async function copyCafeImage() {{
                const btn = document.getElementById('cafeImgCopyBtn');
                const origText = btn.innerText;
                btn.innerText = '⏳ 고화질 다크 이미지 렌더링 중...';
                try {{
                    const target = document.getElementById('cafe-capture-area');
                    const canvas = await html2canvas(target, {{ scale: 2, useCORS: true, backgroundColor: '#0b1120' }});
                    canvas.toBlob(async (blob) => {{
                        try {{
                            const item = new ClipboardItem({{ 'image/png': blob }});
                            await navigator.clipboard.write([item]);
                            btn.innerText = origText;
                            alert('🎉 고화질 다크 스카우팅 카드가 클립보드에 복사되었습니다!\\n카페나 블로그 글쓰기 창에서 [Ctrl + V]를 누르세요.');
                        }} catch (err) {{
                            btn.innerText = origText;
                            alert('클립보드 권한이 제한되었습니다. 우측의 [📥 PNG 파일 저장] 버튼을 이용해 주세요.');
                        }}
                    }}, 'image/png');
                }} catch (e) {{
                    btn.innerText = origText;
                    alert('이미지 변환 중 오류 발생: ' + e);
                }}
            }}
            async function downloadCafeImage() {{
                const target = document.getElementById('cafe-capture-area');
                const canvas = await html2canvas(target, {{ scale: 2, useCORS: true, backgroundColor: '#0b1120' }});
                const link = document.createElement('a');
                link.download = {safe_team_name};
                link.href = canvas.toDataURL('image/png');
                link.click();
            }}
        </script>
    </body>
    </html>
    """
    components.html(wrapper_html, height=height, scrolling=True)


# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="축구 결장자 & 징계 관리 전용 앱",
    page_icon="🚑",
    layout="wide"
)

# ---------------------------------------------------------
# ⚙️ 설정: 구글 시트 ID 및 구단 로고 폴더 설정
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ 데이터베이스 & 로고 설정")
spreadsheet_id = st.sidebar.text_input(
    "구글 시트 Spreadsheet ID",
    value="1-b-QusmoSnsvMhToNFe1B1IK7dJUKjjANs89y5ZekAQ",
    type="default"
)

DEFAULT_LOGO_FOLDER = "https://drive.google.com/drive/folders/1jhKbgnrWEK3t0rQuP9OYTryYrI56Ujye?usp=drive_link"
logo_folder_input = st.sidebar.text_input(
    "📁 구단 로고 폴더 ID (또는 폴더 링크)",
    value=DEFAULT_LOGO_FOLDER,
    placeholder="비워두면 드라이브 전체 로고 자동 인식",
    help="구글 드라이브 축구구단_로고 폴더 링크가 기본으로 등록되어 있습니다."
)

# 시트 및 로고 데이터 로딩
injury_sheet_name = "부상자명단"
stats_sheet_name = "경기내용"

with st.spinner("구글 시트 및 드라이브 로고 데이터를 불러오는 중..."):
    df_injuries = load_sheet_data(injury_sheet_name, spreadsheet_id)
    df_stats_red = load_sheet_data(stats_sheet_name, spreadsheet_id)
    logo_map = load_drive_logo_map(logo_folder_input)

# 사이드바: 로고 연동 개수 실시간 표시 & 새로고침 버튼
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ 구단 로고 연동 상태")
st.sidebar.success(f"현재 드라이브 로고: **총 {len(logo_map)}개** 파일 적용됨")

if st.sidebar.button("🔄 새 로고 파일 새로고침", use_container_width=True, help="구글 드라이브에 새 한글팀명 로고를 추가했을 때 누르면 즉시 반영됩니다."):
    load_drive_logo_map.clear()
    get_logo_base64_src.clear()
    st.rerun()

# 메인 타이틀
st.title("🚑 팀별 부상자/결장자 명단 및 카드 리포트 (결장자 전용 경량 모듈)")
st.markdown("---")

if not spreadsheet_id:
    st.warning("⚠️ 왼쪽 사이드바에 구글 시트의 Spreadsheet ID를 입력해 주세요!")
    st.stop()

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

def find_team_logo_id(team_name, l_map):
    if not team_name or not l_map:
        return None
    t_clean = str(team_name).strip()
    if t_clean in l_map:
        return l_map[t_clean]
    t_nospace = t_clean.replace(" ", "")
    for k, fid in l_map.items():
        if k.replace(" ", "") == t_nospace:
            return fid
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

if logo_map:
    all_known_teams.update(logo_map.keys())

fallback_teams = ["웨스트햄", "리버풀", "맨체스터시티", "아스날", "첼시", "토트넘", "맨체스터유나이티드", "뉴캐슬", "아스톤빌라", "브라이튼"]
all_known_teams.update(fallback_teams)

team_options = sorted([str(t).strip() for t in all_known_teams if str(t).strip() and str(t).strip() != "nan"])

# 구단 로고 매칭 현황판
matched_teams = [t for t in team_options if find_team_logo_id(t, logo_map)]
unmatched_teams = [t for t in team_options if not find_team_logo_id(t, logo_map)]

with st.expander(f"🛡️ 구단 로고 파일 적용 현황 확인 (드라이브 총 {len(logo_map)}개 파일 / 매칭 완료 {len(matched_teams)}개 팀, 미등록 {len(unmatched_teams)}개 팀)", expanded=False):
    st.caption("새 팀이 생기면 구글 드라이브 로고 폴더에 `한글팀명.png` (또는 `.jpg`) 파일을 넣은 뒤 왼쪽 사이드바의 [🔄 새 로고 파일 새로고침]을 누르세요.")
    l_col1, l_col2 = st.columns(2)
    with l_col1:
        st.markdown(f"**✅ 로고 적용 완료 팀 ({len(matched_teams)}개)**")
        st.write(", ".join(matched_teams) if matched_teams else "없음")
    with l_col2:
        st.markdown(f"**⚠️ 로고 미등록 팀 ({len(unmatched_teams)}개)**")
        st.write(", ".join(unmatched_teams) if unmatched_teams else "모든 팀에 로고가 적용되어 있습니다! 🎉")

# =========================================================
# 🎯 팀 & 대회 멀티 필터 영역
# =========================================================
c_s1, c_s2, c_s3 = st.columns([1.1, 1.2, 1.2])
default_inj_idx = 0
if "selected_scan_match" in st.session_state and st.session_state.selected_scan_match:
    sm = st.session_state.selected_scan_match
    if sm["home"] in team_options:
        default_inj_idx = team_options.index(sm["home"])

selected_team = c_s1.selectbox(
    "1️⃣ 조회할 팀명 선택 (🛡️=로고보유)",
    team_options,
    index=default_inj_idx,
    format_func=lambda t: f"🛡️ {t}" if find_team_logo_id(t, logo_map) else f"⚪ {t}",
    key="inj_filter_team"
)

base_competitions = [
    "PL", "EFL", "챔피언십", "Eredivisie", "에레디비지에",
    "UCL", "UEL", "UECL",
    "LaLiga", "SerieA", "Bundesliga", "Ligue1", "컵대회"
]

team_competitions = []
if not df_injuries.empty and team_col_name and league_col_name:
    team_rows = df_injuries[df_injuries[team_col_name].astype(str).str.strip() == str(selected_team).strip()]
    team_competitions = [str(x).strip() for x in team_rows[league_col_name].dropna().unique() if str(x).strip() and str(x).strip() != "nan"]

sheet_all_competitions = []
if not df_injuries.empty and league_col_name:
    sheet_all_competitions += [str(x).strip() for x in df_injuries[league_col_name].dropna().unique() if str(x).strip() and str(x).strip() != "nan"]
if not df_stats_red.empty and lg_col_name in df_stats_red.columns:
    sheet_all_competitions += [str(x).strip() for x in df_stats_red[lg_col_name].dropna().unique() if str(x).strip() and str(x).strip() != "nan"]

comp_options = []
for c in team_competitions + sheet_all_competitions + base_competitions:
    if c not in comp_options:
        comp_options.append(c)
comp_options.append("전체 보기 (통합)")
comp_options.append("➕ 직접 입력 (새 대회/리그)")

selected_comp_raw = c_s2.selectbox(
    "2️⃣ 대회/리그 기준 선택 (스탯 분리)",
    comp_options,
    index=0,
    help="현재 팀에 등록된 대회가 맨 위에 자동으로 표시되며, 목록에 없는 대회는 '➕ 직접 입력'을 선택해 바로 추가할 수 있습니다."
)

if selected_comp_raw == "➕ 직접 입력 (새 대회/리그)":
    custom_comp_input = c_s2.text_input("새 대회/리그명 입력", placeholder="예: K리그1, 포르투갈리그 등", key="custom_comp_top")
    selected_comp = custom_comp_input.strip() if custom_comp_input.strip() else "기타리그"
else:
    selected_comp = selected_comp_raw

auto_title_map = {
    "PL": "잉글랜드 1부리그(PL) 기록",
    "EPL": "잉글랜드 1부리그(PL) 기록",
    "EFL": "잉글랜드 챔피언십(2부) 기록",
    "챔피언십": "잉글랜드 챔피언십(2부) 기록",
    "CHAMPIONSHIP": "잉글랜드 챔피언십(2부) 기록",
    "EREDIVISIE": "네덜란드 에레디비지에 기록",
    "에레디비지에": "네덜란드 에레디비지에 기록",
    "ED": "네덜란드 에레디비지에 기록",
    "UCL": "UEFA 챔피언스리그 기록",
    "챔스": "UEFA 챔피언스리그 기록",
    "UEL": "UEFA 유로파리그 기록",
    "유로파": "UEFA 유로파리그 기록",
    "UECL": "UEFA 컨퍼런스리그 기록",
    "LALIGA": "스페인 라리가 기록",
    "라리가": "스페인 라리가 기록",
    "SERIEA": "이탈리아 세리에A 기록",
    "세리에A": "이탈리아 세리에A 기록",
    "BUNDESLIGA": "독일 분데스리가 기록",
    "분데스리가": "독일 분데스리가 기록",
    "LIGUE1": "프랑스 리그1 기록",
    "리그1": "프랑스 리그1 기록",
    "컵대회": "자국 컵대회 기록",
    "전체 보기 (통합)": "시즌 통합 기록"
}
default_title_val = auto_title_map.get(selected_comp.upper(), auto_title_map.get(selected_comp, f"{selected_comp} 기록"))
inj_league_title = c_s3.text_input("3️⃣ 카드 리포트 기준 표기", value=default_title_val)

ROLE_OPTIONS = ["주전", "핵심 주전", "로테이션", "백업", "유망주", "기타"]

# =========================================================
# 🛠️ 선수 관리 영역 (3단 와이드 배치)
# =========================================================
col_btn1, col_btn2, col_btn3 = st.columns([1.8, 1.2, 1.0])

# [왼쪽 넓은 칸] 새로운 결장 선수 추가
with col_btn1:
    with st.expander("➕ 결장 선수 추가 (넓은 입력창)", expanded=False):
        f_s1, f_s2, f_s3 = st.columns([0.8, 1.2, 1.2])
        add_season = f_s1.text_input("시즌", value="25-26", key="add_inj_season")
        
        add_comp_list = [c for c in comp_options if c not in ["전체 보기 (통합)", "➕ 직접 입력 (새 대회/리그)"]]
        if selected_comp not in ["전체 보기 (통합)", "➕ 직접 입력 (새 대회/리그)"] and selected_comp not in add_comp_list:
            add_comp_list.insert(0, selected_comp)
        add_comp_list.append("➕ 직접 입력")

        default_add_idx = add_comp_list.index(selected_comp) if selected_comp in add_comp_list else 0
        sel_add_league = f_s2.selectbox("대회/리그 선택", add_comp_list, index=default_add_idx, key="add_inj_league_sel")
        
        if sel_add_league == "➕ 직접 입력":
            add_league = f_s2.text_input("새 대회명 직접 입력", placeholder="예: 에레디비지에, 챔피언십", key="add_inj_league_custom")
        else:
            add_league = sel_add_league

        add_team = f_s3.text_input("팀명", value=selected_team, key="add_inj_team")

        f1, f2, f3 = st.columns([1.4, 1.4, 0.7])
        p_name_en = f1.text_input("선수 영문명", placeholder="예: Lucas Paquetá", key="p_name_en")
        p_name_kr = f2.text_input("선수 한글명", placeholder="예: 루카스 파케타", key="p_name_kr")
        p_pos = f3.selectbox("포지션", ["FW", "MF", "DF", "GK"], key="p_pos")

        f4, f5, f6, f7 = st.columns(4)
        p_start = f4.number_input("선발 출전", min_value=0, value=0, key="p_start")
        p_sub = f5.number_input("교체 출전", min_value=0, value=0, key="p_sub")
        p_goals = f6.number_input("골", min_value=0, value=0, key="p_goals")
        p_assists = f7.number_input("도움", min_value=0, value=0, key="p_assists")

        f8, f9, f10 = st.columns([1, 1, 1.5])
        p_role = f8.selectbox("팀 내 역할", ROLE_OPTIONS, index=0, key="p_role")
        p_reason = f9.selectbox("결장 사유", ["부상", "결장의심", "징계/퇴장", "기타"], key="p_reason")
        p_note = f10.text_input("특이사항", value="-", placeholder="예: 복귀 예정 10월", key="p_note")

        if st.button("💾 구글 시트에 저장", type="primary", use_container_width=True):
            if not add_league.strip():
                st.warning("대회/리그명을 입력해 주세요.")
            elif p_name_en.strip() or p_name_kr.strip():
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

# [가운데 칸] 위: 타 대회용 명단 복제 / 아래: 선수 정보 및 스탯 수정
with col_btn2:
    with st.expander("⚡ 타 대회용 명단 복제", expanded=False):
        st.caption("다친 선수는 동일한데 챔스/유로파/컵대회 스탯만 다르게 써야 할 때, 기존 대회 명단을 새 대회용으로 1초 만에 복사합니다.")
        if not df_injuries.empty and team_col_name and league_col_name and team_competitions:
            src_comp = st.selectbox("가져올 원본 대회", team_competitions, key="clone_src_comp")
            
            clone_target_list = ["UCL", "UEL", "UECL", "PL", "EFL", "챔피언십", "Eredivisie", "에레디비지에", "컵대회"]
            for c in comp_options:
                if c not in clone_target_list and c not in ["전체 보기 (통합)", "➕ 직접 입력 (새 대회/리그)"]:
                    clone_target_list.append(c)
            clone_target_list.append("➕ 직접 입력")

            dst_comp_sel = st.selectbox("생성할 대상 대회", clone_target_list, key="clone_dst_comp")
            if dst_comp_sel == "➕ 직접 입력":
                dst_comp = st.text_input("대상 대회명 직접 입력", value="FA컵", key="clone_dst_custom")
            else:
                dst_comp = dst_comp_sel

            reset_stats = st.checkbox("출전/골/도움 스탯 0으로 초기화해서 복사", value=True)

            if st.button("🚀 명단 일괄 복제하기", type="primary", use_container_width=True):
                if not dst_comp.strip():
                    st.warning("대상 대회명을 입력해 주세요.")
                elif src_comp == dst_comp.strip():
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
                                st.success(f"🎉 [{src_comp}] 명단 {len(new_rows_to_append)}명이 [{dst_comp}] 대회용으로 복제되었습니다!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"복제 실패: {e}")
        else:
            st.info(f"[{selected_team}]에 먼저 기본 대회 결장자를 1명 이상 등록해 주세요.")

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
                curr_lg_val = str(target_row_data.get(league_col_name, "PL")).strip() if league_col_name else "PL"
                edit_comp_options = [c for c in comp_options if c not in ["전체 보기 (통합)", "➕ 직접 입력 (새 대회/리그)"]]
                if curr_lg_val not in edit_comp_options:
                    edit_comp_options.insert(0, curr_lg_val)
                edit_comp_options.append("➕ 직접 입력")

                sel_edit_lg = e_col1.selectbox("대회/리그명 수정", edit_comp_options, index=edit_comp_options.index(curr_lg_val), key=f"edit_lg_sel_{sel_idx}")
                if sel_edit_lg == "➕ 직접 입력":
                    e_league = e_col1.text_input("새 대회명 입력", value=curr_lg_val, key=f"edit_lg_custom_{sel_idx}")
                else:
                    e_league = sel_edit_lg
                
                pos_list = ["FW", "MF", "DF", "GK"]
                curr_pos = str(target_row_data.get("포지션", target_row_data.get(df_injuries.columns[5], "MF")))
                pos_idx = pos_list.index(curr_pos) if curr_pos in pos_list else 1
                e_pos = e_col2.selectbox("포지션 수정", pos_list, index=pos_idx, key=f"edit_pos_{sel_idx}")

                e_name1, e_name2 = st.columns(2)
                e_kr = e_name1.text_input("선수 한글명 수정", value=str(target_row_data.get("선수한글명", target_row_data.get(df_injuries.columns[4], ""))), key=f"edit_kr_{sel_idx}")
                e_en = e_name2.text_input("선수 영문명 수정", value=str(target_row_data.get("선수영문명", target_row_data.get(df_injuries.columns[3], ""))), key=f"edit_en_{sel_idx}")

                e1, e2, e3, e4 = st.columns(4)
                e_start = e1.number_input("선발", min_value=0, value=int(target_row_data.get("선발", target_row_data.get(df_injuries.columns[6], 0)) or 0), key=f"edit_start_{sel_idx}")
                e_sub = e2.number_input("교체", min_value=0, value=int(target_row_data.get("교체", target_row_data.get(df_injuries.columns[7], 0)) or 0), key=f"edit_sub_{sel_idx}")
                e_goals = e3.number_input("골", min_value=0, value=int(target_row_data.get("골", target_row_data.get(df_injuries.columns[8], 0)) or 0), key=f"edit_goals_{sel_idx}")
                e_assists = e4.number_input("도움", min_value=0, value=int(target_row_data.get("도움", target_row_data.get(df_injuries.columns[9], 0)) or 0), key=f"edit_assists_{sel_idx}")

                curr_role = str(target_row_data.get("역할", target_row_data.get(df_injuries.columns[10], "주전"))).strip()
                dynamic_role_options = ROLE_OPTIONS if curr_role in ROLE_OPTIONS else [curr_role] + ROLE_OPTIONS
                
                er_col1, er_col2 = st.columns(2)
                e_role = er_col1.selectbox("팀 내 역할 수정", dynamic_role_options, index=dynamic_role_options.index(curr_role), key=f"edit_role_{sel_idx}")
                
                reason_list = ["부상", "결장의심", "징계/퇴장", "기타"]
                curr_reason = str(target_row_data.get("결장사유", target_row_data.get("사유", target_row_data.get(df_injuries.columns[11], "부상"))))
                reason_idx = reason_list.index(curr_reason) if curr_reason in reason_list else 0
                e_reason = er_col2.selectbox("결장 사유 수정", reason_list, index=reason_idx, key=f"edit_reason_{sel_idx}")
                
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

# [오른쪽 칸] 복귀 선수 제외
with col_btn3:
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
# 📊 선택된 팀 & 대회 기준 결장자 필터링 및 2개 탭(블로그용 / 카페용) 출력
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

matched_logo_id = find_team_logo_id(selected_team, logo_map)
team_logo_base64 = get_logo_base64_src(matched_logo_id) if matched_logo_id else ""

logo_status_badge = "🛡️ 카페용 다크 카드 로고 연동됨" if team_logo_base64 else "⚠️ 로고 미등록 (기본 아이콘 표시)"
st.subheader(f"📋 [{selected_team}] ({selected_comp}) 결장자 현황 (총 {len(filtered_df)}명) — {logo_status_badge}")

# 탭 1: 네이버 블로그용 (기존 텍스트 표) / 탭 2: 카페용 (고화질 다크 스카우팅 이미지)
tab_blog, tab_cafe = st.tabs([
    "📝 네이버 블로그용 (텍스트 표 원클릭 복사)",
    "🎨 카페/SNS용 (로고 포함 고화질 다크 이미지 복사 ⭐)"
])

with tab_blog:
    st.markdown(f"##### 📝 [네이버 블로그 전용] [{selected_team}] 텍스트 표 리포트 ({selected_comp})")
    st.caption("기존처럼 이미지 없이 순수 텍스트와 표 서식으로만 복사되어 네이버 블로그 검색 노출(SEO)에 최적화되어 있습니다.")
    naver_inj_html = generate_naver_injury_infographic(
        selected_team, inj_league_title, confirmed_players, doubt_players
    )
    render_clipboard_component(naver_inj_html, "t5_clip_blog", height=540)

with tab_cafe:
    st.markdown(f"##### 🎨 [카페/SNS 전용] [{selected_team}] 다크 스카우팅 리포트 카드 ({selected_comp})")
    st.caption("구단 로고와 전력 누수 요약 대시보드가 포함된 고화질 다크 테마 카드입니다. 파란색 버튼을 누른 뒤 카페 글쓰기에서 Ctrl+V를 누르세요!")
    cafe_dark_html = generate_cafe_dark_infographic(
        selected_team, inj_league_title, confirmed_players, doubt_players, logo_src=team_logo_base64
    )
    dynamic_height = max(580, 380 + len(filtered_df) * 75)
    render_cafe_image_component(cafe_dark_html, "t5_clip_cafe", height=dynamic_height, team_name=selected_team)

with st.expander("🔍 시트에 저장된 원본 데이터 표 보기"):
    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"💡 [{selected_team}]의 [{selected_comp}] 대회에 등록된 부상/결장 선수 데이터가 없습니다. (다른 대회 명단이 있다면 '⚡ 타 대회용 명단 복제'를 눌러 생성해 보세요!)")
