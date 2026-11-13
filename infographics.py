import streamlit.components.v1 as components
import json


# =========================================================
# 🎨 역할별 배지 스타일 생성 헬퍼 함수
# =========================================================
def get_role_badge_html(role, is_dark=False):
    role_str = str(role).strip() if role else "-"
    
    if "핵심" in role_str:
        bg_color = "#7c3aed"  # 보라색 (핵심 주전)
        border_color = "#a78bfa"
    elif "주전" in role_str:
        bg_color = "#ef4444"  # 빨간색 (주전)
        border_color = "#f87171"
    elif "로테이션" in role_str:
        bg_color = "#2563eb"  # 파란색 (로테이션)
        border_color = "#60a5fa"
    elif "백업" in role_str:
        bg_color = "#475569"  # 슬레이트 (백업)
        border_color = "#94a3b8"
    elif "유망주" in role_str:
        bg_color = "#10b981"  # 에메랄드 (유망주)
        border_color = "#34d399"
    else:
        bg_color = "#64748b"  # 회색 (기타)
        border_color = "#94a3b8"

    extra_style = f"border: 1px solid {border_color};" if is_dark else ""
    return (
        f"<span style='background-color: {bg_color}; color: #ffffff; "
        f"padding: 2px 7px; border-radius: 4px; font-size: 10px; "
        f"font-weight: bold; display: inline-block; margin-top: 3px; {extra_style}'>{role_str}</span>"
    )


# =========================================================
# 1️⃣ [탭 1: 네이버 블로그 전용] 텍스트 표 복사 렌더러 (기존 방식 복원)
# =========================================================
def render_clipboard_component(html_content, component_id, height=520):
    escaped_html = json.dumps(html_content)
    wrapper_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: 'Malgun Gothic', sans-serif;
                background-color: transparent;
            }}
            .copy-btn {{
                width: 100%;
                background-color: #03c75a;
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 12px;
            }}
            .copy-btn:hover {{
                background-color: #02b150;
            }}
            .preview-box {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <button class="copy-btn" onclick="copyHtmlToClipboard()">
            📋 [네이버 블로그 텍스트/표 서식 원클릭 복사하기] (클릭 후 블로그에 Ctrl+V)
        </button>
        <div class="preview-box">
            {html_content}
        </div>

        <script>
            function copyHtmlToClipboard() {{
                const htmlData = {escaped_html};
                const blobHtml = new Blob([htmlData], {{ type: 'text/html' }});
                const blobText = new Blob([htmlData.replace(/<[^>]*>?/gm, '')], {{ type: 'text/plain' }});
                const data = [new ClipboardItem({{ 'text/html': blobHtml, 'text/plain': blobText }})];

                navigator.clipboard.write(data).then(() => {{
                    alert('🎉 네이버 블로그용 텍스트 표 서식이 복사되었습니다! 블로그 글쓰기 창에서 [Ctrl + V]를 누르세요.');
                }}).catch(err => {{
                    alert('복사 권한이 제한되었습니다. 아래 미리보기 영역을 직접 드래그(Ctrl+C)해주세요.');
                }});
            }}
        </script>
    </body>
    </html>
    """
    components.html(wrapper_html, height=height, scrolling=True)


# =========================================================
# 1️⃣ [탭 1: 네이버 블로그 전용] 순수 텍스트/표 HTML 생성 (이미지 없음)
# =========================================================
def generate_naver_injury_infographic(team_name, league_title, confirmed_list, doubt_list):
    html = f"""
    <table align="center" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 620px; margin: 0 auto; font-family: 'Malgun Gothic', '맑은 고딕', AppleSDGothicNeo-Regular, sans-serif; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; border-collapse: separate; color: #0f172a;">
        <tr>
            <td style="padding: 20px;">
                <table border="0" cellpadding="0" cellspacing="0" style="width: 100%; border-bottom: 2px solid #0f172a; margin-bottom: 16px;">
                    <tr>
                        <td align="center" style="padding-bottom: 10px; text-align: center;">
                            <div style="font-size: 11px; font-weight: bold; color: #dc2626; letter-spacing: 1px;">INJURY & SUSPENSION REPORT</div>
                            <div style="font-size: 18px; font-weight: bold; color: #0f172a; margin-top: 4px;">
                                🚑 [{team_name}] 결장 및 결장의심 명단
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">기준: <b>{league_title}</b></div>
                        </td>
                    </tr>
                </table>
    """

    if not confirmed_list and not doubt_list:
        html += """
                <table border="0" cellpadding="0" cellspacing="0" style="width: 100%; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; margin-top: 10px; margin-bottom: 10px;">
                    <tr>
                        <td align="center" style="padding: 20px; text-align: center; color: #166534; font-size: 14px; font-weight: bold;">
                            ✅ 현재 등록된 부상 및 징계 결장자가 없습니다.<br>
                            <span style="font-size: 12px; color: #15803d; font-weight: normal; margin-top: 4px; display: inline-block;">(스쿼드 100% 전력 구성 완료 👑)</span>
                        </td>
                    </tr>
                </table>
        """

    if confirmed_list:
        html += """
                <div style="font-size: 13px; font-weight: bold; color: #dc2626; margin-bottom: 6px;">🔴 결장 확정 명단</div>
                <table border="1" cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; border: 1px solid #cbd5e1; margin-bottom: 16px;">
                    <tr style="background-color: #fee2e2;">
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #991b1b; text-align: center;">선수명</th>
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #991b1b; text-align: center;">포지션/역할</th>
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #991b1b; text-align: center;">시즌 기록</th>
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #991b1b; text-align: center;">사유/비고</th>
                    </tr>
        """
        for p in confirmed_list:
            kr = p.get("선수한글명", "")
            en = p.get("선수영문명", "")
            name_str = f"<b>{kr}</b><br><span style='font-size: 10px; color: #64748b;'>{en}</span>" if kr and en else f"<b>{kr or en}</b>"
            pos = p.get("포지션", "MF")
            role = p.get("역할", "-")
            start = p.get("선발", 0)
            sub = p.get("교체", 0)
            goals = p.get("골", 0)
            assists = p.get("도움", 0)
            reason = p.get("결장사유", p.get("사유", "부상"))
            note = p.get("특이사항", "-")
            note_str = f"<br><span style='font-size: 10px; color: #64748b;'>({note})</span>" if note != "-" else ""

            role_badge = get_role_badge_html(role, is_dark=False)

            html += f"""
                    <tr>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">{name_str}</td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;"><b>{pos}</b><br>{role_badge}</td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">{start}선발 {sub}교체<br><b>{goals}골 {assists}도움</b></td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; color: #dc2626; text-align: center;"><b>{reason}</b>{note_str}</td>
                    </tr>
            """
        html += "</table>"

    if doubt_list:
        html += """
                <div style="font-size: 13px; font-weight: bold; color: #d97706; margin-bottom: 6px;">🟡 결장 의심 명단 (GTD)</div>
                <table border="1" cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; border: 1px solid #cbd5e1; margin-bottom: 10px;">
                    <tr style="background-color: #fef3c7;">
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #92400e; text-align: center;">선수명</th>
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #92400e; text-align: center;">포지션/역할</th>
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #92400e; text-align: center;">시즌 기록</th>
                        <th align="center" style="padding: 7px 3px; border: 1px solid #cbd5e1; color: #92400e; text-align: center;">사유/비고</th>
                    </tr>
        """
        for p in doubt_list:
            kr = p.get("선수한글명", "")
            en = p.get("선수영문명", "")
            name_str = f"<b>{kr}</b><br><span style='font-size: 10px; color: #64748b;'>{en}</span>" if kr and en else f"<b>{kr or en}</b>"
            pos = p.get("포지션", "MF")
            role = p.get("역할", "-")
            start = p.get("선발", 0)
            sub = p.get("교체", 0)
            goals = p.get("골", 0)
            assists = p.get("도움", 0)
            reason = p.get("결장사유", p.get("사유", "결장의심"))
            note = p.get("특이사항", "-")
            note_str = f"<br><span style='font-size: 10px; color: #64748b;'>({note})</span>" if note != "-" else ""

            role_badge = get_role_badge_html(role, is_dark=False)

            html += f"""
                    <tr>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">{name_str}</td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;"><b>{pos}</b><br>{role_badge}</td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">{start}선발 {sub}교체<br><b>{goals}골 {assists}도움</b></td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; color: #d97706; text-align: center;"><b>{reason}</b>{note_str}</td>
                    </tr>
            """
        html += "</table>"

    html += """
            </td>
        </tr>
    </table>
    """
    return html


# =========================================================
# 2️⃣ [탭 2: 카페/SNS 전용] 다크 스카우팅 대시보드 이미지 생성기
# =========================================================
def generate_cafe_dark_infographic(team_name, league_title, confirmed_list, doubt_list, logo_src=""):
    all_players = confirmed_list + doubt_list
    total_out = len(all_players)
    
    # 주전급(핵심 주전 + 주전) 인원 및 합산 공격포인트 계산
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

    # 구단 로고 박스 (흰 배경 로고가 엠블럼 배지처럼 보이도록 디자인)
    if logo_src:
        logo_box_html = f"""
        <div style="width: 68px; height: 68px; background: #ffffff; border: 2px solid #38bdf8; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(56, 189, 248, 0.25); padding: 6px; box-sizing: border-box; flex-shrink: 0;">
            <img src="{logo_src}" style="max-width: 54px; max-height: 54px; object-fit: contain; display: block;" />
        </div>
        """
    else:
        logo_box_html = f"""
        <div style="width: 68px; height: 68px; background: #1e293b; border: 2px solid #38bdf8; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 30px; flex-shrink: 0;">
            🛡️
        </div>
        """

    # 포지션별 포인트 색상
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
        
        <!-- 상단 캡슐 태그 바 -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div style="display: flex; gap: 8px; align-items: center;">
                <span style="background: linear-gradient(90deg, #dc2626, #ef4444); color: #ffffff; font-size: 11px; font-weight: 800; padding: 4px 12px; border-radius: 999px; letter-spacing: 0.5px;">SQUAD INJURY REPORT</span>
                <span style="background: #131c31; border: 1px solid #334155; color: #cbd5e1; font-size: 11px; font-weight: bold; padding: 4px 12px; border-radius: 999px;">{league_title}</span>
            </div>
            <div style="background: #131c31; border: 1px solid #1e293b; color: #38bdf8; font-size: 11px; font-weight: bold; padding: 4px 12px; border-radius: 999px;">
                ⚡ 전력 누수 분석
            </div>
        </div>

        <!-- 메인 구단 헤더 박스 -->
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

        <!-- 4칸 핵심 요약 스탯 카드 (스카우팅 리포트 스타일) -->
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

    # 결장 확정 명단 렌더링
    if confirmed_list:
        html += """
        <div style="background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 14px; margin-bottom: 14px;">
            <div style="font-size: 13px; font-weight: 800; color: #f87171; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                <span>🔴 결장 확정 명단 (CONFIRMED OUT)</span>
            </div>
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
            role_badge = get_role_badge_html(role, is_dark=True)

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

    # 결장 의심 명단 렌더링
    if doubt_list:
        html += """
        <div style="background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 14px;">
            <div style="font-size: 13px; font-weight: 800; color: #fbbf24; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
                <span>🟡 결장 의심 명단 (QUESTIONABLE / GTD)</span>
            </div>
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
            role_badge = get_role_badge_html(role, is_dark=True)

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


# =========================================================
# 2️⃣ [탭 2: 카페/SNS 전용] 고화질 이미지 원클릭 복사 렌더러
# =========================================================
def render_cafe_image_component(html_content, component_id, height=680, team_name="팀"):
    safe_team_name = json.dumps(f"{team_name}_결장자리포트_다크.png")
    wrapper_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: 'Malgun Gothic', sans-serif;
                background-color: transparent;
            }}
            .btn-group {{
                display: flex;
                gap: 10px;
                margin-bottom: 14px;
            }}
            .action-btn {{
                flex: 1;
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                padding: 13px 12px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            }}
            .btn-img-copy {{
                background: linear-gradient(90deg, #2563eb, #3b82f6);
            }}
            .btn-img-copy:hover {{
                background: linear-gradient(90deg, #1d4ed8, #2563eb);
            }}
            .btn-img-down {{
                flex: 0.35;
                background-color: #334155;
            }}
            .btn-img-down:hover {{
                background-color: #1e293b;
            }}
            .preview-box {{
                background-color: #060911;
                border: 1px solid #1e293b;
                border-radius: 14px;
                padding: 18px;
                overflow-x: auto;
                display: flex;
                justify-content: center;
            }}
            #cafe-capture-area {{
                display: inline-block;
                width: 100%;
                max-width: 650px;
            }}
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
            <div id="cafe-capture-area">
                {html_content}
            </div>
        </div>

        <script>
            async function copyCafeImage() {{
                const btn = document.getElementById('cafeImgCopyBtn');
                const origText = btn.innerText;
                btn.innerText = '⏳ 고화질 다크 이미지 렌더링 중...';
                try {{
                    const target = document.getElementById('cafe-capture-area');
                    const canvas = await html2canvas(target, {{
                        scale: 2,
                        useCORS: true,
                        backgroundColor: '#0b1120'
                    }});
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
                const canvas = await html2canvas(target, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#0b1120'
                }});
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
