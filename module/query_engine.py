from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime
from module.config import GROQ_API_KEY, MODEL_NAME
import pandas as pd

def get_sql_query(user_query: str, schema_description: str,chat_history: str = "") -> str:
    # 1. Dapatkan tanggal hari ini agar AI paham konteks waktu
    # (Penting untuk pertanyaan seperti "penjualan bulan ini" atau "tahun lalu")
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 2. Prompt Engineering yang lebih spesifik untuk SQLite & E-Commerce
    template = """
    You are an expert SQLite Data Analyst for an E-Commerce company.
    Your task is to convert the user's natural language question into a valid SQLite query.

    ### Context:
    - Current Date: {current_date}
    - Database Schema:
    {schema_description}

    ### LIMITATION RULES (CRITICAL):
    1. **DEFAULT:** If the user DOES NOT specify a quantity, use `LIMIT 10` to keep the interface clean.
    2. **EXCEPTION:** If the user explicitly asks for "all", "semua", "seluruh", "total", or "list of all", **DO NOT USE LIMIT**.
    3. If the user specifies a number (e.g., "top 5"), use that specific LIMIT.

    ### EXAMPLE BEHAVIOR:
    User: "Tampilkan produk" -> SELECT * FROM products LIMIT 10
    User: "Tampilkan 5 produk" -> SELECT * FROM products LIMIT 5
    User: "Tampilkan SELURUH produk" -> SELECT * FROM products (NO LIMIT)
    User: "List semua pelanggan" -> SELECT * FROM customers (NO LIMIT)

    ### CRITICAL INSTRUCTIONS FOR FOLLOW-UP QUESTIONS:
    1. Check the 'Conversation History' CAREFULLY.
    2. If the user asks a short follow-up question (e.g., "How about Jakarta?", "And in 2024?", "What about electronics?"), you MUST maintain the context of the **IMMEDIATELY PRECEDING SQL QUERY**.
    3. **DO NOT** create a simple "SELECT * FROM table" query if the previous topic was specific (like "best selling products" or "total revenue").
    4. **REUSE** the same tables, joins, and logic from the previous SQL query, and ONLY change the filter condition (e.g., change WHERE city = 'Kendari' to WHERE city = 'Jakarta').

    ### Strict Rules:
    1. Output ONLY the SQL query. No markdown, no explanations, no ```sql fences.
    2. Use 'single quotes' for string literals (e.g., city = 'Bandung').
    3. Use "double quotes" for column names if they contain spaces or special chars.
    4. For date filtering, use SQLite functions like strftime() or date().
    5. If the user asks about "sales" or "revenue", calculate using SUM(total_amount) or SUM(subtotal).
    6. LIMIT the results to 10 unless the user asks for more (to keep UI clean).
    7. The user may ask in INDONESIAN language. Translate the intent accurately to SQL.

    ### User Question:
    {user_query}

    ### SQL Query:
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=MODEL_NAME,
        temperature=0 # Set 0 agar hasil konsisten dan tidak kreatif berlebihan
    )

    # 3. Merakit Chain
    chain = prompt | llm | StrOutputParser()

    # 4. Eksekusi
    return chain.invoke({
        "user_query": user_query,
        "schema_description": schema_description,
        "current_date": current_date,
        "chat_history": chat_history
    }).strip()


def generate_data_insight(user_query: str, df: pd.DataFrame) -> str:
    """
    Fungsi ini menerima pertanyaan user dan Dataframe hasil query,
    lalu meminta LLM untuk memberikan analisis singkat.
    """
    
    # Kita hanya mengirim maksimal 10 baris pertama agar tidak boros token
    # dan menjaga performa tetap cepat.
    data_preview = df.head(10).to_markdown(index=False)
    
    template = """
    Anda adalah Senior Data Analyst. Tugas Anda adalah memberikan insight singkat 
    berdasarkan data yang ditemukan untuk menjawab pertanyaan user.

    Pertanyaan User: {user_query}
    
    Data Hasil Query (Preview):
    {data_preview}
    
    Instruksi:
    1. Jelaskan apa arti data tersebut dalam konteks bisnis (maksimal 2-3 kalimat).
    2. Jika ada tren atau angka yang mencolok (tertinggi/terendah), sebutkan.
    3. Gunakan Bahasa Indonesia yang profesional dan luwes.
    4. Jangan mengulang isi tabel mentah-mentah, berikan kesimpulan.
    
    Insight Singkat:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=MODEL_NAME,
        temperature=0.5 # Sedikit kreatif untuk narasi
    )
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "user_query": user_query,
        "data_preview": data_preview
    })

def get_visualization_recommendation(user_query: str, df: pd.DataFrame) -> dict:
    """
    Meminta AI untuk menentukan jenis grafik terbaik berdasarkan konteks data dan pertanyaan.
    Output berupa dictionary (JSON).
    """
    # Jika data terlalu sedikit atau terlalu banyak kolom, tidak usah divisualisasikan
    if len(df) < 2 or len(df.columns) > 5:
         return {"chart_type": "none"}
         
    data_preview = df.head(5).to_markdown(index=False)
    columns_list = ", ".join(df.columns.tolist())

    template = """
    You are a Data Visualization Expert. Your task is to recommend the BEST type of chart
    to visualize the provided data, based on the user's intent.

    User Question: {user_query}
    Available Columns: {columns_list}
    Data Preview:
    {data_preview}

    Rules:
    1.  Analyze the user intent. If they ask for trend over time -> 'line'. Comparison between categories -> 'bar'. Composition/Percentage -> 'pie'.
    2.  If the data is NOT suitable for visualization (e.g., just a list of names), return 'none'.
    3.  Select the most appropriate column for the X-axis (usually categorical or date) and Y-axis (must be numeric).
    4.  Ensure the chosen Y-column is actually numeric in the data preview.

    Output MUST be a strictly valid JSON object with these keys only:
    - "chart_type": one of ["bar", "line", "pie", "none"]
    - "x_column": "name of column for X axis (or category for pie)"
    - "y_column": "name of column for Y axis (or values for pie)"
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0)
    # Menggunakan JsonOutputParser agar AI dipaksa mengeluarkan format JSON yang valid
    chain = prompt | llm | JsonOutputParser()

    try:
        response = chain.invoke({
            "user_query": user_query,
            "columns_list": columns_list,
            "data_preview": data_preview
        })
        return response
    except Exception as e:
        # Jika AI gagal menghasilkan JSON valid, fallback ke tidak ada chart
        print(f"Viz Error: {e}")
        return {"chart_type": "none"}