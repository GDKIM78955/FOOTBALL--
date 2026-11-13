import streamlit.components.v1 as components
import json

# =========================================================
# 🌟 네이버 블로그/카페 원클릭 복사 렌더러 (고화질 이미지 복사 + HTML 표 복사 동시 지원)
# =========================================================
def render_clipboard_component(html_content, component_id, height=580, team_name="팀"):
    escaped_html = json.dumps(html_content)
    safe_team_name = json.dumps(f"{team_name}_결장자리포트.png")
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
                gap: 8px;
                margin-bottom: 12px;
                flex-wrap: wrap;
            }}
            .action-btn {{
                flex: 1;
                min-width: 180px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 10px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 3px 5px rgba(0,0,0,0.1);
                transition: all 0.15s ease;
            }}
            .btn-img-copy {{
                background-color: #2563eb;
            }}
            .btn-img-copy:hover {{
                background-color: #1d4ed8;
            }}
            .btn-img-down {{
                background-color: #475569;
                flex: 0.5;
                min-width: 130px;
            }}
            .btn-img-down:hover {{
                background-color: #334155;
            }}
            .btn-html-copy {{
                background-color: #03c75a;
            }}
            .btn-html-copy:hover {{
                background-color: #02b150;
            }}
            .preview-box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 16px;
                overflow-x: auto;
                display: flex;
                justify-content: center;
            }}
            #capture-area {{
                display: inline-block;
                width: 100%;
                max-width: 620px;
                background-color: transparent;
            }}
        </style>
    </head>
    <body>
        <div class="btn-group">
            <button class="action-btn btn-img-copy" id="imgCopyBtn" onclick="copyAsImage()">
                📸 [추천] 로고 포함 고화질 이미지로 복사 (블로그에 Ctrl+V)
            </button>
            <button class="action-btn btn-img-down" onclick="downloadAsImage()">
                📥 PNG 이미지 저장
            </button>
            <button class="action-btn btn-html-copy" onclick="copyHtmlToClipboard()">
                📋 기존 표(텍스트) 서식 복사
            </button>
        </div>

        <div class="preview-box">
            <div id="capture-area">
                {html_content}
            </div>
        </div>

        <script>
            // 1) 2번 방식: 카드 전체를 고화질 PNG 이미지로 변환하여 클립보드에 복사
            async function copyAsImage() {{
                const btn = document.getElementById('imgCopyBtn');
                const origText = btn.innerText;
                btn.innerText = '⏳ 고화질 이미지 생성 중...';
                try {{
                    const target = document.getElementById('capture-area');
                    const canvas = await html2canvas(target, {{
                        scale: 2,
                        useCORS: true,
                        backgroundColor: null
                    }});
                    canvas.toBlob(async (blob) => {{
                        try {{
                            const item = new ClipboardItem({{ 'image/png': blob }});
                            await navigator.clipboard.write([item]);
                            btn.innerText = origText;
                            alert('🎉 로고가 포함된 고화질 이미지 카드가 복사되었습니다!\\n블로그나 카페 글쓰기 창에서 바로 [Ctrl + V]를 누르세요.');
                        }} catch (err) {{
                            btn.innerText = origText;
                            alert('브라우저 클립보드 권한이 제한되었습니다. 옆의 [📥 PNG 이미지 저장] 버튼을 이용해 주세요.');
                        }}
                    }}, 'image/png');
                }} catch (e) {{
                    btn.innerText = origText;
                    alert('이미지 변환 중 오류가 발생했습니다: ' + e);
                }}
            }}

            // 2) PNG 이미지 파일로 PC에 직접 다운로드
            async function downloadAsImage() {{
                const target = document.getElementById('capture-area');
                const canvas = await html2canvas(target, {{
                    scale: 2,
                    useCORS: true,
                    backgroundColor: null
                }});
                const link = document.createElement('a');
                link.download = {safe_team_name};
                link.href = canvas.toDataURL('image/png');
                link.click();
            }}

            // 3) 기존 HTML 표 서식 복사
            function copyHtmlToClipboard() {{
                const htmlData = {escaped_html};
                const blobHtml = new Blob([htmlData], {{ type: 'text/html' }});
                const blobText = new Blob([htmlData.replace(/<[^>]*>?/gm, '')], {{ type: 'text/plain' }});
                const data = [new ClipboardItem({{ 'text/html': blobHtml, 'text/plain': blobText }})];

                navigator.clipboard.write(data).then(() => {{
                    alert('🎉 네이버 블로그/카페용 표 서식이 복사되었습니다! 블로그 글쓰기 창에서 [Ctrl + V]를 누르세요.');
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
# 🎨 역할별 배지 스타일 생성 헬퍼 함수
# =========================================================
def get_role_badge_html(role):
    role_str = str(role).strip() if role else "-"
    
    if "핵심" in role_str:
        bg_color = "#7c3aed"  # 진한 보라색 (핵심 주전)
    elif "주전" in role_str:
        bg_color = "#ef4444"  # 빨간색 (주전)
    elif "로테이션" in role_str:
        bg_color = "#2563eb"  # 파란색 (로테이션)
    elif "백업" in role_str:
        bg_color = "#475569"  # 진회색/슬레이트 (백업)
    elif "유망주" in role_str:
        bg_color = "#10b981"  # 에메랄드 초록색 (유망주)
    else:
        bg_color = "#94a3b8"  # 연회색 (기타)

    return (
        f"<span style='background-color: {bg_color}; color: #ffffff; "
        f"padding: 2px 6px; border-radius: 4px; font-size: 10px; "
        f"font-weight: bold; display: inline-block; margin-top: 2px;'>{role_str}</span>"
    )


# =========================================================
# 🚑 부상자 인포그래픽 도표 생성 함수 (구단 로고 배지 지원)
# =========================================================
def generate_naver_injury_infographic(team_name, league_title, confirmed_list, doubt_list, logo_src=""):
    # 로고가 있을 때 흰색 배경 로고가 자연스럽게 어우러지도록 둥근 테두리 액자 배지로 렌더링
    if logo_src:
        header_inner_html = f"""
        <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
            <tr>
                <td valign="middle" style="padding-right: 14px;">
                    <div style="width: 58px; height: 58px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.06); overflow: hidden; padding: 4px; box-sizing: border-box;">
                        <img src="{logo_src}" alt="{team_name}" style="max-width: 48px; max-height: 48px; object-fit: contain; display: block; margin: 0 auto;" />
                    </div>
                </td>
                <td valign="middle" align="left" style="text-align: left;">
                    <div style="font-size: 11px; font-weight: bold; color: #dc2626; letter-spacing: 1px;">INJURY & SUSPENSION REPORT</div>
                    <div style="font-size: 19px; font-weight: bold; color: #0f172a; margin-top: 3px;">
                        [{team_name}] 결장 및 결장의심 명단
                    </div>
                    <div style="font-size: 12px; color: #64748b; margin-top: 3px;">기준: <b>{league_title}</b></div>
                </td>
            </tr>
        </table>
        """
    else:
        header_inner_html = f"""
        <div style="font-size: 11px; font-weight: bold; color: #dc2626; letter-spacing: 1px;">INJURY & SUSPENSION REPORT</div>
        <div style="font-size: 18px; font-weight: bold; color: #0f172a; margin-top: 4px;">
            🚑 [{team_name}] 결장 및 결장의심 명단
        </div>
        <div style="font-size: 12px; color: #64748b; margin-top: 4px;">기준: <b>{league_title}</b></div>
        """

    html = f"""
    <table align="center" border="0" cellpadding="0" cellspacing="0" style="width: 100%; max-width: 620px; margin: 0 auto; font-family: 'Malgun Gothic', '맑은 고딕', AppleSDGothicNeo-Regular, sans-serif; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; border-collapse: separate; color: #0f172a;">
        <tr>
            <td style="padding: 20px;">
                <table border="0" cellpadding="0" cellspacing="0" style="width: 100%; border-bottom: 2px solid #0f172a; margin-bottom: 16px;">
                    <tr>
                        <td align="center" style="padding-bottom: 12px; text-align: center;">
                            {header_inner_html}
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

            role_badge = get_role_badge_html(role)

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

            role_badge = get_role_badge_html(role)

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
