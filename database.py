import streamlit as st
import pandas as pd
import gspread
import time
import re
import base64
import requests
from oauth2client.service_account import ServiceAccountCredentials

# 1. 구글 시트 & 드라이브 연동 클라이언트
@st.cache_resource(show_spinner=False)
def get_gspread_client():
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            return gspread.authorize(creds)
        return None
    except Exception:
        return None


# 2. 안전한 시트 데이터 로딩 함수
@st.cache_data(ttl=86400, show_spinner=False)
def load_sheet_data(sheet_name, spreadsheet_id=""):
    client = get_gspread_client()
    if not client or not spreadsheet_id:
        return pd.DataFrame()
    for attempt in range(4):
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            ws = spreadsheet.worksheet(sheet_name)
            data = ws.get_all_values()
            if len(data) > 1:
                cols = [str(c).strip() for c in data[0]]
                df = pd.DataFrame(data[1:], columns=cols)
                df = df.dropna(how='all')
                df.columns = df.columns.str.strip()
                return df
            return pd.DataFrame()
        except Exception:
            time.sleep(1.0 * (attempt + 1))
            continue
    return pd.DataFrame()


# 3. 구글 드라이브 로고 폴더 내 모든 이미지 파일 목록 불러오기 (링크 공개 폴더 완벽 대응)
@st.cache_data(ttl=3600, show_spinner=False)
def load_drive_logo_map(folder_input=""):
    raw_input = str(folder_input).strip()
    folder_id = None

    if raw_input:
        m = re.search(r"folders/([a-zA-Z0-9_-]+)", raw_input)
        if m:
            folder_id = m.group(1)
        elif len(raw_input) >= 20 and re.match(r"^[a-zA-Z0-9_-]+$", raw_input):
            folder_id = raw_input

    logo_map = {}
    client = get_gspread_client()

    # [1차 시도] 구글 드라이브 공식 API (링크 공개 폴더 인식용 파라미터 포함)
    if client:
        try:
            token = client.auth.get_access_token().access_token
            headers = {"Authorization": f"Bearer {token}"}

            if not folder_id and raw_input:
                q_folder = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{raw_input}' and trashed = false"
                r_f = requests.get(
                    "https://www.googleapis.com/drive/v3/files",
                    headers=headers,
                    params={
                        "q": q_folder,
                        "fields": "files(id, name)",
                        "supportsAllDrives": "true",
                        "includeItemsFromAllDrives": "true",
                        "pageSize": 10
                    },
                    timeout=10
                )
                if r_f.status_code == 200:
                    folders = r_f.json().get("files", [])
                    if folders:
                        folder_id = folders[0]["id"]

            q_files = f"'{folder_id}' in parents and trashed = false" if folder_id else "mimeType contains 'image/' and trashed = false"
            page_token = None

            while True:
                params = {
                    "q": q_files,
                    "fields": "nextPageToken, files(id, name, mimeType)",
                    "supportsAllDrives": "true",
                    "includeItemsFromAllDrives": "true",
                    "pageSize": 500
                }
                if page_token:
                    params["pageToken"] = page_token

                res = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params, timeout=15)
                if res.status_code != 200:
                    break

                res_json = res.json()
                for f in res_json.get("files", []):
                    fname = f.get("name", "")
                    if re.search(r"\.(png|jpg|jpeg|webp|gif)$", fname, re.IGNORECASE) or "image/" in f.get("mimeType", ""):
                        team_key = re.sub(r"\.[a-zA-Z0-9]+$", "", fname).strip()
                        if team_key:
                            logo_map[team_key] = f.get("id")

                page_token = res_json.get("nextPageToken")
                if not page_token:
                    break
        except Exception:
            pass

    # [2차 백업 시도] Drive API가 꺼져 있거나 서비스 계정 공유가 안 된 경우 공개 폴더 웹 페이지에서 직접 추출
    if not logo_map and folder_id:
        try:
            embed_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
            res_html = requests.get(embed_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if res_html.status_code == 200:
                entries = re.findall(
                    r'id="entry-([a-zA-Z0-9_-]+)".*?class="flip-entry-title">([^<]+)</div>',
                    res_html.text,
                    re.DOTALL
                )
                for fid, fname in entries:
                    team_key = re.sub(r"\.[a-zA-Z0-9]+$", "", fname).strip()
                    if team_key:
                        logo_map[team_key] = fid
        except Exception:
            pass

    return logo_map


# 4. 선택된 팀의 로고 이미지를 Base64 데이터 URI로 변환 (공개 링크 & API 이중 지원)
@st.cache_data(ttl=86400, show_spinner=False)
def get_logo_base64_src(file_id):
    if not file_id:
        return ""

    # 1) 공개 링크 파일 직접 다운로드 (가장 빠르고 권한 에러 없음)
    try:
        pub_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        res = requests.get(pub_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200 and "image" in res.headers.get("Content-Type", ""):
            b64_str = base64.b64encode(res.content).decode("utf-8")
            content_type = res.headers.get("Content-Type", "image/png")
            return f"data:{content_type};base64,{b64_str}"
    except Exception:
        pass

    # 2) 서비스 계정 토큰을 통한 API 다운로드
    client = get_gspread_client()
    if client:
        try:
            token = client.auth.get_access_token().access_token
            headers = {"Authorization": f"Bearer {token}"}
            url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&supportsAllDrives=true"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                b64_str = base64.b64encode(res.content).decode("utf-8")
                content_type = res.headers.get("Content-Type", "image/png")
                return f"data:{content_type};base64,{b64_str}"
        except Exception:
            pass

    return ""
