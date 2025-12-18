import os
import json

IS_STREAMLIT_CLOUD = os.path.exists('/mount/src')

if IS_STREAMLIT_CLOUD:
    print("Running on Streamlit Cloud")
    import streamlit as st
    
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    DRIVE_FOLDER_IDS = st.secrets.get("DRIVE_FOLDER_IDS", "")
    
    GOOGLE_APPLICATION_CREDENTIALS = "service-account.json"
    
    sa_data = dict(st.secrets["gcp_service_account"])
    
    if "private_key" in sa_data:
        sa_data["private_key"] = sa_data["private_key"].replace("\\n", "\n")
    
    with open(GOOGLE_APPLICATION_CREDENTIALS, 'w') as f:
        json.dump(sa_data, f, indent=2)
    
    print("Loaded secrets from Streamlit Cloud")
    print(f"Service account written to {GOOGLE_APPLICATION_CREDENTIALS}")
    
else:
    # Running locally - use .env
    print("💻 Running locally")
    from dotenv import load_dotenv
    load_dotenv()
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    DRIVE_FOLDER_IDS = os.getenv('DRIVE_FOLDER_IDS', os.getenv('DRIVE_FOLDER_ID', ''))
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    print("Loaded configuration from .env")

if DRIVE_FOLDER_IDS:
    DRIVE_FOLDER_IDS_LIST = [fid.strip() for fid in DRIVE_FOLDER_IDS.split(',') if fid.strip()]
else:
    DRIVE_FOLDER_IDS_LIST = []

GEMINI_MODEL = "gemini-flash-latest"

print(f"📁 {len(DRIVE_FOLDER_IDS_LIST)} folder(s) configured")