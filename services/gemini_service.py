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
    Analisis dengan Thinking Mode + Inline Citations Only (Tanpa Footer Referensi).
    """
    client = get_gemini_client()
    if not client:
        return "Error: Konfigurasi Gemini gagal."
        
    total_score = sum(responses.values())
    
    # Prompt
    prompt = f"""
    Anda adalah **Psikolog Klinis & Peneliti Akademik** yang memiliki spesialisasi dalam kasus Social Media Disorder.
    
    **TUGAS:**
    Analisis hasil skrining user berdasarkan hasil skrining menggunakan "Social Media Disorder Scale (SMDS-27)".
    
    **DATA USER:**
    - Nama/Alias: {profile_data.get('alias')}
    - Pekerjaan: {profile_data.get('occupation')}
    - Usia: {profile_data.get('age')}
    - SKOR TOTAL: {total_score} (Range: 27-135)
    
    **INSTRUKSI BERPIKIR (CHAIN OF THOUGHT):**
    1.  Cari literatur terbaru tentang cutoff score SMDS-27 lewat Google Search.
    2.  Analisis korelasi antara faktor pekerjaan '{profile_data.get('occupation')}' dan lain-lain yang relevan dengan risiko kecanduan.
    3.  Tentukan 3 rekomendasi taktis.
    
    **ATURAN OUTPUT:**
    - Jelaskan temuan Anda dengan bahasa Indonesia formal & empatik.
    - **PENTING:** JANGAN menulis daftar pustaka atau URL manual. Cukup tulis narasi analisisnya. Sistem akan otomatis membuat teks Anda menjadi link yang bisa diklik.
    """
    
 try:
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        config = types.GenerateContentConfig(
            tools=tools,
            temperature=0.2,
            media_resolution="MEDIA_RESOLUTION_HIGH",
            
            # Thinking Mode aktif
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
        
        # Proses Penyuntikan Link
        return inject_citations_and_format(response)

    except Exception as e:
        return f"""
        **Terjadi Kesalahan Analisis:**
        {str(e)}
        """

def inject_citations_and_format(response):
    """
    Hanya menyuntikkan link ke dalam paragraf (Inline).
    Tidak lagi membuat daftar pustaka di bawah.
    """
    text = response.text
    
    # Validasi output model
    if not hasattr(response, 'candidates') or not response.candidates:
        return text

    candidate = response.candidates[0]
    
    # Cek Metadata Grounding
    if not hasattr(candidate, 'grounding_metadata') or not candidate.grounding_metadata:
        return text 

    metadata = candidate.grounding_metadata
    chunks = metadata.grounding_chunks # Sumber (Web URL)
    supports = metadata.grounding_supports # Pemetaan (Kalimat -> Sumber)
    
    if not chunks or not supports:
        return text

    # --- LANGKAH: INJEKSI SITASI INLINE ---
    # Sortir dari belakang ke depan agar indeks karakter tidak bergeser
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)
    
    for support in sorted_supports:
        indices = support.grounding_chunk_indices
        if indices:
            idx = indices[0] # Ambil sumber pertama
            if idx < len(chunks):
                chunk = chunks[idx]
                if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                    # Format: **[[Sumber]](URL)**
                    # Teks "Sumber" atau Angka akan menjadi Hyperlink langsung
                    citation_mark = f" **[[Sumber]]( {chunk.web.uri} )**"
                    
                    insert_pos = support.segment.end_index
                    # Sisipkan link ke dalam teks asli
                    text = text[:insert_pos] + citation_mark + text[insert_pos:]

    # --- Disclaimer Tetap Ada (Penting untuk Safety) ---
    disclaimer = """
    \n\n---
    *Disclaimer: Analisis ini dihasilkan oleh AI (Gemini) dengan verifikasi data via Google Search. Klik pada label **[[Sumber]]** di dalam teks untuk membaca artikel aslinya.*
    """
    
    return text + disclaimer
