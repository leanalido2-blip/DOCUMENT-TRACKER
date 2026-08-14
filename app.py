import streamlit as st
import pandas as pd
import html
import math
import os

# Page Configuration
st.set_page_config(
    page_title="ESNCHS Document Tracking Portal", 
    layout="wide", 
    page_icon="ESNCHS-LOGO.png"
)

# --- 1. PASTE YOUR GOOGLE SHEET LINK HERE ---
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Eu204mywqGj5ih3eCbpJOhTEaoaTP2du3i8hNPWUcCU/edit?usp=sharing"

# Initialize Session State Variables
if "selected_remark" not in st.session_state:
    st.session_state["selected_remark"] = "All Remarks"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = 1

if "entries_per_page" not in st.session_state:
    st.session_state["entries_per_page"] = 10

def set_status_filter(status_name):
    st.session_state["selected_remark"] = status_name
    st.session_state["current_page"] = 1

# --- 2. CSC PORTAL STYLING & CUSTOM CSS ---
font_link = "https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Inter:wght@400;500;600;700&display=swap"
st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)

custom_css = """
    <style>
        /* Base Typography */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        /* Logo background */
        [data-testid="stImage"] img {
            background-color: #FFFFFF !important;
            border-radius: 50% !important;
            padding: 4px !important;
            object-fit: contain !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.12) !important;
        }

        /* Oswald font for Main School Header */
        .school-header {
            font-family: 'Oswald', sans-serif !important;
            font-size: 32px !important; 
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            color: var(--text-color) !important;
            line-height: 1.15 !important;
            margin-bottom: 2px !important;
        }
        
        .portal-subtitle {
            font-size: 14px !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
            opacity: 0.85;
            margin-top: 0px !important;
        }

        /* --- CSC FILTER SECTION --- */
        .csc-filter-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--text-color);
        }

        /* CSC Primary Blue Button */
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #0d6efd !important;
            border-color: #0d6efd !important;
            color: #ffffff !important;
            font-weight: 500 !important;
            height: 38px !important;
            border-radius: 4px !important;
        }

        /* CSC Secondary Grey Button */
        div[data-testid="stButton"] > button[kind="secondary"] {
            background-color: #6c757d !important;
            border-color: #6c757d !important;
            color: #ffffff !important;
            font-weight: 500 !important;
            height: 38px !important;
            border-radius: 4px !important;
        }

        /* --- DASHBOARD TILES --- */
        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button {
            width: 100% !important;
            height: 60px !important;
            border-radius: 6px !important;
            border: 1px solid rgba(128, 128, 128, 0.3) !important;
            background-color: rgba(128, 128, 128, 0.08) !important;
            color: var(--text-color) !important;
            padding: 4px 8px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }

        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button p,
        .metric-tiles div[data-testid="stColumn"] div[data-testid="stButton"] > button span {
            font-family: 'Oswald', sans-serif !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            line-height: 1.2 !important;
            text-transform: uppercase !important;
            color: var(--text-color) !important;
        }

        /* --- CSC TABLE CONTAINER & DESIGN --- */
        .table-wrapper {
            width: 100%;
            overflow-x: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            margin-top: 8px;
            background-color: var(--background-color) !important;
        }

        table.csc-table {
            width: 100%;
            min-width: 1000px;
            border-collapse: collapse;
            font-size: 13px;
            color: var(--text-color) !important;
        }

        /* CSC Dark Table Header */
        table.csc-table th {
            background-color: #3a3a3a !important;
            color: #ffffff !important;
            font-weight: 600;
            padding: 12px 10px;
            text-align: left;
            border-bottom: 2px solid #212529;
            white-space: nowrap !important;
        }

        /* Table Cells & Zebra Striping */
        table.csc-table td {
            padding: 10px 10px;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            vertical-align: middle;
            color: var(--text-color) !important;
            line-height: 1.4;
        }

        table.csc-table tbody tr:nth-of-type(even) {
            background-color: rgba(128, 128, 128, 0.05);
        }

        table.csc-table tbody tr:hover td {
            background-color: rgba(128, 128, 128, 0.12) !important;
        }

        /* CSC Blue Action Details Button */
        .btn-details {
            display: inline-block;
            background-color: #0d6efd;
            color: #ffffff !important;
            text-decoration: none !important;
            padding: 5px 14px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            text-align: center;
            transition: background-color 0.2s ease;
        }

        .btn-details:hover {
            background-color: #0b5ed7;
        }

        /* --- MINI PAGINATION BUTTONS --- */
        .pagination-wrapper div[data-testid="stButton"] > button {
            height: 32px !important;
            min-height: 32px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            padding: 0px 4px !important;
            border-radius: 4px !important;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# Helper function to convert share link into live CSV format
def get_csv_url(sheet_url):
    if "/edit" in sheet_url:
        sheet_id = sheet_url.split("/d/")[1].split("/edit")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    return sheet_url

# Load live data from Google Sheets
@st.cache_data(ttl=10)
def load_data(url):
    try:
        csv_url = get_csv_url(url)
        df = pd.read_csv(csv_url, dtype=str)
        
        # 1. Clean column headers
        df.columns = df.columns.astype(str).str.strip()
        
        # 2. Filter out phantom 'Unnamed' columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
        df = df.loc[:, df.columns != '']
        
        # 3. Clean up empty rows & fill missing values
        df = df.dropna(how='all')
        df = df.fillna("N/A")
        
        return df
    except Exception as e:
        st.error("⚠️ Unable to load Google Sheet data. Please check your share settings.")
        return pd.DataFrame()

df = load_data(GSHEET_URL)

# Locate 'REMARKS' column
target_remarks_col = None
if not df.empty:
    for col in df.columns:
        if col.upper() in ["REMARKS", "REMARK"]:
            target_remarks_col = col
            break

# --- 3. BRANDED HEADER ---
col_logo, col_title = st.columns([1, 6])

with col_logo:
    if os.path.exists("ESNCHS-LOGO.png"):
        st.image("ESNCHS-LOGO.png", width=90)
    else:
        st.title("🏫")

with col_title:
    st.markdown('<p class="school-header">EASTERN SAMAR NATIONAL COMPREHENSIVE HIGH SCHOOL</p>', unsafe_allow_html=True)
    st.markdown('<p class="portal-subtitle">📜 Records & Document Status Tracking Portal</p>', unsafe_allow_html=True)

st.divider()

# --- 4. CLICKABLE DASHBOARD TILES ---
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

# --- 5. CSC-STYLE "FILTER PUBLICATIONS BY" SECTION ---
st.markdown('<p class="csc-filter-title">Filter Records by:</p>', unsafe_allow_html=True)

f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2.5, 1, 1])

with f_col1:
    search_keyword = st.text_input("Document / TRF / Source :", placeholder="e.g. Vacation Leave, TRF 0001, PORFERIO...")

with f_col2:
    default_statuses = ["PENDING", "RETURNED", "RELEASED"]
    sheet_remarks = []
    if target_remarks_col and not df.empty:
        raw_vals = df[target_remarks_col].dropna().unique()
        sheet_remarks = [
            str(r).strip().upper() 
            for r in raw_vals 
            if str(r).strip().upper() not in ["N/A", "NAN", ""]
        ]

    combined_list = list(dict.fromkeys(default_statuses + sorted(sheet_remarks)))
    remark_options = ["All Remarks"] + combined_list

    selected_remark = st.selectbox("Status / Remarks :", remark_options, key="selected_remark")

with f_col3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("✓ Filter", type="primary", use_container_width=True):
        st.session_state["current_page"] = 1

with f_col4:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# --- 6. FILTERING LOGIC ---
filtered_df = df.copy()

if not filtered_df.empty:
    if search_keyword:
        mask_search = filtered_df.apply(
            lambda row: row.astype(str).str.lower().str.contains(search_keyword.lower()).any(), 
            axis=1
        )
        filtered_df = filtered_df[mask_search]

    if selected_remark != "All Remarks":
        if target_remarks_col and target_remarks_col in filtered_df.columns:
            mask_remark = filtered_df[target_remarks_col].astype(str).str.strip().str.upper().str.contains(
                selected_remark.upper(), na=False
            )
            filtered_df = filtered_df[mask_remark]

# --- 7. CSC TOP TABLE CONTROLS BAR (SHOW ENTRIES & QUICK SEARCH) ---
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.5, 4, 3.5])

with ctrl_col1:
    items_per_page = st.selectbox(
        "Show", 
        [10, 25, 50, 100], 
        index=0, 
        key="entries_per_page"
    )

with ctrl_col3:
    table_search = st.text_input("Search:", placeholder="Filter table...", label_visibility="visible")

if table_search:
    mask_tbl = filtered_df.apply(
        lambda row: row.astype(str).str.lower().str.contains(table_search.lower()).any(), 
        axis=1
    )
    filtered_df = filtered_df[mask_tbl]

# --- 8. PAGINATION PREPARATION ---
total_items = len(filtered_df)
total_pages = max(1, math.ceil(total_items / items_per_page))

if st.session_state["current_page"] > total_pages:
    st.session_state["current_page"] = total_pages

current_page = st.session_state["current_page"]

start_idx = (current_page - 1) * items_per_page
end_idx = start_idx + items_per_page
page_df = filtered_df.iloc[start_idx:end_idx]

# --- 9. RENDER CSC-STYLED DATA TABLE WITH ESNCHS COLUMNS ---
if not page_df.empty:
    def format_cell_content(val):
        if pd.isna(val) or str(val).strip() in ['nan', 'None', '']:
            return "N/A"
        raw_str = str(val).replace('\\n', '\n')
        lines = [line.strip() for line in raw_str.split('\n') if line.strip()]
        if len(lines) > 1:
            formatted_items = [f"• {html.escape(item)}" if not item.startswith('•') else html.escape(item) for item in lines]
            return "<br>".join(formatted_items)
        return html.escape(raw_str)

    # Build CSC HTML Table
    table_html = '<div class="table-wrapper"><table class="csc-table"><thead><tr>'
    
    # Render Dynamic Headers from Google Sheet
    for col in page_df.columns:
        table_html += f'<th>{html.escape(str(col).upper())}</th>'
    table_html += '<th style="text-align: center;">ACTION</th></tr></thead><tbody>'

    # Render Table Rows
    for idx, row in page_df.iterrows():
        table_html += '<tr>'
        for col in page_df.columns:
            cell_val = format_cell_content(row[col])
            table_html += f'<td>{cell_val}</td>'
        
        # Action Column (Blue CSC Details Button)
        table_html += f'''
            <td style="text-align: center;">
                <a href="#row-{idx}" class="btn-details">Details</a>
            </td>
        </tr>
        '''
    
    table_html += '</tbody></table></div>'
    st.markdown(table_html, unsafe_allow_html=True)
else:
    st.warning("❌ No matching document records found.")

# --- 10. CSC PAGINATION BAR (MAX 5 VISIBLE NUMBERS) ---
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

    num_buttons = len(visible_pages) + 2
    
    left_space, nav_center, right_space = st.columns([1, min(2.0, num_buttons * 0.28), 1])
    
    with nav_center:
        st.markdown('<div class="pagination-wrapper">', unsafe_allow_html=True)
        nav_cols = st.columns(num_buttons)
        
        # Previous Button
        with nav_cols[0]:
            if st.button("◀", key="btn_prev_csc", disabled=(current_page == 1), use_container_width=True):
                st.session_state["current_page"] -= 1
                st.rerun()

        # 5 Page Number Buttons
        for idx, p in enumerate(visible_pages):
            with nav_cols[idx + 1]:
                btn_type = "primary" if p == current_page else "secondary"
                if st.button(str(p), key=f"btn_p_{p}", type=btn_type, use_container_width=True):
                    st.session_state["current_page"] = p
                    st.rerun()

        # Next Button
        with nav_cols[-1]:
            if st.button("▶", key="btn_next_csc", disabled=(current_page == total_pages), use_container_width=True):
                st.session_state["current_page"] += 1
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center; font-size: 11px; opacity: 0.75; margin-top: 4px;'>Showing page <b>{current_page}</b> of <b>{total_pages}</b> ({total_items} total records)</p>", unsafe_allow_html=True)

# --- 11. FOOTER ---
st.markdown("---")
st.caption("Eastern Samar National Comprehensive High School • Document Tracking Portal")
