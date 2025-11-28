import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import utility modules
from utils.smds_items import SMDS_27_ITEMS, LIKERT_SCALE, get_severity_category
from utils.google_sheets import GoogleSheetsManager
from utils.gemini_analysis import GeminiAnalyzer

# Page configuration
st.set_page_config(
    page_title="SMDS-27 Screening Tool",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #10B981;
    }
    .info-box {
        background-color: #EFF6FF;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F59E0B;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
        margin: 1rem 0;
    }
    .dimension-card {
        background-color: #F9FAFB;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'total_score' not in st.session_state:
        st.session_state.total_score = 0
    if 'dimension_scores' not in st.session_state:
        st.session_state.dimension_scores = {}
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None

def calculate_scores(responses):
    """Calculate total score and dimension scores"""
    total = sum(responses.values())
    
    # Calculate per dimension
    dimension_scores = {}
    for item in SMDS_27_ITEMS:
        dim = item['dimension']
        item_id = f"item_{item['id']}"
        
        if dim not in dimension_scores:
            dimension_scores[dim] = {'total': 0, 'count': 0}
        
        dimension_scores[dim]['total'] += responses.get(item_id, 0)
        dimension_scores[dim]['count'] += 1
    
    return total, dimension_scores

def render_progress_bar():
    """Render progress bar based on current step"""
    progress = 0
    if st.session_state.step == 1:
        progress = 0.25
    elif st.session_state.step == 2:
        progress = 0.50
    elif st.session_state.step == 3:
        progress = 0.75
    elif st.session_state.step == 4:
        progress = 1.0
    
    st.progress(progress)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**① Profil**" if st.session_state.step >= 1 else "① Profil")
    with col2:
        st.markdown("**② Skrining**" if st.session_state.step >= 2 else "② Skrining")
    with col3:
        st.markdown("**③ Penyimpanan**" if st.session_state.step >= 3 else "③ Penyimpanan")
    with col4:
        st.markdown("**④ Analisis**" if st.session_state.step >= 4 else "④ Analisis")

def step_1_profile():
    """Step 1: Collect user profile data"""
    st.markdown('<div class="main-header">🧠 Skrining Kecanduan Media Sosial</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Social Media Disorder Scale - 27 Items (SMDS-27)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>📋 Tentang Skrining Ini</h3>
        <p>SMDS-27 adalah instrumen skrining yang valid dan reliabel untuk mendeteksi potensi 
        kecanduan media sosial. Skrining ini mengukur 9 dimensi gangguan penggunaan media sosial 
        berdasarkan kriteria DSM-5 untuk gangguan perilaku adiktif.</p>
        <p><strong>Waktu pengisian:</strong> ± 10-15 menit</p>
        <p><strong>Kerahasiaan:</strong> Data Anda akan dijaga kerahasiaannya dan hanya digunakan 
        untuk keperluan analisis personal.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📝 Langkah 1: Data Profil Pribadi")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nama = st.text_input(
                "Nama Alias *",
                placeholder="Contoh: Budi123",
                help="Gunakan nama samaran untuk menjaga privasi"
            )
            umur = st.number_input(
                "Umur *",
                min_value=10,
                max_value=100,
                value=25,
                help="Masukkan umur Anda"
            )
        
        with col2:
            gender = st.selectbox(
                "Gender *",
                options=["", "Laki-laki", "Perempuan", "Lainnya"],
                help="Pilih gender Anda"
            )
            pekerjaan = st.selectbox(
                "Pekerjaan/Status *",
                options=[
                    "",
                    "Pelajar/Mahasiswa",
                    "Karyawan Swasta",
                    "PNS/ASN",
                    "Wiraswasta",
                    "Freelancer",
                    "Ibu Rumah Tangga",
                    "Tidak Bekerja",
                    "Lainnya"
                ],
                help="Pilih status pekerjaan Anda"
            )
        
        st.markdown("---")
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Perhatian:</strong> Pastikan semua data sudah diisi dengan benar. 
            Anda tidak dapat mengubah data profil setelah melanjutkan ke tahap berikutnya.
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Lanjutkan ke Skrining →", use_container_width=True, type="primary")
        
        if submitted:
            if not nama or not gender or not pekerjaan:
                st.error("❌ Mohon lengkapi semua data profil yang bertanda (*)")
            elif len(nama) < 3:
                st.error("❌ Nama alias minimal 3 karakter")
            else:
                st.session_state.user_data = {
                    'nama': nama,
                    'umur': umur,
                    'gender': gender,
                    'pekerjaan': pekerjaan
                }
                st.session_state.step = 2
                st.rerun()

def step_2_screening():
    """Step 2: SMDS-27 questionnaire"""
    st.markdown('<div class="main-header">📝 Kuesioner SMDS-27</div>', unsafe_allow_html=True)
    
    # Display user info
    st.markdown(f"""
    <div class="info-box">
        <strong>Peserta:</strong> {st.session_state.user_data['nama']} | 
        <strong>Umur:</strong> {st.session_state.user_data['umur']} tahun | 
        <strong>Gender:</strong> {st.session_state.user_data['gender']} | 
        <strong>Pekerjaan:</strong> {st.session_state.user_data['pekerjaan']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <h4>📌 Petunjuk Pengisian:</h4>
        <ul>
            <li>Baca setiap pernyataan dengan seksama</li>
            <li>Pilih jawaban yang paling sesuai dengan kondisi Anda dalam <strong>3 bulan terakhir</strong></li>
            <li>Tidak ada jawaban benar atau salah - jawablah sejujur mungkin</li>
            <li>Pastikan semua item terjawab sebelum melanjutkan</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.form("smds_form"):
        responses = {}
        
        # Group by dimension for better organization
        current_dimension = None
        
        for item in SMDS_27_ITEMS:
            # Show dimension header if changed
            if item['dimension'] != current_dimension:
                current_dimension = item['dimension']
                st.markdown(f"### 📊 Dimensi: {current_dimension}")
                st.markdown("---")
            
            # Display item
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item['id']}. {item['text']}**")
            
            response = st.radio(
                f"Item {item['id']}",
                options=list(LIKERT_SCALE.keys()),
                key=f"item_{item['id']}",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            responses[f"item_{item['id']}"] = LIKERT_SCALE[response]
            st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("← Kembali ke Profil", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("Simpan & Lanjutkan →", use_container_width=True, type="primary")
            
            if submitted:
                st.session_state.responses = responses
                total, dim_scores = calculate_scores(responses)
                st.session_state.total_score = total
                st.session_state.dimension_scores = dim_scores
                st.session_state.step = 3
                st.rerun()

def step_3_save_data():
    """Step 3: Save data to Google Sheets"""
    st.markdown('<div class="main-header">💾 Penyimpanan Data</div>', unsafe_allow_html=True)
    
    # Calculate category
    category, description = get_severity_category(st.session_state.total_score)
    
    st.markdown(f"""
    <div class="success-box">
        <h3>✅ Skrining Selesai!</h3>
        <p><strong>Total Skor:</strong> {st.session_state.total_score}/108</p>
        <p><strong>Kategori:</strong> {category}</p>
        <p><strong>Deskripsi:</strong> {description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show dimension scores
    st.markdown("### 📊 Skor Per Dimensi")
    
    cols = st.columns(3)
    for idx, (dim, score) in enumerate(st.session_state.dimension_scores.items()):
        max_score = score['count'] * 4
        percentage = (score['total'] / max_score * 100) if max_score > 0 else 0
        
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="dimension-card">
                <h4>{dim}</h4>
                <p><strong>Skor:</strong> {score['total']}/{max_score}</p>
                <p><strong>Persentase:</strong> {percentage:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💾 Menyimpan Data ke Google Sheets")
    
    if st.button("Simpan Data & Lanjut ke Analisis", use_container_width=True, type="primary"):
        with st.spinner("Menyimpan data Anda..."):
            try:
                # Initialize Google Sheets Manager
                sheets_manager = GoogleSheetsManager()
                
                # Save data
                success, rows_updated = sheets_manager.append_response(
                    st.session_state.user_data,
                    st.session_state.responses,
                    st.session_state.total_score,
                    category
                )
                
                if success:
                    st.success(f"✅ Data berhasil disimpan! ({rows_updated} baris ditambahkan)")
                    time.sleep(1)
                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error("❌ Gagal menyimpan data. Silakan coba lagi.")
                    
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {str(e)}")
                st.info("💡 Tip: Pastikan Google Sheets API sudah dikonfigurasi dengan benar di secrets.toml")

def step_4_analysis():
    """Step 4: AI Analysis with Gemini"""
    st.markdown('<div class="main-header">🤖 Analisis AI dengan Gemini</div>', unsafe_allow_html=True)
    
    category, _ = get_severity_category(st.session_state.total_score)
    
    st.markdown(f"""
    <div class="info-box">
        <h3>📊 Ringkasan Hasil Skrining</h3>
        <p><strong>Nama:</strong> {st.session_state.user_data['nama']}</p>
        <p><strong>Total Skor:</strong> {st.session_state.total_score}/108</p>
        <p><strong>Kategori:</strong> {category}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.session_state.analysis_result is None:
        st.subheader("🔍 Memulai Analisis Berbasis AI")
        st.info("Analisis ini menggunakan Gemini 1.5 Pro untuk memberikan rekomendasi yang dipersonalisasi berdasarkan artikel ilmiah terpercaya.")
        
        if st.button("🚀 Mulai Analisis dengan Gemini", use_container_width=True, type="primary"):
            with st.spinner("🧠 Gemini sedang menganalisis data Anda... Mohon tunggu 30-60 detik..."):
                try:
                    analyzer = GeminiAnalyzer()
                    
                    analysis = analyzer.analyze_smds_responses(
                        st.session_state.user_data,
                        st.session_state.responses,
                        st.session_state.total_score,
                        category,
                        st.session_state.dimension_scores
                    )
                    
                    st.session_state.analysis_result = analysis
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan saat analisis: {str(e)}")
                    st.info("💡 Tip: Pastikan Gemini API key sudah dikonfigurasi dengan benar di secrets.toml")
    else:
        st.subheader("📄 Hasil Analisis Personal Anda")
        
        # Display analysis result
        st.markdown(st.session_state.analysis_result)
        
        st.markdown("---")
        
        # Download options
        col1, col2 = st.columns(2)
        
        with col1:
            # Download as text
            st.download_button(
                label="📥 Download Hasil Analisis (TXT)",
                data=st.session_state.analysis_result,
                file_name=f"analisis_smds27_{st.session_state.user_data['nama']}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 Mulai Skrining Baru", use_container_width=True):
                # Reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Disclaimer</h4>
            <p>Hasil skrining ini bersifat informatif dan bukan diagnosis klinis. 
            Jika Anda merasa memerlukan bantuan profesional, silakan berkonsultasi dengan 
            psikolog atau psikiater yang berkompeten.</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application flow"""
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/brain.png", width=80)
        st.title("SMDS-27 Screening")
        st.markdown("---")
        
        st.markdown(f"### 📍 Progress Anda")
        render_progress_bar()
        
        st.markdown("---")
        st.markdown("### ℹ️ Informasi")
        st.info("""
        **SMDS-27** adalah instrumen skrining yang mengukur 9 dimensi gangguan media sosial:
        
        1. Preoccupation
        2. Tolerance
        3. Withdrawal
        4. Persistence
        5. Escape
        6. Problems
        7. Displacement
        8. Deception
        9. Conflict
        """)
        
        st.markdown("---")
        st.markdown("### 🔒 Privasi")
        st.success("Data Anda dijaga kerahasiaannya dan hanya digunakan untuk analisis personal.")
        
        st.markdown("---")
        st.markdown("### 📞 Bantuan")
        st.markdown("""
        Jika Anda memerlukan bantuan profesional:
        - **Halo Kemkes**: 119 ext 8
        - **Sejiwa**: 119 ext 8
        - **Into The Light**: @intothelightid
        """)
    
    # Main content based on step
    if st.session_state.step == 1:
        step_1_profile()
    elif st.session_state.step == 2:
        step_2_screening()
    elif st.session_state.step == 3:
        step_3_save_data()
    elif st.session_state.step == 4:
        step_4_analysis()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; padding: 2rem 0;">
        <p>SMDS-27 Screening Tool | Powered by Streamlit & Gemini AI</p>
        <p style="font-size: 0.8rem;">© 2024 | Untuk Keperluan Penelitian dan Edukasi</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
