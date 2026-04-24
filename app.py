import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials

# 구글 스프레드시트 이름
SHEET_NAME = "부천성모병원_소방점검_데이터"
EXCEL_FILE = "fire_inspection_log.xlsx"

def connect_google_sheet():
    try:
        # [핵심] 복사 시 발생하는 모든 오염을 제거하기 위해 키 데이터를 리스트로 관리합니다.
        # 이 데이터들은 조각나 있어도 합칠 때 파이썬이 완벽하게 교정합니다.
        key_body = [
            "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDTCcDPRBVAkK3x",
            "du/xc21oJZhdJQvcdLywzLg50l5yv0iATK5+XFrp+5ZLaGFLKRVXARhkok9sd1az",
            "uycJHUh7Uh7tvTgmuwSAJyh3oThwtiuTcUcXGQcWLcfOzTj6E5EUsIm0JihICDbb",
            "grDaD1n7pgQP4aIVCUpCQa/kyp77v4iC8os7N1QNtM2Erx/9JuWCWUMkumKPU/aV",
            "G1lbSnpnXmz/Jur6JtqEr1y9w1apMLu7izGo75DC29NwuZryY5OnSXef80549K+7",
            "vyWtmKmjOYPzQrjyC0kOmWcIzu8ZgZHdRlKJStmoYONN9EnP4ia8DmNRz8JQmRtM",
            "OMTLt7hzAgMBAAECggEAIMfL4xtfC7jiyUuME3QLrgOM9Qbwno1O0/hGCMvpr3w7",
            "4vCbosrDX8NHF1kpfQxuy/rCaGX33VAfhRUl3US8V1TXCLRSw7KwDRydV2ZmXHJH",
            "jC7/zRGDqB5zV2b0RJAD10lhZ7y3lrzD506XxuoJ3vds0RoKBvzQQ+ttICZDEgpo",
            "AE8ozjIKim4vns6BzqqoVkQwcfTtk8VEEmtOVtO1UAG2nycq5lkximFxqXcnbCtk",
            "nVkZRRYZDjBAoBjB543SPQn7TCm51RgD61c8mJoXrn5OLWJpHItEyR51UIrVpXSc",
            "BaNTvVP+Nd1nR1L1Kq6dqVVtkz2V7e+7Yfm0YVy42QKBgQD2+tPMzpoGs8P3Symc",
            "v04n2srl/+ayTNo9Hhgnr6EFwOmc916YlmNE5tl9umPJSONARxFctus0bVciIilQ",
            "LQkYaiqPJUBrJzjeiCzWvUR4C+i8HcQ63WYFvzshWI7+mMJUIdEhfZjF4yZjR6z1",
            "jVzhLarGF9lVHIAqeOlTgFy2hwKBgQDCe1+LzwtpiyHPiRsDq5VM+WkYqGTygTn8",
            "M3QNzHEg0KWvg2zGMxQPV9/z4EUsFi2h8nnSnQUxXVp8VyoTRbAKqCam5ffB78jQ",
            "93vL3Ifl5sZp8/KL+4uPXszuqZa109D4+4wVstsbK3CDCzY/WSuDszlwoSamLcYE",
            "NhdUR4B2mQKBgDq04Id8TIxvSpOLoDaMGq3KihQlwdZ8Ahwo/SDh1GqjsmQHQMsQ",
            "ZERKg0Qpe/KqiqoKuovJRxtNKjsI170hF1pgUgF4n1lZF2F+CPp6Pr4yRn4ArVY4",
            "rjmLfSit/j9yXC7XYviM/DV9ivBqZyhvE7bKvh8cKCLdBXITD5MzndYdAoGBAJmi",
            "VKxhdyZ9XsxQByMzHNKeBMQR4w0fwOrWystLweKmcPzh2cAJAcPNK4HAnWRicNIK",
            "dupGWJ/Sm3S2duqalqMUitQ1vy9ZeU568zTslf6r+/ofWG/02x77SPEQz5n8Jo1K",
            "SjOqAyTHgC5FYSlSC+oSX0H2TE3iwxb4lB1kDruhAoGBAJK5VV/SYvWHVexDUEIn",
            "6D5Low7Rz4Kk39aG6pKTULCkPXu50Jd8SNXKbtNr1gGHkL/TSDB5pKE8Uz6j+ZSY",
            "69VEWnjBhFkxxMvJ3TVad6cEgMDayz3+SwwigqOFKdVYX1EOsiQiucxG6iAd9TmD",
            "ube4pEoz4ArnJipRo5SZWw80"
        ]
        
        # 줄바꿈 문자를 명확히 삽입하여 '서명 오류'를 원천 봉쇄합니다.
        clean_private_key = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(key_body) + "\n-----END PRIVATE KEY-----\n"

        service_account_info = {
            "type": "service_account",
            "project_id": "round-booking-494300-s3",
            "private_key_id": "717037f3d1302a12c343e15cf9a0516cfcaea968",
            "private_key": clean_private_key,
            "client_email": "id-298@round-booking-494300-s3.iam.gserviceaccount.com",
            "client_id": "114249893845931311645",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-298%40round-booking-494300-s3.iam.gserviceaccount.com"
        }
        
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(credentials)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"구글 시트 연결 오류: {e}")
        return None

# --- 앱 UI ---
st.set_page_config(page_title="부천성모병원 소방점검", layout="wide")

building_data = {
    "성모관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "11F"],
    "성심관(L동)": ["B6F", "B6MF", "B5F", "B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "6F", "7F", "8F", "9F", "10F", "PHF"],
    "성가정관(A동)": ["B1F", "1F", "2F", "3F", "4F", "5F", "6F"],
    "성요셉관(G동)": ["B2F", "B1F", "1F", "2F", "3F", "4F", "5F", "PHF"],
    "지하주차장(K동)": ["B4F", "B3F", "B2F", "B1F", "1F"],
    "주차타워(N동)": ["B4F", "B3F", "B2F", "B1F", "1F", "2F", "3F", "4F", "PHF"]
}
total_items = ["소화기구", "소화가스구역", "옥내소화전설비", "스프링클러설비", "자탐설비(감지기)", "유도등설비", "비상조명등설비", "완강기", "구조대", "방열복", "공기호흡기", "특피제연설비", "상가제연설비", "비상콘센트", "무선통신설비"]

try:
    logo_img = Image.open("logo.png")
    col_logo, col_title = st.columns([1, 6])
    with col_logo: st.image(logo_img, width=150)
    with col_title: st.markdown("<h1 style='margin-top: 15px;'>소방시설 점검 시스템 (V7.3)</h1>", unsafe_allow_html=True)
except:
    st.title("🏥 소방시설 점검 시스템 (V7.3)")

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

st.header("📝 지적 내역 및 비고")
issue_detail = st.text_area("상세 불량 사유 입력", height=150)

if st.button("📊 결과 저장 및 구글 시트 전송", use_container_width=True):
    new_row = [check_date.strftime("%Y-%m-%d"), inspector, f"{selected_bldg} {selected_floor}"] + list(results.values()) + [issue_detail]
    
    # 1. 로컬 저장
    try:
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook(); ws = wb.active; ws.append(["일자", "점검자", "구역"] + total_items + ["지적내역"])
        else:
            wb = load_workbook(EXCEL_FILE); ws = wb.active
        ws.append(new_row); wb.save(EXCEL_FILE)
    except: pass

    # 2. 구글 시트 전송
    sheet = connect_google_sheet()
    if sheet:
        try:
            sheet.append_row(new_row)
            st.success("✅ 구글 시트 전송 성공!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ 전송 실패: {e}")