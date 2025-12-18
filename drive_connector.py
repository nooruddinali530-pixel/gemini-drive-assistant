import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import PyPDF2
from docx import Document
import config

class DriveConnector:
    
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            config.GOOGLE_APPLICATION_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        print("Connected to Google Drive")
    
    def list_files(self, folder_id):
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size)"
            ).execute()
            
            files = results.get('files', [])
            print(f"📁 Found {len(files)} files in folder")
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def download_file(self, file_id):
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            return file_content
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def extract_text_from_pdf(self, file_content):
        try:
            pdf_reader = PyPDF2.PdfReader(file_content)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_content):
        try:
            doc = Document(file_content)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_txt(self, file_content):
        try:
            return file_content.read().decode('utf-8')
        except Exception as e:
            print(f"❌ Error extracting TXT text: {e}")
            return ""
    
    def get_file_content(self, file_id, mime_type):
        file_content = self.download_file(file_id)
        if not file_content:
            return ""
        
        if mime_type == 'application/pdf':
            return self.extract_text_from_pdf(file_content)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self.extract_text_from_docx(file_content)
        elif mime_type == 'text/plain':
            return self.extract_text_from_txt(file_content)
        elif mime_type == 'application/vnd.google-apps.document':
            # For Google Docs, export as plain text
            try:
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                )
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                file_content.seek(0)
                return file_content.read().decode('utf-8')
            except Exception as e:
                print(f"Error exporting Google Doc: {e}")
                return ""
        else:
            print(f"Unsupported file type: {mime_type}")
            return ""
    
    def get_all_documents_content(self, folder_id):
        """Get combined text content from all documents in folder"""
        files = self.list_files(folder_id)
        
        combined_content = []
        for file in files:
            print(f"Processing: {file['name']}")
            content = self.get_file_content(file['id'], file['mimeType'])
            if content:
                combined_content.append(f"=== {file['name']} ===\n{content}\n")
        
        return "\n\n".join(combined_content)