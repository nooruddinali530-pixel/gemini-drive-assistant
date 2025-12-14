import streamlit as st
import config
from drive_connector import DriveConnector
from gemini_query import GeminiQueryEngine

# Page configuration
# Page configuration - FORCE DARK MODE
st.set_page_config(
    page_title="Gemini Drive Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force dark theme
st.markdown("""
<script>
    var stTheme = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
    if (stTheme) {
        stTheme.setAttribute('data-theme', 'dark');
    }
</script>
""", unsafe_allow_html=True)

# hide_streamlit_style = """
#             <style>
            
#             </style>
#             """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom CSS for dark theme

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0e1117;
        color: #ffffff;
        padding: 2rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #1e3a8a 0%, #4c1d95 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    /* Chat input box */
    .stChatInput {
        background-color: #1e1e1e !important;
    }
    
    .stChatInput input {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    .stChatInput input::placeholder {
        color: #888 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #1e1e1e !important;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #ffffff !important;
    }
    
    /* User message */
    [data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-weight: 600;
        background-color: #4c1d95;
        color: white !important;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #5b21b6;
        border: none;
    }
    
    /* Success boxes */
    .success-box, [data-testid="stSuccess"] {
        background-color: #1e4620 !important;
        border: 1px solid #2d5a2f !important;
        color: #4ade80 !important;
    }
    
    /* Info boxes */
    .info-box, [data-testid="stInfo"] {
        background-color: #1e3a5f !important;
        border: 1px solid #2d5a8f !important;
        color: #60a5fa !important;
    }
    
    /* Warning boxes */
    [data-testid="stWarning"] {
        background-color: #5f4a1e !important;
        border: 1px solid #8f6d2d !important;
        color: #fbbf24 !important;
    }
    
    /* Checkboxes */
    .stCheckbox {
        color: #ffffff !important;
    }
    
    /* Checkbox labels */
    .stCheckbox label {
        color: #ffffff !important;
    }
    
    /* Document item styling */
    .doc-item {
        background-color: #2d2d2d;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #4c1d95;
    }
    
    .doc-item-selected {
        background-color: #3d2d5d;
        border-left: 3px solid #9333ea;
    }
    
    /* Divider */
    hr {
        border-color: #444 !important;
    }
    
    /* All text elements */
    p, span, div, label {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'drive_connector' not in st.session_state:
    st.session_state.drive_connector = None
if 'gemini_engine' not in st.session_state:
    st.session_state.gemini_engine = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'documents_content' not in st.session_state:
    st.session_state.documents_content = ""
if 'document_list' not in st.session_state:
    st.session_state.document_list = []
if 'selected_documents' not in st.session_state:
    st.session_state.selected_documents = set()
if 'document_contents' not in st.session_state:
    st.session_state.document_contents = {}

def initialize_connectors():
    """Initialize Drive and Gemini connectors"""
    try:
        with st.spinner("🔌 Connecting to Google Drive..."):
            st.session_state.drive_connector = DriveConnector()
        
        with st.spinner("🤖 Connecting to Gemini..."):
            st.session_state.gemini_engine = GeminiQueryEngine()
        
        return True
    except Exception as e:
        st.error(f"❌ Error initializing connectors: {str(e)}")
        return False

def load_documents():
    """Load documents from Drive folder"""
    try:
        with st.spinner("📂 Fetching document list from Drive..."):
            # Get file list from all configured folders
            all_files = []
            
            for folder_id in config.DRIVE_FOLDER_IDS_LIST:
                files = st.session_state.drive_connector.list_files(folder_id)
                # Add folder info to each file
                for file in files:
                    file['folder_id'] = folder_id
                all_files.append(files)
            
            # Flatten the list
            st.session_state.document_list = [f for sublist in all_files for f in sublist]
            st.session_state.document_list = files
            
            # Select all documents by default
            st.session_state.selected_documents = {file['id'] for file in files}
            
            st.session_state.documents_loaded = True
        
        return True
    except Exception as e:
        st.error(f"❌ Error loading documents: {str(e)}")
        return False

def load_selected_documents():
    """Load content only from selected documents"""
    if not st.session_state.selected_documents:
        st.warning("⚠️ No documents selected!")
        st.session_state.documents_content = ""
        return False
    
    try:
        with st.spinner(f"📄 Loading {len(st.session_state.selected_documents)} selected documents..."):
            combined_content = []
            
            for file in st.session_state.document_list:
                if file['id'] in st.session_state.selected_documents:
                    # Check if already cached
                    if file['id'] not in st.session_state.document_contents:
                        content = st.session_state.drive_connector.get_file_content(
                            file['id'], 
                            file['mimeType']
                        )
                        st.session_state.document_contents[file['id']] = content
                    else:
                        content = st.session_state.document_contents[file['id']]
                    
                    if content:
                        combined_content.append(f"=== {file['name']} ===\n{content}\n")
            
            st.session_state.documents_content = "\n\n".join(combined_content)
        
        return True
    except Exception as e:
        st.error(f"❌ Error loading document content: {str(e)}")
        return False

def get_file_icon(mime_type):
    """Get emoji icon for file type"""
    if mime_type == 'application/pdf':
        return "📕"
    elif 'document' in mime_type:
        return "📝"
    elif 'text' in mime_type:
        return "📃"
    elif 'spreadsheet' in mime_type:
        return "📊"
    elif 'presentation' in mime_type:
        return "📊"
    else:
        return "📄"

# Header
st.markdown("""
<div class="header">
    <h1>🤖 Gemini Drive Assistant</h1>
    <p>AI-powered document querying with Google Gemini and Drive</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=100)
    st.title("⚙️ Configuration")
    
    # Connection status
    st.subheader("📡 Connection Status")
    
    if st.session_state.drive_connector is None:
        st.warning("Not connected to Google Drive")
    else:
        st.success("✅ Connected to Google Drive")
    
    if st.session_state.gemini_engine is None:
        st.warning("Not connected to Gemini")
    else:
        st.success("✅ Connected to Gemini")
    
    st.divider()
    
    # Initialize button
    if st.button("🚀 Initialize Connection", use_container_width=True):
        if initialize_connectors():
            st.success("✅ Successfully connected!")
            st.rerun()
    
    # Load documents button
    if st.session_state.drive_connector is not None:
        if st.button("📁 Fetch Documents", use_container_width=True):
            if load_documents():
                st.success(f"✅ Found {len(st.session_state.document_list)} documents!")
                st.rerun()
    
    st.divider()
    
    # Document selection
    if st.session_state.documents_loaded:
        st.subheader("📚 Select Documents")
        
        # Select/Deselect all buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Select All", use_container_width=True):
                st.session_state.selected_documents = {file['id'] for file in st.session_state.document_list}
                st.rerun()
        with col2:
            if st.button("❌ Deselect All", use_container_width=True):
                st.session_state.selected_documents = set()
                st.rerun()
        
        st.write(f"**{len(st.session_state.selected_documents)}/{len(st.session_state.document_list)}** selected")
        
        # Document checkboxes
        st.markdown("---")
        
        for file in st.session_state.document_list:
            file_icon = get_file_icon(file['mimeType'])
            
            # Checkbox for each document
            is_selected = file['id'] in st.session_state.selected_documents
            
            checkbox_label = f"{file_icon} {file['name']}"
            
            # Create checkbox
            selected = st.checkbox(
                checkbox_label,
                value=is_selected,
                key=f"doc_{file['id']}"
            )
            
            # Update selection
            if selected and file['id'] not in st.session_state.selected_documents:
                st.session_state.selected_documents.add(file['id'])
            elif not selected and file['id'] in st.session_state.selected_documents:
                st.session_state.selected_documents.remove(file['id'])
        
        st.divider()
        
        # Load selected documents button
        if st.button("🔄 Load Selected Documents", use_container_width=True, type="primary"):
            if load_selected_documents():
                st.success(f"✅ Loaded {len(st.session_state.selected_documents)} documents!")
                # Clear chat when documents change
                st.session_state.messages = []
                st.rerun()
        
        # Stats
        if st.session_state.documents_content:
            st.divider()
            total_chars = len(st.session_state.documents_content)
            st.metric("Total Characters", f"{total_chars:,}")
            st.metric("Estimated Tokens", f"{total_chars // 4:,}")
    
    st.divider()
    
    # Settings
    st.subheader("🔧 Settings")
    st.text(f"Model: {config.GEMINI_MODEL}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat with Your Documents")
    
    # Check if ready to chat
    if not st.session_state.documents_loaded:
        st.info("👈 **Step 1:** Click 'Initialize Connection' in sidebar")
        st.info("👈 **Step 2:** Click 'Fetch Documents' to see available files")
    elif not st.session_state.selected_documents:
        st.warning("👈 **Step 3:** Select at least one document from the sidebar")
    elif not st.session_state.documents_content:
        st.info("👈 **Step 4:** Click 'Load Selected Documents' to start chatting")
    else:
        # Display selected documents info
        st.info(f"💡 Currently querying **{len(st.session_state.selected_documents)}** selected documents")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your selected documents..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = st.session_state.gemini_engine.query(
                            st.session_state.documents_content,
                            prompt
                        )
                        st.markdown(response)
                        
                        # Add assistant message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })

with col2:
    st.subheader("💡 Quick Actions")
    
    # Example questions
    st.markdown("**Try asking:**")
    example_questions = [
        "What are the main topics?",
        "Summarize the key points",
        "What is mentioned about [topic]?",
        "Compare the documents",
        "Extract important dates"
    ]
    
    for question in example_questions:
        if st.button(question, key=question, use_container_width=True):
            if st.session_state.documents_content:
                # Add to chat
                st.session_state.messages.append({"role": "user", "content": question})
                
                # Generate response
                try:
                    response = st.session_state.gemini_engine.query(
                        st.session_state.documents_content,
                        question
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please load documents first!")
    
    st.divider()
    
    # Currently selected documents display
    if st.session_state.documents_loaded and st.session_state.selected_documents:
        st.markdown("**📑 Active Documents:**")
        for file in st.session_state.document_list:
            if file['id'] in st.session_state.selected_documents:
                file_icon = get_file_icon(file['mimeType'])
                st.markdown(f"{file_icon} {file['name']}")
    
    st.divider()
    
    # Help section
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        **Steps:**
        1. Click **"Initialize Connection"**
        2. Click **"Fetch Documents"**
        3. **Select/deselect** documents
        4. Click **"Load Selected Documents"**
        5. Start asking questions!
        
        **Tips:**
        - Only selected documents are queried
        - Change selection anytime
        - Chat history clears when you reload
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Powered by Google Gemini API and Google Drive API</p>
    <p>Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)