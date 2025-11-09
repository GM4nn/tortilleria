import sqlite3

class DatabaseManager:
    
    def __init__(self, db_name="tortilleria.db"):
        self.db_name = db_name
        self.init_database()


    def init_database(self):

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Products Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                active INTEGER DEFAULT 1
            )
        """)
        
        # Sales Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total REAL NOT NULL
            )
        """)
        
        # Detail sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                quantity REAL,
                unit_price REAL,
                subtotal REAL,
                FOREIGN KEY (sale_id) REFERENCES ventas(id),
                FOREIGN KEY (product_id) REFERENCES productos(id)
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            productos_default = [
                ("Tortilla de Maíz", 18.00),
                ("Tostadas", 15.00),
                ("Tlayudas", 25.00),
                ("Sopes", 12.00),
                ("Tamales", 20.00),
                ("Salsa Roja", 30.00),
                ("Salsa Verde", 30.00),
                ("Frijoles Refritos", 25.00),
                ("Quesadillas", 35.00),
                ("Gorditas", 22.00),
            ]
            cursor.executemany(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                productos_default
            )
        
        conn.commit()
        conn.close()


    def get_products(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products WHERE active = 1")
        productos = cursor.fetchall()
        conn.close()
        return productos


    def save_sale(self, items, total):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:

            cursor.execute(
                "INSERT INTO sales (total) VALUES (?)",
                (total,)
            )
            sale_id = cursor.lastrowid
            
            for item in items:
                cursor.execute(
                    """INSERT INTO sales_detail 
                       (sale_id, product_id, quantity, unit_price, subtotal)
                       VALUES (?, ?, ?, ?, ?)""",
                    (sale_id, item['id'], item['quantity'],
                     item['price'], item['subtotal'])
                )
            
            conn.commit()
            return True, sale_id
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()


    def get_sales_today(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*), SUM(total) 
            FROM sales 
            WHERE DATE(date) = DATE('now')
        """)
        result = cursor.fetchone()
        conn.close()
        return result[0] or 0, result[1] or 0.0


    def add_product(self, name, price):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                (name, price)
            )
            conn.commit()
            return True, cursor.lastrowid
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
    
    def update_product(self, product_id, name, price):

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE products SET name = ?, price = ? WHERE id = ?",
                (name, price, product_id)
            )
            conn.commit()
            return True, "Producto actualizado"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
    
    def delete_product(self, product_id):

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE products SET active = 0 WHERE id = ?",
                (product_id,)
            )
            conn.commit()
            return True, "Producto eliminado"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()