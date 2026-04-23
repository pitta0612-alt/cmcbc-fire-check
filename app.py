import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook

# 엑셀 파일 이름 설정
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

# 앱 설정
st.set_page_config(page_title="부천성모병원 소방점검", layout="wide")
st.title("🏥 소방시설 전 항목 점검 시스템 (V3.2)")

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
# 3개의 열로 분할하여 배치
cols = st.columns(3)

for idx, item in enumerate(total_items):
    with cols[idx % 3]:
        # 라디오 버튼 형식이 가장 빠르고 정확함
        results[item] = st.radio(
            f"**{item}**",
            ["양호", "불량"],
            key=f"check_{item}",
            horizontal=True
        )

st.divider()

# 지적 내역 입력
st.header("📝 지적 내역 및 비고")
issue_detail = st.text_area("상세 불량 사유를 입력하세요 (없으면 공란)", placeholder="예: 3번 소화기 압력 저하 등")

# 저장 버튼
if st.button("📊 점검 결과 엑셀 저장", use_container_width=True):
    # 저장할 데이터 구조 생성
    new_data = {
        "점검일자": check_date.strftime("%Y-%m-%d"),
        "점검자": inspector,
        "구역": full_location
    }
    new_data.update(results)
    new_data["지적내역"] = issue_detail
    
    # 엑셀 파일 처리 로직
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.append(list(new_data.keys())) # 헤더 생성
    else:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

    ws.append(list(new_data.values())) # 데이터 추가
    wb.save(EXCEL_FILE)
    
    st.success(f"✅ {full_location} 점검 데이터가 성공적으로 저장되었습니다!")
    st.balloons()