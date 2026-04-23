import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook

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

# 앱 설정
st.set_page_config(page_title="부천성모병원 소방점검", layout="wide")
st.title("🏥 소방시설 정밀 점검 시스템 (V4.0)")

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

# --- 수정된 기능: 후면 카메라 권장 및 선택형 활성화 ---
col_img, col_txt = st.columns([1, 1])

with col_img:
    st.header("📸 현장 사진 첨부")
    
    # 안내 문구 추가
    st.caption("💡 스마트폰 접속 시 '후면 카메라'를 사용해 주세요.")
    
    show_camera = st.checkbox("📷 사진 촬영 기능 켜기 (후면 권장)")
    
    img_file = None
    if show_camera:
        # Streamlit의 camera_input은 브라우저의 마지막 설정을 기억하는 경우가 많습니다.
        # 아래는 표준 입력 방식이며, 모바일 브라우저에서 '카메라 전환' 버튼이 보일 것입니다.
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

# 저장 버튼
if st.button("📊 점검 결과 저장 및 데이터 전송", use_container_width=True):
    # 저장 데이터 구성
    new_data = {
        "점검일자": check_date.strftime("%Y-%m-%d"),
        "점검자": inspector,
        "구역": full_location
    }
    new_data.update(results)
    new_data["지적내역"] = issue_detail
    # 사진 여부 기록 (나중에 사진을 구글 드라이브 등에 올리는 로직을 위해)
    new_data["사진첨부"] = "Y" if img_file else "N"
    
    # 1. 로컬 엑셀 저장 (백업용)
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.append(list(new_data.keys()))
    else:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

    ws.append(list(new_data.values()))
    wb.save(EXCEL_FILE)
    
    # 2. 구글 시트 연동 안내 (다음 단계)
    st.success(f"✅ {full_location} 점검 데이터가 로컬에 저장되었습니다!")
    if img_file:
        st.write("📷 사진이 함께 캡처되었습니다.")
    
    st.warning("⚠️ 외부에서 접속 중이라면 현재 데이터는 서버 임시 폴더에 저장됩니다. 안전한 보관을 위해 구글 시트 연동을 완료해 주세요.")
    st.balloons()