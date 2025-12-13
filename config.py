# import os
# from dotenv import load_dotenv

# load_dotenv()

# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')


# GEMINI_MODEL = "gemini-flash-latest"  

# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY not found in .env file")
# if not GOOGLE_APPLICATION_CREDENTIALS:
#     raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in .env file")
# if not DRIVE_FOLDER_ID:
#     raise ValueError("DRIVE_FOLDER_ID not found in .env file")

# print("✅ Configuration loaded successfully!")


import os

# Detect if we're running on Streamlit Cloud
IS_STREAMLIT_CLOUD = os.path.exists('/mount/src')

if IS_STREAMLIT_CLOUD:
    # Running on Streamlit Cloud - use secrets
    print("🌐 Running on Streamlit Cloud")
    import streamlit as st
    
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    DRIVE_FOLDER_IDS = st.secrets.get("DRIVE_FOLDER_IDS", "")
    
    # Service account from secrets
    GOOGLE_APPLICATION_CREDENTIALS = "service-account.json"
    
    # Write service account JSON to file from secrets
    import json
    with open(GOOGLE_APPLICATION_CREDENTIALS, 'w') as f:
        json.dump(dict(st.secrets["gcp_service_account"]), f)
    
    print("✅ Loaded secrets from Streamlit Cloud")
    
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
    
    print("✅ Loaded configuration from .env")

# Convert to list
if DRIVE_FOLDER_IDS:
    DRIVE_FOLDER_IDS_LIST = [fid.strip() for fid in DRIVE_FOLDER_IDS.split(',') if fid.strip()]
else:
    DRIVE_FOLDER_IDS_LIST = []

# Gemini Model Configuration
GEMINI_MODEL = "gemini-1.5-flash-latest"

print(f"📁 {len(DRIVE_FOLDER_IDS_LIST)} folder(s) configured")