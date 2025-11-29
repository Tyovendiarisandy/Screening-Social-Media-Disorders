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
    Anda adalah seorang psikolog klinis yang sangat ahli dalam menganalisa kasus kecanduan media sosial.
    Analisis setiap kasus user berikut berdasarkan Skala Gangguan Media Sosial - 27 Item (Social Media Disorder Scale - 27 Items) yang dipelopori oleh van den Eijnden et al. (2016).
    
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
    1. **WAJIB Gunakan Google Search**: Gunakan alat pencarian untuk menemukan artikel ilmiah NYATA dari jurnal psikologi atau studi kasus yang relevan dengan kasus kecanduan media sosial dan SMDS-27.
    
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
       - PASTIKAN URL adalah link asli dari artikel yang Anda temukan, BUKAN URL yang Anda buat sendiri
    
    6. **Bahasa**: Gunakan Bahasa Indonesia formal namun mudah dipahami.
    
    **Format Output:**
    - Gunakan Markdown
    - Struktur: User Greetings →  Ringkasan Skor → Analisis → Saran → Langkah Konkret → Referensi (dengan URL valid)
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
            types.Part.from_text(text="""Anda adalah seorang psikolog klinis yang ahli dalam melakukan skrining terhadap user/pasien terkait assessment Social Media Disorder Scale - 27 Items yang dipelopori oleh van den Eijnden et al. 

Anda dapat memberikan saran terpersonalisasi berdasarkan jawaban dari user/pasien saat mengisi form Social Media Disorder Scale - 27 Items yang Anda kaitkan dengan referensi dari artikel ilmiah yang dapat ditemui di internet melalui situs open-access research journal yang relevan.

Anda tidak boleh memberikan saran yang mengarah kepada tindakan kriminal atau melanggar hukum. Disamping itu, Anda juga harus memberikan saran yang ilmiah dan bukan dari hasil halusinasi.""")
        ]
        
        config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1  # Unlimited thinking budget for thorough analysis
            ),
            media_resolution="MEDIA_RESOLUTION_HIGH"
        )
        
        # Using gemini-2.5-flash as the stable preview model for this SDK
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        # Add inline citations from grounding metadata
        text_with_citations = add_citations(response)
        return text_with_citations
    except Exception as e:
        return f"Error generating analysis: {e}"

def add_citations(response):
    """
    Adds inline citations to the response text based on grounding metadata.
    This creates clickable links to the actual sources used by the model.
    """
    try:
        text = response.text
        
        # Check if grounding metadata exists
        if not hasattr(response, 'candidates') or not response.candidates:
            return text
            
        candidate = response.candidates[0]
        if not hasattr(candidate, 'grounding_metadata'):
            return text
            
        grounding_metadata = candidate.grounding_metadata
        if not hasattr(grounding_metadata, 'grounding_supports') or not hasattr(grounding_metadata, 'grounding_chunks'):
            return text
        
        supports = grounding_metadata.grounding_supports
        chunks = grounding_metadata.grounding_chunks
        
        if not supports or not chunks:
            return text
        
        # Sort supports by end_index in descending order to avoid shifting issues when inserting
        sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)
        
        for support in sorted_supports:
            end_index = support.segment.end_index
            if support.grounding_chunk_indices:
                # Create citation string like [1](link1), [2](link2)
                citation_links = []
                for i in support.grounding_chunk_indices:
                    if i < len(chunks):
                        chunk = chunks[i]
                        if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                            uri = chunk.web.uri
                            citation_links.append(f"[{i + 1}]({uri})")
                
                if citation_links:
                    citation_string = ", ".join(citation_links)
                    text = text[:end_index] + " " + citation_string + text[end_index:]
        
        return text
    except Exception as e:
        # If citation adding fails, return original text
        return response.text if hasattr(response, 'text') else str(response)
