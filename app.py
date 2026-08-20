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
