from google import genai
from google.genai import types
import streamlit as st
import re

def get_gemini_client():
    try:
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None

def analyze_response(profile_data, responses):
    """
    Analisis dengan 3 Fitur Utama:
    1. Thinking Mode (CoT)
    2. Grounding (Google Search)
    3. Smart Citation Injection (Link Valid)
    """
    client = get_gemini_client()
    if not client:
        return "Error: Konfigurasi Gemini gagal."
        
    total_score = sum(responses.values())
    
    # Prompt Instruksi Tingkat Tinggi
    prompt = f"""
    Anda adalah **Psikolog Klinis & Peneliti Akademik**.
    
    **TUGAS:**
    Analisis hasil skrining "Social Media Disorder Scale (SMDS-27)".
    
    **DATA USER:**
    - Alias: {profile_data.get('alias')}
    - Pekerjaan: {profile_data.get('occupation')}
    - Usia: {profile_data.get('age')}
    - SKOR TOTAL: {total_score} (Range: 27-135)
    
    **JAWABAN DETIL:**
    {responses}

    **INSTRUKSI BERPIKIR (CHAIN OF THOUGHT):**
    1.  Cari literatur terbaru tentang cutoff score SMDS-27 lewat Google Search.
    2.  Analisis korelasi pekerjaan '{profile_data.get('occupation')}' dengan risiko kecanduan.
    3.  Tentukan 3 rekomendasi taktis.
    
    **ATURAN OUTPUT:**
    - Jelaskan temuan Anda dengan bahasa Indonesia formal & empatik.
    - JANGAN menulis URL/Link secara manual di dalam teks (biarkan sistem yang menyisipkannya).
    - Fokus pada analisis mendalam.
    """
    
    try:
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        config = types.GenerateContentConfig(
            tools=tools,
            temperature=0.2, # Rendah agar stabil
            media_resolution="MEDIA_RESOLUTION_HIGH",
            
            # --- MENGAKTIFKAN MODE THINKING (CoT) ---
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1, # Memberikan token untuk berpikir (Reasoning)
                include_thoughts=False # Hanya ambil hasil akhirnya
            )
        )
        
        # Eksekusi Model
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        # Proses Penyuntikan Link (Agar tidak ada link 404)
        return inject_citations_and_format(response)

    except Exception as e:
        # Fallback error handling
        return f"""
        **Terjadi Kesalahan Analisis:**
        {str(e)}
        
        *Tips: Jika muncul error '400' atau 'ThinkingConfig', kemungkinan akun Google AI Studio Anda belum mengaktifkan fitur Thinking untuk model Flash. Coba hapus parameter 'thinking_config' di kode.*
        """

def inject_citations_and_format(response):
    """
    Mengambil teks polos dan menyuntikkan link referensi asli
    tepat di kalimat yang relevan berdasarkan metadata grounding.
    """
    text = response.text
    
    # Validasi output model
    if not hasattr(response, 'candidates') or not response.candidates:
        return text

    candidate = response.candidates[0]
    
    # Cek Metadata Grounding
    if not hasattr(candidate, 'grounding_metadata') or not candidate.grounding_metadata:
        return text + "\n\n*(Analisis dilakukan berdasarkan logika klinis internal model tanpa query spesifik ke web saat ini.)*"

    metadata = candidate.grounding_metadata
    chunks = metadata.grounding_chunks # Sumber (Web URL)
    supports = metadata.grounding_supports # Pemetaan (Kalimat -> Sumber)
    
    if not chunks or not supports:
        return text

    # --- LANGKAH 1: INJEKSI SITASI INLINE ---
    # Sortir dari belakang ke depan agar indeks karakter tidak bergeser
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)
    
    for support in sorted_supports:
        indices = support.grounding_chunk_indices
        if indices:
            idx = indices[0] # Ambil sumber pertama
            if idx < len(chunks):
                chunk = chunks[idx]
                if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                    # Format: **[[Nomor]](URL)**
                    # Ini membuat angka kecil yang bisa diklik langsung ke sumber
                    citation_mark = f" **[[{idx + 1}]]({chunk.web.uri})**"
                    
                    insert_pos = support.segment.end_index
                    # Sisipkan link ke dalam teks asli
                    text = text[:insert_pos] + citation_mark + text[insert_pos:]

    # --- LANGKAH 2: FOOTER DAFTAR PUSTAKA ---
    unique_sources = {}
    
    for i, chunk in enumerate(chunks):
        if hasattr(chunk, 'web') and hasattr(chunk.web, 'title') and hasattr(chunk.web, 'uri'):
            title = chunk.web.title
            uri = chunk.web.uri
            # Filter link internal google (jaga-jaga)
            if "google.com/grounding-api-redirect" not in uri:
                unique_sources[i+1] = (title, uri)

    for idx, (title, uri) in unique_sources.items():
        footer += f"{idx}. **[{title}]({uri})**\n"

    disclaimer = """
    \n---
    *Disclaimer: Analisis ini menggunakan teknologi 'Reasoning AI' (Gemini) yang memverifikasi data melalui Google Search. 
    Klik angka di dalam teks (contoh: [[1]]) untuk membaca sumber aslinya.*
    """
    
    return text + footer + disclaimer
