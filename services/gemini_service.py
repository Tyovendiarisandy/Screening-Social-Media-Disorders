from google import genai
from google.genai import types
import streamlit as st

def get_gemini_client():
    """Configures and returns the Gemini Client."""
    try:
        # Pastikan API Key tersimpan di st.secrets
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None

def analyze_response(profile_data, responses):
    """
    Analyzes the user response using Gemini with Google Search grounding.
    """
    client = get_gemini_client()
    if not client:
        return "Error: Gemini not configured."
        
    # Hitung skor total
    total_score = sum(responses.values())
    
    # --- STRATEGI PROMPT BARU ---
    # Kita menggunakan teknik "Chain of Thought" yang dipandu (Guided Chain of Thought)
    # untuk memaksa model mencari referensi dulu sebelum menjawab.
    
    prompt = f"""
    Bertindaklah sebagai **Psikolog Klinis Senior** dan **Peneliti Akademik** yang berspesialisasi dalam *Cyberpsychology* dan gangguan perilaku adiksi (Addictive Behaviors).
    
    Tugas Anda adalah menganalisis hasil skrining **Social Media Disorder Scale (SMDS-27)** dari pengguna berikut secara mendalam, ilmiah, namun tetap empatik.

    **DATA PENGGUNA:**
    - Alias: {profile_data.get('alias')}
    - Usia: {profile_data.get('age')}
    - Jenis Kelamin: {profile_data.get('gender')}
    - Pekerjaan: {profile_data.get('occupation')}
    - **SKOR TOTAL:** {total_score} (Skala 27-135)
    
    **DETAIL JAWABAN (1-5):**
    {responses}

    ---
    **INSTRUKSI EKSEKUSI (WAJIB DIKERJAKAN SECARA BERURUTAN):**

    **LANGKAH 1: RISET MENDALAM (Internal Process)**
    Gunakan *Google Search Tool* untuk mencari informasi terkini (utamakan 5 tahun terakhir) tentang:
    1. "Social Media Disorder Scale interpretation cutoff scores". Cari tahu apakah skor {total_score} tergolong rendah, sedang, atau tinggi berdasarkan literatur.
    2. Dampak kecanduan media sosial spesifik pada demografi: **{profile_data.get('occupation')}** usia **{profile_data.get('age')}**.
    3. Temukan minimal 2 jurnal ilmiah atau artikel psikologi kredibel (misal: dari ScienceDirect, PubMed, Jurnal Psikologi Universitas, atau WebMD/Psychology Today yang terverifikasi) yang relevan dengan kasus ini.

    **LANGKAH 2: PENYUSUNAN LAPORAN (Output untuk User)**
    Buat laporan analisis dengan format berikut. Gunakan Bahasa Indonesia yang profesional, hangat, dan mudah dimengerti.

    **STRUKTUR LAPORAN:**

    1.  **Interpretasi Klinis & Validasi Ilmiah**
        *   Jelaskan makna skor {total_score} secara spesifik. Apakah ini mengindikasikan gangguan?
        *   **KEHARUSAN:** Anda WAJIB menyertakan referensi ilmiah di sini. Contoh kalimat: *"Berdasarkan studi dari [Nama Peneliti/Jurnal](URL_ASLI_DARI_SEARCH), skor di atas X menandakan..."* atau *"Penelitian mengenai pekerja [Pekerjaan] menunjukkan bahwa..."*.
        *   Gunakan data fakta yang Anda temukan di Langkah 1 untuk memvalidasi analisis Anda.

    2.  **Analisis Pola Jawaban**
        *   Lihat item dengan nilai '4' atau '5'. Jelaskan implikasi psikologisnya. Hubungkan dengan konsep seperti *FOMO*, *Escapism*, atau *Social Comparison*.

    3.  **Rekomendasi Berbasis Bukti (Evidence-Based Advice)**
        *   Berikan 3 saran konkret yang *actionable*.
        *   Setiap saran harus didukung alasan ilmiah. (Contoh: *"Lakukan teknik 'Digital Detox' selama 30 menit sebelum tidur, karena cahaya biru dapat mengganggu ritme sirkadian (Sumber: [Jurnal X](URL))."*)

    4.  **Daftar Pustaka & Bacaan Lanjutan**
        *   **PENTING:** List semua artikel/jurnal yang Anda gunakan sebagai dasar analisis di atas.
        *   Format: **Judul Artikel** - [Baca Sumber Asli di sini](URL_VALID_DARI_GOOGLE_SEARCH).
        *   Pastikan URL dapat diklik dan valid (bukan URL halusinasi).

    **CONSTRAINT/BATASAN:**
    *   JANGAN mengarang referensi. Jika tidak menemukan jurnal spesifik untuk pekerjaan user, gunakan riset umum tentang "adult social media usage" namun tetap beri disclaimer.
    *   Pastikan nada bicara tidak menghakimi (non-judgmental).
    *   Semua klaim medis/psikologis harus ada sitasinya (inline link Markdown).
    """
    
    try:
        # Konfigurasi Tools
        tools = [
            types.Tool(google_search=types.GoogleSearch())
        ]
        
        # System Instruction untuk persona yang kuat
        system_instruction = [
            types.Part.from_text(text="""Anda adalah AI Psikolog berbasis bukti (Evidence-Based AI Psychologist). 
            Prioritas utama Anda adalah akurasi ilmiah dan keamanan pengguna. 
            Setiap kali Anda membuat klaim tentang diagnosis atau dampak kesehatan mental, 
            Anda harus memverifikasinya melalui Google Search dan memberikan tautan sumbernya.""")
        ]
        
        config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_instruction,
            # Thinking config tetap bagus untuk analisis mendalam
            thinking_config=types.ThinkingConfig(
                thinking_budget=1024 # Memberi budget token untuk "berpikir" sebelum menjawab
            ), 
            response_modalities=["TEXT"], # Pastikan output teks
        )
        
        # Eksekusi Model
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=config,
        )
        
        # Karena kita sudah meminta model memformat Markdown Link di prompt,
        # kita bisa langsung mengambil text-nya.
        # Namun, kita tetap ambil grounding metadata jika model menaruhnya terpisah.
        
        return format_output_with_grounding(response)

    except Exception as e:
        return f"Terjadi kesalahan saat menganalisis: {e}"

def format_output_with_grounding(response):
    """
    Menggabungkan teks respons dengan metadata grounding jika link tidak ter-render sempurna di teks utama.
    """
    text = response.text
    
    # Cek apakah ada grounding metadata (sumber yang ditemukan Google Search)
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            metadata = candidate.grounding_metadata
            
            # Jika model sudah pintar membuat link di text (sesuai prompt), kita tidak perlu menumpuknya.
            # Namun untuk keamanan (fallback), kita bisa list sumber di bawah jika belum ada di teks.
            
            # Opsional: Menambahkan bagian "Sumber Terverifikasi Google" secara otomatis di bawah
            # jika Anda ingin memastikan user melihat sumbernya terlepas dari format teks model.
            
            sources_text = "\n\n---\n**Sumber Terverifikasi Sistem (Google Search):**\n"
            has_sources = False
            
            if hasattr(metadata, 'grounding_chunks'):
                for i, chunk in enumerate(metadata.grounding_chunks):
                    if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri') and hasattr(chunk.web, 'title'):
                        has_sources = True
                        sources_text += f"{i+1}. [{chunk.web.title}]({chunk.web.uri})\n"
            
            # Hanya tempel jika ada sumber dan teks belum mengandung bagian "Daftar Pustaka" (untuk menghindari duplikasi)
            if has_sources and "Daftar Pustaka" not in text:
                text += sources_text
                
    return text
