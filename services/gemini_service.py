from google import genai
from google.genai import types
import streamlit as st

def get_gemini_client():
    """Configures and returns the Gemini Client."""
    try:
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None

def analyze_response(profile_data, responses):
    """
    Analyzes the user response using Gemini with Google Search grounding.
    Uses the new google-genai SDK.
    
    Args:
        profile_data (dict): User profile information.
        responses (dict): User answers to the questionnaire.
        
    Returns:
        str: The analysis text from Gemini.
    """
    client = get_gemini_client()
    if not client:
        return "Error: Gemini not configured."
        
    # Calculate score
    total_score = sum(responses.values())
    
    prompt = f"""
    Anda adalah seorang psikolog klinis yang memiliki spesialisasi dalam kecanduan media sosial.
    Analisis kasus berikut berdasarkan Social Media Disorder Scale - 27 Item (SMDS-27).
    
    **Profil Pengguna:**
    - Alias: {profile_data.get('alias')}
    - Usia: {profile_data.get('age')}
    - Jenis Kelamin: {profile_data.get('gender')}
    - Pekerjaan: {profile_data.get('occupation')}
    
    **Hasil Asesmen:**
    - Skor Total: {total_score} (Rentang: 27-135)
    - Jawaban Item (1=Sangat Tidak Setuju, 5=Sangat Setuju):
    {responses}
    
    **Persyaratan Analisis Ketat:**
    1. **Gunakan Google Search**: Anda WAJIB menggunakan alat Google Search untuk mencari artikel ilmiah terbaru dan relevan (jurnal psikologi, studi kasus) yang mendukung analisis Anda.
    2. **Dasar Ilmiah**: Berikan analisis berdasarkan temuan ilmiah yang Anda dapatkan dari pencarian tersebut.
    3. **Saran yang Dipersonalisasi**: Tawarkan saran khusus yang disesuaikan dengan profil pengguna dan area skor tinggi mereka.
    4. **Kesimpulan yang Dapat Ditindaklanjuti**: Berikan langkah-langkah konkret.
    5. **Sitasi Valid**: Sertakan judul artikel dan URL valid dari sumber ilmiah yang Anda temukan melalui Google Search.
    6. **Bahasa**: Gunakan Bahasa Indonesia yang formal namun mudah dipahami.
    
    Format output dengan jelas menggunakan Markdown.
    """
    
    try:
        # Configure Tools: Google Search and URL Context
        # Using the new google-genai SDK types
        tools = [
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(url_context=types.UrlContext())
        ]
        
        config = types.GenerateContentConfig(
            tools=tools
        )
        
        # Using gemini-2.5-flash
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        return response.text
    except Exception as e:
        return f"Error generating analysis: {e}"
