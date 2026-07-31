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
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Eu204mywqGj5ih3eCbpJOhTEaoaTP2du3i8hNPWUcCU/edit?usp=sharing"

# --- 2. ADVANCED STYLING & CUSTOM CSS ---
font_link = "https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600&display=swap"
st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)

custom_css = """
    <style>
        /* Base typography & layout refinements */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Sleek white circle background for logo */
        [data-testid="stImage"] img {
            background-color: #FFFFFF !important;
            border-radius: 50% !important;
            padding: 4px !important;
            object-fit: contain !important;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15) !important;
        }

        /* Oswald font for Main School Header */
        .school-header {
            font-family: 'Oswald', sans-serif !important;
            font-size: 42px !important; 
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            color: var(--text-color) !important;
            line-height: 1.15 !important;
            margin-bottom: 2px !important;
        }
        
        /* Subtitle */
        .portal-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 17px !important;
            font-weight: 500;
            color: var(--text-color) !important;
            opacity: 0.75;
            margin-top: 0px !important;
        }

        /* KPI Metric Cards Styling */
        [data-testid="stMetric"] {
            background-color: rgba(125, 125, 125, 0.08);
            border-radius: 12px;
            padding: 14px 18px;
            border: 1px solid rgba(125, 125, 125, 0.15);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }
        [data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            font-size: 13px !important;
            letter-spacing: 0.5px;
            opacity: 0.8;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Oswald', sans-serif !important;
            font-size: 32px !important;
            font-weight: 700 !important;
        }

        /* Vertically centers logo with text */
        [data-testid="stHorizontalBlock"] {
            align-items: center;
        }

        /* Footer styling */
        .portal-footer {
            text-align: center;
            padding: 20px;
            opacity: 0.6;
            font-size: 13px;
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
        # dtype=str ensures numbers keep leading zeros (e.g. 0001 stays 0001)
        df = pd.read_csv(csv_url, dtype=str)
        df = df.fillna("N/A")
        # Strip leading/trailing spaces from headers
        df.columns = df.columns.str.strip()
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
        st.image("ESNCHS-LOGO.png", width=110)
    else:
        st.title("🏫")

with col_title:
    st.markdown('<p class="school-header">EASTERN SAMAR NATIONAL COMPREHENSIVE HIGH SCHOOL</p>', unsafe_allow_html=True)
    st.markdown('<p class="portal-subtitle">📜 Records & Document Status Tracking Portal</p>', unsafe_allow_html=True)

st.divider()

# --- 4. SUMMARY METRICS (SUMMARY CARDS) ---
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
    m1.metric("TOTAL RECORDS", total_docs)
    m2.metric("⏳ PENDING", pending_count)
    m3.metric("↩️ RETURNED", returned_count)
    m4.metric("✅ RELEASED", released_count)

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

with col2 if 'col2' in locals() else col_filter:
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

    selected_remark = st.selectbox("Filter by Remark", remark_options, label_visibility="collapsed")

# --- 6. FILTERING LOGIC ---
filtered_df = df.copy()

if not filtered_df.empty:
    # 1. Search Bar Filter across all text
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
        else:
            st.error(
                f"⚠️ Could not find a column named 'REMARKS' or 'REMARK' in your Google Sheet. "
                f"Detected columns: **{list(df.columns)}**"
            )

# --- 7. RECORDBOOK DISPLAY ---
st.markdown(f"#### 📋 Document Records ({len(filtered_df)} showing)")

if not filtered_df.empty:
    st.dataframe(
        filtered_df, 
        use_container_width=True, 
        hide_index=True,
        height=450
    )
else:
    st.warning(f"❌ No records found matching your query/filter.")

# --- 8. FOOTER & REFRESH ---
st.markdown("---")
col_bot1, col_bot2 = st.columns([4, 1])

with col_bot1:
    st.caption("Eastern Samar National Comprehensive High School • Document Management & Registrar Office")

with col_bot2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
