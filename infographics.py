import streamlit.components.v1 as components
import json

# =========================================================
# 🌟 네이버 블로그 원클릭 복사 렌더러 컴포넌트
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
            📋 [네이버 블로그/카페 서식 원클릭 복사하기] (클릭 후 블로그에 Ctrl+V)
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
                    alert('🎉 네이버 블로그/카페용 서식이 복사되었습니다! 블로그 글쓰기 창에서 [Ctrl + V]를 누르세요.');
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
# 🚑 부상자 인포그래픽 도표 생성 함수 (결장자 전용)
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

            role_badge = f"<span style='background-color: #ef4444; color: white; padding: 1px 5px; border-radius: 3px; font-size: 10px;'>{role}</span>" if "주전" in str(role) else f"<span style='background-color: #64748b; color: white; padding: 1px 5px; border-radius: 3px; font-size: 10px;'>{role}</span>"

            html += f"""
                    <tr>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">{name_str}</td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">`{pos}`<br>{role_badge}</td>
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

            role_badge = f"<span style='background-color: #f59e0b; color: white; padding: 1px 5px; border-radius: 3px; font-size: 10px;'>{role}</span>"

            html += f"""
                    <tr>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">{name_str}</td>
                        <td align="center" style="padding: 6px 3px; border: 1px solid #e2e8f0; text-align: center;">`{pos}`<br>{role_badge}</td>
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
