import google.generativeai as genai
import streamlit as st

def configure_gemini():
    """Configures the Gemini API."""
    try:
        api_key = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return False

def analyze_response(profile_data, responses):
    """
    Analyzes the user response using Gemini 1.5 Pro.
    
    Args:
        profile_data (dict): User profile information.
        responses (dict): User answers to the questionnaire.
        
    Returns:
        str: The analysis text from Gemini.
    """
    if not configure_gemini():
        return "Error: Gemini not configured."
        
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Calculate score (simple sum for context, though Gemini can do it too)
    total_score = sum(responses.values())
    
    prompt = f"""
    You are an expert psychologist specializing in social media addiction. 
    Analyze the following case based on the Social Media Disorder Scale - 27 Items (SMDS-27).
    
    **User Profile:**
    - Alias: {profile_data.get('alias')}
    - Age: {profile_data.get('age')}
    - Gender: {profile_data.get('gender')}
    - Occupation: {profile_data.get('occupation')}
    
    **Assessment Results:**
    - Total Score: {total_score} (Range: 27-135)
    - Item Responses (1=Strongly Disagree, 5=Strongly Agree):
    {responses}
    
    **Strict Analysis Requirements:**
    1. **Scientific Basis**: Provide an analysis based ONLY on relevant scientific articles and psychological frameworks regarding social media addiction.
    2. **Personalized Advice**: Offer specific advice tailored to the user's profile (age, occupation) and their specific high-scoring areas.
    3. **Actionable Conclusion**: Provide concrete, actionable steps the user can take immediately.
    4. **Citations**: You MUST include the URLs of the scientific articles you reference.
    
    Format the output clearly with Markdown.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating analysis: {e}"
