"""
SMDS-27 Items berdasarkan Social Media Disorder Scale
Referensi: van den Eijnden et al. (2016)
"""

SMDS_27_ITEMS = [
    # Preoccupation
    {
        "id": 1,
        "dimension": "Preoccupation",
        "text": "Seberapa sering Anda terus memikirkan media sosial bahkan ketika tidak menggunakannya?"
    },
    {
        "id": 2,
        "dimension": "Preoccupation",
        "text": "Seberapa sering Anda merencanakan bagaimana Anda akan menggunakan media sosial?"
    },
    {
        "id": 3,
        "dimension": "Preoccupation",
        "text": "Seberapa sering Anda merasa gelisah jika tidak bisa mengecek media sosial?"
    },
    
    # Tolerance
    {
        "id": 4,
        "dimension": "Tolerance",
        "text": "Seberapa sering Anda merasa perlu menghabiskan lebih banyak waktu di media sosial untuk merasa puas?"
    },
    {
        "id": 5,
        "dimension": "Tolerance",
        "text": "Seberapa sering Anda merasa bahwa waktu yang Anda habiskan di media sosial tidak pernah cukup?"
    },
    {
        "id": 6,
        "dimension": "Tolerance",
        "text": "Seberapa sering Anda ingin menggunakan media sosial lebih lama lagi?"
    },
    
    # Withdrawal
    {
        "id": 7,
        "dimension": "Withdrawal",
        "text": "Seberapa sering Anda merasa tidak nyaman ketika tidak bisa menggunakan media sosial?"
    },
    {
        "id": 8,
        "dimension": "Withdrawal",
        "text": "Seberapa sering Anda merasa bad mood atau irritable ketika tidak bisa mengecek media sosial?"
    },
    {
        "id": 9,
        "dimension": "Withdrawal",
        "text": "Seberapa sering Anda merasa cemas jika dilarang menggunakan media sosial?"
    },
    
    # Persistence
    {
        "id": 10,
        "dimension": "Persistence",
        "text": "Seberapa sering Anda gagal ketika mencoba mengurangi waktu penggunaan media sosial?"
    },
    {
        "id": 11,
        "dimension": "Persistence",
        "text": "Seberapa sering Anda tidak berhasil mengontrol penggunaan media sosial Anda?"
    },
    {
        "id": 12,
        "dimension": "Persistence",
        "text": "Seberapa sering Anda terus menggunakan media sosial meskipun sudah berencana untuk berhenti?"
    },
    
    # Escape
    {
        "id": 13,
        "dimension": "Escape",
        "text": "Seberapa sering Anda menggunakan media sosial untuk menghindari masalah pribadi?"
    },
    {
        "id": 14,
        "dimension": "Escape",
        "text": "Seberapa sering Anda menggunakan media sosial untuk melarikan diri dari perasaan negatif?"
    },
    {
        "id": 15,
        "dimension": "Escape",
        "text": "Seberapa sering Anda menggunakan media sosial untuk melupakan masalah yang Anda hadapi?"
    },
    
    # Problems
    {
        "id": 16,
        "dimension": "Problems",
        "text": "Seberapa sering Anda memiliki konflik dengan orang tua/keluarga karena penggunaan media sosial?"
    },
    {
        "id": 17,
        "dimension": "Problems",
        "text": "Seberapa sering Anda mengabaikan teman atau keluarga karena terlalu fokus pada media sosial?"
    },
    {
        "id": 18,
        "dimension": "Problems",
        "text": "Seberapa sering penggunaan media sosial menyebabkan masalah dalam hubungan Anda?"
    },
    
    # Displacement
    {
        "id": 19,
        "dimension": "Displacement",
        "text": "Seberapa sering Anda mengabaikan pekerjaan/tugas sekolah karena media sosial?"
    },
    {
        "id": 20,
        "dimension": "Displacement",
        "text": "Seberapa sering kinerja sekolah/pekerjaan Anda menurun karena penggunaan media sosial?"
    },
    {
        "id": 21,
        "dimension": "Displacement",
        "text": "Seberapa sering Anda kehilangan kesempatan atau aktivitas penting karena media sosial?"
    },
    
    # Deception
    {
        "id": 22,
        "dimension": "Deception",
        "text": "Seberapa sering Anda berbohong kepada orang lain tentang seberapa banyak waktu yang Anda habiskan di media sosial?"
    },
    {
        "id": 23,
        "dimension": "Deception",
        "text": "Seberapa sering Anda menyembunyikan dari orang lain berapa lama Anda menggunakan media sosial?"
    },
    {
        "id": 24,
        "dimension": "Deception",
        "text": "Seberapa sering Anda menutupi penggunaan media sosial Anda dari keluarga atau teman?"
    },
    
    # Conflict
    {
        "id": 25,
        "dimension": "Conflict",
        "text": "Seberapa sering Anda bertengkar dengan orang lain karena penggunaan media sosial Anda?"
    },
    {
        "id": 26,
        "dimension": "Conflict",
        "text": "Seberapa sering orang-orang mengeluh tentang penggunaan media sosial Anda?"
    },
    {
        "id": 27,
        "dimension": "Conflict",
        "text": "Seberapa sering Anda mengalami masalah interpersonal karena media sosial?"
    }
]

LIKERT_SCALE = {
    "Tidak Pernah": 0,
    "Jarang": 1,
    "Kadang-kadang": 2,
    "Sering": 3,
    "Sangat Sering": 4
}

def get_severity_category(total_score):
    """
    Kategorisasi tingkat kecanduan berdasarkan total skor
    Total maksimal: 27 items × 4 = 108
    """
    if total_score <= 27:
        return "Rendah", "Penggunaan media sosial Anda dalam batas normal."
    elif total_score <= 54:
        return "Sedang", "Terdapat indikasi penggunaan media sosial yang bermasalah."
    elif total_score <= 81:
        return "Tinggi", "Terdapat tanda-tanda kecanduan media sosial yang signifikan."
    else:
        return "Sangat Tinggi", "Indikasi kecanduan media sosial yang serius."
