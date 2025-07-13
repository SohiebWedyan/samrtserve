import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json 
# تهيئة Firebase Admin مرة واحدة فقط
if not firebase_admin._apps:
    firebase_key = st.secrets["FIREBASE_KEY"]
    cred = credentials.Certificate(json.loads(firebase_key))
    firebase_admin.initialize_app(cred)

db = firestore.client()
RESTAURANT_ID = "restaurant1"

st.set_page_config(layout="centered", page_title="لوحة إدارة المطعم")
st.markdown("<h2 style='color:#F9E27B;text-align:center;'>لوحة الطلبات - SmartServe AI</h2>", unsafe_allow_html=True)

# قراءة الطلبات من فايربيز
def get_orders():
    orders_ref = db.collection("restaurants").document(RESTAURANT_ID).collection("orders")
    docs = orders_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    orders = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        orders.append(data)
    return orders

orders = get_orders()

if not orders:
    st.warning("لا يوجد طلبات جديدة حالياً.")
else:
    for idx, order in enumerate(orders):
        st.markdown(f"""
            <div style="background:#26282b;border-radius:14px;padding:13px 17px;margin-bottom:12px;">
            <b>رقم الطلب:</b> {idx+1}<br>
            <b>الوقت:</b> {order.get("timestamp", "---")}<br>
            <b>رقم الطاولة:</b> {order.get("table_number", "---")}<br>
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
