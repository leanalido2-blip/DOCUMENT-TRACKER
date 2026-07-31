import streamlit as st
import pandas as pd
import os

# Page Configuration using your official ESNCHS logo as the browser tab icon
st.set_page_config(
    page_title="ESNCHS Document Tracking Portal", 
    layout="wide", 
    page_icon="ESNCHS-LOGO.png"
)

# --- 1. PASTE YOUR GOOGLE SHEET LINK HERE ---
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Eu204mywqGj5ih3eCbpJOhTEaoaTP2du3i8hNPWUcCU/edit?usp=sharing"

# --- 2. CUSTOM CSS FOR LOGO BADGE & FONT ---
font_link = "https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap"
st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)

custom_css = """
    <style>
        /* Sleek white circle background for logo */
        [data-testid="stImage"] img {
            background-color: #FFFFFF !important;
            border-radius: 50% !important;
            padding: 3px !important;
            object-fit: contain !important;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.25) !important;
        }

        /* Oswald font for School Header */
        .school-header {
            font-family: 'Oswald', sans-serif !important;
            font-size: 48px !important; 
            font-weight: 700 !important;
            color: var(--text-color) !important;
            line-height: 1.1 !important;
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
        
        /* Subtitle */
        .portal-subtitle {
            font-family: 'Source Sans Pro', sans-serif;
            font-size: 20px !important;
            color: var(--text-color) !important;
            opacity: 0.85;
            margin-top: 0px !important;
        }

        /* Vertically centers logo with text */
        [data-testid="stHorizontalBlock"] {
            align-items: center;
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
        return df
    except Exception as e:
        st.error("⚠️ Unable to load Google Sheet data. Please check your share settings.")
        return pd.DataFrame()

df = load_data(GSHEET_URL)

# --- DYNAMICALLY DETECT REMARK/STATUS COLUMN ---
remark_col = None
if not df.empty:
    possible_names = [
        "remark", "remarks", "status", "document status", 
        "doc status", "action", "action taken", "state", "remarks/status"
    ]
    for col in df.columns:
        if col.strip().lower() in possible_names:
            remark_col = col
            break
            
    if not remark_col:
        for col in df.columns:
            if "remark" in col.lower() or "status" in col.lower() or "action" in col.lower():
                remark_col = col
                break

# --- 3. BRANDED HEADER (LOGO + SCHOOL NAME) ---
col_logo, col_title = st.columns([1, 6])

with col_logo:
    if os.path.exists("ESNCHS-LOGO.png"):
        st.image("ESNCHS-LOGO.png", width=110)
    else:
        st.title("🏫")

with col_title:
    st.markdown('<p class="school-header">EASTERN SAMAR NATIONAL COMPREHENSIVE HIGH SCHOOL</p>', unsafe_allow_html=True)
    st.markdown('<p class="portal-subtitle">Document Status & Tracking Portal</p>', unsafe_allow_html=True)

st.divider()

# --- 4. SEARCH & FILTER CONTROLS ---
st.markdown("### 🔍 Search & Filter")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "🔍 Search", 
        placeholder="Type TRF No, Report Name, or Source to filter...", 
        label_visibility="collapsed"
    ).strip().lower()

with col2:
    default_statuses = ["PENDING", "RETURNED", "RELEASED"]
    
    sheet_remarks = []
    if remark_col:
        sheet_remarks = [
            str(r).strip().upper() 
            for r in df[remark_col].unique() 
            if str(r).strip().upper() not in ["N/A", "NAN", ""]
        ]

    # Combine defaults + actual sheet statuses without duplicates
    combined_list = list(dict.fromkeys(default_statuses + sorted(sheet_remarks)))
    remark_options = ["All Remarks"] + combined_list

    selected_remark = st.selectbox("Filter by Remark", remark_options, label_visibility="collapsed")

# --- 5. FILTERING LOGIC ---
filtered_df = df.copy()

if not filtered_df.empty:
    # 1. Search Bar Filter (Searches across all text in the table)
    if search_query:
        mask_search = filtered_df.apply(
            lambda row: row.astype(str).str.lower().str.contains(search_query).any(), 
            axis=1
        )
        filtered_df = filtered_df[mask_search]

    # 2. Status Dropdown Filter (Automatic Fail-Safe)
    if selected_remark != "All Remarks":
        if remark_col and remark_col in filtered_df.columns:
            # Filter specifically by the status column
            mask_status = filtered_df[remark_col].astype(str).str.upper().str.contains(selected_remark.upper(), na=False)
            filtered_df = filtered_df[mask_status]
        else:
            # Fallback: Search across ALL columns for the selected status keyword
            mask_status = filtered_df.apply(
                lambda row: row.astype(str).str.upper().str.contains(selected_remark.upper()).any(), 
                axis=1
            )
            filtered_df = filtered_df[mask_status]

# --- 6. RECORDBOOK DISPLAY ---
st.subheader(f"📋 Tracked Documents ({len(filtered_df)} records)")

if not filtered_df.empty:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
else:
    st.warning(f"❌ No records found with status '{selected_remark}'.")

# Refresh Button
st.markdown("---")
if st.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.rerun()
