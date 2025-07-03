import streamlit as st
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os
from datetime import datetime

# اتصال Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'gen-lang-client-0062251257-04dccc58918d.json', scope
)
client = gspread.authorize(creds)

SHEET_ID = '1E3SIGQjSYfD_YoKOlkIxApKqMu6yBCWEFlqja1RyG2c'
sh = client.open_by_key(SHEET_ID)
worksheet = sh.sheet1  # يمكنك تغييرها إذا كان اسم الورقة مختلف

# قائمة الطعام
menu = [
    {"name": "كبسة دجاج", "type": "لحوم", "desc": "أرز مع بهارات ودجاج"},
    {"name": "منسف أردني", "type": "لحوم", "desc": "لحم مع لبن وجوز هند"},
    {"name": "بيتزا مارغريتا", "type": "نباتي", "desc": "طماطم، جبنة موزاريلا، ريحان"},
    {"name": "سلطة فتوش", "type": "نباتي", "desc": "خس، طماطم، خيار، خبز محمص"},
    {"name": "حمص", "type": "نباتي", "desc": "حمص مهروس مع طحينة"},
    {"name": "فلافل", "type": "نباتي", "desc": "كرات حمص مقلية"},
    {"name": "شاورما دجاج", "type": "لحوم", "desc": "شرائح دجاج متبلة"},
    {"name": "بقلاوة", "type": "حلويات", "desc": "عجينة مع مكسرات وعسل"},
    {"name": "كنافة نابلسية", "type": "حلويات", "desc": "شعر كنافة مع جبنة"},
    {"name": "شوربة عدس", "type": "حساء", "desc": "شوربة صحية بعدس وبصل وبهارات"},
    {"name": "بيبسي", "type": "مشروبات", "desc": "مشروب غازي بارد"},
    {"name": "كوكاكولا", "type": "مشروبات", "desc": "مشروب غازي منعش"},
    {"name": "شاي", "type": "مشروبات ساخنة", "desc": "مشروب ساخن منعش"},
    {"name": "قهوة عربية", "type": "مشروبات ساخنة", "desc": "قهوة محمصة مع هيل"},
    {"name": "قهوة تركية", "type": "مشروبات ساخنة", "desc": "قهوة مطحونة تُغلى مع السكر"},
    {"name": "حليب ساخن", "type": "مشروبات ساخنة", "desc": "حليب مغلي"},
    {"name": "يانسون", "type": "مشروبات ساخنة", "desc": "مشروب اليانسون الساخن"},
    {"name": "زعتر", "type": "مشروبات ساخنة", "desc": "شاي زعتر صحي"},
    {"name": "كابتشينو", "type": "مشروبات ساخنة", "desc": "إسبريسو مع حليب رغوي"},
    {"name": "نسكافيه", "type": "مشروبات ساخنة", "desc": "قهوة سريعة الذوبان"},
]

# دالة حفظ الطلب في Google Sheets
def add_order_to_sheet(cart_items, table_number):
    for item in cart_items:
        worksheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            table_number,
            item["name"],
            item["qty"],
            item["notes"]
        ])

# إعدادات الواجهة
st.set_page_config(layout="centered", page_title="SmartServe AI")
st.markdown("""
<style>
#MainMenu, header, footer, .st-emotion-cache-18ni7ap.ezrtsby0 {visibility: hidden;}
body, .stApp {
    background: url('https://wallpapers.com/images/featured/restaurant-background-2ez77umko2vj5w02.jpg') no-repeat center center fixed !important;
    background-size: cover !important;
}
.main {
    background: rgba(24, 25, 28, 0.78) !important;
    border-radius: 18px;
}
.msg-user {
    background: #222b2ecc;
    border-radius: 14px;
    padding: 12px 17px;
    margin-bottom: 4px;
    font-size: 17px;
    text-align: right;
    color: #cfcfcf;
    direction: rtl;
}
.msg-bot {
    background: #242110cc;
    border-radius: 14px;
    padding: 13px 17px;
    margin-bottom: 9px;
    font-weight: 600;
    font-size: 17px;
    text-align: right;
    color: #ffe48c;
    direction: rtl;
}
.cart-box {
    background: #1e222aee;
    border-radius: 14px;
    padding: 13px 15px;
    margin-bottom: 12px;
    font-size: 17px;
    color: #fff;
    direction: rtl;
    border: 2px solid #444;
}
.stTextInput input { font-size:17px; text-align:right; }
.stButton>button {font-size:17px;border-radius:8px;margin-top:1px;}
@media only screen and (max-width: 600px) {
    .msg-user, .msg-bot, .cart-box {font-size:15px; padding: 11px 8px;}
}
</style>
""", unsafe_allow_html=True)

# لوجو ومقدمة
LOGO_URL = "https://img.pikbest.com/png-images/20241111/-22creative-food-logo-collection-for-culinary-brands-22_11079861.png!sw800"
st.markdown(f"""
    <div style='text-align:center;'>
        <img src="{LOGO_URL}" style="width:85px; margin-bottom:-18px;" />
        <div style='font-size:30px; font-weight:bold; color:#F9E27B;'>SmartServe AI</div>
        <div style='font-size:17px;color:#FFFDEB;'>مساعد ذكي لطلبات الطعام والمشروبات</div>
    </div>
""", unsafe_allow_html=True)

# سجل الجلسة
if "history" not in st.session_state:
    st.session_state.history = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table_number" not in st.session_state:
    st.session_state.table_number = ""

# --- حقل رقم الطاولة ---
st.markdown("**رقم الطاولة**", unsafe_allow_html=True)
table_number = st.text_input("أدخل رقم الطاولة", key="table_input", value=st.session_state.table_number)
if table_number != st.session_state.table_number:
    st.session_state.table_number = table_number

# إدخال المستخدم (نص + صوت)
col1, col2 = st.columns([8,1])
with col1:
    user_input = st.text_input("", placeholder="اكتب هنا أو استخدم المايك...", key="input", label_visibility="collapsed")
with col2:
    audio = audio_recorder("", icon_size="lg")

# التحويل الصوتي (إذا وُجد صوت)
voice_text = ""
if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio)
        temp_audio_file_path = temp_audio_file.name
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            voice_text = recognizer.recognize_google(audio_data, language="ar-JO")
            st.toast("✅ تم تحويل الصوت: " + voice_text)
        except Exception as e:
            st.toast("❌ لم يتم التعرف على الصوت")
    os.remove(temp_audio_file_path)

# زر الإرسال يدعم الإدخال الموحد (صوتي أو كتابي)
if st.button("إرسال", use_container_width=True):
    if voice_text.strip():
        final_input = voice_text
    else:
        final_input = st.session_state.input

    if final_input.strip():
        menu_results = [m for m in menu if final_input in m["name"] or final_input in m["desc"] or final_input in m["type"]]
        if menu_results:
            msg = "إليك بعض الخيارات من المنيو لدينا:\n"
            for item in menu_results:
                msg += f"- **{item['name']}**: {item['desc']}\n"
            st.session_state.history.append(("الزبون", final_input))
            st.session_state.history.append(("SmartServe", msg))
        else:
            msgs = [{"role": "system", "content": "أنت مساعد مطاعم ذكي ترد بالعربية الفصحى."}]
            for s, m in st.session_state.history[-6:]:
                msgs.append({"role": "user" if s == "الزبون" else "assistant", "content": m})
            msgs.append({"role": "user", "content": final_input})
            with st.spinner("جاري البحث الذكي ..."):
                answer = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=msgs,
                    temperature=0.3,
                    top_p=0.7,
                    max_tokens=256,
                ).choices[0].message.content.strip()
            st.session_state.history.append(("الزبون", final_input))
            st.session_state.history.append(("SmartServe", answer))

# نموذج السلة
st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
st.subheader("أضف صنف للسلة", divider="rainbow")
col1, col2, col3 = st.columns([3, 1, 2])
with col1:
    item_choice = st.selectbox("اختر الصنف", [m["name"] for m in menu])
with col2:
    qty = st.number_input("الكمية", min_value=1, max_value=20, value=1)
with col3:
    notes = st.text_input("ملاحظات (اختياري)")

if st.button("إضافة للسلة"):
    item = next(m for m in menu if m["name"] == item_choice)
    st.session_state.cart.append({"name": item["name"], "qty": qty, "notes": notes.strip()})
    st.success(f"تمت إضافة {item['name']} للسلة!")

# عرض السلة في الشريط الجانبي
with st.sidebar:
    st.markdown("<div style='font-size:24px;color:#ffe48c;font-weight:700;'>🛒 سلة الطلبات</div>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.markdown("<div class='cart-box'>السلة فارغة.</div>", unsafe_allow_html=True)
    else:
        for i, x in enumerate(st.session_state.cart):
            st.markdown(
                f"<div class='cart-box'><b>{x['name']}</b> × <b>{x['qty']}</b>"
                f"{('<br><span style=\"font-size:13px;color:#ffe48c\">ملاحظات: '+x['notes']+'</span>') if x['notes'] else ''}"
                f"</div>", unsafe_allow_html=True
            )
            if st.button(f"❌ حذف {x['name']}", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.experimental_rerun()
        if st.button("✅ تأكيد الطلب"):
            if not st.session_state.cart:
                st.warning("السلة فارغة!")
            elif not st.session_state.table_number.strip():
                st.warning("يرجى إدخال رقم الطاولة.")
            else:
                add_order_to_sheet(st.session_state.cart, st.session_state.table_number.strip())
                st.success("تم إرسال الطلب بنجاح!")
                st.session_state.cart.clear()

# --- عرض المحادثة ---
for sender, text in st.session_state.history[-8:]:
    class_name = 'msg-user' if sender == "الزبون" else 'msg-bot'
    icon = "👤" if sender == "الزبون" else "🤖"
    st.markdown(f"<div class='{class_name}'><b>{icon} {sender}:</b><br>{text}</div>", unsafe_allow_html=True)

# --- عرض السلة أيضاً أسفل الصفحة (للجوال/كل الشاشات) ---
if st.session_state.cart:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:20px;color:#ffe48c;font-weight:700;text-align:right;'>🛒 سلة الطلبات الحالية</div>", unsafe_allow_html=True)
    for i, x in enumerate(st.session_state.cart):
        cols = st.columns([10,1])
        with cols[0]:
            st.markdown(
                f"<div class='cart-box'><b>{x['name']}</b> × <b>{x['qty']}</b>"
                f"{('<br><span style=\"font-size:13px;color:#ffe48c\">ملاحظات: '+x['notes']+'</span>') if x['notes'] else ''}"
                f"</div>", unsafe_allow_html=True
            )
        with cols[1]:
            if st.button("❌", key=f"del_bottom_{i}"):
                st.session_state.cart.pop(i)
                st.experimental_rerun()
    if st.button("✅ تأكيد الطلب (من هنا)"):
        if not st.session_state.cart:
            st.warning("السلة فارغة!")
        elif not st.session_state.table_number.strip():
            st.warning("يرجى إدخال رقم الطاولة.")
        else:
            add_order_to_sheet(st.session_state.cart, st.session_state.table_number.strip())
            st.success("تم إرسال الطلب بنجاح!")
            st.session_state.cart.clear()

# --- إخراج صوتي للرد الأخير ---
if st.session_state.history and st.session_state.history[-1][0] == "SmartServe":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")
