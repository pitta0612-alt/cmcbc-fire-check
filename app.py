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

# [중요] 구글 스프레드시트 이름
SHEET_NAME = "부천성모병원_소방점검_데이터"

# 구글 시트 연결 함수 (보안키를 코드에 직접 내장)
def connect_google_sheet():
    try:
        # 모든 줄바꿈을 \n 기호로 바꿔서 '한 줄'로 만든 암호 키입니다.
        # [수정] 새로 받으신 키 값으로 교체되었습니다.
        one_line_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDTCcDPRBVAkK3x\ndu/xc21oJZhdJQvcdLywzLg50l5yv0iATK5+XFrp+5ZLaGFLKRVXARhkok9sd1az\nuycJHUh7Uh7tvTgmuwSAJyh3oThwtiuTcUcXGQcWLcfOzTj6E5EUsIm0JihICDbb\ngrDaD1n7pgQP4aIVCUpCQa/kyp77v4iC8os7N1QNtM2Erx/9JuWCWUMkumKPU/aV\nG1lbSnpnXmz/Jur6JtqEr1y9w1apMLu7izGo75DC29NwuZryY5OnSXef80549K+7\nvyWtmKmjOYPzQrjyC0kOmWcIzu8ZgZHdRlKJStmoYONN9EnP4ia8DmNRz8JQmRtM\nOMTLt7hzAgMBAAECggEAIMfL4xtfC7jiyUuME3QLrgOM9Qbwno1O0/hGCMvpr3w7\n4vCbosrDX8NHF1kpfQxuy/rCaGX33VAfhRUl3US8V1TXCLRSw7KwDRydV2ZmXHJH\njC7/zRGDqB5zV2b0RJAD10lhZ7y3lrzD506XxuoJ3vds0RoKBvzQQ+ttICZDEgpo\nAE8ozjIKim4vns6BzqqoVkQwcfTtk8VEEmtOVtO1UAG2nycq5lkximFxqXcnbCtk\nnVkZRRYZDjBAoBjB543SPQn7TCm51RgD61c8mJoXrn5OLWJpHItEyR51UIrVpXSc\nBaNTvVP+Nd1nR1L1Kq6dqVVtkz2V7e+7Yfm0YVy42QKBgQD7wut2Uo49rsxfjPaJ\nJ2J0OmBDJVNBB7Wr0YYCynl15Pj6mhBIn/ADwwZ7n3Ov4/La9dpcVqhHg2JgB0Qc\nZXCFw8pHKBlrOMz+vMwo/HfZZ2DkaN3nmbMWZjJOBkh/Ru9AF9XhVu0eALTyPyNs\npdJ5YAmnRewklRJy+niuBIwBKwKBgQDWl1FaSnwlhvRIAMvTCeDrBfrm1n2alPaR\nnx0hKk8PEfj6JmiisQWdbRV+46vTMsxiGvP7tG3msNyzfgMGoT3/8p8yulMO37nA\n4Vzz8/MMyIGdtVtHSgrrPbLnMS/vtEU856tLkmDuFYBqZxUvuZ5WAo2XSNjx7Tn7\nek6q9rSx2QKBgA3x1/Tv0a0c93j7Z9Rk+BEUAqz1bk0Vzjw8GL4i1ONw0VGgIvLC\n2Rp8POmwBUpix9rU70laC2wanOJQxLcF71uZYqTaVb4YoVIixvQmN8U08qr0HAZt\n/vtoobSsqGtUVIAqUdBvbibRRzR7xsyHysaqSR6YwuGr2B/CO9j3q4GNAoGAcidW\n2JBNEG2FH5SE2QQlSQEKYqfxcz0RGZAqH81w9xRZfUDXYsyGryMrTy/v5M7eGMY7\nykdGO3UUQsui8nDuGWzIsWSa8IulNezs1L2OKtuyz+F86CSEQHW26POqi3o7ZtXa\nsr3woFaB1Jh3lcbJavm6tqLC/Zdzw8phdOL+ZqkCgYAlJmg2Qft9SZxd9lOzHwUm\nb/i5NSmM4BGof9OXyq9PaC8gsmh+ZPHH4obo87MXeLPRtYHiSidJ0QQKPx8SKw+b\nmFSY7f1ejYu24NH1klExjlmbyAhz6kzdjp1KaVmP9N8mdHcKWbHFWqV3TbIGlPy8\nUlJbcKuB/UmO4acfSmYOog==\n-----END PRIVATE KEY-----\n"

        service_account_info = {
            "type": "service_account",
            "project_id": "round-booking-494300-s3",
            "private_key_id": "717037f3d1302a12c343e15cf9a0516cfcaea968",
            "private_key": one_line_key,
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
        st.error(f"구글 시트 연결 중 오류 발생: {e}")
        return None

# --- 앱 UI 구성 (이전과 동일) ---
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

# 로고 및 타이틀
try:
    logo_img = Image.open("logo.png")
    col_logo, col_title = st.columns([1, 6])
    with col_logo: st.image(logo_img, width=150)
    with col_title: st.markdown("<h1 style='margin-top: 15px;'>소방시설 점검 시스템 (V5.5)</h1>", unsafe_allow_html=True)
except:
    st.title("🏥 소방시설 점검 시스템 (V5.5)")

# 점검 정보 입력
st.sidebar.header("📋 점검 기본 정보")
inspector = st.sidebar.text_input("점검자", value="이용민")
check_date = st.sidebar.date_input("점검 일자", datetime.now())
selected_bldg = st.sidebar.selectbox("건물 선택", list(building_data.keys()))
selected_floor = st.sidebar.selectbox("층수 선택", building_data[selected_bldg])
full_location = f"{selected_bldg} {selected_floor}"

# 점검 항목 체크
st.header(f"🔍 {full_location} 시설물 상태 체크")
results = {}
cols = st.columns(3)
for idx, item in enumerate(total_items):
    with cols[idx % 3]:
        results[item] = st.radio(f"**{item}**", ["양호", "불량"], key=f"check_{item}", horizontal=True)

st.divider()

# 사진 및 비고
col_img, col_txt = st.columns([1, 1])
with col_img:
    st.header("📸 현장 사진 첨부")
    show_camera = st.checkbox("📷 사진 촬영 기능 켜기")
    img_file = st.camera_input("불량 항목 사진 촬영") if show_camera else None
with col_txt:
    st.header("📝 지적 내역 및 비고")
    issue_detail = st.text_area("상세 불량 사유 입력", height=150)

st.divider()

# 저장 로직
if st.button("📊 점검 결과 저장 및 구글 시트 전송", use_container_width=True):
    new_row = [
        check_date.strftime("%Y-%m-%d"),
        inspector,
        full_location
    ] + list(results.values()) + [issue_detail, "Y" if img_file else "N"]
    
    # 1. 로컬 엑셀 저장
    try:
        if not os.path.exists(EXCEL_FILE):
            wb = Workbook(); ws = wb.active; ws.append(["일자", "점검자", "구역"] + total_items + ["지적내역", "사진"])
        else:
            wb = load_workbook(EXCEL_FILE); ws = wb.active
        ws.append(new_row); wb.save(EXCEL_FILE)
    except: pass

    # 2. 구글 시트 전송
    sheet = connect_google_sheet()
    if sheet:
        try:
            sheet.append_row(new_row)
            st.success("✅ 구글 스프레드시트에 성공적으로 저장되었습니다!")
            st.balloons()
        except Exception as e:
            st.error(f"구글 시트 저장 실패: {e}")
    else:
        st.warning("⚠️ 구글 시트 연결에 실패했습니다. 시트 이름을 확인해 주세요.")