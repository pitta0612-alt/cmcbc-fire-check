import streamlit as st
import pandas as pd
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from PIL import Image

# [설정]
SHEET_NAME = "부천성모병원_소방점검_데이터"
FOLDER_ID = "1HHGdjoQFtI2Z1LbLpXh1cF8pz6-gQHir"
# 깃허브에 올린 JSON 파일 이름과 정확히 일치해야 합니다.
KEY_PATH = "google_key.json" 

# 1. 인증 로직 (파일 경로를 직접 사용)
def get_creds():
    try:
        # 파일이 실제로 존재하는지 확인
        if not os.path.exists(KEY_PATH):
            st.error(f"인증 파일을 찾을 수 없습니다: {KEY_PATH}")
            return None
            
        return Credentials.from_service_account_file(
            KEY_PATH,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
    except Exception as e:
        st.error(f"인증 파일 로드 중 오류: {e}")
        return None

# 2. 구글 드라이브/시트 연결 함수
def upload_to_drive(file_data, file_name):
    creds = get_creds()
    if not creds: return None
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype='image/jpeg')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    except Exception as e:
        st.error(f"드라이브 업로드 에러: {e}")
        return None

def connect_google_sheet():
    creds = get_creds()
    if not creds: return None
    try:
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"구글 시트 연결 에러: {e}")
        return None

# --- 앱 UI ---
st.set_page_config(page_title="부천성모병원 소방점검 V6.6", layout="wide")

building_data = {
    "성모관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "11F"],
    "성심관(L동)": ["B6F", "B6MF", "B5F", "B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "PHF"],
    "성가정관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F"],
    "성요셉관(G동)": ["B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "PHF"],
    "지하주차장(K동)": ["B4F", "B3F", "B2F", "B1F", "1F"],
    "주차타워(N동)": ["B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "PHF"]
}
total_items = ["소화기구", "소화가스구역", "옥내소화전설비", "스프링클러설비", "자탐설비(감지기)", "유도등설비", "비상조명등설비", "완강기", "구조대", "방열복", "공기호흡기", "특피제연설비", "상가제연설비", "비상콘센트", "무선통신설비"]

st.title("🏥 소방시설 점검 기록 시스템")

st.sidebar.header("📋 점검 기본 정보")
inspector = st.sidebar.text_input("점검자", value="이용민")
check_date = st.sidebar.date_input("점검 일자", datetime.now())
selected_bldg = st.sidebar.selectbox("건물 선택", list(building_data.keys()))
selected_floor = st.sidebar.selectbox("층수 선택", building_data[selected_bldg])

st.header(f"🔍 {selected_bldg} {selected_floor} 상태 체크")
results = {}
cols = st.columns(3)
for idx, item in enumerate(total_items):
    with cols[idx % 3]:
        results[item] = st.radio(f"**{item}**", ["양호", "불량"], key=f"check_{item}", horizontal=True)

st.divider()

col_img, col_txt = st.columns([1, 1])
with col_img:
    st.header("📸 현장 사진")
    show_camera = st.checkbox("📷 사진 촬영 기능 켜기")
    img_file = st.camera_input("불량 항목 사진 촬영") if show_camera else None
with col_txt:
    st.header("📝 지적 내역")
    issue_detail = st.text_area("상세 불량 사유", height=150)

if st.button("📊 점검 결과 저장 및 전송", use_container_width=True):
    image_url = ""
    if img_file:
        with st.spinner('사진 업로드 중...'):
            file_name = f"{check_date.strftime('%Y%m%d')}_{selected_bldg}_{selected_floor}_{inspector}.jpg"
            image_url = upload_to_drive(img_file.getvalue(), file_name)
    
    photo_formula = f'=IMAGE("{image_url}")' if image_url else "사진없음"
    row_to_add = [check_date.strftime("%Y-%m-%d"), inspector, f"{selected_bldg} {selected_floor}"] + list(results.values()) + [issue_detail, photo_formula]

    sheet = connect_google_sheet()
    if sheet:
        try:
            sheet.append_row(row_to_add, value_input_option='USER_ENTERED')
            st.success("✅ 전송 성공!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ 전송 실패: {e}")