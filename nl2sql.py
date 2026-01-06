import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Import module
from module.query_engine import get_sql_query, generate_data_insight, get_visualization_recommendation
from module.sql_utils import execute_sql_query, get_current_schema
from module.download_utils import download_button
from module.history_utils import load_history_from_disk, save_history_to_disk, clear_all_history
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="E-Commerce AI Analyst",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_history_from_disk()
# --- Advanced Custom CSS ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] .element-container {
        color: #e0e0e0;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(102, 126, 234, 0.4);
    }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-weight: 600;
        font-size: 0.95rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Title Styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #e0e0e0;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 0%, transparent 100%);
        border-left: 4px solid #667eea;
        padding: 12px 20px;
        border-radius: 8px;
        margin: 20px 0;
        color: #ffffff;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Cards for Quick Actions */
    .action-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .action-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        backdrop-filter: blur(10px);
        margin: 10px 0;
    }
    
    /* Dataframe Styling */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Chat Input */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
    }
    
    /* Welcome Text */
    .welcome-text {
        color: #e0e0e0;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Code blocks */
    code {
        background: rgba(102, 126, 234, 0.2) !important;
        border-radius: 6px;
        padding: 2px 6px;
        color: #a8b4ff !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Helper Functions ---
def format_chat_history(history):
    formatted_history = ""
    recent_history = history[-5:] 
    for role, content in recent_history:
        if role == "user":
            formatted_history += f"User: {content}\n"
        elif role == "assistant_sql":
            formatted_history += f"Assistant (SQL): {content}\n"
    return formatted_history

def get_database_summary():
    """Mengambil statistik cepat untuk Dashboard awal"""
    try:
        res_prod, _ = execute_sql_query("SELECT COUNT(*) FROM products")
        res_cust, _ = execute_sql_query("SELECT COUNT(*) FROM customers")
        res_rev, _ = execute_sql_query("SELECT SUM(total_amount) FROM orders")
        
        total_products = res_prod[0][0] if res_prod else 0
        total_customers = res_cust[0][0] if res_cust else 0
        total_revenue = res_rev[0][0] if res_rev else 0
        
        return total_products, total_customers, total_revenue
    except:
        return 0, 0, 0

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🛍️ E-Commerce Data")
    st.markdown("---")
    
    st.markdown("#### 📂 Database Schema")
    with st.expander("View Tables & Columns", expanded=False):
        st.code(get_current_schema(), language="sql")
    
    st.markdown("---")
    st.markdown("#### ⚙️ Settings")
    st.caption("Powered by Llama 3 & Groq")
    if st.button("🗑️ Reset Conversation"):
        clear_all_history() # Hapus file fisik & memori
        st.rerun()

# --- MAIN LOGIC ---

# 1. Judul Utama dengan Icon
col_title1, col_title2 = st.columns([0.1, 0.9])
with col_title1:
    st.markdown("## 🤖")
with col_title2:
    st.title("AI Data Analyst SQL Assistant")

# 2. LOGIKA TAMPILAN AWAL (LANDING PAGE)
if len(st.session_state.chat_history) == 0:
    st.markdown('<p class="welcome-text">Selamat datang! Saya adalah asisten pintar yang terhubung langsung ke database penjualan Anda. <strong>Pilih menu cepat di bawah atau ketik pertanyaan Anda.</strong></p>', unsafe_allow_html=True)
    
    # --- SECTION A: LIVE METRICS ---
    st.markdown('<div class="section-header">📊 Live Database Overview</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    # Ambil data real-time
    t_prod, t_cust, t_rev = get_database_summary()
    
    with col1:
        st.metric("Total Produk", f"{t_prod:,}", delta="Items", delta_color="off")
    with col2:
        st.metric("Total Pelanggan", f"{t_cust:,}", delta="Active", delta_color="off")
    with col3:
        rev_fmt = f"Rp {t_rev:,.0f}".replace(",", ".")
        st.metric("Total Pendapatan", rev_fmt, delta="All Time", delta_color="off")

    # --- SECTION B: QUICK ACTION CARDS ---
    st.markdown('<div class="section-header">🚀 Mulai Analisis Cepat</div>', unsafe_allow_html=True)
    
    qc1, qc2, qc3, qc4 = st.columns(4)
    
    prompt_clicked = None
    
    with qc1:
        if st.button("🏆 Top Produk", help="Lihat 5 produk termahal", use_container_width=True):
            prompt_clicked = "Tampilkan 5 produk dengan harga termahal"
    with qc2:
        if st.button("📈 Tren Penjualan", help="Analisis tren penjualan per bulan", use_container_width=True):
            prompt_clicked = "Tampilkan tren penjualan harian berdasarkan tanggal order"
    with qc3:
        if st.button("🏙️ Analisis Kota", help="Total pendapatan per kota", use_container_width=True):
            prompt_clicked = "Berapa total pendapatan dari masing-masing kota?"
    with qc4:
        if st.button("📦 Cek Stok", help="Produk dengan stok menipis", use_container_width=True):
            prompt_clicked = "Tampilkan produk dengan stok kurang dari 20"

    if prompt_clicked:
        st.session_state.chat_history.append(("user", prompt_clicked))
        save_history_to_disk("sql")
        st.rerun()

# 3. TAMPILAN CHAT HISTORY
if len(st.session_state.chat_history) > 0:
    st.markdown('<div class="section-header">💬 Conversation History</div>', unsafe_allow_html=True)
    
    last_df = None 
    for role, content in st.session_state.chat_history:
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        elif role == "assistant_sql":
            with st.expander("🛠️ Lihat Query SQL", expanded=False):
                st.code(content, language="sql")
        elif role == "error":
            with st.chat_message("assistant", avatar="🤖"):
                st.error(f"❌ Terjadi kesalahan: {content}")
        elif role == "result":
            result_data, col_names = content
            with st.chat_message("assistant", avatar="🤖"):
                if result_data:
                    last_df = pd.DataFrame(result_data, columns=col_names)
                    last_df.index = last_df.index + 1
                    st.dataframe(last_df, use_container_width=True)
                else:
                    st.warning("📭 Tidak ada data.")
                    last_df = None
        elif role == "insight":
            with st.chat_message("assistant", avatar="💡"):
                st.markdown(f"**Analisis:** {content}")
        elif role == "viz_config":
            viz_config = content
            if last_df is not None and not last_df.empty:
                chart_type = viz_config.get("chart_type")
                x_col = viz_config.get("x_column")
                y_col = viz_config.get("y_column")
                
                if chart_type != "none":
                    cols_lower = {c.lower(): c for c in last_df.columns}
                    x_col = cols_lower.get(x_col.lower(), x_col) if x_col else None
                    y_col = cols_lower.get(y_col.lower(), y_col) if y_col else None

                    if x_col and y_col and x_col in last_df.columns and y_col in last_df.columns:
                        try:
                            template = "plotly_dark"
                            fig = None
                            
                            if chart_type == "bar":
                                df_sorted = last_df.sort_values(by=y_col, ascending=False).head(10)
                                fig = px.bar(
                                    df_sorted, 
                                    x=x_col, 
                                    y=y_col, 
                                    color=x_col,
                                    template=template,
                                    title=f"Top {y_col} by {x_col}",
                                    color_discrete_sequence=px.colors.qualitative.Vivid
                                )
                            elif chart_type == "line":
                                fig = px.line(
                                    last_df, 
                                    x=x_col, 
                                    y=y_col, 
                                    markers=True,
                                    template=template,
                                    title=f"Trend: {y_col} vs {x_col}",
                                    color_discrete_sequence=['#667eea']
                                )
                            elif chart_type == "pie":
                                fig = px.pie(
                                    last_df, 
                                    names=x_col, 
                                    values=y_col,
                                    hole=0.4,
                                    template=template,
                                    title=f"Distribution of {y_col}",
                                    color_discrete_sequence=px.colors.qualitative.Vivid
                                )
                            
                            if fig:
                                fig.update_layout(
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    font=dict(color="#e0e0e0"),
                                    title_font_size=20,
                                    title_font_color="#667eea",
                                    showlegend=True,
                                    height=500
                                )
                                with st.chat_message("assistant", avatar="📊"):
                                    st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass

# 4. PEMROSESAN INPUT
user_input = st.chat_input("💭 Tanyakan sesuatu tentang data Anda...")

process_trigger = False
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    save_history_to_disk("sql")
    process_trigger = True
elif len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1][0] == "user":
    user_input = st.session_state.chat_history[-1][1]
    process_trigger = True

if process_trigger:
    should_run = True
    if len(st.session_state.chat_history) > 1:
        if st.session_state.chat_history[-1][0] != "user":
            should_run = False
            
    if should_run:
        schema = get_current_schema()
        history_text = format_chat_history(st.session_state.chat_history[:-1])

        with st.spinner("🔍 Menganalisis pertanyaan..."):
            try:
                # 1. Generate SQL & Simpan
                sql_query = get_sql_query(user_input, schema, chat_history=history_text)
                st.session_state.chat_history.append(("assistant_sql", sql_query))
                save_history_to_disk("sql") # <--- SIMPAN
                
                # 2. Execute SQL
                result, columns = execute_sql_query(sql_query)
                
                if isinstance(result, str) and result.startswith("SQL Error"):
                    st.session_state.chat_history.append(("error", result))
                else:
                    st.session_state.chat_history.append(("result", (result, columns)))
                    save_history_to_disk("sql") # <--- SIMPAN DATA
                    
                    if result:
                        df_temp = pd.DataFrame(result, columns=columns)
                        
                        # 3. Insight & Viz
                        insight = generate_data_insight(user_input, df_temp)
                        st.session_state.chat_history.append(("insight", insight))
                        
                        viz_config = get_visualization_recommendation(user_input, df_temp)
                        st.session_state.chat_history.append(("viz_config", viz_config))
                
                save_history_to_disk("sql") # <--- SIMPAN FINAL
                st.rerun()
                        
            except Exception as e:
                st.session_state.chat_history.append(("error", f"System Error: {str(e)}"))
                save_history_to_disk("sql") # <--- SIMPAN ERROR
                st.rerun()
# Download Button
if len(st.session_state.chat_history) > 0:
    st.markdown("---")
    download_button(st.session_state.chat_history)