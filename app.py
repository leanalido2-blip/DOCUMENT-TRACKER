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

# --- 2. CUSTOM CSS FOR TIGHT LOGO BADGE & FONT ---
font_link = "https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap"
st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)

custom_css = """
    <style>
        /* Sleek, tight white circle background for logo without overlapping */
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

# --- 3. BRANDED HEADER (LOGO + SCHOOL NAME) ---
col_logo, col_title = st.columns([1, 6])

with col_logo:
    if os.path.exists("ESNCHS-LOGO.png"):
        st.image("ESNCHS-LOGO.png", width=110)
    else:
        st.title("🏫")

with col_title:
    # ✏️ REPLACE WITH YOUR ACTUAL SCHOOL NAME BELOW:
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
    # Explicit status options + dynamic ones found in the sheet
    default_statuses = ["PENDING", "RETURNED", "RELEASED"]
    
    sheet_remarks = []
    if "Remark" in df.columns:
        sheet_remarks = [
            str(r).strip().upper() 
            for r in df["Remark"].unique() 
            if str(r).strip().upper() not in ["N/A", "NAN", ""]
        ]

    # Combines defaults + sheet statuses while removing duplicates
    combined_list = list(dict.fromkeys(default_statuses + sorted(sheet_remarks)))
    remark_options = ["All Remarks"] + combined_list

    selected_remark = st.selectbox("Filter by Remark", remark_options, label_visibility="collapsed")

# --- 5. FILTERING LOGIC ---
filtered_df = df.copy()

if not filtered_df.empty:
    # Apply Search Filter
    if search_query:
        mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)
        filtered_df = filtered_df[mask]

    # Apply Status/Remark Filter (Case-Insensitive)
    if selected_remark != "All Remarks" and "Remark" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["Remark"].astype(str).str.strip().str.upper() == selected_remark.upper()
        ]

# --- 6. RECORDBOOK DISPLAY ---
st.subheader(f"📋 Tracked Documents ({len(filtered_df)} records)")

if not filtered_df.empty:
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
else:
    st.warning("❌ No matching records found.")

# Refresh Button
st.markdown("---")
if st.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.rerun()
