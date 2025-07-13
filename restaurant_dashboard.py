import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# لا تكرر التهيئة إذا كان التطبيق مُهيأ مسبقًا!
if not firebase_admin._apps:
    cred = credentials.Certificate("smartserve-multirestaurant-firebase-adminsdk-fbsvc-1ed7850c3f.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
RESTAURANT_ID = "restaurant1"  # عدل هنا لو أردت

st.set_page_config(layout="centered", page_title="لوحة إدارة المطعم")
st.markdown("<h2 style='color:#F9E27B;text-align:center;'>لوحة الطلبات - SmartServe AI</h2>", unsafe_allow_html=True)

orders_ref = db.collection("restaurants").document(RESTAURANT_ID).collection("orders")

def get_all_orders():
    orders = orders_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    result = []
    for doc in orders:
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)
    return result

def delete_all_orders():
    orders = orders_ref.stream()
    for doc in orders:
        doc.reference.delete()

st.info("تحديث تلقائي للطلبات عند كل تحديث للصفحة (يمكنك الضغط F5 أو ↻)")

orders = get_all_orders()
if not orders:
    st.warning("لا يوجد طلبات حالياً.")
else:
    for idx, order in enumerate(orders):
        st.markdown(f"""
            <div style="background:#26282b;border-radius:14px;padding:13px 17px;margin-bottom:12px;">
            <b>رقم الطاولة:</b> {order.get('table_number','---')}<br>
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
        delete_all_orders()
        st.success("تم حذف جميع الطلبات بنجاح!")
        st.experimental_rerun()
