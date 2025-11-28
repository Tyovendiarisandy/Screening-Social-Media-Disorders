import streamlit as st
from services.gemini_service import analyze_response
from datetime import datetime

st.set_page_config(page_title="Skrining SMDS-27", page_icon="icon.jpg", layout="wide")

def main():
    # Display header image
    st.image("icon.jpg", use_container_width=True)
    
    st.title("🧠 Skrining Skala Gangguan Media Sosial (SMDS-27)")
    st.markdown("""
    Alat ini memungkinkan Anda untuk melakukan skrining mandiri terhadap kecanduan media sosial menggunakan instrumen standar SMDS-27.
    Jawaban Anda akan dianalisis untuk memberikan wawasan yang dipersonalisasi dan didukung secara ilmiah.
    """)
    
    # Disclaimer
    st.warning("""
    ⚠️ **DISCLAIMER PENTING**
    
    Aplikasi skrining ini berfungsi **hanya sebagai alat self-assessment** yang dibantu oleh kecerdasan buatan (AI). 
    
    - **Bukan merupakan diagnosis medis atau psikologis** terhadap kondisi Anda
    - Hasil analisis hanya bersifat **informasi pendamping** 
    - Jika diperlukan, gunakan hasil ini sebagai **bahan diskusi dengan profesional** (psikolog/konselor) untuk mendapatkan penanganan yang tepat
    - Untuk masalah kesehatan mental yang serius, segera konsultasikan dengan tenaga profesional berlisensi
    """)
    
    
    # Initialize session state for steps
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if st.session_state.step == 1:
        render_profile_form()
    elif st.session_state.step == 2:
        render_questionnaire()
    elif st.session_state.step == 3:
        render_results()

def render_profile_form():
    st.header("Langkah 1: Profil Pribadi")
    
    with st.form("profile_form"):
        alias = st.text_input("Nama Alias (Nama Samaran)")
        age = st.number_input("Usia", min_value=10, max_value=100, step=1)
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan", "Non-biner", "Tidak ingin menyebutkan"])
        occupation = st.text_input("Pekerjaan")
        
        submitted = st.form_submit_button("Lanjut")
        
        if submitted:
            if alias and occupation:
                st.session_state.profile = {
                    "alias": alias,
                    "age": age,
                    "gender": gender,
                    "occupation": occupation
                }
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Mohon isi semua kolom.")

# ... (render_questionnaire is already translated) ...

def render_results():
    st.header("Langkah 3: Hasil Analisis")
    
    with st.spinner("Menganalisis jawaban Anda..."):
        # 1. Store Data
        if 'stored' not in st.session_state:
            success = store_response(st.session_state.profile, st.session_state.responses)
            if success:
                st.success("Data berhasil disimpan.")
            else:
                st.warning("Gagal menyimpan data (periksa konfigurasi secrets). Melanjutkan analisis...")
            st.session_state.stored = True
            
        # 2. Analyze with Gemini
        if 'analysis' not in st.session_state:
            analysis = analyze_response(st.session_state.profile, st.session_state.responses)
            st.session_state.analysis = analysis
            
        st.markdown(st.session_state.analysis)
        
    if st.button("Mulai Ulang"):
        st.session_state.clear()
        st.rerun()

def render_questionnaire():
    st.header("Langkah 2: Kuesioner SMDS-27")
    st.info("Silakan jawab 27 pertanyaan berikut dengan jujur berdasarkan pengalaman Anda selama satu tahun terakhir.")
    
    questions = [
        # Preoccupation
        "1. Apakah Anda sering memikirkan tentang media sosial meskipun kamu tidak sedang menggunakannya?",
        "2. Apakah Anda sering merasa tidak sabar untuk segera menggunakan media sosial kembali?",
        "3. Apakah Anda sering berpikir tentang apa yang akan Anda lakukan atau lihat di media sosial nanti?",
        
        # Tolerance
        "4. Apakah Anda merasa perlu menggunakan media sosial lebih sering dari sebelumnya?",
        "5. Apakah Anda merasa perlu menghabiskan waktu lebih lama di media sosial untuk merasa puas?",
        "6. Apakah Anda merasa bahwa waktu yang kamu habiskan di media sosial saat ini terasa kurang cukup?",
        
        # Withdrawal
        "7. Apakah Anda merasa gelisah atau stres jika tidak bisa menggunakan media sosial?",
        "8. Apakah Anda menjadi mudah marah atau tersinggung ketika dilarang atau tidak bisa mengakses media sosial?",
        "9. Apakah Anda merasa sedih atau hampa jika tidak membuka media sosial dalam beberapa waktu?",
        
        # Persistence
        "10. Apakah Anda sudah mencoba mengurangi waktu bermain media sosial tetapi gagal?",
        "11. Apakah Anda sering berniat hanya membuka sebentar, tetapi malah menghabiskan waktu berjam-jam?",
        "12. Apakah Anda merasa tidak mampu menghentikan kebiasaan menggunakan media sosial meskipun kamu ingin?",
        
        # Displacement
        "13. Apakah Anda lebih memilih bermain media sosial daripada berkumpul/berinteraksi dengan teman atau keluarga secara langsung?",
        "14. Apakah Anda mengurangi waktu untuk melakukan hobi atau olahraga demi dapat bermain media sosial?",
        "15. Apakah Anda merasa dunia maya lebih menarik daripada kegiatan di dunia nyata?",
        
        # Problems
        "16. Apakah Anda sering menelantarkan tugas sekolah/pekerjaan karena asyik bermain media sosial?",
        "17. Apakah kualitas tidur Anda sering terganggu karena menggunakan media sosial hingga larut malam?",
        "18. Apakah Anda sering mengabaikan pekerjaan rumah atau kewajiban sehari-hari demi media sosial?",
        
        # Deception
        "19. Apakah Anda sering berbohong kepada orang tua atau teman tentang berapa lama Anda menggunakan media sosial?",
        "20. Apakah Anda pernah menggunakan media sosial secara diam-diam agar tidak ketahuan orang lain?",
        "21. Apakah Anda menyembunyikan fakta bahwa Anda sedang online dari orang-orang di sekitar Anda?",
        
        # Escape
        "22. Apakah Anda menggunakan media sosial untuk melupakan masalah pribadi?",
        "23. Apakah Anda sering menggunakan media sosial untuk menghilangkan perasaan sedih, cemas, atau bersalah?",
        "24. Apakah Anda bermain media sosial untuk menghindari memikirkan hal-hal yang tidak menyenangkan?",
        
        # Conflict
        "25. Apakah Anda sering bertengkar dengan orang tua, saudara, atau pasangan karena penggunaan media sosial?",
        "26. Apakah orang-orang di sekitar Anda sering mengeluh bahwa Anda terlalu banyak menggunakan media sosial?",
        "27. Apakah hubungan Anda dengan orang terdekat menjadi renggang karena Anda terlalu fokus pada media sosial?"
    ]
    
    with st.form("smds_form"):
        responses = {}
        
        for i, question in enumerate(questions):
            st.markdown(f"**{question}**")
            # Use a unique key for each slider
            responses[f"Q{i+1}"] = st.slider(
                "Jawaban Anda", 
                min_value=1, 
                max_value=5, 
                value=3, 
                key=f"q{i+1}",
                help="1=Sangat Tidak Setuju, 5=Sangat Setuju",
                label_visibility="collapsed"
            )
            st.divider()
            
        submitted = st.form_submit_button("Kirim & Analisis", type="primary")
        
        if submitted:
            st.toast("⏳ Mohon Tunggu Sebentar! Sistem sedang menganalisis jawaban Anda.", icon="⚙️")
            st.session_state.responses = responses
            st.session_state.step = 3
            st.rerun()

def render_results():
    st.header("Langkah 3: Hasil Analisis")
    
    with st.spinner("Menganalisis jawaban Anda..."):
        # Analyze with Gemini
        if 'analysis' not in st.session_state:
            analysis = analyze_response(st.session_state.profile, st.session_state.responses)
            st.session_state.analysis = analysis
            
        st.markdown(st.session_state.analysis)
    
    # Prepare download content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_score = sum(st.session_state.responses.values())
    
    download_content = f"""HASIL SKRINING SMDS-27
{'='*50}

Tanggal Asesmen: {timestamp}

PROFIL PENGGUNA:
- Nama Alias: {st.session_state.profile.get('alias')}
- Usia: {st.session_state.profile.get('age')}
- Jenis Kelamin: {st.session_state.profile.get('gender')}
- Pekerjaan: {st.session_state.profile.get('occupation')}

HASIL ASESMEN:
- Skor Total: {total_score} (Rentang: 27-135)

JAWABAN KUESIONER:
"""
    
    for i in range(1, 28):
        download_content += f"Q{i}: {st.session_state.responses.get(f'Q{i}', 'N/A')}\n"
    
    download_content += f"\n{'='*50}\nANALISIS:\n{'='*50}\n\n"
    download_content += st.session_state.analysis
    
    # Download button
    st.download_button(
        label="📥 Download Hasil Asesmen (TXT)",
        data=download_content,
        file_name=f"SMDS27_Hasil_{st.session_state.profile.get('alias')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    
    if st.button("Mulai Ulang"):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()
