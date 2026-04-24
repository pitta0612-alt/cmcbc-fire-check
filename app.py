import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# [설정] 파일 및 폴더 정보
EXCEL_FILE = "fire_inspection_log.xlsx"
SHEET_NAME = "부천성모병원_소방점검_데이터"
FOLDER_ID = "1HHGdjoQFtI2Z1LbLpXh1cF8pz6-gQHir"

# 1. 건물 데이터
building_data = {
    "성모관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "11F"],
    "성심관(L동)": ["B6F", "B6MF", "B5F", "B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "PHF"],
    "성가정관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F"],
    "성요셉관(G동)": ["B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "PHF"],
    "지하주차장(K동)": ["B4F", "B3F", "B2F", "B1F", "1F"],
    "주차타워(N동)": ["B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "PHF"]
}

total_items = [
    "소화기구", "소화가스구역", "옥내소화전설비", "스프링클러설비", 
    "자탐설비(감지기)", "유도등설비", "비상조명등설비", "완강기", 
    "구조대", "방열복", "공기호흡기", "특피제연설비", 
    "상가제연설비", "비상콘센트", "무선통신설비"
]

# [인증] r""(raw string) 사용으로 특수문자 경고 해결
one_line_key = r"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7oRsy7oHR0ZmI\n43rGFZ7ugH/oFnPRwgzIBHjWZlj6nIaJQ52TiKeL+O13amFKSoVuqfxMJ4guY4xM\n9xRfxSkXgRmnJtyfZXMFiVGARIwz3XIHGYHMbVZKCl/8vcx9I7QOiKcA8Vz25JBD\n65bPLSbzC1TMb7mV+L71TqpO2bbaIrX9dKdiQDmROO1mTI4gFMJbtJJN1szBvzbI\nxLnAr0ALFVhy5rMI2AIQFb4evnhNK+WOnw7hoABudbgqqHA3t8oE5FHyx5nZPeDV\nGLYJ4iF5G7CsIZCsriUUvBTu3KP5Cx9gPLrK86SfVuuuV7yQolzDtl0sNnRfGP91\n2lkoC1CvAgMBAAECggEADmW2MBTOylpdKnywwuVi0iXzFUyFFknfxYiuUF6pzOUu\nNPcxbreJimXkrDPyA4uErJwHkOe8Uo7vSPKb/MiktrnVzZaKTwLaWMjo2OupnyCK\nwOe1/DPsRKHXgWMmVKM6NvPzw1CXU8Hwc1MZueEFlZhqKTEY2lysI9JQTYegOSGs\nhEvAbw6k4cJ2pGBOXwfJorBSOV2HCHK3oKp/X8J283UT6GBfI76Ckpzp/tKlvtPn\nerjxKllDXPX4YLvyzw+ZS5DP5IIEFELJKFIBc9QqXN9poqAMx54MT/UP/FgB4/3y\nbjuMyNICoCdT4ejRsNLtoK6D0SBoxG50IxC47x/rOQKBgQD2+tPMzpoGs8P3Symc\nv04n2srl/+ayTNo9Hhgnr6EFwOmc916YlmNE5tl9umPJSONARxFctus0bVciIilQ\ LQkYaiqPJUBrJzjeiCzWvUR4C+i8HcQ63WYFvzshWI7+mMJUIdEhfZjF4yZjR6z1\njVzhLarGF9lVHIAqeOlTgFy2hwKBgQDCe1+LzwtpiyHPiRsDq5VM+WkYqGTygTn8\nM3QNzHEg0KWvg2zGMxQPV9/z4EUsFi2h8nnSnQUxXVp8VyoTRbAKqCam5ffB78jQ\n93vL3Ifl5sZp8/KL+4uPXszuqZa109D4+4wVstsbK3CDCzY/WSuDszlwoSamLcYE\nNhdUR4B2mQKBgDq04Id8TIxvSpOLoDaMGq3KihQlwdZ8Ahwo/SDh1GqjsmQHQMsQ\ZERKg0Qpe/KqiqoKuovJRxtNKjsI170hF1pgUgF4n1lZF2F+CPp6Pr4yRn4ArVY4\nrjmLfSit/j9yXC7XYviM/DV9ivBqZyhvE7bKvh8cKCLdBXITD5MzndYdAoGBAJmi\nVKxhdyZ9XsxQByMzHNKeBMQR4w0fwOrWystLweKmcPzh2cAJAcPNK4HAnWRicNIK\ndupGWJ/Sm3S2duqalqMUitQ1vy9ZeU568zTslf6r+/ofWG/02x77SPEQz5n8Jo1K\nSjOqAyTHgC5FYSlSC+oSX0H2TE3iwxb4lB1kDruhAoGBAJK5VV/SYvWHVexDUEIn\n6D5Low7Rz4Kk39aG6pKTULCkPXu50Jd8SNXKbtNr1gGHkL/TSDB5pKE8Uz6j+ZSY\n69VEWnjBhFkxxMvJ3TVad6cEgMDayz3+SwwigqOFKdVYX1EOsiQiucxG6iAd9TmD\nube4pEoz4ArnJipRo5SZWw80\n-----END PRIVATE KEY-----\n".replace(r"\n", "\n")

service_account_info = {
    "type": "service_account",
    "project_id": "round-booking-494300-s3",
    "private_key_id": "795d62b1e25929e3565c56671d19d8a276e559e3",
    "private_key": one_line_key,
    "client_email": "id-298@round-booking-494300-s3.iam.gserviceaccount.com",
    "client_id": "114249893845931311645",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-298%40round-booking-494300-s3.iam.gserviceaccount.com"
}

def upload_to_drive(file_data, file_name):
    try:
        creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/drive"])
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
    try:
        credentials = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(credentials)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"구글 시트 연결 에러: {e}")
        return None

# --- 앱 UI ---
st.set_page_config(page_title="부천성모병원 소방점검", layout="wide")

try:
    logo_img = Image.open("logo.png")
    col_logo, col_title = st.columns([1, 6])
    with col_logo: st.image(logo_img, width=150)
    with col_title: st.markdown("<h1 style='margin-top: 15px;'>소방시설 점검 기록 시스템 (V6.0)</h1>", unsafe_allow_html=True)
except Exception:
    st.title("🏥 소방시설 정밀 점검 시스템 (V6.0)")

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
        # 에러가 났던 부분입니다. 따옴표를 확실히 닫았습니다.
        results[item] = st.radio(f"**{item}**", ["양호", "불량"], key=f"check_{item}", horizontal=True)

st.divider()

col_img, col_txt = st.columns([1, 1])
with col_img:
    st.header("📸 현장 사진 첨부")
    show_camera = st.checkbox("📷 사진 촬영 기능 켜기")
    img_file = st.camera_input("불량 항목 사진 촬영") if show_camera else None
with col_txt:
    st.header("📝 지적 내역 및 비고")
    issue_detail = st.text_area("상세 불량 사유 입력", height=150)

if st.button("📊 점검 결과 저장 및 구글 시트 전송", use_container_width=True):
    image_url = ""
    if img_file:
        with st.spinner('사진 업로드 중...'):
            file_name = f"{check_date}_{selected_bldg}_{selected_floor}_{inspector}.jpg"
            image_url = upload_to_drive(img_file.getvalue(), file_name)
    
    photo_formula = f'=IMAGE("{image_url}")' if image_url else "사진없음"
    
    # 데이터 리스트 구성
    row_to_add = [check_date.strftime("%Y-%m-%d"), inspector, f"{selected_bldg} {selected_floor}"]
    for item in total_items:
        row_to_add.append(results[item])
    row_to_add.append(issue_detail)
    row_to_add.append(photo_formula)

    # 1. 로컬 백업
    try:
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook(); ws = wb.active; ws.append(["날짜", "점검자", "구역"] + total_items + ["비고", "사진"])
        else:
            wb = load_workbook(EXCEL_FILE); ws = wb.active
        ws.append(row_to_add); wb.save(EXCEL_FILE)
    except: pass

    # 2. 구글 시트 전송
    sheet = connect_google_sheet()
    if sheet:
        try:
            sheet.append_row(row_to_add, value_input_option='USER_ENTERED')
            st.success("✅ 구글 시트에 저장 성공!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ 시트 전송 실패: {e}")