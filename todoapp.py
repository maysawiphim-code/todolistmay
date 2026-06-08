import streamlit as st
import pandas as pd
import os
from datetime import datetime


# --- โค้ดแอปหลักของคุณเริ่มตรงนี้ ---
st.title("ระบบจัดการรายการงาน")
st.write("คุณสามารถใช้งานแอปได้แล้วตอนนี้!")

DATA_FILE = 'tasks.csv'

# โหลดข้อมูล
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=['Task', 'Status', 'Date'])

st.title("ระบบจัดการรายการงาน")

# 1. เพิ่มงาน
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

# 2. ค้นหา
search = st.text_input("🔍 ค้นหาชื่อรายการ:")
if search:
    # ค้นหาแบบกรองข้อมูลแต่ยังรักษา Index เดิมไว้เพื่อลบ
    display_df = df[df['Task'].str.contains(search, case=False, na=False)]
else:
    display_df = df

st.write("---")

# 3. แสดงรายการ
for i, row in display_df.iterrows():
    # แบ่งคอลัมน์: [ปุ่มเสร็จ] [ชื่อ] [วันที่] [ขั้นตอน] [ปุ่มลบ]
    col1, col2, col3, col4, col5 = st.columns([0.8, 2, 1, 1.5, 0.8])
    
    # ปุ่มทำเสร็จ
    if col1.button("✅", key=f"done_{i}"):
        df.at[i, 'Status'] = 'ทำแล้ว'
        df.to_csv(DATA_FILE, index=False)
        st.rerun()
    
    col2.write(f"**{row['Task']}**")
    col3.write(f"{row['Date']}")
    
    # เลือกขั้นตอน
    status_options = ['เตรียมข้อมูล', 'รอจับ', 'จับแล้ว']
    current_status = row['Status']
    default_idx = status_options.index(current_status) if current_status in status_options else 0
    
    new_status = col4.selectbox("ขั้นตอน", status_options, index=default_idx, key=f"sel_{i}", label_visibility="collapsed")
    if new_status != current_status:
        df.at[i, 'Status'] = new_status
        df.to_csv(DATA_FILE, index=False)
        st.rerun()

    # ปุ่มลบรายการ (ใหม่)
    if col5.button("🗑️", key=f"del_{i}"):
        df = df.drop(index=i)
        df.to_csv(DATA_FILE, index=False)
        st.rerun()