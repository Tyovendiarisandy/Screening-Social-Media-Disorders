import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheets_connection():
    """Establishes connection to Google Sheets using secrets."""
    try:
        # Load credentials from secrets
        # Streamlit secrets handles toml parsing automatically
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Comprehensive fix for Streamlit Cloud private key formatting issues
        if "private_key" in creds_dict:
            private_key = creds_dict["private_key"]
            
            # 1. Remove potential surrounding quotes
            private_key = private_key.strip().strip('"').strip("'")
            
            # 2. Handle ALL possible newline representations
            # Replace literal \n with actual newlines
            private_key = private_key.replace("\\n", "\n")
            # Also handle double-escaped newlines
            private_key = private_key.replace("\\\\n", "\n")
            
            # 3. Remove any extra whitespace between lines
            lines = [line.strip() for line in private_key.split('\n') if line.strip()]
            
            # 4. Reconstruct with proper formatting
            if lines:
                # Ensure proper header
                if lines[0] != "-----BEGIN PRIVATE KEY-----":
                    lines.insert(0, "-----BEGIN PRIVATE KEY-----")
                
                # Ensure proper footer
                if lines[-1] != "-----END PRIVATE KEY-----":
                    lines.append("-----END PRIVATE KEY-----")
                
                # Join with newlines
                private_key = "\n".join(lines)
                
            creds_dict["private_key"] = private_key
        
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=SCOPES
        )
        
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def store_response(profile_data, responses):
    """
    Stores the user response to the Google Sheet.
    
    Args:
        profile_data (dict): User profile information.
        responses (dict): User answers to the questionnaire.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    client = get_sheets_connection()
    if not client:
        return False
        
    try:
        sheet_url = st.secrets["sheets"]["spreadsheet_url"]
        sheet = client.open_by_url(sheet_url).sheet1
        
        # Prepare row data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Flatten data for the row
        row = [timestamp]
        row.extend([
            profile_data.get("alias"),
            profile_data.get("age"),
            profile_data.get("gender"),
            profile_data.get("occupation")
        ])
        
        # Add responses in order (assuming keys are Q1, Q2, etc. or ordered list)
        # We'll assume responses is a dict like {'Q1': 5, 'Q2': 1, ...}
        # Sorting keys to ensure order
        for key in sorted(responses.keys(), key=lambda x: int(x[1:])):
            row.append(responses[key])
            
        # Calculate and append total score
        total_score = sum(responses.values())
        row.append(total_score)
            
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error storing data: {e}")
        return False
