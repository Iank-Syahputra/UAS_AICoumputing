# ----------------------- sql_utils.py -----------------------
import sqlite3
from module.config import DATABASE_PATH

def execute_sql_query(query: str):

    # --- 1. SANITASI QUERY (Fix "One statement at a time" Error) ---
    # Kadang LLM menghasilkan "SELECT ...; SELECT ...;"
    # Kita pecah berdasarkan titik koma, dan hanya ambil yang pertama.
    
    # Hapus whitespace di awal/akhir
    clean_query = query.strip()
    
    # Jika ada titik koma, ambil bagian pertamanya saja
    if ";" in clean_query:
        parts = [p.strip() for p in clean_query.split(";") if p.strip()]
        if len(parts) > 0:
            clean_query = parts[0] # Ambil statement pertama saja
    # --- FITUR KEAMANAN (POINT A) ---
    # Mencegah perintah berbahaya yang mengubah struktur/isi database
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    
    # Cek apakah query mengandung kata terlarang
    # Kita ubah ke uppercase agar pengecekan tidak case-sensitive
    query_upper = query.strip().upper()
    
    for keyword in forbidden_keywords:
        if keyword in query_upper:
            return f"SQL Error: Perintah '{keyword}' tidak diizinkan demi keamanan data (Read-Only Mode).", []
    # --------------------------------
    
    try:
        # Gunakan mode uri=True dan query parameter ?mode=ro (Read Only) untuk proteksi ganda (opsional)
        # Tapi untuk SQLite standar, logic Python di atas sudah cukup kuat.
        with sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(query)

            if query.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                col_names = [description[0] for description in cursor.description]
                return rows, col_names
            else:
                # Seharusnya tidak akan sampai sini karena filter di atas, tapi untuk jaga-jaga:
                return "SQL executed (No data returned)", []
                
    except sqlite3.Error as e:
        return f"SQL Error: {str(e)}", []


def get_current_schema():
    # Untuk mengambil schema, kita tetap butuh koneksi standar
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            schema = ""
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                cols = cursor.fetchall()
                schema += f"- {table_name}({', '.join([col[1] for col in cols])})\n"
            return schema.strip()
    except Exception:
        return "Schema not found."