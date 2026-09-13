import streamlit as st
import pandas as pd
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

# 1. 구글 시트 연동 클라이언트
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

# 2. 안전한 시트 데이터 로딩 함수 (공백 제거 및 24시간 캐시 적용으로 로딩 속도 최적화)
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
