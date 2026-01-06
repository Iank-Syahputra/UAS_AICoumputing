import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

# Import modules
from module.query_engine import get_sql_query, generate_data_insight, get_visualization_recommendation
from module.sql_utils import execute_sql_query, get_current_schema
from module.download_utils import download_button
# Import History Utils (Pastikan file module/history_utils.py masih ada)
from module.history_utils import load_history_from_disk, save_history_to_disk, clear_all_history

load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="E-Commerce AI Analyst",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize History (Agar tidak hilang saat refresh) ---
load_history_from_disk()

# --- Advanced Custom CSS (Estetika) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); border-right: 1px solid rgba(255, 255, 255, 0.1); }
    [data-testid="stSidebar"] .element-container { color: #e0e0e0; }
    
    /* Metrics & Cards */
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    [data-testid="stMetric"] { background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 16px; padding: 20px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); backdrop-filter: blur(4px); }
    
    /* Chat Elements */
    [data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; backdrop-filter: blur(10px); margin: 10px 0; }
    [data-testid="stChatInput"] { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 12px; }
    
    /* Dataframe & Tables */
    [data-testid="stDataFrame"] { background: rgba(255, 255, 255, 0.05); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); }
    
    /* Button Styles */
    .stButton button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; color: white; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6); }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def format_chat_history(history):
    formatted_history = ""
    recent_history = history[-5:] 
    for role, content in recent_history:
        if role == "user": formatted_history += f"User: {content}\n"
        elif role == "assistant_sql": formatted_history += f"Assistant (SQL): {content}\n"
    return formatted_history

def get_database_summary():
    try:
        res_prod, _ = execute_sql_query("SELECT COUNT(*) FROM products")
        res_cust, _ = execute_sql_query("SELECT COUNT(*) FROM customers")
        res_rev, _ = execute_sql_query("SELECT SUM(total_amount) FROM orders")
        return (res_prod[0][0] if res_prod else 0, 
                res_cust[0][0] if res_cust else 0, 
                res_rev[0][0] if res_rev else 0)
    except:
        return 0, 0, 0

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🛍️ E-Commerce Data")
    st.markdown("---")
    with st.expander("View Tables & Columns", expanded=False):
        st.code(get_current_schema(), language="sql")
    st.markdown("---")
    st.markdown("#### ⚙️ Settings")
    
    if st.button("🗑️ Clear History (Reset)"):
        clear_all_history() # Hapus file fisik & memori
        st.rerun()

# --- MAIN HEADER ---
col_title1, col_title2 = st.columns([0.1, 0.9])
with col_title1: st.markdown("## 🤖")
with col_title2: st.title("Enterprise AI Data Analyst")

# ==========================================
# MAIN LOGIC (SINGLE VIEW)
# ==========================================

# 1. Landing Page (Hanya muncul jika history kosong)
if len(st.session_state.chat_history) == 0:
    st.markdown('Selamat datang! Saya siap membantu menganalisis data penjualan Anda secara mendalam. **Pilih menu cepat di bawah atau ketik pertanyaan Anda.**')
    
    # Live Metrics
    st.markdown("### 📊 Live Database Overview")
    c1, c2, c3 = st.columns(3)
    tp, tc, tr = get_database_summary()
    c1.metric("Total Produk", f"{tp:,}")
    c2.metric("Total Pelanggan", f"{tc:,}")
    c3.metric("Total Pendapatan", f"Rp {tr:,.0f}".replace(",", "."))

    # Quick Actions
    st.markdown("### 🚀 Mulai Analisis Cepat")
    q1, q2, q3, q4 = st.columns(4)
    prompt_clk = None
    if q1.button("🏆 Top Produk", use_container_width=True): prompt_clk = "Tampilkan 5 produk dengan harga termahal"
    if q2.button("📈 Tren Jual", use_container_width=True): prompt_clk = "Tampilkan tren penjualan harian berdasarkan tanggal order"
    if q3.button("🏙️ Kota", use_container_width=True): prompt_clk = "Berapa total pendapatan dari masing-masing kota?"
    if q4.button("📦 Cek Stok", use_container_width=True): prompt_clk = "Tampilkan produk dengan stok kurang dari 20"
    
    if prompt_clk:
        st.session_state.chat_history.append(("user", prompt_clk))
        save_history_to_disk("sql") 
        st.rerun()

# 2. Display Chat History
if len(st.session_state.chat_history) > 0:
    st.markdown("### 💬 Conversation History")
    last_df = None 
    for role, content in st.session_state.chat_history:
        if role == "user":
            with st.chat_message("user", avatar="👤"): st.markdown(content)
        elif role == "assistant_sql":
            with st.expander("🛠️ Lihat Query SQL"): st.code(content, language="sql")
        elif role == "error":
            with st.chat_message("assistant", avatar="🤖"): st.error(f"❌ Error: {content}")
        elif role == "result":
            res, cols = content
            with st.chat_message("assistant", avatar="🤖"):
                if res:
                    last_df = pd.DataFrame(res, columns=cols)
                    # FIX: Index mulai dari 1
                    last_df.index = last_df.index + 1 
                    # FIX: Auto-height
                    st.dataframe(last_df, use_container_width=True) 
                else:
                    st.warning("📭 Tidak ada data.")
                    last_df = None
        elif role == "insight":
            with st.chat_message("assistant", avatar="💡"): st.markdown(f"**Analisis:** {content}")
        elif role == "viz_config":
            viz = content
            if last_df is not None and not last_df.empty:
                chart = viz.get("chart_type")
                x, y = viz.get("x_column"), viz.get("y_column")
                if chart != "none":
                    cols_low = {c.lower(): c for c in last_df.columns}
                    x, y = cols_low.get(str(x).lower()), cols_low.get(str(y).lower())
                    if x and y:
                        try:
                            template = "plotly_dark"
                            fig = None
                            if chart == "bar":
                                df_srt = last_df.sort_values(by=y, ascending=False).head(10)
                                fig = px.bar(df_srt, x=x, y=y, color=x, template=template, title=f"Top {y} by {x}")
                            elif chart == "line":
                                fig = px.line(last_df, x=x, y=y, markers=True, template=template, title=f"Trend: {y} vs {x}")
                            elif chart == "pie":
                                fig = px.pie(last_df, names=x, values=y, hole=0.4, template=template, title=f"Dist. {y}")
                            
                            if fig:
                                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=500)
                                with st.chat_message("assistant", avatar="📊"): st.plotly_chart(fig, use_container_width=True)
                        except: pass

# 3. Input Processing
user_in = st.chat_input("💭 Tanya data penjualan...", key="sql_in")
trigger = False

if user_in:
    st.session_state.chat_history.append(("user", user_in))
    save_history_to_disk("sql") 
    trigger = True
elif len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1][0] == "user":
    user_in = st.session_state.chat_history[-1][1]
    trigger = True

if trigger:
    should_run = True
    if len(st.session_state.chat_history) > 1 and st.session_state.chat_history[-1][0] != "user":
        should_run = False
        
    if should_run:
        schema = get_current_schema()
        hist_txt = format_chat_history(st.session_state.chat_history[:-1])

        with st.spinner("🔍 Menganalisis..."):
            try:
                # 1. SQL Generation
                sql = get_sql_query(user_in, schema, chat_history=hist_txt)
                st.session_state.chat_history.append(("assistant_sql", sql))
                save_history_to_disk("sql")
                
                # 2. Execution
                res, cols = execute_sql_query(sql)
                if isinstance(res, str) and res.startswith("SQL Error"):
                    st.session_state.chat_history.append(("error", res))
                else:
                    st.session_state.chat_history.append(("result", (res, cols)))
                    save_history_to_disk("sql")
                    
                    if res:
                        df_tmp = pd.DataFrame(res, columns=cols)
                        # 3. Insight & Viz (Dikirim data mentah/index asli)
                        ins = generate_data_insight(user_in, df_tmp)
                        st.session_state.chat_history.append(("insight", ins))
                        viz = get_visualization_recommendation(user_in, df_tmp)
                        st.session_state.chat_history.append(("viz_config", viz))
                
                save_history_to_disk("sql")
                st.rerun()
            except Exception as e:
                st.session_state.chat_history.append(("error", str(e)))
                save_history_to_disk("sql")
                st.rerun()

if len(st.session_state.chat_history) > 0:
    st.markdown("---")
    download_button(st.session_state.chat_history)