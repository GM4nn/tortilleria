"""
Script para copiar TODAS las órdenes de SQLite a Neon (bulk insert).
Uso: python sync_orders_to_neon.py
"""

from sqlalchemy import create_engine, text

NEON_URL = "postgresql://neondb_owner:npg_D6tI8ynNBopG@ep-dark-thunder-ac9gb4ns-pooler.sa-east-1.aws.neon.tech/tortilleria?sslmode=require"
SQLITE_URL = "sqlite:///tortilleria.db"
BATCH = 100

neon = create_engine(NEON_URL)
sqlite = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


def bulk_insert(conn, sql, rows, label):
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        conn.execute(text(sql), batch)
        print(f"  {label}: {min(i+BATCH, len(rows))}/{len(rows)}")


def sync():
    # Leer todo de SQLite
    with sqlite.connect() as s:
        products = [dict(id=r[0], name=r[1], price=r[2], active=bool(r[3]))
                    for r in s.execute(text(
                        "SELECT id, name, price, active FROM products")).fetchall()]
        print(f"SQLite: {len(products)} productos")

        customers = [dict(id=r[0], name=r[1], dir=r[2], cat=r[3], phone=r[4], active=bool(r[5]))
                     for r in s.execute(text(
                         "SELECT id, customer_name, customer_direction, customer_category, "
                         "customer_phone, active FROM customers")).fetchall()]
        print(f"SQLite: {len(customers)} clientes")

        orders = [dict(id=r[0], date=r[1], total=r[2], cid=r[3], status=r[4],
                       completed=r[5], notes=r[6], paid=r[7])
                  for r in s.execute(text(
                      "SELECT id, date, total, customer_id, status, completed_at, notes, amount_paid "
                      "FROM orders")).fetchall()]
        print(f"SQLite: {len(orders)} ordenes")

        details = [dict(id=r[0], oid=r[1], pid=r[2], qty=r[3], price=r[4], sub=r[5])
                   for r in s.execute(text(
                       "SELECT id, order_id, product_id, quantity, unit_price, subtotal "
                       "FROM order_details")).fetchall()]
        print(f"SQLite: {len(details)} detalles")

    # Escribir en Neon
    with neon.connect() as n:
        # Limpiar
        n.execute(text("DELETE FROM order_details"))
        n.execute(text("DELETE FROM orders"))
        n.commit()
        print("\nNeon: Limpiado orders y order_details")

        # Products (upsert)
        if products:
            bulk_insert(n,
                "INSERT INTO products (id, name, price, active) "
                "VALUES (:id, :name, :price, :active) "
                "ON CONFLICT (id) DO NOTHING",
                products, "Productos")

        # Customers (upsert - ON CONFLICT skip)
        if customers:
            bulk_insert(n,
                "INSERT INTO customers (id, customer_name, customer_direction, "
                "customer_category, customer_phone, active) "
                "VALUES (:id, :name, :dir, :cat, :phone, :active) "
                "ON CONFLICT (id) DO NOTHING",
                customers, "Clientes")

        # Orders (bulk)
        if orders:
            bulk_insert(n,
                "INSERT INTO orders (id, date, total, customer_id, status, "
                "completed_at, notes, amount_paid) "
                "VALUES (:id, :date, :total, :cid, :status, :completed, :notes, :paid)",
                orders, "Ordenes")

        # Details (bulk)
        if details:
            bulk_insert(n,
                "INSERT INTO order_details (id, order_id, product_id, quantity, "
                "unit_price, subtotal) VALUES (:id, :oid, :pid, :qty, :price, :sub)",
                details, "Detalles")

        n.commit()
        print("\nCommit OK!")

    # Verificar
    with neon.connect() as n:
        count = n.execute(text("SELECT COUNT(*) FROM orders")).fetchone()[0]
        print(f"Verificacion: {count} ordenes en Neon")


if __name__ == "__main__":
    sync()
