import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

# Inisialisasi Faker dengan lokasi Indonesia
fake = Faker('id_ID')

# Nama database
DB_NAME = "ecommerce.db"

def create_tables(cursor):
    # Tabel Produk
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price INTEGER,
        stock_quantity INTEGER
    )
    ''')

    # Tabel Pelanggan
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        join_date DATE
    )
    ''')

    # Tabel Transaksi (Orders)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date DATE,
        total_amount INTEGER DEFAULT 0,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    )
    ''')

    # Tabel Detail Item (Order Items)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        subtotal INTEGER,
        FOREIGN KEY(order_id) REFERENCES orders(order_id),
        FOREIGN KEY(product_id) REFERENCES products(product_id)
    )
    ''')
    print("✅ Tabel berhasil dibuat.")

def generate_data(cursor):
    # --- 1. Generate Produk (50 item) ---
    categories = {
        'Elektronik': ['Laptop', 'Smartphone', 'Headphone', 'Monitor', 'Mouse', 'Keyboard'],
        'Pakaian': ['Kemeja Batik', 'Kaos Polos', 'Celana Jeans', 'Jaket Hoodie', 'Sepatu Sneakers'],
        'Perabot': ['Meja Kerja', 'Kursi Gaming', 'Lampu Tidur', 'Rak Buku', 'Lemari'],
        'Buku': ['Novel', 'Komik', 'Buku Pemrograman', 'Ensiklopedia']
    }
    
    products = []
    print("⏳ Sedang membuat data produk...")
    for _ in range(50):
        cat = random.choice(list(categories.keys()))
        item = random.choice(categories[cat])
        brand = fake.word().capitalize()
        name = f"{item} {brand}"
        
        # Harga acak berdasarkan kategori (dalam Rupiah)
        if cat == 'Elektronik':
            price = random.randint(1_000_000, 15_000_000)
        elif cat == 'Perabot':
            price = random.randint(500_000, 3_000_000)
        else:
            price = random.randint(50_000, 500_000)
            
        # Bulatkan harga ke ribuan terdekat agar rapi
        price = round(price, -3)
        stock = random.randint(5, 100)
        
        cursor.execute('INSERT INTO products (name, category, price, stock_quantity) VALUES (?, ?, ?, ?)', 
                       (name, cat, price, stock))
        products.append(cursor.lastrowid)

    # --- 2. Generate Pelanggan (100 orang) ---
    customers = []
    print("⏳ Sedang membuat data pelanggan...")
    cities = ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Makassar', 'Semarang', 'Yogyakarta', 'Kendari', 'Denpasar']
    
    for _ in range(100):
        name = fake.name()
        city = random.choice(cities)
        join_date = fake.date_between(start_date='-2y', end_date='today')
        
        cursor.execute('INSERT INTO customers (name, city, join_date) VALUES (?, ?, ?)', 
                       (name, city, join_date))
        customers.append(cursor.lastrowid)

    # --- 3. Generate Orders & Order Items (200 Transaksi) ---
    print("⏳ Sedang membuat transaksi penjualan...")
    for _ in range(200):
        cust_id = random.choice(customers)
        # Tanggal order dalam 1 tahun terakhir
        ord_date = fake.date_between(start_date='-1y', end_date='today')
        
        # Buat order kosong dulu
        cursor.execute('INSERT INTO orders (customer_id, order_date) VALUES (?, ?)', (cust_id, ord_date))
        order_id = cursor.lastrowid
        
        # Isi keranjang belanja (1-5 item per order)
        num_items = random.randint(1, 5)
        current_order_total = 0
        
        for _ in range(num_items):
            prod_id = random.choice(products)
            qty = random.randint(1, 3)
            
            # Ambil harga produk
            cursor.execute('SELECT price FROM products WHERE product_id = ?', (prod_id,))
            price = cursor.fetchone()[0]
            
            subtotal = price * qty
            current_order_total += subtotal
            
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, subtotal)
                VALUES (?, ?, ?, ?)
            ''', (order_id, prod_id, qty, subtotal))
            
        # Update total amount di tabel orders
        cursor.execute('UPDATE orders SET total_amount = ? WHERE order_id = ?', (current_order_total, order_id))

    print("✅ Data dummy berhasil di-generate!")

def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Bersihkan data lama jika ada (opsional, agar tidak duplikat saat run ulang)
    cursor.execute("DROP TABLE IF EXISTS order_items")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS products")
    
    create_tables(cursor)
    generate_data(cursor)
    
    conn.commit()
    conn.close()
    print(f"🎉 Database '{DB_NAME}' siap digunakan untuk proyek LLM kamu!")

if __name__ == "__main__":
    main()