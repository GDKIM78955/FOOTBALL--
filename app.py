import streamlit as st
import pandas as pd
import re
from database import load_sheet_data
from infographics import generate_naver_injury_infographic, render_clipboard_component
spreadsheet_id = st.sidebar.text_input(
    "구글 시트 Spreadsheet ID",
    value="1-b-QusmoSnsvMhToNFe1B1IK7dJUKjjANs89y5ZekAQ", # 기존 앱에서 쓰시던 ID 입력
    type="default"
)
