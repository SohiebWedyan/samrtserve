import streamlit as st
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os

HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "NousResearch/Hermes-3-Llama-3.1-8B"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

LOGO_URL = "https://raw.githubusercontent.com/sohiebwedyan/smartserve_logo/main/smartserve-logo-v2.png"
BG_URL = "https://wallpapers.com/images/featured/restaurant-background-2ez77umko2vj5w02.jpg"

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

# ========== إعداد CSS للخلفية والشفافية ==========
st.set_page_config(layout="centered", page_title="مساعد SmartServe AI الذكي")
st.markdown(f"""
    <style>
    body, .stApp {{
        background: url('{BG_URL}') no-repeat center center fixed !important;
        background-size: cover !important;
    }}
    .main {{
        background: rgba(24, 25, 28, 0.76) !important;
        border-radius: 18px;
        padding: 0px 0px;
    }}
    .msg-user {{
        background: #e7f1ffcc;
        border-radius: 14px;
        padding: 12px 17px;
        margin-bottom: 4px;
        font-size: 17px;
        text-align: right;
        color: #232323;
        direction: rtl;
    }}
    .msg-bot  {{
        background: #fff9e3cc;
        border-radius: 14px;
        padding: 13px 17px;
        margin-bottom: 9px;
        font-weight: 600;
        font-size: 17px;
        text-align: right;
        color: #363616;
        direction: rtl;
    }}
    .stTextInput input {{ font-size:17px; text-align:right; }}
    .stButton>button {{font-size:17px;border-radius:8px;margin-top:1px;}}
    @media only screen and (max-width: 600px) {{
        .msg-user, .msg-bot {{font-size:15px; padding: 11px 8px;}}
    }}
    </style>
""", unsafe_allow_html=True)

# ---- رأس الصفحة واللوجو ----
st.markdown(f"""
    <div style='text-align:center;margin-bottom:1px;'>
        <img src="{LOGO_URL}" style="width:80px; margin-bottom:-16px;" />
        <div style='font-size:32px;font-weight:900;color:#ffe186;text-shadow:0 2px 15px #000c;'>SmartServe</div>
        <div style='font-size:19px;color:#fffbe9;margin-bottom:10px;'>مساعد ذكي لطلبات الطعام والمشروبات</div>
    </div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div style='font-size:15px;color:#ffe186;margin-bottom:10px;text-align:right'>
        👇 <b>مثال:</b> <b>وجبة غداء نباتية</b> أو <b>ما هي مكونات المنسف؟</b>
    </div>
    """,
    unsafe_allow_html=True
)

# ==== سجل المحادثة والسلة ====
if "history" not in st.session_state:
    st.session_state.history = []
if "cart" not in st.session_state:
    st.session_state.cart = []

def search_menu(user_input):
    user_input = user_input.strip().lower()
    matches = []
    for item in menu:
        if user_input in item['name'] or user_input in item['desc'] or user_input in item['type']:
            matches.append(item)
    return matches

def ask_ai(messages):
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        temperature=0.3,
        top_p=0.7,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()

# ---- إدخال نص وصوت بنفس الصف ----
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

# --- زر إرسال ومعالجة ---
if final_input and st.button("إرسال", use_container_width=True):
    menu_results = search_menu(final_input)
    if menu_results:
        msg = "اختر ما تريد إضافته للسلة 👇:<br>"
        for i, item in enumerate(menu_results):
            add_key = f"add_{i}_{item['name']}"
            qty_key = f"qty_{i}_{item['name']}"
            note_key = f"note_{i}_{item['name']}"
            with st.expander(f"➕ أضف {item['name']}", expanded=False):
                qty = st.number_input(f"الكمية ({item['name']})", 1, 20, 1, key=qty_key)
                note = st.text_input(f"ملاحظات ({item['name']})", key=note_key, placeholder="مثلاً: بدون ملح أو زيادة خبز...")
                if st.button(f"إضافة {item['name']} للسلة", key=add_key):
                    st.session_state.cart.append({"name": item['name'], "desc": item['desc'], "qty": qty, "note": note})
                    st.success(f"تمت إضافة {item['name']} للسلة!")
        st.session_state.history.append(("الزبون", final_input))
    else:
        msgs = [{"role": "system", "content": "أنت مساعد مطاعم ذكي ترد بالعربية الفصحى وتوضح اقتراحات الطعام أو أي معلومات غذائية أو نصائح حول المنيو."}]
        for s, m in st.session_state.history[-6:]:
            msgs.append({"role": "user" if s == "الزبون" else "assistant", "content": m})
        msgs.append({"role": "user", "content": final_input})
        with st.spinner("جاري البحث الذكي ..."):
            answer = ask_ai(msgs)
        st.session_state.history.append(("الزبون", final_input))
        st.session_state.history.append(("SmartServe", answer))

# ---- عرض المحادثة ----
for sender, text in st.session_state.history[-8:]:
    if sender == "الزبون":
        st.markdown(f"<div class='msg-user'><b>👤 الزبون:</b><br>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg-bot'><b>🤖 SmartServe:</b><br>{text}</div>", unsafe_allow_html=True)

# ---- سلة الطلبات في الشريط الجانبي ----
with st.sidebar:
    st.markdown("<div style='text-align:right;font-size:24px;color:#ffe186;'>🛒 سلة الطلبات</div>", unsafe_allow_html=True)
    if st.session_state.cart:
        for idx, item in enumerate(st.session_state.cart):
            st.markdown(
                f"""<div style='background:#222c;padding:7px 9px;border-radius:7px;margin-bottom:6px;'>
                <b>{item['name']}</b> | <span style='color:#ffe186'>الكمية:</span> {item['qty']}
                <br><span style='color:#fff7a4'>{item['desc']}</span>
                <br><span style='font-size:15px;color:#ffe;'>{'ملاحظات: '+item['note'] if item['note'] else ''}</span>
                </div>""", unsafe_allow_html=True)
            if st.button("❌ حذف", key=f"del_{idx}_{item['name']}"):
                st.session_state.cart.pop(idx)
                st.experimental_rerun()
        if st.button("✅ إرسال الطلب", key="order_btn"):
            st.success("تم إرسال الطلب بنجاح! 🍽️ شكراً لاستخدامك SmartServe.")
            st.session_state.cart.clear()
    else:
        st.info("السلة فارغة. أضف أصنافك المفضلة من المنيو.")

# ---- إخراج صوتي ----
if st.session_state.history and st.session_state.history[-1][0] == "SmartServe":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")
