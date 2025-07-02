import streamlit as st
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os

# إعدادات الـ API
import os
HF_TOKEN = os.environ.get("HF_TOKEN")
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)
# لوجو SmartServe (يمكنك تغييره برابط آخر)
LOGO_URL = "https://raw.githubusercontent.com/sohiebwedyan/smartserve_logo/main/smartserve-logo-v2.png"

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

# ========== إعدادات الصفحة وتنسيقات CSS ==========
st.set_page_config(layout="centered", page_title="مساعد SmartServe الذكي")
st.markdown("""
    <style>
    body, .stApp { background-color: #18191c !important; }
    .main { background-color: #18191c !important; }
    .msg-user {background:#e7f1ff;border-radius:14px;padding:12px 17px;margin-bottom:4px;font-size:17px;text-align:right;color:#232323;direction:rtl}
    .msg-bot  {background:#fff9e3;border-radius:14px;padding:13px 17px;margin-bottom:9px;font-weight:600;font-size:17px;text-align:right;color:#363616;direction:rtl}
    .stTextInput input { font-size:17px; text-align:right; }
    .stButton>button {font-size:17px;border-radius:8px;margin-top:1px;}
    @media only screen and (max-width: 600px) {
        .msg-user, .msg-bot {font-size:15px; padding: 11px 8px;}
    }
    </style>
""", unsafe_allow_html=True)

# لوجو ومقدمة أعلى الصفحة
st.markdown(f"""
    <div style='text-align:center;margin-bottom:1px;'>
        <img src="{LOGO_URL}" style="width:85px; margin-bottom:-18px" />
        <div style='font-size:30px; font-weight:bold; color:#F9E27B; margin-bottom:4px; margin-top:10px;'>SmartServe</div>
        <div style='font-size:17px;color:#F7F6F4;margin-bottom:8px;'>مساعد ذكي لطلبات الطعام والمشروبات</div>
    </div>
""", unsafe_allow_html=True)

# مثال تحت الإدخال
st.markdown(
    """
    <div style='font-size:15px;color:#F9E27B;margin-bottom:10px;text-align:right'>
        👇 مثال: <b>وجبة غداء نباتية</b> أو <b>ما هي مكونات المنسف؟</b>
    </div>
    """,
    unsafe_allow_html=True
)

if "history" not in st.session_state:
    st.session_state.history = []

def search_menu(user_input):
    user_input = user_input.strip().lower()
    matches = []
    for item in menu:
        if user_input in item['name'] or user_input in item['desc'] or user_input in item['type']:
            matches.append(item)
    return matches

def ask_ai(messages):
    # محادثة مع نموذج الدردشة
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        temperature=0.3,
        top_p=0.7,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()

# =========== إدخال نص وصوت (في صف واحد) ============
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

# =========== زر إرسال ومعالجة ============
if final_input and st.button("إرسال", use_container_width=True):
    menu_results = search_menu(final_input)
    if menu_results:
        msg = "إليك بعض الخيارات من المنيو لدينا:\n"
        for item in menu_results:
            msg += f"- **{item['name']}**: {item['desc']}\n"
        st.session_state.history.append(("الزبون", final_input))
        st.session_state.history.append(("SmartServe", msg))
    else:
        # استخدم الذكاء الاصطناعي
        msgs = [{"role": "system", "content": "أنت مساعد مطاعم ذكي ترد بالعربية الفصحى وتوضح اقتراحات الطعام أو أي معلومات غذائية أو نصائح حول المنيو."}]
        for s, m in st.session_state.history[-6:]:
            msgs.append({"role": "user" if s == "الزبون" else "assistant", "content": m})
        msgs.append({"role": "user", "content": final_input})
        with st.spinner("جاري البحث الذكي ..."):
            answer = ask_ai(msgs)
        st.session_state.history.append(("الزبون", final_input))
        st.session_state.history.append(("SmartServe", answer))

# =========== عرض رسائل المحادثة ============
for sender, text in st.session_state.history[-8:]:
    if sender == "الزبون":
        st.markdown(f"<div class='msg-user'><b>👤 الزبون:</b><br>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg-bot'><b>🤖 SmartServe:</b><br>{text}</div>", unsafe_allow_html=True)

# =========== إخراج صوتي ============
if st.session_state.history and st.session_state.history[-1][0] == "SmartServe":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")
