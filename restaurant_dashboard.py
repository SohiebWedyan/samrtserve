import streamlit as st
import json
import os

st.set_page_config(layout="centered", page_title="لوحة إدارة المطعم")
st.markdown("<h2 style='color:#F9E27B;text-align:center;'>لوحة الطلبات - SmartServe AI</h2>", unsafe_allow_html=True)

ORDERS_FILE = "orders.json"

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = []
    return data

def clear_orders():
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        f.write("[]")

st.info("يتم تحديث الطلبات تلقائياً عند كل تحديث للصفحة (يمكنك الضغط F5 أو ↻)")

orders = load_orders()
if not orders:
    st.warning("لا يوجد طلبات جديدة حالياً.")
else:
    for idx, order in enumerate(reversed(orders)):  # الأحدث في الأعلى
        st.markdown(f"""
            <div style="background:#26282b;border-radius:14px;padding:13px 17px;margin-bottom:12px;">
            <b>رقم الطلب:</b> {len(orders)-idx}<br>
            <b>الوقت:</b> {order.get("timestamp","---")}<br>
            <b>الأصناف:</b>
            <ul>
        """, unsafe_allow_html=True)
        for item in order["items"]:
            st.markdown(
                f"<li><b>{item['name']}</b> × {item['qty']} "
                f"{' | <span style=\"color:#ffe48c\">ملاحظة: '+item['notes']+'</span>' if item['notes'] else ''}</li>",
                unsafe_allow_html=True
            )
        st.markdown("</ul></div>", unsafe_allow_html=True)
    if st.button("🧹 حذف جميع الطلبات (بعد التنفيذ)", type="primary"):
        clear_orders()
        st.success("تم حذف جميع الطلبات بنجاح!")
        st.experimental_rerun()
