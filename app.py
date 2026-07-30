import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Document Status Portal", layout="wide", page_icon="📄")

# --- 1. PASTE YOUR GOOGLE SHEET LINK HERE ---
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Eu204mywqGj5ih3eCbpJOhTEaoaTP2du3i8hNPWUcCU/edit?usp=sharing"

# Helper function to convert share link into live data format
def get_csv_url(sheet_url):
    if "/edit" in sheet_url:
        sheet_id = sheet_url.split("/d/")[1].split("/edit")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    return sheet_url

st.title("📄 Live Document Tracking & Status Portal")

# Load live data from Google Sheets
@st.cache_data(ttl=10)  # Auto-refresh every 10 seconds
def load_data(url):
    try:
        csv_url = get_csv_url(url)
        df = pd.read_csv(csv_url)
        df = df.fillna("N/A")
        df = df.astype(str)
        return df
    except Exception as e:
        st.error("⚠️ Unable to load Google Sheet. Make sure 'Anyone with the link' is set in Share settings.")
        return pd.DataFrame()

# Fetch data
df = load_data(GSHEET_URL)

# --- SEARCH & FILTER BAR ---
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("🔍 Search by TRF No, Report Name, or Source", "").strip().lower()

with col2:
    status_filter = st.selectbox(
        "Filter by Status", 
        ["All Statuses", "Pending", "Under Review", "Approved", "Returned for Revision", "Completed"]
    )

# Search & Filter Logic
filtered_df = df.copy()

if not filtered_df.empty:
    if search_query:
        mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)
        filtered_df = filtered_df[mask]

    if status_filter != "All Statuses" and "Status" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]

# --- USER DISPLAY TABLE ---
st.subheader(f"Tracked Documents ({len(filtered_df)} records)")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
