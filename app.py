import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# 엑셀 파일 이름 설정 (로컬 백업용)
EXCEL_FILE = "fire_inspection_log.xlsx"

# --- [중요] 구글 스프레드시트 설정 ---
# 구글 시트의 실제 이름과 토씨 하나 틀리지 않게 똑같이 적어주세요.
SHEET_NAME = "부천성모병원_소방점검_데이터"

# 1. 건물 및 층수 데이터 설정
building_data = {
    "성모관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "11F"],
    "성심관(L동)": ["B6F", "B6MF", "B5F", "B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "PHF"],
    "성가정관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F"],
    "성요셉관(G동)": ["B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "PHF"],
    "지하주차장(K동)": ["B4F", "B3F", "B2F", "B1F", "1F"],
    "주차타워(N동)": ["B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "PHF"]
}

# 점검 설비 리스트 (총 15종)
total_items = [
    "소화기구", "소화가스구역", "옥내소화전설비", "스프링클러설비", 
    "자탐설비(감지기)", "유도등설비", "비상조명등설비", "완강기", 
    "구조대", "방열복", "공기호흡기", "특피제연설비", 
    "상가제연설비", "비상콘센트", "무선통신설비"
]

# 구글 시트 연결 함수
def connect_google_sheet():
    try:
        # Streamlit Secrets에서 설정한 [gcp_service_account]를 불러옵니다.
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        # 구글 시트 이름으로 파일을 엽니다.
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"구글 시트 연결 중 오류 발생: {e}")
        return None

# 앱 페이지 설정
st.set_page_config(page_title="부천성모병원 소방점검", layout="wide")

# 로고 및 제목 부분
try:
    logo_img = Image.open("logo.png")
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image(logo_img, width=150)
    with col_title:
        st.markdown("<h1 style='margin-top: 15px;'>소방시설 점검 기록 시스템 (V5.0)</h1>", unsafe_allow_html=True)
except Exception:
    st.title("🏥 소방시설 정밀 점검 시스템 (V5.0)")

# 사이드바 - 점검 기본 정보
st.sidebar.header("📋 점검 기본 정보")
inspector = st.sidebar.text_input("점검자", value="이용민")
check_date = st.sidebar.date_input("점검 일자", datetime.now())
selected_bldg = st.sidebar.selectbox("건물 선택", list(building_data.keys()))
selected_floor = st.sidebar.selectbox("층수 선택", building_data[selected_bldg])
full_location = f"{selected_bldg} {selected_floor}"

# 메인 화면 - 설비 점검
st.header(f"🔍 {full_location} 시설물 상태 체크")
results = {}
cols = st.columns(3)
for idx, item in enumerate(total_items):
    with cols[idx % 3]:
        results[item] = st.radio(f"**{item}**", ["양호", "불량"], key=f"check_{item}", horizontal=True)

st.divider()

# 카메라 및 지적 내역
col_img, col_txt = st.columns([1, 1])
with col_img:
    st.header("📸 현장 사진 첨부")
    show_camera = st.checkbox("📷 사진 촬영 기능 켜기")
    img_file = st.camera_input("불량 항목 사진 촬영") if show_camera else None

with col_txt:
    st.header("📝 지적 내역 및 비고")
    issue_detail = st.text_area("상세 불량 사유 입력", height=150)

st.divider()

# 저장 버튼
if st.button("📊 점검 결과 저장 및 구글 시트 전송", use_container_width=True):
    # 저장용 데이터 구성
    new_data = {
        "점검일자": check_date.strftime("%Y-%m-%d"),
        "점검자": inspector,
        "구역": full_location,
        **results,
        "지적내역": issue_detail,
        "사진첨부": "Y" if img_file else "N"
    }
    
    # 1. 로컬 엑셀 백업 (서버 임시 저장)
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook(); ws = wb.active; ws.append(list(new_data.keys()))
    else:
        wb = load_workbook(EXCEL_FILE); ws = wb.active
    ws.append(list(new_data.values()))
    wb.save(EXCEL_FILE)

    # 2. 구글 시트 전송
    sheet = connect_google_sheet()
    if sheet:
        try:
            sheet.append_row(list(new_data.values()))
            st.success("✅ 구글 스프레드시트에 데이터가 안전하게 기록되었습니다!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ 데이터 전송 실패: {e}")
    else:
        st.warning("⚠️ 구글 시트를 찾을 수 없어 로컬에만 저장되었습니다. 시트 이름을 확인해 주세요.")