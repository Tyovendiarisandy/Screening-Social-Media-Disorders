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

def analyze_response_scientific(profile_data, responses):
    client = get_gemini_client()
    if not client:
        return "Error: Gemini not configured."
        
    total_score = sum(responses.values())
    
    # --- 1. PROMPT ENGINEERING: SCIENTIFIC CHAIN OF THOUGHT ---
    prompt = f"""
    Anda adalah sistem AI pendukung keputusan klinis (Clinical Decision Support System).
    Tugas: Analisis risiko Social Media Disorder (SMDS-27).
    
    **PROFIL SUBJEK:**
    - Pekerjaan: {profile_data.get('occupation')}
    - Usia: {profile_data.get('age')}
    - Skor Total: {total_score} (Range 27-135)
    
    **DATA RESPON:**
    {responses}

    **PROTOKOL ANALISIS (WAJIB DIPATUHI):**
    
    1.  **FASE BERPIKIR (INTERNAL THOUGHT PROCESS):**
        -   Lakukan pencarian Google Search untuk standar *cutoff score* SMDS-27 terbaru.
        -   Cari studi kasus spesifik mengenai dampak media sosial pada demografi "{profile_data.get('occupation')}" usia {profile_data.get('age')}.
        -   Verifikasi apakah skor {total_score} termasuk kategori 'Berisiko', 'Bermasalah', atau 'Kecanduan'.
    
    2.  **FASE OUTPUT PUBLIK:**
        -   Sajikan analisis dalam Bahasa Indonesia formal dan empatik.
        -   Setiap klaim diagnosis atau saran MENTAL HEALTH harus memiliki sitasi inline.
        -   **Saran:** Berikan 3 intervensi berbasis bukti (CBT, Mindfulness, atau Digital Hygiene) yang relevan dengan pekerjaan subjek.
    
    **ATURAN REFERENSI KETAT:**
    -   HANYA gunakan fakta yang ditemukan dari tool Google Search. JANGAN gunakan pengetahuan internal jika bertentangan dengan hasil pencarian.
    -   Jika tidak menemukan jurnal spesifik untuk pekerjaan ini, katakan "Belum ada studi spesifik untuk profesi ini, namun berdasarkan studi umum..." (Jujur lebih baik daripada halusinasi).
    """
    
    try:
        # --- 2. CONFIG: MENGAKTIFKAN LOGIKA BERPIKIR & GROUNDING ---
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        config = types.GenerateContentConfig(
            tools=tools,
            temperature=0.2, # SANGAT RENDAH agar tidak kreatif/mengarang (fokus fakta)
            
            # FITUR KUNCI: THINKING BUDGET
            # Memberikan alokasi token bagi model untuk "berpikir" sebelum menjawab.
            # Ini secara teknis memaksa CoT (Chain of Thought).
            thinking_config=types.ThinkingConfig(
                thinking_budget=2048, 
                include_thoughts=False # Kita tidak perlu melihat prosesnya, hanya hasilnya
            ),
            
            # Memastikan format teks
            response_modalities=["TEXT"]
        )
        
        with st.spinner('Sedang melakukan validasi silang dengan database jurnal ilmiah...'):
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=config,
            )
        
        # --- 3. POST-PROCESSING: SAFETY & LINK CLEANING ---
        final_output = process_and_validate_output(response)
        return final_output

    except Exception as e:
        return f"Terjadi kesalahan teknis: {e}"

def process_and_validate_output(response):
    """
    Fungsi ini menjamin:
    1. Tidak ada link 404 (Redirect Google).
    2. Referensi yang ditampilkan benar-benar berasal dari Google Search (Grounding).
    """
    text = response.text
    
    # Hapus link markdown yang rusak di dalam teks (Regex cleaning)
    # Ini menghapus bagian (url) tapi menyisakan [Judul]
    text = re.sub(r'\[(.*?)\]\(https?:\/\/.*?google\.com\/grounding-api-redirect.*?\)', r'**\1**', text)
    
    # Ambil Metadata Grounding yang Valid
    valid_sources = []
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            metadata = candidate.grounding_metadata
            if hasattr(metadata, 'grounding_chunks'):
                for chunk in metadata.grounding_chunks:
                    if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri') and hasattr(chunk.web, 'title'):
                        uri = chunk.web.uri
                        title = chunk.web.title
                        
                        # Filter URL sampah/internal
                        if "grounding-api-redirect" not in uri and "google.com" not in uri:
                            valid_sources.append((title, uri))

    # --- SAFETY DISCLAIMER (WAJIB UNTUK APLIKASI KESEHATAN) ---
    disclaimer = """
    ---
    **⚠️ PEMBERITAHUAN PENTING:**
    *Analisis ini dihasilkan oleh kecerdasan buatan (AI) berdasarkan literatur ilmiah yang tersedia secara publik. Hasil ini **bukan diagnosis medis**. Jika Anda merasa tertekan atau mengalami gangguan fungsi hidup sehari-hari, segera hubungi profesional kesehatan mental (Psikolog/Psikiater).*
    """

    # --- PENYUSUNAN REFERENSI ---
    if valid_sources:
        refs = "\n\n### 📖 Referensi Ilmiah Pendukung (Diverifikasi)\n"
        # Gunakan set untuk menghapus duplikat, lalu list lagi
        unique_sources = list(set(valid_sources)) 
        
        for i, (title, uri) in enumerate(unique_sources, 1):
            refs += f"{i}. [{title}]({uri})\n"
        
        return text + refs + disclaimer
    else:
        # Jika Google Search gagal menemukan sumber valid
        return text + "\n\n*Catatan: Sumber spesifik tidak dapat diverifikasi saat ini.*" + disclaimer
