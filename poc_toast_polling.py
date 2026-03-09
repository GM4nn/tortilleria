"""
POC: Polling Neon + Toast Notification

Flujo:
1. Usuario guarda pedido en app de escritorio (SQLite)
2. POC consulta SQLite: pedidos de hoy con status 'pendiente'
3. Los sube a Neon (si no existen)
4. Polling cada 15s: si en Neon cambió de 'pendiente' a 'completado'
   → actualiza SQLite local + muestra toast

Uso:
    python poc_toast_polling.py

Requisitos:
    pip install psycopg2-binary ttkbootstrap
"""

import threading
from datetime import datetime

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification

from sqlalchemy import create_engine, text

# ── Configuración ──────────────────────────────────────────────
NEON_URL = "postgresql://neondb_owner:npg_D6tI8ynNBopG@ep-dark-thunder-ac9gb4ns-pooler.sa-east-1.aws.neon.tech/tortilleria?sslmode=require"
SQLITE_URL = "sqlite:///tortilleria.db"
POLLING_INTERVAL_MS = 15000  # 15 segundos para la POC

# ── Engines ────────────────────────────────────────────────────
neon_engine = create_engine(NEON_URL)
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


class ToastPollingPOC:
    def __init__(self):
        self.root = ttk.Window(themename="flatly", title="POC - Toast Polling Neon")
        self.root.geometry("700x450")

        # IDs de pedidos de hoy que ya subimos a Neon y monitoreamos
        self.synced_ids = set()
        self.polling_active = True

        self._build_ui()
        self._iniciar_polling()

    def _build_ui(self):
        header = ttk.Label(
            self.root, text="POC: Polling Neon - Toast",
            font=("Helvetica", 16, "bold"),
            bootstyle="inverse-primary", padding=10
        )
        header.pack(fill=X)

        log_frame = ttk.Labelframe(self.root, text="Log de eventos", padding=10)
        log_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.log_text = ttk.Text(log_frame, height=15, font=("Consolas", 10))
        self.log_text.pack(fill=BOTH, expand=YES)

        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttk.Button(
            btn_frame, text="Forzar ciclo ahora",
            bootstyle="info", command=self._forzar_ciclo
        ).pack(side=LEFT, padx=5)

    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, lambda: self._append_log(f"[{timestamp}] {msg}"))

    def _append_log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    # ── Ciclo principal ────────────────────────────────────────

    def _iniciar_polling(self):
        self._log(f"Polling iniciado (cada {POLLING_INTERVAL_MS // 1000}s)")
        self._programar_ciclo()

    def _programar_ciclo(self):
        thread = threading.Thread(target=self._ciclo, daemon=True)
        thread.start()
        if self.polling_active:
            self.root.after(POLLING_INTERVAL_MS, self._programar_ciclo)

    def _forzar_ciclo(self):
        thread = threading.Thread(target=self._ciclo, daemon=True)
        thread.start()

    def _ciclo(self):
        """
        Paso 1: SQLite → pedidos de hoy pendientes → subirlos a Neon
        Paso 2: Neon → checar si alguno cambió de status → toast
        """
        # ── Paso 1: Subir pedidos pendientes de hoy a Neon ──
        try:
            with sqlite_engine.connect() as sconn:
                pedidos = sconn.execute(text(
                    "SELECT id, date, total, customer_id, status, completed_at, notes, amount_paid "
                    "FROM orders "
                    "WHERE date(date) = date('now', 'localtime') AND status = 'pendiente'"
                )).fetchall()

                # Filtrar los que aún no hemos subido
                nuevos = [p for p in pedidos if p[0] not in self.synced_ids]

                if nuevos:
                    # Obtener clientes necesarios
                    customer_ids = list(set(p[3] for p in nuevos))
                    c_ph = ", ".join([f":c_{i}" for i in range(len(customer_ids))])
                    c_params = {f"c_{i}": cid for i, cid in enumerate(customer_ids)}
                    clientes = sconn.execute(text(
                        f"SELECT id, customer_name, customer_direction, customer_category, "
                        f"customer_phone, active FROM customers WHERE id IN ({c_ph})"
                    ), c_params).fetchall()

                    # Obtener detalles
                    new_ids = [p[0] for p in nuevos]
                    o_ph = ", ".join([f":o_{i}" for i in range(len(new_ids))])
                    o_params = {f"o_{i}": oid for i, oid in enumerate(new_ids)}
                    detalles = sconn.execute(text(
                        f"SELECT id, order_id, product_id, quantity, unit_price, subtotal "
                        f"FROM order_details WHERE order_id IN ({o_ph})"
                    ), o_params).fetchall()

                    # Subir a Neon
                    with neon_engine.connect() as nconn:
                        for c in clientes:
                            exists = nconn.execute(
                                text("SELECT 1 FROM customers WHERE id = :id"), {"id": c[0]}
                            ).fetchone()
                            if not exists:
                                nconn.execute(text(
                                    "INSERT INTO customers (id, customer_name, customer_direction, "
                                    "customer_category, customer_phone, active) "
                                    "VALUES (:id, :name, :dir, :cat, :phone, CAST(:active AS boolean))"
                                ), {"id": c[0], "name": c[1], "dir": c[2],
                                    "cat": c[3], "phone": c[4], "active": c[5]})

                        for p in nuevos:
                            exists = nconn.execute(
                                text("SELECT 1 FROM orders WHERE id = :id"), {"id": p[0]}
                            ).fetchone()
                            if not exists:
                                nconn.execute(text(
                                    "INSERT INTO orders (id, date, total, customer_id, status, "
                                    "completed_at, notes, amount_paid) "
                                    "VALUES (:id, :date, :total, :cid, :status, :completed, :notes, :paid)"
                                ), {"id": p[0], "date": p[1], "total": p[2], "cid": p[3],
                                    "status": p[4], "completed": p[5], "notes": p[6], "paid": p[7]})

                        for d in detalles:
                            exists = nconn.execute(
                                text("SELECT 1 FROM order_details WHERE id = :id"), {"id": d[0]}
                            ).fetchone()
                            if not exists:
                                nconn.execute(text(
                                    "INSERT INTO order_details (id, order_id, product_id, quantity, "
                                    "unit_price, subtotal) VALUES (:id, :oid, :pid, :qty, :price, :sub)"
                                ), {"id": d[0], "oid": d[1], "pid": d[2],
                                    "qty": d[3], "price": d[4], "sub": d[5]})

                        nconn.commit()

                    inserted = 0
                    for p in nuevos:
                        self.synced_ids.add(p[0])
                        # Checar si realmente se insertó (no existía antes)
                    for p in nuevos:
                        with neon_engine.connect() as check:
                            row = check.execute(text(
                                "SELECT id, status FROM orders WHERE id = :id"
                            ), {"id": p[0]}).fetchone()
                            if row:
                                inserted += 1
                                self._log(f"  -> Pedido #{p[0]} verificado en Neon (status: {row[1]})")
                            else:
                                self._log(f"  -> Pedido #{p[0]} NO encontrado en Neon!")
                    self._log(f"Subidos {len(nuevos)} pedidos de hoy a Neon ({inserted} verificados)")
                else:
                    if not self.synced_ids:
                        self._log("No hay pedidos pendientes de hoy en SQLite")

        except Exception as e:
            self._log(f"Error sincronizando a Neon: {e}")
            return

        # ── Paso 2: Checar cambios en Neon ──
        if not self.synced_ids:
            return

        try:
            with neon_engine.connect() as nconn:
                ids_list = list(self.synced_ids)
                ph = ", ".join([f":id_{i}" for i in range(len(ids_list))])
                params = {f"id_{i}": oid for i, oid in enumerate(ids_list)}

                rows = nconn.execute(text(
                    f"SELECT o.id, o.status, c.customer_name "
                    f"FROM orders o JOIN customers c ON o.customer_id = c.id "
                    f"WHERE o.id IN ({ph})"
                ), params).fetchall()

                cambios = []
                for row in rows:
                    order_id, neon_status, customer = row[0], row[1], row[2]
                    if neon_status != "pendiente":
                        cambios.append((order_id, neon_status, customer))

                if cambios:
                    for order_id, new_status, customer in cambios:
                        self._aplicar_cambio(order_id, new_status, customer)
                else:
                    self._log(f"Polling... sin cambios ({len(ids_list)} monitoreados en Neon)")

        except Exception as e:
            self._log(f"Error consultando Neon: {e}")

    # ── Aplicar cambio + Toast ─────────────────────────────────

    def _aplicar_cambio(self, order_id, new_status, customer):
        # Actualizar SQLite
        try:
            with sqlite_engine.connect() as conn:
                if new_status == "completado":
                    conn.execute(text(
                        "UPDATE orders SET status = :status, completed_at = :at WHERE id = :id"
                    ), {"status": new_status, "at": datetime.now().isoformat(), "id": order_id})
                else:
                    conn.execute(text(
                        "UPDATE orders SET status = :status WHERE id = :id"
                    ), {"status": new_status, "id": order_id})
                conn.commit()
            self._log(f"SQLite actualizado: Pedido #{order_id} -> {new_status}")
        except Exception as e:
            self._log(f"Error actualizando SQLite: {e}")
            return

        # Ya no lo monitoreamos
        self.synced_ids.discard(order_id)

        # Toast
        self.root.after(0, lambda: self._mostrar_toast(order_id, new_status, customer))

    def _mostrar_toast(self, order_id, new_status, customer):
        if new_status == "completado":
            title, icon, style = "Pedido Completado", "V", "success"
        elif new_status == "cancelado":
            title, icon, style = "Pedido Cancelado", "X", "danger"
        else:
            title, icon, style = "Pedido Actualizado", "!", "info"

        toast = ToastNotification(
            title=f"  {icon}  {title}",
            message=f"Pedido #{order_id} de {customer}\nha sido {new_status}",
            duration=5000,
            bootstyle=style,
            position=(80, 80, "se"),
        )
        toast.show_toast()
        self._log(f"TOAST: {title} - Pedido #{order_id} ({customer})")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self.polling_active = False
        self.root.destroy()


if __name__ == "__main__":
    app = ToastPollingPOC()
    app.run()
