import streamlit as st
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os

# --- إعدادات النموذج وواجهة الذكاء الاصطناعي ---
HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "Qwen/Qwen1.5-4B-Chat"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN , provider="featherless-ai")

# --- لوجو احترافي ---
LOGO_URL = "https://img.pikbest.com/png-images/20241111/-22creative-food-logo-collection-for-culinary-brands-22_11079861.png!sw800"

# --- قائمة المنيو ---
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

# --- CSS وتنسيق ---
st.set_page_config(layout="centered", page_title="مساعد SmartServe AI الذكي")
st.markdown("""
    <style>
    body, .stApp {
        background: url('https://wallpapers.com/images/featured/restaurant-background-2ez77umko2vj5w02.jpg') no-repeat center center fixed !important;
        background-size: cover !important;
    }
    .main {
        background: rgba(24, 25, 28, 0.78) !important;
        border-radius: 18px;
        padding: 0px 0px;
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
    .msg-bot  {
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

# --- لوجو + مقدمة ---
st.markdown(f"""
    <div style='text-align:center;margin-bottom:1px;'>
        <img src="{LOGO_URL}" style="width:85px; margin-bottom:-18px;" />
        <div style='font-size:30px; font-weight:bold; color:#F9E27B; margin-bottom:4px; margin-top:10px;'>SmartServe</div>
        <div style='font-size:17px;color:#FFFDEB;margin-bottom:8px;'>مساعد ذكي لطلبات الطعام والمشروبات</div>
    </div>
""", unsafe_allow_html=True)

# --- مثال جاهز تحت الإدخال ---
st.markdown(
    """
    <div style='font-size:15px;color:#FFD95E;margin-bottom:10px;text-align:right'>
        👇 <b>مثال:</b> <b>وجبة غداء نباتية</b> أو <b>ما هي مكونات المنسف؟</b>
    </div>
    """,
    unsafe_allow_html=True
)

# --- سجل المحادثة + السلة ---
if "history" not in st.session_state:
    st.session_state.history = []
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- إدخال نص وصوت (بنفس السطر) ---
col1, col2 = st.columns([8,1], gap="small")
with col1:
    user_input = st.text_input("", placeholder="اكتب هنا أو استخدم المايك...", key="input", label_visibility="collapsed")
with col2:
    audio = audio_recorder("", icon_size="lg")

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
            st.success(f"تم تحويل الصوت: {voice_text}")
        except Exception as e:
            st.error(f"خطأ في التعرف على الصوت: {e}")
    os.remove(temp_audio_file_path)

final_input = voice_text if voice_text else user_input

# --- زر إرسال ومعالجة الذكاء الاصطناعي ---
if final_input and st.button("إرسال", use_container_width=True):
    menu_results = [m for m in menu if final_input in m["name"] or final_input in m["desc"] or final_input in m["type"]]
    if menu_results:
        msg = "إليك بعض الخيارات من المنيو لدينا:\n"
        for item in menu_results:
            msg += f"- **{item['name']}**: {item['desc']}\n"
        st.session_state.history.append(("الزبون", final_input))
        st.session_state.history.append(("SmartServe", msg))
    else:
        msgs = [{"role": "system", "content": "أنت مساعد مطاعم ذكي ترد بالعربية الفصحى وتوضح اقتراحات الطعام أو أي معلومات غذائية أو نصائح حول المنيو."}]
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

# --- نموذج إضافة للسلة ---
st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
st.subheader("أضف صنف للسلة", divider="rainbow")
cart_col1, cart_col2, cart_col3 = st.columns([3, 1, 2])
with cart_col1:
    item_choice = st.selectbox("اختر الصنف", [m["name"] for m in menu], key="cart_item")
with cart_col2:
    qty = st.number_input("الكمية", min_value=1, max_value=20, value=1, key="cart_qty")
with cart_col3:
    notes = st.text_input("ملاحظات (اختياري)", key="cart_notes")

if st.button("إضافة للسلة"):
    if item_choice:
        item = next(m for m in menu if m["name"] == item_choice)
        st.session_state.cart.append({
            "name": item["name"],
            "qty": qty,
            "notes": notes.strip()
        })
        st.success(f"تمت إضافة {item['name']} للسلة!")

# --- عرض السلة في الشريط الجانبي ---
with st.sidebar:
    st.markdown("<div style='font-size:24px;color:#ffe48c;font-weight:700;'><span style='font-size:22px'>🛒</span> سلة الطلبات</div>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.markdown("<div class='cart-box'>السلة فارغة. أضف أصنافك المفضلة من المنيو!</div>", unsafe_allow_html=True)
    else:
        for i, x in enumerate(st.session_state.cart):
            st.markdown(
                f"<div class='cart-box'>"
                f"<b>{x['name']}</b> × <b>{x['qty']}</b>"
                f"{('<br><span style=\"font-size:13px;color:#ffe48c\">ملاحظات: '+x['notes']+'</span>') if x['notes'] else ''}"
                f"<br><button style='margin-top:3px;color:#fff;background:#A72626;padding:2px 9px;border:none;border-radius:6px;font-size:13px;cursor:pointer' onclick='window.location.search+=\"&del={i}\"'>❌ حذف</button>"
                f"</div>", unsafe_allow_html=True)
            # حذف الصنف عند الضغط (زر خارجي)
            if st.button(f"❌ حذف {x['name']}", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.experimental_rerun()
        if st.button("تأكيد الطلب"):
            st.success("✅ تم إرسال الطلب بنجاح!")
            st.session_state.cart.clear()

# --- عرض المحادثة ---
for sender, text in st.session_state.history[-8:]:
    if sender == "الزبون":
        st.markdown(f"<div class='msg-user'><b>👤 الزبون:</b><br>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg-bot'><b>🤖 SmartServe:</b><br>{text}</div>", unsafe_allow_html=True)

# --- إخراج صوتي للرد الأخير ---
if st.session_state.history and st.session_state.history[-1][0] == "SmartServe":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")
