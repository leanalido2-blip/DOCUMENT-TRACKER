import streamlit as st
import pandas as pd
import html
import math
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ESNCHS Document Tracking Portal", 
    layout="wide", 
    page_icon="ESNCHS-LOGO.png"
)

# --- 2. GOOGLE SHEET RECORD-BOOK LINK ---
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Eu204mywqGj5ih3eCbpJOhTEaoaTP2du3i8hNPWUcCU/edit?usp=sharing"

# Initialize Session State Variables
if "selected_remark" not in st.session_state:
    st.session_state["selected_remark"] = "All Remarks"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = 1

def set_status_filter(status_name):
    st.session_state["selected_remark"] = status_name
    st.session_state["current_page"] = 1  # Reset to page 1 on filter click

# --- 3. CUSTOM STYLING (ESNCHS CRIMSON & GOLD THEME) ---
font_link = "https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Inter:wght@400;500;600;700&display=swap"
st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)

custom_css = """
    <style>
        /* Base Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Logo background */
        [data-testid="stImage"] img {
            background-color: #FFFFFF !important;
            border-radius: 50% !important;
            padding: 4px !important;
            object-fit: contain !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15) !important;
            border: 2px solid #fef08a !important;
        }

        /* Header Styling */
        .school-header {
            font-family: 'Oswald', sans-serif !important;
            font-size: 32px !important; 
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            color: #6B1111 !important;
            line-height: 1.15 !important;
            margin-bottom: 2px !important;
        }
        
        .portal-subtitle {
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #64748b !important;
            margin-top: 0px !important;
        }

        /* --- DASHBOARD METRIC TILES --- */
        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button {
            width: 100% !important;
            height: 68px !important;
            border-radius: 8px !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            color: #6B1111 !important;
            padding: 4px 8px !important;
            transition: all 0.2s ease-in-out !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }

        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button p,
        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button span {
            font-family: 'Oswald', sans-serif !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            line-height: 1.2 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            text-align: center !important;
            white-space: pre-wrap !important;
            color: #6B1111 !important;
            margin: 0 !important;
        }

        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            border-color: #d97706 !important;
            background-color: #fefce8 !important;
        }

        /* --- TABLE CONTAINER & TYPOGRAPHY --- */
        .table-wrapper {
            width: 100%;
            max-height: 520px;
            overflow-y: auto;
            overflow-x: auto;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }

        table.record-table {
            width: 100%;
            min-width: 1050px;
            border-collapse: separate;
            border-spacing: 0;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: #1e293b !important;
        }

        /* Crimson Header Bar for Table */
        table.record-table th {
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: #6B1111 !important;
            color: #ffffff !important;
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 10px 12px;
            text-align: left;
            border-bottom: 3px solid #d97706;
            white-space: nowrap !important;
        }

        /* Cells */
        table.record-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            color: #334155 !important;
            line-height: 1.4;
            word-break: break-word;
        }

        /* Column Constraints */
        table.record-table th:nth-child(1), table.record-table td:nth-child(1) { width: 75px; min-width: 75px; }   /* TRF NO */
        table.record-table th:nth-child(2), table.record-table td:nth-child(2) { width: 95px; min-width: 95px; white-space: nowrap !important; } /* DATE */
        table.record-table th:nth-child(3), table.record-table td:nth-child(3) { min-width: 160px; }              /* SOURCE */
        table.record-table th:nth-child(4), table.record-table td:nth-child(4) { min-width: 280px; }              /* REPORTS */
        table.record-table th:nth-child(5), table.record-table td:nth-child(5) { width: 100px; min-width: 100px; } /* DESTINATION */
        table.record-table th:nth-child(6), table.record-table td:nth-child(6) { width: 90px; min-width: 90px; }   /* STATUS */
        table.record-table th:nth-child(7), table.record-table td:nth-child(7) { width: 90px; min-width: 90px; }   /* REMARKS */
        table.record-table th:nth-child(8), table.record-table td:nth-child(8) { width: 110px; min-width: 110px; white-space: nowrap !important; } /* DATE RETURNED */

        table.record-table tbody tr:hover td {
            background-color: #f8fafc !important;
        }

        /* --- MINI PAGINATION BUTTONS --- */
        .pagination-wrapper div[data-testid="stButton"] > button {
            height: 32px !important;
            min-height: 32px !important;
            font-size: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            padding: 0px 4px !important;
            border-radius: 5px !important;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# Helper function to convert share link into CSV download link
def get_csv_url(sheet_url):
    if "/edit" in sheet_url:
        sheet_id = sheet_url.split("/d/")[1].split("/edit")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    return sheet_url

# Load live data from Google Sheets (Re-checks every 10 seconds)
@st.cache_data(ttl=10)
def load_data(url):
    try:
        csv_url = get_csv_url(url)
        df = pd.read_csv(csv_url, dtype=str)
        
        # Clean headers & remove blank columns
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
        df = df.loc[:, df.columns != '']
        
        # Clean rows
        df = df.dropna(how='all')
        df = df.fillna("N/A")
        
        return df
    except Exception as e:
        st.error("⚠️ Unable to connect to Google Sheet. Please check your document share settings.")
        return pd.DataFrame()

df = load_data(GSHEET_URL)

# Locate 'REMARKS' column
target_remarks_col = None
if not df.empty:
    for col in df.columns:
        if col.upper() in ["REMARKS", "REMARK"]:
            target_remarks_col = col
            break

# --- 4. BRANDED HEADER ---
col_logo, col_title = st.columns([1, 6])

with col_logo:
    if os.path.exists("ESNCHS-LOGO.png"):
        st.image("ESNCHS-LOGO.png", width=95)
    else:
        st.title("🏫")

with col_title:
    st.markdown('<p class="school-header">EASTERN SAMAR NATIONAL COMPREHENSIVE HIGH SCHOOL</p>', unsafe_allow_html=True)
    st.markdown('<p class="portal-subtitle">📜 Records & Document Status Tracking Portal</p>', unsafe_allow_html=True)

st.divider()

# --- 5. CLICKABLE DASHBOARD TILES ---
if not df.empty:
    total_docs = len(df)
    pending_count = 0
    returned_count = 0
    released_count = 0

    if target_remarks_col:
        remarks_series = df[target_remarks_col].astype(str).str.strip().str.upper()
        pending_count = (remarks_series.str.contains("PENDING", na=False)).sum()
        returned_count = (remarks_series.str.contains("RETURNED", na=False)).sum()
        released_count = (remarks_series.str.contains("RELEASED", na=False)).sum()

    st.markdown('<div class="metric-tiles">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.button(f"📊 TOTAL\n{total_docs}", on_click=set_status_filter, args=("All Remarks",), use_container_width=True)
    with m2:
        st.button(f"⏳ PENDING\n{pending_count}", on_click=set_status_filter, args=("PENDING",), use_container_width=True)
    with m3:
        st.button(f"↩️ RETURNED\n{returned_count}", on_click=set_status_filter, args=("RETURNED",), use_container_width=True)
    with m4:
        st.button(f"✅ RELEASED\n{released_count}", on_click=set_status_filter, args=("RELEASED",), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# --- 6. SEARCH & FILTER CONTROLS ---
col_search, col_filter = st.columns([3, 1])

with col_search:
    search_query = st.text_input(
        "Search records", 
        placeholder="Type TRF No, Document Name, or Source to search...", 
        label_visibility="collapsed"
    ).strip().lower()

with col_filter:
    default_statuses = ["PENDING", "RETURNED", "RELEASED"]
    
    sheet_remarks = []
    if target_remarks_col:
        raw_vals = df[target_remarks_col].dropna().unique()
        sheet_remarks = [
            str(r).strip().upper() 
            for r in raw_vals 
            if str(r).strip().upper() not in ["N/A", "NAN", ""]
        ]

    combined_list = list(dict.fromkeys(default_statuses + sorted(sheet_remarks)))
    remark_options = ["All Remarks"] + combined_list

    selected_remark = st.selectbox(
        "Filter by Remark", 
        remark_options, 
        key="selected_remark",
        label_visibility="collapsed"
    )

# Reset page on query/filter changes
if ("last_search" in st.session_state and st.session_state["last_search"] != search_query) or \
   ("last_remark" in st.session_state and st.session_state["last_remark"] != selected_remark):
    st.session_state["current_page"] = 1

st.session_state["last_search"] = search_query
st.session_state["last_remark"] = selected_remark

# --- 7. FILTERING LOGIC ---
filtered_df = df.copy()

if not filtered_df.empty:
    if search_query:
        mask_search = filtered_df.apply(
            lambda row: row.astype(str).str.lower().str.contains(search_query).any(), 
            axis=1
        )
        filtered_df = filtered_df[mask_search]

    if selected_remark != "All Remarks":
        if target_remarks_col and target_remarks_col in filtered_df.columns:
            mask_remark = filtered_df[target_remarks_col].astype(str).str.strip().str.upper().str.contains(
                selected_remark.upper(), na=False
            )
            filtered_df = filtered_df[mask_remark]

# --- 8. PAGINATION SETUP (10 ITEMS PER PAGE) ---
ITEMS_PER_PAGE = 10
total_items = len(filtered_df)
total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

if st.session_state["current_page"] > total_pages:
    st.session_state["current_page"] = total_pages

current_page = st.session_state["current_page"]

start_idx = (current_page - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
page_df = filtered_df.iloc[start_idx:end_idx]

# --- 9. DISPLAY RECORDS ---
st.markdown(f"#### 📋 Document Records ({total_items} total records • Page {current_page} of {total_pages})")

if not page_df.empty:
    def format_cell_content(val):
        if pd.isna(val) or str(val).strip() in ['nan', 'None', '']:
            return "N/A"
        
        raw_str = str(val).replace('\\n', '\n')
        lines = [line.strip() for line in raw_str.split('\n') if line.strip()]
        
        if len(lines) > 1:
            formatted_items = []
            for item in lines:
                escaped = html.escape(item)
                if not escaped.startswith('•'):
                    formatted_items.append(f"• {escaped}")
                else:
                    formatted_items.append(escaped)
            return "<br>".join(formatted_items)
        
        return html.escape(raw_str)

    display_df = page_df.copy()
    for col in display_df.columns:
        display_df[col] = display_df[col].apply(format_cell_content)

    raw_html = display_df.to_html(index=False, classes="record-table", escape=False)
    st.markdown(f'<div class="table-wrapper">{raw_html}</div>', unsafe_allow_html=True)
else:
    st.warning("❌ No records found matching your search or filter criteria.")

# --- 10. PAGINATION BAR ---
if total_pages > 1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    MAX_VISIBLE = 5
    if total_pages <= MAX_VISIBLE:
        visible_pages = list(range(1, total_pages + 1))
    else:
        half = MAX_VISIBLE // 2
        start_p = max(1, current_page - half)
        end_p = min(total_pages, start_p + MAX_VISIBLE - 1)
        
        if end_p - start_p + 1 < MAX_VISIBLE:
            start_p = max(1, end_p - MAX_VISIBLE + 1)
            
        visible_pages = list(range(start_p, end_p + 1))

    num_buttons = len(visible_pages) + 2  # Visible numbers + Prev + Next
    
    left_space, nav_center, right_space = st.columns([1, min(2.0, num_buttons * 0.28), 1])
    
    with nav_center:
        st.markdown('<div class="pagination-wrapper">', unsafe_allow_html=True)
        nav_cols = st.columns(num_buttons)
        
        # Previous Button
        with nav_cols[0]:
            if st.button("◀", key="btn_prev_num", disabled=(current_page == 1), use_container_width=True):
                st.session_state["current_page"] -= 1
                st.rerun()

        # Page Numbers
        for idx, p in enumerate(visible_pages):
            with nav_cols[idx + 1]:
                btn_type = "primary" if p == current_page else "secondary"
                if st.button(str(p), key=f"btn_page_{p}", type=btn_type, use_container_width=True):
                    st.session_state["current_page"] = p
                    st.rerun()

        # Next Button
        with nav_cols[-1]:
            if st.button("▶", key="btn_next_num", disabled=(current_page == total_pages), use_container_width=True):
                st.session_state["current_page"] += 1
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center; font-size: 11px; opacity: 0.75; margin-top: 4px;'>Page <b>{current_page}</b> of <b>{total_pages}</b> ({total_items} records • 10 per page)</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Manual Refresh Button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- 11. FOOTER ---
st.markdown("---")
st.caption("Eastern Samar National Comprehensive High School • Document Tracking Portal")
