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

def set_status_filter(status_name):
    st.session_state["selected_remark"] = status_name
    st.session_state["current_page"] = 1  # Reset to page 1 on filter click

# --- 2. ADVANCED STYLING & CUSTOM CSS ---
font_link = "https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Inter:wght@400;500;600;700&display=swap"
st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)

custom_css = """
    <style>
        /* Base Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Sleek white circle background for logo */
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
            font-size: 38px !important; 
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            color: var(--text-color) !important;
            line-height: 1.15 !important;
            margin-bottom: 2px !important;
        }
        
        /* Subtitle */
        .portal-subtitle {
            font-family: 'Inter', sans-serif !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
            opacity: 0.85;
            margin-top: 0px !important;
        }

        /* Minimalist & Compact KPI Cards */
        div[data-testid="stColumn"] div[data-testid="stButton"] > button {
            width: 100% !important;
            height: 75px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(128, 128, 128, 0.3) !important;
            background-color: rgba(128, 128, 128, 0.08) !important;
            color: var(--text-color) !important;
            padding: 8px 12px !important;
            transition: all 0.2s ease-in-out !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }

        /* Enforce Oswald Font on Dashboard Tiles */
        div[data-testid="stColumn"] div[data-testid="stButton"] > button,
        div[data-testid="stColumn"] div[data-testid="stButton"] > button p,
        div[data-testid="stColumn"] div[data-testid="stButton"] > button div,
        div[data-testid="stColumn"] div[data-testid="stButton"] > button span {
            font-family: 'Oswald', sans-serif !important;
            font-weight: 700 !important;
            font-size: 20px !important;
            line-height: 1.2 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            text-align: center !important;
            white-space: pre-wrap !important;
            color: var(--text-color) !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            border-color: rgba(128, 128, 128, 0.6) !important;
            background-color: rgba(128, 128, 128, 0.16) !important;
        }

        /* --- ROCK-SOLID TABLE CONTAINER --- */
        .table-wrapper {
            width: 100%;
            max-height: 620px;
            overflow-y: auto;
            overflow-x: auto;
            border: 1px solid rgba(128, 128, 128, 0.3);
            border-radius: 8px;
            margin-top: 12px;
            background-color: var(--background-color, #0e1117);
        }

        table.record-table {
            width: 100%;
            min-width: 1100px;
            border-collapse: separate;
            border-spacing: 0;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: var(--text-color, #ffffff) !important;
        }

        /* OPAQUE STICKY HEADER (Guaranteed no bleed-through) */
        table.record-table th {
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: var(--secondary-background-color, #1a1d24) !important;
            color: var(--text-color, #ffffff) !important;
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 12px 14px;
            text-align: left;
            border-bottom: 2px solid rgba(128, 128, 128, 0.4);
            white-space: nowrap !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        /* TABLE BODY CELLS */
        table.record-table td {
            padding: 10px 14px;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            vertical-align: top;
            color: var(--text-color, #ffffff) !important;
            line-height: 1.5;
            white-space: normal;
            word-break: break-word;
        }

        /* Column Constraints */
        table.record-table td:nth-child(1) { min-width: 80px; width: 80px; }   /* TRF NO */
        table.record-table td:nth-child(2) { min-width: 100px; width: 100px; } /* DATE */
        table.record-table td:nth-child(3) { min-width: 180px; }              /* SOURCE */
        table.record-table td:nth-child(4) { min-width: 320px; }              /* REPORTS */
        table.record-table td:nth-child(5) { min-width: 110px; width: 110px; } /* DESTINATION */
        table.record-table td:nth-child(6) { min-width: 100px; width: 100px; } /* STATUS */
        table.record-table td:nth-child(7) { min-width: 100px; width: 100px; } /* REMARKS */
        table.record-table td:nth-child(8) { min-width: 120px; width: 120px; } /* DATE RETURNED */

        /* Subtle row hover highlight */
        table.record-table tbody tr:hover td {
            background-color: rgba(128, 128, 128, 0.1) !important;
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

# Load live data from Google Sheets with strict column cleaning
@st.cache_data(ttl=10)
def load_data(url):
    try:
        csv_url = get_csv_url(url)
        df = pd.read_csv(csv_url, dtype=str)
        
        # 1. Clean column headers
        df.columns = df.columns.astype(str).str.strip()
        
        # 2. Filter out phantom 'Unnamed' columns from Google Sheets
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

# --- LOCATE 'REMARKS' OR 'REMARK' COLUMN ---
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
        st.image("ESNCHS-LOGO.png", width=100)
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

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.button(
            f"📊 TOTAL\n{total_docs}", 
            on_click=set_status_filter, 
            args=("All Remarks",),
            use_container_width=True
        )
    with m2:
        st.button(
            f"⏳ PENDING\n{pending_count}", 
            on_click=set_status_filter, 
            args=("PENDING",),
            use_container_width=True
        )
    with m3:
        st.button(
            f"↩️ RETURNED\n{returned_count}", 
            on_click=set_status_filter, 
            args=("RETURNED",),
            use_container_width=True
        )
    with m4:
        st.button(
            f"✅ RELEASED\n{released_count}", 
            on_click=set_status_filter, 
            args=("RELEASED",),
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SEARCH & FILTER CONTROLS ---
st.markdown("### 🔍 Search & Filter Controls")

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

# Reset page to 1 whenever search query or remark filter changes
if ("last_search" in st.session_state and st.session_state["last_search"] != search_query) or \
   ("last_remark" in st.session_state and st.session_state["last_remark"] != selected_remark):
    st.session_state["current_page"] = 1

st.session_state["last_search"] = search_query
st.session_state["last_remark"] = selected_remark

# --- 6. FILTERING LOGIC ---
filtered_df = df.copy()

if not filtered_df.empty:
    # 1. Search Bar Filter
    if search_query:
        mask_search = filtered_df.apply(
            lambda row: row.astype(str).str.lower().str.contains(search_query).any(), 
            axis=1
        )
        filtered_df = filtered_df[mask_search]

    # 2. Strict REMARKS Column Filter
    if selected_remark != "All Remarks":
        if target_remarks_col and target_remarks_col in filtered_df.columns:
            mask_remark = filtered_df[target_remarks_col].astype(str).str.strip().str.upper().str.contains(
                selected_remark.upper(), na=False
            )
            filtered_df = filtered_df[mask_remark]

# --- 7. PAGINATION PREPARATION ---
ITEMS_PER_PAGE = 15
total_items = len(filtered_df)
total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

# Keep current page within valid bounds
if st.session_state["current_page"] > total_pages:
    st.session_state["current_page"] = total_pages

current_page = st.session_state["current_page"]

# Slice dataframe for current page
start_idx = (current_page - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
page_df = filtered_df.iloc[start_idx:end_idx]

# --- 8. RECORDBOOK DISPLAY ---
st.markdown(f"#### 📋 Document Records ({total_items} total records • Showing Page {current_page} of {total_pages})")

if not page_df.empty:
    # Clean text & split multiline entries into clean bullet points
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

    # Apply HTML formatting
    display_df = page_df.copy()
    for col in display_df.columns:
        display_df[col] = display_df[col].apply(format_cell_content)

    # Render Table
    raw_html = display_df.to_html(index=False, classes="record-table", escape=False)
    st.markdown(f'<div class="table-wrapper">{raw_html}</div>', unsafe_allow_html=True)
else:
    st.warning("❌ No records found matching your query/filter.")

# --- 9. PAGINATION BUTTONS AT BOTTOM ---
if total_pages > 1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render direct page numbers if 7 or fewer pages
    if total_pages <= 7:
        page_cols = st.columns(total_pages + 2)
        
        # Previous Button
        with page_cols[0]:
            if st.button("◀", key="btn_prev_num", disabled=(current_page == 1), use_container_width=True):
                st.session_state["current_page"] -= 1
                st.rerun()

        # Numbered Page Buttons
        for p in range(1, total_pages + 1):
            with page_cols[p]:
                btn_type = "primary" if p == current_page else "secondary"
                if st.button(str(p), key=f"btn_page_{p}", type=btn_type, use_container_width=True):
                    st.session_state["current_page"] = p
                    st.rerun()

        # Next Button
        with page_cols[-1]:
            if st.button("▶", key="btn_next_num", disabled=(current_page == total_pages), use_container_width=True):
                st.session_state["current_page"] += 1
                st.rerun()

    # Dropdown selector for large page numbers (> 7 pages)
    else:
        c_prev, c_select, c_next = st.columns([1, 2, 1])
        
        with c_prev:
            if st.button("◀ Previous", key="btn_prev_drop", disabled=(current_page == 1), use_container_width=True):
                st.session_state["current_page"] -= 1
                st.rerun()

        with c_select:
            selected_p = st.selectbox(
                "Jump to page",
                options=list(range(1, total_pages + 1)),
                index=current_page - 1,
                key="page_dropdown_select",
                label_visibility="collapsed"
            )
            if selected_p != current_page:
                st.session_state["current_page"] = selected_p
                st.rerun()

        with c_next:
            if st.button("Next ▶", key="btn_next_drop", disabled=(current_page == total_pages), use_container_width=True):
                st.session_state["current_page"] += 1
                st.rerun()

    st.markdown(f"<p style='text-align: center; font-size: 13px; opacity: 0.85; margin-top: 6px;'>Page <b>{current_page}</b> of <b>{total_pages}</b> ({total_items} matching records • 15 per page)</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Refresh Data button
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- 10. FOOTER ---
st.markdown("---")
st.caption("Eastern Samar National Comprehensive High School")
