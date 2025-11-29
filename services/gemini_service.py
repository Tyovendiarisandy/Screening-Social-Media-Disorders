from google import genai
from google.genai import types
import streamlit as st
import re

def get_gemini_client():
    try:
        # Pastikan API Key ada di .streamlit/secrets.toml
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None

def analyze_response(profile_data, responses):
    """
    Menganalisis hasil skrining menggunakan Gemini 2.5 Flash
    dengan fitur Thinking (CoT) maksimal dan Grounding Google Search.
    """
    client = get_gemini_client()
    if not client:
        return "Error: Konfigurasi Gemini gagal."
        
    total_score = sum(responses.values())
    
    # Prompt dirancang untuk memicu Deep Reasoning sebelum menjawab
    prompt = f"""
    Anda adalah **Psikolog Klinis Senior & Peneliti Cyberpsychology yang sangat ahli dalam menganalisis kasus kecanduan media sosial**.
    
    **TUGAS:**
    Lakukan analisis mendalam terhadap hasil skrining "Social Media Disorder Scale (SMDS-27)".
    
    **PROFIL SUBJEK:**
    - Nama/Alias: {profile_data.get('alias')}
    - Pekerjaan: {profile_data.get('occupation')}
    - Usia: {profile_data.get('age')}
    - Skor Total: {total_score} (Range: 27-135)
    
    **RESPON PER ITEM:**
    {responses}

    **INSTRUKSI BERPIKIR (CHAIN OF THOUGHT):**
    Gunakan kapabilitas berpikir Anda untuk:
    1.  Mencari standar *cutoff* klinis terbaru untuk SMDS-27 lewat Google Search.
    2.  Mengevaluasi korelasi spesifik antara pekerjaan '{profile_data.get('occupation')}' dengan risiko kecanduan digital.
    3.  Memverifikasi validitas jurnal yang ditemukan sebelum mengutipnya.
    
    **OUTPUT FINAL (UNTUK USER):**
    -   **Analisis Klinis:** Jelaskan arti skor secara ilmiah.
    -   **Dampak Spesifik:** Bagaimana skor ini mempengaruhi kinerja {profile_data.get('occupation')}.
    -   **Rekomendasi:** 3 langkah taktis dan terukur.
    -   **Validasi:** Pastikan semua klaim medis memiliki rujukan.
    """
    
    try:
        # 1. Konfigurasi Tools (Google Search)
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        # 2. System Instruction (Memperkuat Persona)
        sys_instruct = "Anda adalah AI Clinical Decision Support System yang mengutamakan Evidence-Based Practice."

        # 3. KONFIGURASI POWERFUL (Thinking + High Res)
        config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=sys_instruct,
            temperature=0.2, # Rendah agar fokus pada fakta, bukan kreatifitas
            
            # FITUR THINKING (CoT)
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1, # -1 = Unlimited/Auto budget untuk berpikir maksimal
                include_thoughts=False # False = Kita hanya ingin hasil akhirnya, proses berpikir di backend
            ),
            
            # RESOLUSI TINGGI
            media_resolution="MEDIA_RESOLUTION_HIGH",
            
            response_modalities=["TEXT"]
        )
        
        # 4. Eksekusi Model
        # Pastikan menggunakan nama model yang tepat.
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        # 5. Post-Processing (Pembersihan Link 404 & Formatting)
        return process_and_validate_output(response)

    except Exception as e:
        # Fallback error handling yang informatif
        return f"""
        **Terjadi Kesalahan Teknis:**
        {str(e)}
        
        *Saran: Jika error berkaitan dengan 'ThinkingConfig' atau '400', kemungkinan model 'gemini-2.5-flash' di akun Anda belum mendukung fitur Thinking secara penuh. Coba hapus parameter thinking_config atau ganti model ke varian eksperimental.*
        """

def process_and_validate_output(response):
    """
    Membersihkan link redirect Google dan menyusun referensi valid.
    """
    text = response.text
    
    # Hapus link markdown yang mengandung google redirect (Penyebab Error 404)
    # Mengubah [Teks](https://google.com/redirect...) menjadi **Teks**
    text = re.sub(r'\[(.*?)\]\(https?:\/\/.*?google\.com\/grounding-api-redirect.*?\)', r'**\1**', text)
    
    # Ambil Metadata Grounding yang Valid dari Response Object
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
                        
                        # Filter URL sampah
                        if "grounding-api-redirect" not in uri and "google.com" not in uri:
                            valid_sources.append((title, uri))

    # Tambahkan Disclaimer
    disclaimer = "\n\n---\n*Disclaimer: Analisis ini dibantu oleh AI dengan referensi jurnal daring. Bukan pengganti diagnosis medis profesional.*"

    # Susun Bagian Referensi
    if valid_sources:
        refs = "\n\n### 📚 Referensi Ilmiah Terverifikasi\n"
        unique_sources = list(set(valid_sources))
        
        for i, (title, uri) in enumerate(unique_sources, 1):
            refs += f"{i}. [{title}]({uri})\n"
        
        return text + refs + disclaimer
    else:
        return text + disclaimer
