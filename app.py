import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Document Status Portal", layout="wide", page_icon="🛡️")

# --- 1. SET YOUR ADMIN PASSWORD HERE ---
ADMIN_PASSWORD = "AdminPassword123"  # Change "AdminPassword123" to your secret password

# --- 2. INITIALIZE DATABASE ---
if "doc_db" not in st.session_state:
    st.session_state.doc_db = pd.DataFrame([
        {
            "Doc ID": "DOC-2026-001",
            "Document Name": "Oath-Taking Ceremony Layout",
            "Category": "Design",
            "Submitted By": "Alice Smith",
            "Submission Date": "2026-07-15",
            "Status": "Approved",
            "Last Updated": "2026-07-18"
        },
        {
            "Doc ID": "DOC-2026-002",
            "Document Name": "Q2 Financial Audit Report",
            "Category": "Finance",
            "Submitted By": "Bob Jones",
            "Submission Date": "2026-07-20",
            "Status": "Under Review",
            "Last Updated": "2026-07-22"
        },
        {
            "Doc ID": "DOC-2026-003",
            "Document Name": "Campus Integrity Guidelines PDF",
            "Category": "Policy",
            "Submitted By": "Charlie Brown",
            "Submission Date": "2026-07-28",
            "Status": "Pending",
            "Last Updated": "2026-07-28"
        },
    ])

# Session state for Admin Login
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("📄 Live Document Tracking & Status Portal")

# --- SIDEBAR: LOGIN & SUBMISSIONS ---
with st.sidebar:
    st.header("🔑 Admin Login")
    if not st.session_state.is_admin:
        input_pwd = st.text_input("Enter Admin Password", type="password")
        if st.button("Login as Admin"):
            if input_pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("Logged in as Admin!")
                st.rerun()
            else:
                st.error("Incorrect Password")
    else:
        st.success("🟢 Logged in as Admin")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("---")
    st.header("➕ Submit New Document")
    doc_name = st.text_input("Document Name / Title")
    category = st.selectbox("Category", ["Design", "Finance", "Policy", "Operations", "General"])
    submitted_by = st.text_input("Your Name")
    
    if st.button("Submit Document", type="primary"):
        if doc_name and submitted_by:
            new_id = f"DOC-2026-{len(st.session_state.doc_db) + 1:03d}"
            today = datetime.now().strftime("%Y-%m-%d")
            
            new_entry = {
                "Doc ID": new_id,
                "Document Name": doc_name,
                "Category": category,
                "Submitted By": submitted_by,
                "Submission Date": today,
                "Status": "Pending",
                "Last Updated": today
            }
            
            st.session_state.doc_db = pd.concat(
                [st.session_state.doc_db, pd.DataFrame([new_entry])], 
                ignore_index=True
            )
            st.success(f"Submitted! Tracking ID: **{new_id}**")
        else:
            st.error("Please fill in both fields.")

# --- MAIN PAGE: SEARCH & MONITOR ---
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("🔍 Search documents by ID, Title, or Submitter", "").strip().lower()

with col2:
    status_filter = st.selectbox("Filter by Status", ["All Statuses", "Pending", "Under Review", "Approved", "Completed"])

# Filter Logic
df = st.session_state.doc_db.copy()

if search_query:
    df = df[
        df["Doc ID"].str.lower().str.contains(search_query) |
        df["Document Name"].str.lower().str.contains(search_query) |
        df["Submitted By"].str.lower().str.contains(search_query)
    ]

if status_filter != "All Statuses":
    df = df[df["Status"] == status_filter]

# --- USER VIEW ---
st.subheader(f"Tracked Documents ({len(df)} records)")
st.dataframe(df, use_container_width=True, hide_index=True)

# --- ADMIN-ONLY CONTROL PANEL ---
if st.session_state.is_admin:
    st.markdown("---")
    st.header("⚙️ Admin Control Panel (Status Management)")
    
    if not st.session_state.doc_db.empty:
        selected_id = st.selectbox("Select Document ID to Manage", st.session_state.doc_db["Doc ID"])
        doc_row = st.session_state.doc_db[st.session_state.doc_db["Doc ID"] == selected_id].iloc[0]
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.write(f"**Document:** {doc_row['Document Name']}")
            st.write(f"**Submitted By:** {doc_row['Submitted By']}")
        
        with col_b:
            new_status = st.selectbox(
                "Update Status", 
                ["Pending", "Under Review", "Approved", "Completed"],
                index=["Pending", "Under Review", "Approved", "Completed"].index(doc_row["Status"])
            )
            if st.button("Save Status Update"):
                idx = st.session_state.doc_db.index[st.session_state.doc_db["Doc ID"] == selected_id][0]
                st.session_state.doc_db.at[idx, "Status"] = new_status
                st.session_state.doc_db.at[idx, "Last Updated"] = datetime.now().strftime("%Y-%m-%d")
                st.success(f"Updated {selected_id} to **{new_status}**!")
                st.rerun()

        with col_c:
            st.write("**Danger Zone**")
            if st.button("❌ Delete Document Log", type="secondary"):
                st.session_state.doc_db = st.session_state.doc_db[st.session_state.doc_db["Doc ID"] != selected_id]
                st.warning(f"Deleted record {selected_id}.")
                st.rerun()
