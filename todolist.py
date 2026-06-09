import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="ระบบจัดการรายการงาน", layout="wide")

DATA_FILE = 'tasks.csv'
COLS = ['Task', 'Status', 'Date', 'Detail']

# --- โหลดข้อมูล ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # เพิ่มคอลัมน์ Detail ถ้ายังไม่มี (backward compat)
    if 'Detail' not in df.columns:
        df['Detail'] = ''
else:
    df = pd.DataFrame(columns=COLS)

def save(dataframe):
    dataframe.to_csv(DATA_FILE, index=False)

# --- State สำหรับ popup รายละเอียด ---
if 'open_detail' not in st.session_state:
    st.session_state.open_detail = None  # เก็บ index ที่เปิดอยู่

# ============================================================
# หัว + แดชบอร์ด
# ============================================================
st.title("📋 ระบบจัดการรายการงาน")

if not df.empty:
    status_counts = df['Status'].value_counts()
    cols = st.columns(max(len(status_counts), 1))
    for idx, (status, count) in enumerate(status_counts.items()):
        cols[idx].metric(label=status, value=count)
else:
    st.info("ยังไม่มีข้อมูลรายการงาน")

st.divider()

# ============================================================
# เพิ่มงานใหม่
# ============================================================
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
                    'Task':   [new_task],
                    'Status': ['รอจับ'],
                    'Date':   [selected_date.strftime("%Y-%m-%d")],
                    'Detail': [''],
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save(df)
                st.rerun()

# ============================================================
# ค้นหา / กรอง
# ============================================================
col_search, col_filter = st.columns([2, 1])
with col_search:
    search = st.text_input("🔍 ค้นหาชื่อรายการ:")
with col_filter:
    status_options = ['ทั้งหมด', 'เตรียมข้อมูล', 'รอจับ', 'จับแล้ว']
    selected_filter = st.selectbox("🎯 กรองสถานะ:", status_options)

# เรียงใหม่สุดก่อน แล้วค่อยกรอง
display_df = df.copy()
display_df['_sort_date'] = pd.to_datetime(display_df['Date'], errors='coerce')
display_df = display_df.sort_values('_sort_date', ascending=False).drop(columns='_sort_date')

if search:
    display_df = display_df[display_df['Task'].str.contains(search, case=False, na=False)]
if selected_filter != 'ทั้งหมด':
    display_df = display_df[display_df['Status'] == selected_filter]

st.write("---")

# ============================================================
# หัวตาราง
# ============================================================
col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([0.8, 2.2, 1, 1.5, 0.8])
col_h2.markdown("**📍 ชื่อไซต์**")
col_h3.markdown("**📅 วันที่**")
col_h4.markdown("**⚙️ สถานะ**")

ALL_STATUS = ['เตรียมข้อมูล', 'รอจับ', 'จับแล้ว']

# ============================================================
# รายการ
# ============================================================
for i in display_df.index:
    row = df.loc[i]
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([0.8, 2.2, 1, 1.5, 0.8])

        # ปุ่มทำเสร็จ
        if col1.button("✅", key=f"done_{i}"):
            df.at[i, 'Status'] = 'จับแล้ว'
            save(df)
            st.balloons()
            st.rerun()

        # ชื่อไซต์ — คลิกได้ เปิด/ปิด popup รายละเอียด
        if col2.button(f"**{row['Task']}**", key=f"name_{i}", use_container_width=True):
            if st.session_state.open_detail == i:
                st.session_state.open_detail = None   # ปิดถ้าคลิกซ้ำ
            else:
                st.session_state.open_detail = i

        col3.write(row['Date'])

        # Selectbox สถานะ
        current_status = row['Status']
        default_idx = ALL_STATUS.index(current_status) if current_status in ALL_STATUS else 0
        new_status = col4.selectbox(
            "ขั้นตอน", ALL_STATUS, index=default_idx,
            key=f"sel_{i}", label_visibility="collapsed"
        )
        if new_status != current_status:
            df.at[i, 'Status'] = new_status
            save(df)
            st.rerun()

        # ปุ่มลบ
        if col5.button("🗑️", key=f"del_{i}"):
            df = df.drop(index=i).reset_index(drop=True)
            save(df)
            if st.session_state.open_detail == i:
                st.session_state.open_detail = None
            st.rerun()

    # --- แผง รายละเอียด (แสดงใต้แถวที่คลิก) ---
    if st.session_state.open_detail == i:
        with st.container(border=True):
            st.markdown(f"#### 📝 รายละเอียด: {row['Task']}")
            detail_text = st.text_area(
                "รายละเอียด",
                value=str(row['Detail']) if pd.notna(row['Detail']) else '',
                height=150,
                key=f"detail_text_{i}",
                label_visibility="collapsed",
                placeholder="กรอกรายละเอียดเพิ่มเติม เช่น หมายเหตุ, ข้อมูลพิเศษ..."
            )
            btn_save, btn_close = st.columns([1, 5])
            if btn_save.button("💾 บันทึก", key=f"save_detail_{i}", type="primary"):
                df.at[i, 'Detail'] = detail_text
                save(df)
                st.success("บันทึกรายละเอียดเรียบร้อยแล้ว!")
                st.rerun()
            if btn_close.button("✖ ปิด", key=f"close_detail_{i}"):
                st.session_state.open_detail = None
                st.rerun()
