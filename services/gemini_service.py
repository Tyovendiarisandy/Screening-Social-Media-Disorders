from google import genai
from google.genai import types
import streamlit as st
import re

# --- 1. SETUP CLIENT ---
def get_gemini_client():
    try:
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None

# --- 2. FUNGSI UTAMA DENGAN CACHING ---
@st.cache_data(show_spinner=False, ttl=3600) 
def analyze_response(profile_data, responses):
    """
    Analisis dengan Forced Grounding (Wajib Search) & Caching.
    """
    client = get_gemini_client()
    if not client:
        return "Error: Konfigurasi Gemini gagal."
        
    total_score = sum(responses.values())
    
    # Prompt
    prompt = f"""
    Anda adalah **Psikolog Klinis** yang ahli dalam melakukan skrining terhadap kasus kecanduan Social Media.
    
    **TUGAS:**
    Analisis hasil skrining user berdasarkan "Social Media Disorder Scale (SMDS-27)".
    
    **DATA USER:**
    - Nama/Alias: {profile_data.get('alias')}
    - Pekerjaan: {profile_data.get('occupation')}
    - Usia: {profile_data.get('age')}
    - SKOR TOTAL: {total_score} (Range: 27-135)
    
    **RESPON USER:**
    {responses}

    **INSTRUKSI:**
    1.  **WAJIB SEARCH:** Gunakan Google Search untuk validasi cutoff score dan risiko spesifik pekerjaan user.
    2.  **ANALISIS:** Berikan interpretasi skor, dampak pekerjaan, faktor lain yang berkaitan dan 3 saran taktis.
    3.  **FORMAT:** Narasi formal empatik. JANGAN tulis URL manual.
    """
    
    try:
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        # KONFIGURASI AGAR KONSISTEN
        config = types.GenerateContentConfig(
            tools=tools,
            temperature=0.2, # Sangat rendah agar jawaban stabil/konsisten
            media_resolution="MEDIA_RESOLUTION_HIGH",
            
            # MEMAKSA MODEL MENGGUNAKAN SEARCH (Grounding Wajib)
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY" # ANY = Wajib menggunakan salah satu tools (Search)
                )
            ),
            
            # Thinking Config (Opsional, matikan jika sering error/lambat di HP)
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1, 
                include_thoughts=False 
            )
        )
        
        # Eksekusi Model
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        # Format Hasil
        return inject_citations_and_format(response)

    except Exception as e:
        return f"Terjadi kesalahan teknis: {str(e)}"

# --- 3. FUNGSI FORMATTING ---
def inject_citations_and_format(response):
    text = response.text
    
    if not hasattr(response, 'candidates') or not response.candidates:
        return text

    candidate = response.candidates[0]
    
    # Validasi Metadata
    if not hasattr(candidate, 'grounding_metadata') or not candidate.grounding_metadata:
        return text 

    metadata = candidate.grounding_metadata
    chunks = metadata.grounding_chunks 
    supports = metadata.grounding_supports 
    
    if not chunks or not supports:
        return text

    # Injeksi Link
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)
    
    for support in sorted_supports:
        indices = support.grounding_chunk_indices
        if indices:
            idx = indices[0]
            if idx < len(chunks):
                chunk = chunks[idx]
                if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                    citation_mark = f" **[[Sumber]]({chunk.web.uri})**"
                    insert_pos = support.segment.end_index
                    text = text[:insert_pos] + citation_mark + text[insert_pos:]

    disclaimer = """
    \n\n---
    *Disclaimer: Analisis ini dihasilkan oleh AI (Gemini) dengan verifikasi data via Google Search*
    """
    
    return text + disclaimer
