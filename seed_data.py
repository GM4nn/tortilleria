"""
Script de datos de prueba para la Tortilleria.
Genera 6 meses de datos realistas (Aug 2025 - Feb 2026).
Lee datos base desde CSVs en app/data/default/.

Uso: python seed_data.py
"""

import csv
import random
from datetime import datetime, timedelta, date
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.data.database import SessionLocal, engine, Base
from app.models import (
    Customer, Product, Supplier, Supply, SupplyPurchase,
    Sale, SaleDetail, Order, OrderDetail
)
from app.models.cash_cut import CashCut

random.seed(42)

START_DATE = date(2025, 8, 21)
END_DATE = date(2026, 2, 21)

CSV_DIR = Path(__file__).parent / "app" / "data" / "default"

# Configuración realista de compras por insumo
# - quantities: cantidades reales que se compran (números redondos)
# - daily_consumption: rango de consumo diario en la tortillería
PURCHASE_CONFIG = {
    "Maíz": {
        "freq_days": (2, 4),
        "quantities": [25, 30, 35, 40, 45, 50],
        "price_range": (8.50, 10.50),
        "unit": "kilos",
        "daily_consumption": (10, 18),
    },
    "Cal": {
        "freq_days": (12, 20),
        "quantities": [5, 8, 10, 12, 15],
        "price_range": (3.50, 5.50),
        "unit": "kilos",
        "daily_consumption": (0.4, 0.9),
    },
    "Harina": {
        "freq_days": (5, 8),
        "quantities": [15, 20, 25, 30],
        "price_range": (12.50, 15.50),
        "unit": "kilos",
        "daily_consumption": (3, 6),
    },
    "Feca de maiz": {
        "freq_days": (7, 14),
        "quantities": [2, 3, 5, 8, 10],
        "price_range": (45.00, 65.00),
        "unit": "costales",
        "daily_consumption": (0.3, 0.8),
    },
}

# ─── Helpers ─────────────────────────────────────────────────

def random_time(d):
    """Genera un datetime con hora aleatoria entre 7am y 8pm"""
    hour = random.randint(7, 19)
    minute = random.randint(0, 59)
    return datetime(d.year, d.month, d.day, hour, minute, random.randint(0, 59))


def date_range(start, end):
    """Genera todas las fechas entre start y end"""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


# ─── Seed functions ──────────────────────────────────────────

def seed_customers(db):
    """Lee customers.csv e inserta todos los clientes (sin verificar duplicados)."""
    created = []
    with open(CSV_DIR / "customers.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            c = Customer(
                customer_name=row["customer_name"],
                customer_direction=row["customer_direction"] or None,
                customer_category=row["customer_category"],
                customer_phone=row["customer_phone"] or None,
                active=bool(int(row["active"])),
                active2=bool(int(row["active2"])),
            )
            db.add(c)
            created.append(c)
    db.flush()
    print(f"  Clientes: {len(created)}")
    return created


def seed_products(db):
    """Lee products.csv e inserta todos los productos."""
    created = []
    with open(CSV_DIR / "products.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = Product(
                icon=row["icon"],
                name=row["name"],
                price=float(row["price"]),
                active=row["active"].lower() == "true",
            )
            db.add(p)
            created.append(p)
    db.flush()
    print(f"  Productos: {len(created)}")
    return created


def seed_suppliers(db):
    """Lee suppliers.csv e inserta todos los proveedores."""
    created = []
    with open(CSV_DIR / "suppliers.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s = Supplier(
                supplier_name=row["supplier_name"],
                contact_name=row["contact_name"],
                phone=row["phone"],
                email=row["email"],
                address=row["address"],
                city=row["city"],
                product_type=row["product_type"],
                active=bool(int(row["active"])),
            )
            db.add(s)
            created.append(s)
    db.flush()
    print(f"  Proveedores: {len(created)}")
    return created


def seed_supplies(db, suppliers):
    """Lee supplies.csv e inserta todos los insumos."""
    supplier_map = {s.supplier_name: s for s in suppliers}
    created = []
    with open(CSV_DIR / "supplies.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            supplier = supplier_map.get(row["supplier_name"])
            if not supplier:
                print(f"  AVISO: Proveedor '{row['supplier_name']}' no encontrado para '{row['supply_name']}'. Saltando.")
                continue
            s = Supply(supply_name=row["supply_name"], supplier_id=supplier.id, unit=row["unit"])
            db.add(s)
            created.append(s)
    db.flush()
    print(f"  Insumos: {len(created)}")
    return created


def seed_supply_purchases(db, supplies, suppliers):
    """Genera compras realistas con remaining (lo que sobro del periodo anterior).

    Reglas:
    - Primera compra: remaining = 0
    - Compras posteriores: remaining = lo que sobro del consumo del periodo anterior
    """
    purchase_count = 0
    supplier_map = {s.id: s for s in suppliers}

    for supply in supplies:
        cfg = PURCHASE_CONFIG.get(supply.supply_name)
        if not cfg:
            print(f"  AVISO: Sin config de compras para '{supply.supply_name}'. Saltando.")
            continue
        supplier = supplier_map.get(supply.supplier_id)

        current_date = START_DATE
        stock = 0.0
        is_first = True
        prev_date = None

        while current_date <= END_DATE:
            qty = random.choice(cfg["quantities"])
            price = round(random.uniform(*cfg["price_range"]), 2)
            total = round(qty * price, 2)

            remaining = 0.0
            if not is_first:
                # Simular consumo del periodo anterior
                days_elapsed = (current_date - prev_date).days
                daily_rate = round(random.uniform(*cfg["daily_consumption"]), 2)
                consumed = round(min(daily_rate * days_elapsed, stock), 2)
                remaining = round(max(0, stock - consumed), 2)

            p = SupplyPurchase(
                supply_id=supply.id,
                supplier_id=supplier.id,
                purchase_date=current_date,
                quantity=qty,
                unit=cfg["unit"],
                unit_price=price,
                total_price=total,
                remaining=remaining,
            )
            db.add(p)
            purchase_count += 1

            stock = remaining + qty
            prev_date = current_date
            is_first = False

            freq = random.randint(*cfg["freq_days"])
            current_date += timedelta(days=freq)

    db.flush()
    print(f"  Compras de insumos: {purchase_count}")


def delete_supply_data(db):
    """Elimina todas las compras de insumos existentes."""
    deleted_p = db.query(SupplyPurchase).delete()
    db.flush()
    print(f"  Eliminados: {deleted_p} compras")


def seed_orders(db, customers, products):
    order_count = 0
    detail_count = 0
    batch_orders = []
    batch_details = []  # list of (order_index, prod, qty, subtotal)

    for d in date_range(START_DATE, END_DATE):
        weekday = d.weekday()
        num_orders = random.choices([0, 1, 2, 3], weights=[10, 40, 35, 15] if weekday < 6 else [40, 35, 20, 5])[0]

        for _ in range(num_orders):
            customer = random.choice(customers)
            dt = random_time(d)

            num_products = random.randint(1, 4)
            selected = random.sample(products, min(num_products, len(products)))

            order_total = 0.0
            details = []
            for prod in selected:
                qty = round(random.choice([0.5, 1, 1.5, 2, 3, 5, 10]), 1)
                subtotal = round(qty * prod.price, 2)
                order_total += subtotal
                details.append((prod, qty, subtotal))

            status = random.choices(["completado", "pendiente", "cancelado"], weights=[75, 15, 10])[0]
            completed_at = None
            if status == "completado":
                completed_at = dt + timedelta(minutes=random.randint(15, 120))

            order = Order(
                date=dt, total=round(order_total, 2),
                customer_id=customer.id, status=status, completed_at=completed_at,
            )
            batch_orders.append((order, details))
            order_count += 1

    # Insertar en batches para reducir round-trips
    BATCH_SIZE = 50
    for i in range(0, len(batch_orders), BATCH_SIZE):
        chunk = batch_orders[i:i+BATCH_SIZE]
        for order, details in chunk:
            db.add(order)
        db.flush()  # 1 flush por batch, asigna IDs
        for order, details in chunk:
            for prod, qty, subtotal in details:
                db.add(OrderDetail(
                    order_id=order.id, product_id=prod.id,
                    quantity=qty, unit_price=prod.price, subtotal=subtotal,
                ))
                detail_count += 1
        db.flush()
        if (i // BATCH_SIZE) % 5 == 0:
            print(f"    ... pedidos batch {i+len(chunk)}/{len(batch_orders)}")

    print(f"  Pedidos: {order_count}")
    print(f"  Detalle pedidos: {detail_count}")


def seed_sales(db, customers, products):
    """Ventas POS (mostrador). Usan customer_id del Mostrador generico."""
    mostrador = db.query(Customer).filter(Customer.active2 == False).first()
    if not mostrador:
        mostrador = db.query(Customer).filter(Customer.customer_category == "Mostrador").first()
    if not mostrador:
        print("  AVISO: No se encontro cliente Mostrador. Saltando ventas POS.")
        return

    sale_count = 0
    detail_count = 0
    batch_sales = []

    for d in date_range(START_DATE, END_DATE):
        weekday = d.weekday()
        base = random.randint(8, 15) if weekday >= 5 else random.randint(5, 12)

        for _ in range(base):
            dt = random_time(d)
            num_products = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            selected = random.sample(products, min(num_products, len(products)))

            sale_total = 0.0
            details = []
            for prod in selected:
                qty = round(random.choice([0.5, 1, 1.5, 2, 3]), 1)
                subtotal = round(qty * prod.price, 2)
                sale_total += subtotal
                details.append((prod, qty, subtotal))

            sale = Sale(date=dt, total=round(sale_total, 2), customer_id=mostrador.id)
            batch_sales.append((sale, details))
            sale_count += 1

    # Insertar en batches
    BATCH_SIZE = 50
    for i in range(0, len(batch_sales), BATCH_SIZE):
        chunk = batch_sales[i:i+BATCH_SIZE]
        for sale, details in chunk:
            db.add(sale)
        db.flush()
        for sale, details in chunk:
            for prod, qty, subtotal in details:
                db.add(SaleDetail(
                    sale_id=sale.id, product_id=prod.id,
                    quantity=qty, unit_price=prod.price, subtotal=subtotal,
                ))
                detail_count += 1
        db.flush()
        if (i // BATCH_SIZE) % 10 == 0:
            print(f"    ... ventas batch {i+len(chunk)}/{len(batch_sales)}")

    db.flush()
    print(f"  Ventas POS: {sale_count}")
    print(f"  Detalle ventas: {detail_count}")


# ─── Main ────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("SEED DATA - Tortillería")
    print(f"Período: {START_DATE} → {END_DATE}")
    print("=" * 50)

    with SessionLocal() as db:
        try:
            print("\nCreando datos base desde CSVs...")
            customers = seed_customers(db)
            products = seed_products(db)
            suppliers = seed_suppliers(db)
            supplies = seed_supplies(db, suppliers)

            print("\nCreando compras de insumos...")
            seed_supply_purchases(db, supplies, suppliers)

            print("\nCreando pedidos (6 meses)...")
            seed_orders(db, customers, products)

            print("\nCreando ventas POS (6 meses)...")
            seed_sales(db, customers, products)

            db.commit()
            print("\n✅ Datos insertados correctamente.")

        except Exception as e:
            db.rollback()
            print(f"\n❌ Error: {e}")
            raise


def main_purchases_only():
    """Re-seed solo compras y consumos de insumos."""
    print("=" * 50)
    print("RE-SEED COMPRAS DE INSUMOS")
    print(f"Periodo: {START_DATE} -> {END_DATE}")
    print("=" * 50)

    with SessionLocal() as db:
        try:
            print("\nEliminando compras existentes...")
            delete_supply_data(db)

            suppliers = db.query(Supplier).all()
            supplies = db.query(Supply).all()
            print(f"  Proveedores: {len(suppliers)}")
            print(f"  Insumos: {len(supplies)}")

            if not suppliers or not supplies:
                print("  No hay proveedores/insumos. Ejecuta primero: python seed_data.py")
                sys.exit(1)

            print("\nCreando compras realistas...")
            seed_supply_purchases(db, supplies, suppliers)

            db.commit()
            print("\nCompras re-generadas correctamente.")

        except Exception as e:
            db.rollback()
            print(f"\nError: {e}")
            raise


def main_today():
    """Genera ventas y pedidos de HOY para probar corte de caja."""
    from app.constants import mexico_now
    today = mexico_now().date()

    print("=" * 50)
    print("SEED DATA - Datos de HOY (Corte de Caja)")
    print(f"Fecha: {today}")
    print("=" * 50)

    with SessionLocal() as db:
        try:
            products = seed_products(db)

            # Mostrador customer
            mostrador = db.query(Customer).filter(Customer.active2 == False).first()
            if not mostrador:
                mostrador = db.query(Customer).filter(Customer.customer_category == "Mostrador").first()
            if not mostrador:
                print("  No se encontro cliente Mostrador.")
                sys.exit(1)

            customers = db.query(Customer).filter(Customer.active2 == True).all()
            if not customers:
                customers = db.query(Customer).filter(Customer.customer_category != "Mostrador").all()

            # --- Ventas POS de hoy ---
            sale_count = 0
            num_sales = random.randint(8, 15)
            for _ in range(num_sales):
                dt = random_time(today)
                num_products = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
                selected = random.sample(products, min(num_products, len(products)))

                sale_total = 0.0
                details = []
                for prod in selected:
                    qty = round(random.choice([0.5, 1, 1.5, 2, 3]), 1)
                    subtotal = round(qty * prod.price, 2)
                    sale_total += subtotal
                    details.append((prod, qty, subtotal))

                sale = Sale(date=dt, total=round(sale_total, 2), customer_id=mostrador.id)
                db.add(sale)
                db.flush()

                for prod, qty, subtotal in details:
                    db.add(SaleDetail(
                        sale_id=sale.id, product_id=prod.id,
                        quantity=qty, unit_price=prod.price, subtotal=subtotal,
                    ))
                sale_count += 1

            print(f"  Ventas POS hoy: {sale_count}")

            # --- Pedidos de hoy ---
            order_count = 0
            num_orders = random.randint(2, 5)
            for _ in range(num_orders):
                if not customers:
                    break
                customer = random.choice(customers)
                dt = random_time(today)
                num_products = random.randint(1, 4)
                selected = random.sample(products, min(num_products, len(products)))

                order_total = 0.0
                details = []
                for prod in selected:
                    qty = round(random.choice([0.5, 1, 1.5, 2, 3, 5, 10]), 1)
                    subtotal = round(qty * prod.price, 2)
                    order_total += subtotal
                    details.append((prod, qty, subtotal))

                status = random.choices(
                    ["completado", "pendiente", "cancelado"],
                    weights=[70, 20, 10]
                )[0]
                completed_at = None
                if status == "completado":
                    completed_at = dt + timedelta(minutes=random.randint(15, 120))

                order = Order(
                    date=dt, total=round(order_total, 2),
                    customer_id=customer.id, status=status,
                    completed_at=completed_at,
                )
                db.add(order)
                db.flush()

                for prod, qty, subtotal in details:
                    db.add(OrderDetail(
                        order_id=order.id, product_id=prod.id,
                        quantity=qty, unit_price=prod.price, subtotal=subtotal,
                    ))
                order_count += 1

            print(f"  Pedidos hoy: {order_count}")

            db.commit()
            print("\nDatos de hoy insertados correctamente.")

        except Exception as e:
            db.rollback()
            print(f"\nError: {e}")
            raise


def seed_cash_cuts(db):
    """Genera cortes de caja diarios basados en ventas y pedidos existentes."""
    from sqlalchemy import func as sqlfunc

    cut_count = 0

    for d in date_range(START_DATE, END_DATE):
        day_start = datetime(d.year, d.month, d.day)
        day_end = day_start + timedelta(days=1)

        # Get actual sales for this day
        sales_result = db.query(
            sqlfunc.count(Sale.id),
            sqlfunc.coalesce(sqlfunc.sum(Sale.total), 0.0)
        ).filter(Sale.date >= day_start, Sale.date < day_end).first()

        sales_count = sales_result[0] or 0
        sales_total = float(sales_result[1] or 0.0)

        # Get completed orders for this day
        orders_result = db.query(
            sqlfunc.count(Order.id),
            sqlfunc.coalesce(sqlfunc.sum(Order.total), 0.0)
        ).filter(
            Order.status == 'completado',
            Order.completed_at >= day_start,
            Order.completed_at < day_end,
        ).first()

        orders_count = orders_result[0] or 0
        orders_total = float(orders_result[1] or 0.0)

        expected_total = sales_total + orders_total

        # Skip days with no activity
        if sales_count == 0 and orders_count == 0:
            continue

        # Simulate declared amounts with realistic variance
        # 70% exact, 20% small difference, 10% notable difference
        variance_type = random.choices(
            ['exact', 'small', 'notable'],
            weights=[70, 20, 10]
        )[0]

        if variance_type == 'exact':
            diff = 0.0
        elif variance_type == 'small':
            diff = round(random.uniform(-20, 15), 2)
        else:
            diff = round(random.uniform(-80, -20) if random.random() < 0.7 else random.uniform(20, 50), 2)

        declared_total = round(expected_total + diff, 2)

        # Split declared into payment methods realistically
        # 60-80% cash, 10-25% card, 5-15% transfer
        cash_pct = random.uniform(0.60, 0.80)
        card_pct = random.uniform(0.10, 0.25)
        transfer_pct = 1.0 - cash_pct - card_pct

        declared_cash = round(declared_total * cash_pct, 2)
        declared_card = round(declared_total * card_pct, 2)
        declared_transfer = round(declared_total - declared_cash - declared_card, 2)

        # Close time: between 7pm and 9pm
        closed_at = datetime(d.year, d.month, d.day,
                             random.randint(19, 20),
                             random.randint(0, 59),
                             random.randint(0, 59))
        opened_at = datetime(d.year, d.month, d.day, 0, 0, 0)

        notes = None
        if variance_type == 'notable':
            notes_options = [
                "Faltante sin identificar",
                "Error en cambio",
                "Se pago proveedor en efectivo",
                "Sobrante del dia anterior",
                "Diferencia por redondeo acumulado",
            ]
            notes = random.choice(notes_options)

        cut = CashCut(
            opened_at=opened_at,
            closed_at=closed_at,
            sales_count=sales_count,
            orders_count=orders_count,
            sales_total=sales_total,
            orders_total=orders_total,
            expected_total=expected_total,
            declared_cash=declared_cash,
            declared_card=declared_card,
            declared_transfer=declared_transfer,
            declared_total=declared_total,
            difference=round(diff, 2),
            notes=notes,
        )
        db.add(cut)
        cut_count += 1

    db.flush()
    print(f"  Cortes de caja: {cut_count}")


def main_cash_cuts_only():
    """Seed solo cortes de caja basados en ventas/pedidos existentes."""
    print("=" * 50)
    print("SEED DATA - Cortes de Caja")
    print(f"Periodo: {START_DATE} -> {END_DATE}")
    print("=" * 50)

    with SessionLocal() as db:
        try:
            # Delete existing cash cuts
            deleted = db.query(CashCut).delete()
            print(f"\n  Eliminados: {deleted} cortes existentes")

            print("\nGenerando cortes de caja...")
            seed_cash_cuts(db)

            db.commit()
            print("\nCortes de caja generados correctamente.")

        except Exception as e:
            db.rollback()
            print(f"\nError: {e}")
            raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--purchases":
        main_purchases_only()
    elif len(sys.argv) > 1 and sys.argv[1] == "--today":
        main_today()
    elif len(sys.argv) > 1 and sys.argv[1] == "--cash-cuts":
        main_cash_cuts_only()
    else:
        main()
