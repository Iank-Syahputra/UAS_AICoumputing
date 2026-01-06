import os
import pickle
import streamlit as st

# Nama file penyimpanan
HISTORY_FILE_SQL = "history_sql.pkl"
HISTORY_FILE_PYTHON = "history_python.pkl"

def load_history_from_disk():
    """Memuat riwayat chat dari file fisik saat aplikasi pertama dibuka"""
    
    # 1. Load History SQL
    if "chat_history" not in st.session_state:
        if os.path.exists(HISTORY_FILE_SQL):
            try:
                with open(HISTORY_FILE_SQL, "rb") as f:
                    st.session_state.chat_history = pickle.load(f)
            except Exception:
                st.session_state.chat_history = [] # Jika file rusak, reset
        else:
            st.session_state.chat_history = []

    # 2. Load History Python Agent
    if "python_history" not in st.session_state:
        if os.path.exists(HISTORY_FILE_PYTHON):
            try:
                with open(HISTORY_FILE_PYTHON, "rb") as f:
                    st.session_state.python_history = pickle.load(f)
            except Exception:
                st.session_state.python_history = []
        else:
            st.session_state.python_history = []

def save_history_to_disk(type="sql"):
    """Menyimpan riwayat chat ke file fisik setiap kali ada update"""
    try:
        if type == "sql":
            with open(HISTORY_FILE_SQL, "wb") as f:
                pickle.dump(st.session_state.chat_history, f)
        elif type == "python":
            with open(HISTORY_FILE_PYTHON, "wb") as f:
                pickle.dump(st.session_state.python_history, f)
    except Exception as e:
        print(f"Gagal menyimpan history: {e}")

def clear_all_history():
    """Menghapus file fisik dan memori saat tombol Reset ditekan"""
    # Hapus Memori
    st.session_state.chat_history = []
    st.session_state.python_history = []
    
    # Hapus File Fisik
    if os.path.exists(HISTORY_FILE_SQL): os.remove(HISTORY_FILE_SQL)
    if os.path.exists(HISTORY_FILE_PYTHON): os.remove(HISTORY_FILE_PYTHON)