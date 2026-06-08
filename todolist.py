import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="ระบบจัดการรายการงาน", layout="wide")

# --- การตั้งค่าไฟล์ข้อมูล ---
DATA_FILE = 'tasks.csv'

# โหลดข้อมูล
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=['Task', 'Status', 'Date'])

# --- ส่วนหัวของแอป ---
st.title("📋 ระบบจัดการรายการงาน")
st.write("ยินดีต้อนรับเข้าสู่ระบบจัดการงานของคุณ!")

# 1. แดชบอร์ดสรุปผล
st.subheader("📊 สรุปสถานะงาน")
if not df.empty:
    status_counts = df['Status'].value_counts()
    cols = st.columns(len(status_counts))
    for idx, (status, count) in enumerate(status_counts.items()):
        cols[idx].metric(label=status, value=count)
else:
    st.info("ยังไม่มีข้อมูลรายการงาน")

st.divider()

# 2. เพิ่มงานใหม่
with st.expander("➕ เพิ่มงานใหม่", expanded=True):
    col_input, col_date, col_btn = st.columns([3, 1, 1])
    with col_input:
        new_task = st.text_input("ชื่อรายการงาน:")
    with col_date:
        selected_date = st.date_input("วันที่:", datetime.now())
    with col_btn:
        st.write(" ")
        if st.button("บันทึกรายการ", use_container_width=True):
            if new_task:
                new_row = pd.DataFrame({
                    'Task': [new_task], 
                    'Status': ['รอจับ'], 
                    'Date': [selected_date.strftime("%Y-%m-%d")]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.rerun()

# 3. ส่วนการค้นหาและตัวกรอง
col_search, col_filter = st.columns([2, 1])
with col_search:
    search = st.text_input("🔍 ค้นหาชื่อรายการ:")
with col_filter:
    status_options = ['ทั้งหมด', 'เตรียมข้อมูล', 'รอจับ', 'จับแล้ว']
    selected_filter = st.selectbox("🎯 กรองสถานะ:", status_options)

# กรองข้อมูล
display_df = df
if search:
    display_df = display_df[display_df['Task'].str.contains(search, case=False, na=False)]
if selected_filter != 'ทั้งหมด':
    display_df = display_df[display_df['Status'] == selected_filter]

st.write("---")

# 4. หัวตาราง
col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([0.8, 2, 1, 1.5, 0.8])
col_h2.markdown("**📍 ชื่อไซต์**")
col_h3.markdown("**📅 วันที่**")
col_h4.markdown("**⚙️ สถานะ**")

# 5. แสดงรายการ
for i, row in display_df.iterrows():
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([0.8, 2, 1, 1.5, 0.8])
        
        # ปุ่มทำเสร็จ
        if col1.button("✅", key=f"done_{i}"):
            df.at[i, 'Status'] = 'จับแล้ว'
            df.to_csv(DATA_FILE, index=False)
            st.balloons()
            st.rerun()
        
        col2.write(f"**{row['Task']}**")
        col3.write(f"{row['Date']}")
        
        # เลือกขั้นตอน
        all_status = ['เตรียมข้อมูล', 'รอจับ', 'จับแล้ว']
        current_status = row['Status']
        default_idx = all_status.index(current_status) if current_status in all_status else 0
        
        new_status = col4.selectbox("ขั้นตอน", all_status, index=default_idx, key=f"sel_{i}", label_visibility="collapsed")
        if new_status != current_status:
            df.at[i, 'Status'] = new_status
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
        
        # ปุ่มลบ
        if col5.button("🗑️", key=f"del_{i}"):
            df = df.drop(index=i)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
