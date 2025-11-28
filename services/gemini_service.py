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
    Analyzes the user response using Gemini with Google Search grounding.
    
    Args:
        profile_data (dict): User profile information.
        responses (dict): User answers to the questionnaire.
        
    Returns:
        str: The analysis text from Gemini.
    """
    if not configure_gemini():
        return "Error: Gemini not configured."
        
    # Calculate score
    total_score = sum(responses.values())
    
    prompt = f"""
    Anda adalah seorang psikolog ahli yang berspesialisasi dalam kecanduan media sosial.
    Analisis kasus berikut berdasarkan Skala Gangguan Media Sosial - 27 Item (SMDS-27).
    
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
        # Use Gemini 1.5 Flash with Google Search Grounding
        # For google-generativeai SDK, the key is 'google_search_retrieval'
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        tools = [
            {'google_search_retrieval': {
                'dynamic_retrieval_config': {
                    'mode': 'dynamic',
                    'dynamic_threshold': 0.3,
                }
            }}
        ]
        
        response = model.generate_content(prompt, tools=tools)
        return response.text
    except Exception as e:
        return f"Error generating analysis: {e}"
