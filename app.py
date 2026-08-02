import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(
    page_title="ESNCHS Document Tracking Portal", 
    layout="wide", 
    page_icon="ESNCHS-LOGO.png"
)

# --- 1. PASTE YOUR GOOGLE SHEET LINK HERE ---
GSHEET_URL = "YOUR_GOOGLE_SHEET_LINK_HERE"

# Initialize Filter Session State
if "selected_remark" not in st.session_state:
    st.session_state["selected_remark"] = "All Remarks"

def set_status_filter(status_name):
    st.session_state["selected_remark"] = status_name

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
            font-size: 40px !important; 
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            color: var(--text-color) !important;
            line-height: 1.15 !important;
            margin-bottom: 2px !important;
        }
        
        /* Subtitle */
        .portal-subtitle {
            font-family: 'Inter', sans-serif !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
            opacity: 0.75;
            margin-top: 0px !important;
        }

        /* Minimalist & Compact KPI Cards */
        div[data-testid="stColumn"] div[data-testid="stButton"] > button {
            width: 100% !important;
            height: 78px !important;
            border-radius: 10px !important;
            border: 1px solid rgba(125, 125, 125, 0.22) !important;
            background-color: rgba(125, 125, 125, 0.03) !important;
            color: var(--text-color) !important;
            padding: 8px 12px !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }

        /* Enforce Oswald Font, Bold Weight, and Perfectly Centered Text */
        div[data-testid="stColumn"] div[data-testid="stButton"] > button,
        div[data-testid="stColumn"] div[data-testid="stButton"] > button p,
        div[data-testid="stColumn"] div[data-testid="stButton"] > button div,
        div[data-testid="stColumn"] div[data-testid="stButton"] > button span {
            font-family: 'Oswald', sans-serif !important;
            font-weight: 700 !important;
            font-size: 21px !important;
            line-height: 1.2 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            text-align: center !important;
            white-space: pre-wrap !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stColumn"] div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            border-color: rgba(125, 125, 125, 0.5) !important;
            background-color: rgba(125, 125, 125, 0.08) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06) !important;
        }

        /* Full width dataframe container */
        [data-testid="stDataFrame"] {
            width: 100% !important;
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
        st.image("ESNCHS-LOGO.png", width=105)
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

# --- 7. RECORDBOOK DISPLAY ---
st.markdown(f"#### 📋 Document Records ({len(filtered_df)} showing)")

if not filtered_df.empty:
    # Dynamically calculate sentence length for each column to auto-adapt widths
    column_configs = {}
    for col in filtered_df.columns:
        # Get max string length in the column (comparing header name vs content)
        max_char_len = max(
            filtered_df[col].astype(str).map(len).max() if len(filtered_df) > 0 else 0,
            len(str(col))
        )
        
        # Assign dynamic width based on sentence length
        if max_char_len > 40:
            assigned_width = "large"
        elif max_char_len > 18:
            assigned_width = "medium"
        else:
            assigned_width = "small"
            
        column_configs[col] = st.column_config.TextColumn(
            col,
            width=assigned_width,
            help="Double-click any cell to expand and copy full text"
        )

    st.dataframe(
        filtered_df, 
        use_container_width=True, 
        hide_index=True,
        column_config=column_configs
    )
else:
    st.warning("❌ No records found matching your query/filter.")

# Refresh Data button
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- 8. FOOTER ---
st.markdown("---")
st.caption("Eastern Samar National Comprehensive High School")
