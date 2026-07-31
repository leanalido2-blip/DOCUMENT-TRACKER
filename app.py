import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(
    page_title="Document Tracking Portal", 
    layout="wide", 
    page_icon="📜"
)

# --- PASTE YOUR GOOGLE SHEET LINK HERE ---
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Eu204mywqGj5ih3eCbpJOhTEaoaTP2du3i8hNPWUcCU/edit?usp=sharing"

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
        df = pd.read_csv(csv_url)
        df = df.fillna("N/A")
        df = df.astype(str)
        return df
    except Exception as e:
        st.error("⚠️ Unable to load Google Sheet data. Please check your share settings.")
        return pd.DataFrame()

df = load_data(GSHEET_URL)

# --- BRANDED HEADER (LOGO + SCHOOL NAME) ---
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Looks for logo.png in your GitHub repository
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)
    else:
        st.title("🏫")

with col_title:
    # ✏️ REPLACE WITH YOUR ACTUAL SCHOOL / UNIVERSITY NAME BELOW:
    st.markdown("## **EASTERN SAMAR NATIONAL COMPREHENSIVE HIGH SCHOOL**")
    st.markdown("##### **Document Status & Tracking Portal**")

st.info(
    "💡 **How to check your document:** Type your **TRF No.**, **Name (Document Source)**, "
    "or **Report Name (e.g., TOR, COG)** into the search bar below."
)

st.divider()

# --- SEARCH INTERFACE ---
search_query = st.text_input(
    "🔍 Search Query", 
    placeholder="Type TRF No, Report Name, or Source...", 
    label_visibility="collapsed"
).strip().lower()

# --- FILTERING & RESULTS ---
filtered_df = df.copy()

if search_query:
    if not filtered_df.empty:
        mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)
        filtered_df = filtered_df[mask]
        
        if not filtered_df.empty:
            st.success(f"Found {len(filtered_df)} matching record(s):")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.warning("❌ No matching records found.")
else:
    st.info("🔒 **Search Active:** Type your details in the search box above to display your document status.")

# Refresh Button
st.markdown("---")
if st.button("🔄 Refresh Live Data"):
    st.cache_data.clear()
    st.rerun()
