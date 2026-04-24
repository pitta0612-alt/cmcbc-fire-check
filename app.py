import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook
from PIL import Image

# 엑셀 파일 이름 설정 (로컬 백업용)
EXCEL_FILE = "fire_inspection_log.xlsx"

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

# 앱 페이지 설정
st.set_page_config(page_title="부천성모병원 소방점검", layout="wide")

# --- 수정된 상단 로고 및 제목 부분 ---
try:
    # logo.png 파일이 같은 경로에 있어야 합니다.
    logo_img = Image.open("logo.png")
    col_logo, col_title = st.columns([1, 6])
    
    with col_logo:
        st.image(logo_img, width=200)
    with col_title:
        st.markdown("<h1 style='margin-top: 15px;'>소방시설 점검 기록 시스템 (V4.2)</h1>", unsafe_allow_html=True)
except Exception:
    # 이미지 로딩 실패 시 기존 제목 표시
    st.title("🏥 소방시설 정밀 점검 시스템 (V4.2)")

# 사이드바 - 점검 기본 정보
st.sidebar.header("📋 점검 기본 정보")
inspector = st.sidebar.text_input("점검자", value="이용민")
check_date = st.sidebar.date_input("점검 일자", datetime.now())

st.sidebar.subheader("📍 점검 구역")
selected_bldg = st.sidebar.selectbox("건물 선택", list(building_data.keys()))
selected_floor = st.sidebar.selectbox("층수 선택", building_data[selected_bldg])
full_location = f"{selected_bldg} {selected_floor}"

# 메인 화면 - 설비 점검 (3열 배치)
st.header(f"🔍 {full_location} 시설물 상태 체크")
st.info("각 설비의 상태를 체크해 주세요. 기본값은 '양호'입니다.")

results = {}
cols = st.columns(3)

for idx, item in enumerate(total_items):
    with cols[idx % 3]:
        results[item] = st.radio(
            f"**{item}**",
            ["양호", "불량"],
            key=f"check_{item}",
            horizontal=True
        )

st.divider()

# --- 선택형 카메라 활성화 및 지적 내역 ---
col_img, col_txt = st.columns([1, 1])

with col_img:
    st.header("📸 현장 사진 첨부")
    # 체크박스를 선택할 때만 카메라 기능을 활성화합니다.
    show_camera = st.checkbox("📷 사진 촬영 기능 켜기")
    
    img_file = None
    if show_camera:
        # 스마트폰 브라우저에서 후면 카메라가 안 뜬다면 전환 버튼을 눌러주세요.
        img_file = st.camera_input("불량 항목 사진 촬영")
    else:
        st.write("사진 촬영이 필요하면 위 체크박스를 선택하세요.")

with col_txt:
    st.header("📝 지적 내역 및 비고")
    issue_detail = st.text_area(
        "상세 불량 사유를 입력하세요", 
        placeholder="예: 3번 소화기 압력 저하 등",
        height=150
    )

st.divider()

# 저장 버튼 로직
if st.button("📊 점검 결과 저장 및 데이터 전송", use_container_width=True):
    # 데이터 정리
    new_data = {
        "점검일자": check_date.strftime("%Y-%m-%d"),
        "점검자": inspector,
        "구역": full_location
    }
    new_data.update(results)
    new_data["지적내역"] = issue_detail
    new_data["사진첨부"] = "Y" if img_file else "N"
    
    # 엑셀 파일 처리 로직 (서버 내 로컬 백업)
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.append(list(new_data.keys()))
    else:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

    ws.append(list(new_data.values()))
    wb.save(EXCEL_FILE)
    
    st.success(f"✅ {full_location} 점검 데이터가 저장되었습니다!")
    if img_file:
        st.write("📷 사진 데이터가 함께 기록되었습니다.")
    st.balloons()