import google.generativeai as genai
import config

class GeminiQueryEngine:
    """Handles queries to Gemini with document context"""
    
    def __init__(self):
        """Initialize Gemini API"""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        print("✅ Connected to Gemini API")
    
    def query(self, context, user_question, system_prompt=""):
        """Query Gemini with document context and optional system prompt"""
        try:
            # Build the complete prompt
            if system_prompt:
                # With custom persona
                prompt = f"""SYSTEM ROLE: {system_prompt}

You have access to the following documents:

{context}

Based on the documents above and your assigned role, please answer the following question:
{user_question}

Remember to stay in character according to your role while using the documents as your source material. Generate creative, original content that deeply references the provided material."""
            else:
                # Default mode
                prompt = f"""You are an AI assistant with access to the following documents:

{context}

Based on the documents above, please answer the following question:
{user_question}

You can provide summaries, analysis, or generate new creative content based on the documents. If the answer requires synthesis or creative generation, feel free to create original work that references the material."""

            print("🤔 Sending query to Gemini...")
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"❌ Error querying Gemini: {e}")
            return f"Error: {str(e)}"