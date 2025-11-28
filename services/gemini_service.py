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
    1. **WAJIB Gunakan Google Search**: Gunakan alat pencarian untuk menemukan artikel ilmiah NYATA dari jurnal psikologi atau studi kasus yang relevan dengan kecanduan media sosial dan SMDS-27.
    
    2. **Dasar Ilmiah**: Analisis HARUS berdasarkan temuan dari artikel yang Anda temukan melalui pencarian. JANGAN membuat referensi fiktif.
    
    3. **Saran Dipersonalisasi**: Berikan saran khusus sesuai profil pengguna (usia, pekerjaan) dan area skor tinggi mereka.
    
    4. **Langkah Konkret**: Berikan tindakan spesifik yang dapat dilakukan segera.
    
    5. **SITASI DENGAN URL VALID**:
       - WAJIB sertakan bagian "Referensi" di akhir analisis
       - Untuk SETIAP artikel yang Anda kutip, tuliskan:
         * Judul lengkap artikel
         * Nama penulis dan tahun
         * URL lengkap yang dapat diklik (harus berupa link NYATA dari hasil pencarian)
       - Format: [Judul Artikel](URL_lengkap) - Penulis, Tahun
       - Minimal 3-5 referensi dengan URL valid
       - PERINGATAN KERAS: PASTIKAN URL adalah link asli dari artikel yang Anda temukan, BUKAN URL yang Anda buat sendiri
    
    6. **Bahasa**: Gunakan Bahasa Indonesia formal namun mudah dipahami.
    
    **Format Output:**
    - Gunakan Markdown
    - Struktur: Ringkasan Skor → Analisis → Saran Terpersonalisasi → Langkah Konkret → Referensi (dengan URL valid bisa diakses dan sesuai artikel ilmiah yang dirujuk)
    """
    
    try:
        # Configure Tools: Google Search and URL Context
        # Using the new google-genai SDK types
        tools = [
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(url_context=types.UrlContext())
        ]
        
        # System instruction to guide the model's behavior
        system_instruction = [
            types.Part.from_text(text="""You are a clinical psychologist who is highly skilled in screening users/patients using the 27-item Social Media Disorder Scale assessment pioneered by Van den Eijnden, Lemmens, & Valkenburg (2016). 

You can provide personalized advice based on the user/patient's responses when completing the Social Media Disorder Scale - 27 Items (SMDS-27) form, which you can link to references from scientific articles found online through relevant open-access research journals related to the user's case.


IMPORTANT NOTES (MUST BE STRICTLY ADHERED TO):

1. You must not provide advice that leads to criminal or illegal actions.

3. You must also provide scientific advice by including valid URLs from the scientific articles you cite and use in your analysis. 

3. Avoid hallucinations when responding to users.

4. If you do not understand the actual condition of the user based on the results of this SMDS-27 assessment, then state that you cannot provide relevant analysis and advice based on the user's condition.

5. Always respond in Indonesian.""")
        ]
        
        config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1  # Unlimited thinking budget for thorough analysis
            ),
            media_resolution="MEDIA_RESOLUTION_HIGH"
        )
        
        # Using gemini-2.5-flash-exp as the stable preview model for this SDK
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        return response.text
    except Exception as e:
        return f"Error generating analysis: {e}"
