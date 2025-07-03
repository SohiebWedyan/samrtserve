import streamlit as st
import sqlite3

st.set_page_config(layout="centered", page_title="لوحة إدارة المطعم")
st.markdown("<h2 style='color:#F9E27B;text-align:center;'>لوحة الطلبات - SmartServe AI</h2>", unsafe_allow_html=True)

DB_FILE = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            table_number TEXT,
            item_name TEXT,
            quantity INTEGER,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_orders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''SELECT id, timestamp, table_number, item_name, quantity, notes
                 FROM orders
                 ORDER BY timestamp DESC, id DESC''')
    rows = c.fetchall()
    conn.close()
    return rows

def clear_orders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM orders")
    conn.commit()
    conn.close()

# ⭐️ تهيئة قاعدة البيانات
init_db()

st.info("يتم تحديث الطلبات تلقائياً عند كل تحديث للصفحة (يمكنك الضغط F5 أو ↻)")

orders = load_orders()
if not orders:
    st.warning("لا يوجد طلبات جديدة حالياً.")
else:
    grouped = {}
    for row in orders:
        order_id, timestamp, table_number, item_name, quantity, notes = row
        key = (timestamp, table_number)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            "item_name": item_name,
            "quantity": quantity,
            "notes": notes
        })
    for idx, ((timestamp, table_number), items) in enumerate(sorted(grouped.items(), reverse=True)):
        st.markdown(f"""
            <div style="background:#26282b;border-radius:14px;padding:13px 17px;margin-bottom:12px;">
            <b>رقم الطلب:</b> {len(grouped) - idx}<br>
            <b>رقم الطاولة:</b> {table_number}<br>
            <b>الوقت:</b> {timestamp}<br>
            <b>الأصناف:</b>
            <ul>
        """, unsafe_allow_html=True)
        for item in items:
            st.markdown(
                f"<li><b>{item['item_name']}</b> × {item['quantity']} "
                f"{' | <span style=\"color:#ffe48c\">ملاحظة: '+item['notes']+'</span>' if item['notes'] else ''}</li>",
                unsafe_allow_html=True
            )
        st.markdown("</ul></div>", unsafe_allow_html=True)
    if st.button("🧹 حذف جميع الطلبات (بعد التنفيذ)", type="primary"):
        clear_orders()
        st.success("تم حذف جميع الطلبات بنجاح!")
        st.experimental_rerun()
