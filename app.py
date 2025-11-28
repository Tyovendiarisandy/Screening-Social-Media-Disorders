import streamlit as st
from services.sheets_service import store_response
from services.gemini_service import analyze_response

st.set_page_config(page_title="Skrining SMDS-27", page_icon="🧠", layout="wide")

def main():
    st.title("🧠 Skrining Skala Gangguan Media Sosial (SMDS-27)")
    st.markdown("""
    Alat ini memungkinkan Anda untuk melakukan skrining mandiri terhadap kecanduan media sosial menggunakan instrumen standar SMDS-27.
    Jawaban Anda akan dianalisis untuk memberikan wawasan yang dipersonalisasi dan didukung secara ilmiah.
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
        "1. Selama setahun terakhir, apakah Anda sering merasa sulit untuk tidak melihat pesan di media sosial ketika sedang melakukan hal lain (misalnya, tugas sekolah/kuliah/kerja)?",
        "2. Selama setahun terakhir, apakah Anda sering merasa tidak bisa memikirkan hal lain selain saat di mana Anda bisa menggunakan media sosial lagi?",
        "3. Selama setahun terakhir, apakah Anda sering duduk menunggu sampai sesuatu terjadi lagi di media sosial?",
        
        # Tolerance
        "4. Selama setahun terakhir, apakah Anda sering merasa tidak puas karena ingin menghabiskan lebih banyak waktu di media sosial?",
        "5. Selama setahun terakhir, apakah Anda sering merasa perlu menghabiskan waktu lebih banyak di media sosial untuk mendapatkan perasaan puas yang sama?",
        "6. Selama setahun terakhir, apakah Anda sering mengalami perasaan puas dari menggunakan media sosial hanya bertahan sebentar dan Anda ingin segera menggunakannya lagi?",
        
        # Withdrawal
        "7. Selama setahun terakhir, apakah Anda sering merasa buruk ketika tidak bisa menggunakan media sosial?",
        "8. Selama setahun terakhir, apakah Anda sering merasa gelisah, jengkel, atau tidak bahagia ketika tidak bisa menggunakan media sosial?",
        "9. Selama setahun terakhir, apakah Anda sering mengalami dorongan kuat untuk menggunakan media sosial ketika Anda tidak bisa melakukannya?",
        
        # Persistence
        "10. Selama setahun terakhir, apakah Anda pernah mencoba mengurangi waktu bermain media sosial, tetapi gagal?",
        "11. Selama setahun terakhir, apakah Anda sering gagal mengurangi penggunaan media sosial meskipun orang lain menyuruh Anda menguranginya?",
        "12. Selama setahun terakhir, apakah Anda sering merasa sulit untuk mengurangi penggunaan media sosial, bahkan ketika Anda sangat ingin melakukannya?",
        
        # Displacement
        "13. Selama setahun terakhir, apakah Anda sering mengabaikan aktivitas lain (misalnya, hobi, olahraga, tugas) karena ingin menggunakan media sosial?",
        "14. Selama setahun terakhir, apakah Anda sering menghabiskan lebih sedikit waktu untuk kegiatan penting karena lebih memilih menggunakan media sosial?",
        "15. Selama setahun terakhir, apakah Anda sering memilih menggunakan media sosial daripada bertemu teman atau melakukan aktivitas lain?",
        
        # Problems
        "16. Selama setahun terakhir, apakah Anda sering bertengkar dengan orang lain karena penggunaan media sosial Anda?",
        "17. Selama setahun terakhir, apakah Anda sering mengalami masalah di sekolah, tempat kerja, atau dengan teman/keluarga karena penggunaan media sosial Anda?",
        "18. Selama setahun terakhir, apakah Anda sering merasakan konsekuensi negatif (misalnya, nilai buruk, teguran) akibat penggunaan media sosial Anda?",
        
        # Deception
        "19. Selama setahun terakhir, apakah Anda sering berbohong kepada orang tua atau teman tentang jumlah waktu yang Anda habiskan di media sosial?",
        "20. Selama setahun terakhir, apakah Anda sering menyembunyikan berapa banyak waktu yang Anda habiskan di media sosial dari orang lain?",
        "21. Selama setahun terakhir, apakah Anda sering meremehkan penggunaan media sosial Anda untuk menghindari kritik dari orang lain?",
        
        # Escape
        "22. Selama setahun terakhir, apakah Anda sering menggunakan media sosial untuk melarikan diri dari perasaan negatif?",
        "23. Selama setahun terakhir, apakah Anda sering menggunakan media sosial untuk melupakan masalah pribadi atau meredakan perasaan negatif seperti rasa bersalah atau kecemasan?",
        "24. Selama setahun terakhir, apakah Anda sering beralih ke media sosial ketika merasa sedih, cemas, atau bosan?",
        
        # Conflict
        "25. Selama setahun terakhir, apakah Anda mengalami konflik serius dengan orang tua, saudara (teman, pasangan, dll.) karena penggunaan media sosial Anda?",
        "26. Selama setahun terakhir, apakah Anda sering membahayakan hubungan penting karena penggunaan media sosial Anda?",
        "27. Selama setahun terakhir, apakah Anda sering membahayakan peluang pendidikan atau karier karena penggunaan media sosial Anda?"
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
            
        submitted = st.form_submit_button("Kirim & Analisis")
        
        if submitted:
            st.session_state.responses = responses
            st.session_state.step = 3
            st.rerun()

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

if __name__ == "__main__":
    main()
