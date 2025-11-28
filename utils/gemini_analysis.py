import streamlit as st
import google.generativeai as genai
from typing import Dict, List

class GeminiAnalyzer:
    def __init__(self):
        """Initialize Gemini API"""
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            st.error(f"Error initializing Gemini: {str(e)}")
            raise
    
    def analyze_smds_responses(self, user_data: Dict, responses: Dict, 
                               total_score: int, category: str, 
                               dimension_scores: Dict) -> str:
        """
        Analyze SMDS-27 responses using Gemini with strict academic criteria
        
        Args:
            user_data: User profile information
            responses: Item responses
            total_score: Total SMDS score
            category: Severity category
            dimension_scores: Scores per dimension
        
        Returns:
            Analysis text with scientific backing
        """
        
        prompt = f"""
Anda adalah seorang psikolog klinis dan peneliti yang ahli dalam kecanduan media sosial. 
Anda diminta untuk menganalisis hasil skrining SMDS-27 (Social Media Disorder Scale - 27 Items) 
dari seorang pengguna dengan KRITERIA YANG SANGAT KETAT.

INFORMASI PENGGUNA:
- Nama (Alias): {user_data['nama']}
- Umur: {user_data['umur']} tahun
- Gender: {user_data['gender']}
- Pekerjaan: {user_data['pekerjaan']}

HASIL SKRINING:
- Total Skor: {total_score}/108
- Kategori: {category}

SKOR PER DIMENSI (dari 9 dimensi SMDS):
{self._format_dimension_scores(dimension_scores)}

DETAIL RESPON ITEMS (Skala 0-4):
{self._format_item_responses(responses)}

INSTRUKSI ANALISIS (WAJIB DIPATUHI):

1. DASAR ANALISIS - HANYA GUNAKAN ARTIKEL ILMIAH:
   - Analisis HARUS berdasarkan artikel penelitian peer-reviewed tentang Social Media Disorder, 
     Internet Gaming Disorder, atau behavioral addiction
   - Rujuk minimal 3-5 artikel ilmiah yang relevan
   - Fokus pada artikel dari jurnal psikologi/psikiatri terkemuka (contoh: Journal of Behavioral Addictions, 
     Computers in Human Behavior, Cyberpsychology, Behavior, and Social Networking)
   - Sebutkan temuan spesifik dari penelitian (bukan asumsi umum)

2. PERSONALISASI BERDASARKAN DATA:
   - Identifikasi dimensi dengan skor tertinggi dan jelaskan implikasinya spesifik untuk user ini
   - Pertimbangkan konteks umur dan pekerjaan dalam memberikan saran
   - Berikan contoh konkret yang relevan dengan situasi user

3. SARAN ACTIONABLE BERBASIS BUKTI:
   - Rekomendasikan intervensi yang telah terbukti efektif dalam penelitian ilmiah
   - Setiap saran harus disertai rujukan penelitian yang mendukungnya
   - Berikan langkah-langkah praktis yang bisa dilakukan mulai hari ini
   - Hindari saran generik - sesuaikan dengan profil dan skor user

4. KESIMPULAN DENGAN RUJUKAN URL:
   - Akhiri dengan kesimpulan yang jelas dan actionable
   - WAJIB: Sertakan minimal 3-5 URL artikel ilmiah asli (DOI atau URL jurnal) 
     yang digunakan dalam analisis
   - Format URL: tuliskan dalam format "Referensi Ilmiah:" di akhir laporan

FORMAT OUTPUT:
Gunakan format berikut dalam bahasa Indonesia yang profesional namun mudah dipahami:

## 📊 Ringkasan Hasil Skrining
[Interpretasi singkat skor dan kategori]

## 🔍 Analisis Mendalam Berdasarkan Penelitian Ilmiah
[Analisis detail per dimensi dengan rujukan penelitian spesifik]

## 💡 Rekomendasi Personal Berbasis Bukti Ilmiah
[3-5 rekomendasi spesifik dengan rujukan penelitian]

## ⚠️ Tanda Bahaya yang Perlu Diwaspadai
[Jika ada, berdasarkan literatur]

## 🎯 Langkah Tindak Lanjut
[Action plan konkret dengan timeline]

## 📚 Referensi Ilmiah
[List 3-5 URL artikel ilmiah yang digunakan dalam format APA]

PENTING: 
- Jangan membuat rujukan palsu atau fiktif
- Hanya gunakan penelitian yang benar-benar ada dan relevan
- Jika tidak yakin tentang suatu klaim, jangan sertakan
- Fokus pada evidence-based recommendations

Mulai analisis sekarang:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error generating analysis: {str(e)}")
            return "Maaf, terjadi kesalahan dalam menganalisis data Anda."
    
    def _format_dimension_scores(self, dimension_scores: Dict) -> str:
        """Format dimension scores for prompt"""
        formatted = []
        for dim, score in dimension_scores.items():
            max_score = score['count'] * 4  # Each item max 4 points
            percentage = (score['total'] / max_score * 100) if max_score > 0 else 0
            formatted.append(f"- {dim}: {score['total']}/{max_score} ({percentage:.1f}%)")
        return "\n".join(formatted)
    
    def _format_item_responses(self, responses: Dict) -> str:
        """Format item responses for prompt"""
        formatted = []
        for item_id, score in sorted(responses.items()):
            item_num = item_id.split('_')[1]
            formatted.append(f"Item {item_num}: {score}")
        return "\n".join(formatted)
