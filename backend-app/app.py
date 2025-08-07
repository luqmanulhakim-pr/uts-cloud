# app.py
from flask import Flask, jsonify, request
import mysql.connector
import os
from flask_cors import CORS # Import CORS untuk mengizinkan permintaan dari frontend

app = Flask(__name__)
CORS(app) # Aktifkan CORS untuk semua rute

# Konfigurasi koneksi database RDS
# Menggunakan variabel lingkungan untuk keamanan dan fleksibilitas
DB_HOST = os.environ.get('DB_HOST', 'uts-db.cdyg220estzd.ap-southeast-2.rds.amazonaws.com') # Ganti dengan endpoint RDS Anda (dari AWS RDS console)
DB_USER = os.environ.get('DB_USER', 'admin') # Ganti dengan username Master RDS Anda
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Ah_hoohLah*123') # Ganti dengan password Master RDS Anda
DB_NAME = os.environ.get('DB_NAME', 'uts_db_product') # Nama database yang Anda buat

def get_db_connection():
    """Membuat dan mengembalikan koneksi database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("Connected to MySQL database!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def initialize_db():
    """Menginisialisasi database: membuat tabel dan menyisipkan data dummy jika kosong."""
    conn = get_db_connection()
    if conn is None:
        print("Failed to get DB connection for initialization.")
        return

    cursor = conn.cursor()
    try:
        # Buat tabel jika belum ada
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(255)
            );
        """
        cursor.execute(create_table_sql)
        print("Products table created or already exists.")

        # Sisipkan data dummy jika tabel kosong
        cursor.execute("SELECT COUNT(*) AS count FROM products")
        result = cursor.fetchone()
        if result[0] == 0:
            insert_data_sql = f"""
                INSERT INTO products (name, price, image_url) VALUES
                ('Produk A', 100.00, 'https://uts-bucket-assets.s3.ap-southeast-2.amazonaws.com/product_a.jpg'),
                ('Produk B', 150.00, 'https://uts-bucket-assets.s3.ap-southeast-2.amazonaws.com/product_b.jpg');
            """
            cursor.execute(insert_data_sql)
            conn.commit()
            print("Dummy data inserted.")
        else:
            print("Products table already contains data.")

    except mysql.connector.Error as err:
        print(f"Error during database initialization: {err}")
    finally:
        cursor.close()
        conn.close()

# Inisialisasi database saat aplikasi dimulai
# Penting: Pastikan ini dijalankan dalam konteks aplikasi Flask
with app.app_context():
    initialize_db()

# Endpoint untuk mendapatkan semua produk (READ - All)
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True) # Mengembalikan hasil sebagai dictionary
    try:
        sql = 'SELECT id, name, price, image_url FROM products ORDER BY id DESC' # Urutkan berdasarkan ID terbaru
        cursor.execute(sql)
        products = cursor.fetchall()
        return jsonify(products)
    except mysql.connector.Error as err:
        print(f"Error fetching products: {err}")
        return jsonify({"error": "Error fetching products"}), 500
    finally:
        cursor.close()
        conn.close()

# Endpoint untuk mendapatkan produk berdasarkan ID (READ - Single)
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        sql = 'SELECT id, name, price, image_url FROM products WHERE id = %s'
        cursor.execute(sql, (product_id,))
        product = cursor.fetchone()
        if product:
            return jsonify(product)
        else:
            return jsonify({"message": "Product not found"}), 404
    except mysql.connector.Error as err:
        print(f"Error fetching product: {err}")
        return jsonify({"error": "Error fetching product"}), 500
    finally:
        cursor.close()
        conn.close()

# Endpoint untuk membuat produk baru (CREATE)
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    image_url = data.get('image_url')

    if not name or price is None: # Pastikan price tidak None
        return jsonify({"message": "Name and price are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        sql = 'INSERT INTO products (name, price, image_url) VALUES (%s, %s, %s)'
        cursor.execute(sql, (name, price, image_url))
        conn.commit()
        return jsonify({"message": "Product added successfully", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        print(f"Error adding product: {err}")
        return jsonify({"error": "Error adding product", "details": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Endpoint untuk memperbarui produk (UPDATE)
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    image_url = data.get('image_url')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        sql = 'UPDATE products SET name = %s, price = %s, image_url = %s WHERE id = %s'
        cursor.execute(sql, (name, price, image_url, product_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Product not found or no changes made"}), 404
        return jsonify({"message": "Product updated successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error updating product: {err}")
        return jsonify({"error": "Error updating product", "details": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Endpoint untuk menghapus produk (DELETE)
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        sql = 'DELETE FROM products WHERE id = %s'
        cursor.execute(sql, (product_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Product not found"}), 404
        return jsonify({"message": "Product deleted successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error deleting product: {err}")
        return jsonify({"error": "Error deleting product", "details": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # Jalankan aplikasi Flask
    # Di lingkungan produksi, disarankan menggunakan Gunicorn atau sejenisnya
    app.run(host='0.0.0.0', port=5000)
