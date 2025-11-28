import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime

class GoogleSheetsManager:
    def __init__(self):
        """Initialize Google Sheets API connection"""
        try:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            self.sheet_id = st.secrets["GOOGLE_SHEET_ID"]
        except Exception as e:
            st.error(f"Error initializing Google Sheets: {str(e)}")
            raise
    
    def append_response(self, user_data, responses, total_score, category):
        """
        Append user response to Google Sheets
        
        Args:
            user_data: Dictionary with profile data
            responses: Dictionary with SMDS-27 responses
            total_score: Total calculated score
            category: Severity category
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare row data
            row = [
                timestamp,
                user_data['nama'],
                user_data['umur'],
                user_data['gender'],
                user_data['pekerjaan']
            ]
            
            # Add all 27 item responses
            for i in range(1, 28):
                row.append(responses.get(f'item_{i}', 0))
            
            # Add total score and category
            row.extend([total_score, category])
            
            # Append to sheet
            body = {'values': [row]}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range='Responses!A:AH',  # A to AH (34 columns total)
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True, result.get('updates').get('updatedRows')
            
        except HttpError as error:
            st.error(f"Google Sheets API error: {error}")
            return False, None
        except Exception as e:
            st.error(f"Error appending data: {str(e)}")
            return False, None
    
    def initialize_sheet_headers(self):
        """Create headers in the sheet if not exists"""
        try:
            headers = [
                'Timestamp', 'Nama', 'Umur', 'Gender', 'Pekerjaan'
            ]
            
            # Add item headers
            for i in range(1, 28):
                headers.append(f'Item_{i}')
            
            headers.extend(['Total_Score', 'Category'])
            
            body = {'values': [headers]}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range='Responses!A1:AH1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            st.error(f"Error initializing headers: {str(e)}")
            return False
    
    def get_all_responses(self):
        """Retrieve all responses from the sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='Responses!A:AH'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return pd.DataFrame()
            
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
            
        except Exception as e:
            st.error(f"Error retrieving data: {str(e)}")
            return pd.DataFrame()
