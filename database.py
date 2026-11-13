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


# 2. 안전한 시트 데이터 로딩 함수 (공백 제거 및 24시간 캐시 적용)
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


# 3. 구글 드라이브 로고 폴더 내 모든 이미지 파일 목록 불러오기
@st.cache_data(ttl=3600, show_spinner=False)
def load_drive_logo_map(folder_input=""):
    """
    폴더 URL, 폴더 ID, 또는 폴더 이름(예: '구단로고', '로고')을 입력받아
    { '한글팀명': '파일ID' } 형태의 딕셔너리를 반환합니다.
    입력값이 비어있으면 서비스 계정이 접근 가능한 모든 이미지 파일을 스캔합니다.
    """
    client = get_gspread_client()
    if not client:
        return {}

    try:
        token = client.auth.get_access_token().access_token
        headers = {"Authorization": f"Bearer {token}"}
        folder_id = None
        raw_input = str(folder_input).strip()

        if raw_input:
            # 1) 전체 URL을 붙여넣은 경우 폴더 ID 추출
            m = re.search(r"folders/([a-zA-Z0-9_-]+)", raw_input)
            if m:
                folder_id = m.group(1)
            # 2) 긴 영문/숫자 형태의 폴더 ID인 경우
            elif len(raw_input) >= 20 and re.match(r"^[a-zA-Z0-9_-]+$", raw_input):
                folder_id = raw_input
            # 3) 폴더 이름(예: '구단로고')으로 검색하는 경우
            else:
                q_folder = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{raw_input}' and trashed = false"
                r_f = requests.get(
                    "https://www.googleapis.com/drive/v3/files",
                    headers=headers,
                    params={"q": q_folder, "fields": "files(id, name)", "pageSize": 10},
                    timeout=10
                )
                if r_f.status_code == 200:
                    folders = r_f.json().get("files", [])
                    if folders:
                        folder_id = folders[0]["id"]

        # 이미지 파일 검색 쿼리 구성
        if folder_id:
            q_files = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        else:
            q_files = "mimeType contains 'image/' and trashed = false"

        logo_map = {}
        page_token = None
        while True:
            params = {
                "q": q_files,
                "fields": "nextPageToken, files(id, name, mimeType)",
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
                # 확장자(.png, .jpg, .webp 등) 제거 후 한글 팀명만 추출
                team_key = re.sub(r"\.[a-zA-Z0-9]+$", "", fname).strip()
                if team_key:
                    logo_map[team_key] = f.get("id")

            page_token = res_json.get("nextPageToken")
            if not page_token:
                break

        return logo_map
    except Exception:
        return {}


# 4. 선택된 팀의 로고 이미지를 Base64 데이터 URI로 변환 (깨짐 방지 및 24시간 캐싱)
@st.cache_data(ttl=86400, show_spinner=False)
def get_logo_base64_src(file_id):
    if not file_id:
        return ""
    client = get_gspread_client()
    if not client:
        return ""
    try:
        token = client.auth.get_access_token().access_token
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            b64_str = base64.b64encode(res.content).decode("utf-8")
            content_type = res.headers.get("Content-Type", "image/png")
            return f"data:{content_type};base64,{b64_str}"
    except Exception:
        pass
    return ""
