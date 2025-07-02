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

# ==== CSS للتصميم الحديث مع وضوح تام للنصوص ====
st.set_page_config(layout="centered", page_title="مساعد SmartServe AI الذكي")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700;900&family=Tajawal:wght@400;700&display=swap');
    body, .stApp {
        background: url('https://wallpapers.com/images/featured/restaurant-background-2ez77umko2vj5w02.jpg') no-repeat center center fixed !important;
        background-size: cover !important;
        font-family: 'Cairo', 'Tajawal', sans-serif !important;
    }
    .main {background: rgba(0, 0, 0, 0.5) !important; border-radius: 20px;}
    .bubble-user {
        background: rgba(30,30,36,0.79);
        border-radius: 18px 0 18px 18px;
        margin-bottom: 8px; padding: 15px 21px 11px 15px; font-size:19px; text-align:right;
        color:#fff;direction:rtl; max-width:80%; margin-left:auto; margin-right:2vw;
        box-shadow: 0 4px 12px #000a;
        border:1.5px solid #fff2;
        text-shadow: 0 2px 7px #000b;
    }
    .bubble-bot  {
        background: rgba(255,245,180,0.78);
        border-radius: 0 18px 18px 18px;
        margin-bottom: 12px; padding: 15px 21px 13px 15px; font-size:19px;
        font-weight:600;text-align:right;color:#382a00;direction:rtl; max-width:80%; margin-right:auto; margin-left:2vw;
        box-shadow: 0 2px 10px #0008;
        border:1.3px solid #ffe27a;
        text-shadow: 0 2px 8px #fff8, 0 1px 3px #ffe59e;
    }
    .stTextInput input {
        font-size:19px; text-align:right; border-radius:11px;
        background:rgba(28,28,34,0.93)!important; color:#ffe !important;
        border: 2px solid #ffd95ba1;
        box-shadow: 0 2px 8px #000a;
    }
    .stTextInput input::placeholder {color:#fff6;}
    .stButton>button {
        background: linear-gradient(90deg,#ffd95b 60%, #ffeeba 100%);
        color: #28220d; font-size:20px; font-weight:bold; border-radius:12px; padding:8px 0;
        border: 1.8px solid #ffd95b; box-shadow:0 2px 8px #23201290;
    }
    .stButton>button:hover { background: #fff7dc !important; color: #a87e00;}
    .example-hint {
        font-size:17px;color:#fff; background:rgba(40,32,0,0.33);border-radius:11px; padding:7px 17px; margin-bottom:18px;text-align:right;box-shadow:0 2px 8px #0003;
        text-shadow:0 2px 8px #0009;
    }
    .app-header {
        color: #ffe186;
        text-shadow: 0 2px 15px #000c, 0 2px 4px #6a4a015c;
        font-size: 36px;
        font-weight: 900;
        margin-bottom: 4px;
        margin-top: 7px;
    }
    .app-subheader {
        font-size:20px;color:#fffbe9;margin-bottom:15px;
        text-shadow:0 1px 7px #000c;
    }
    @media only screen and (max-width: 700px) {
        .bubble-user, .bubble-bot {font-size:15px; padding: 9px 4px;}
        .main {border-radius:0;}
        .app-header {font-size:27px;}
        .app-subheader {font-size:15px;}
        .example-hint {font-size:13px;}
    }
    </style>
""", unsafe_allow_html=True)

# ---- رأس الصفحة واللوجو ----
st.markdown(f"""
    <div style='text-align:center;margin-bottom:1px;'>
        <img src="{LOGO_URL}" style="width:80px; margin-bottom:-16px;" />
        <div class='app-header'>SmartServe</div>
        <div class='app-subheader'>مساعد ذكي لطلبات الطعام والمشروبات</div>
    </div>
""", unsafe_allow_html=True)

# ---- مثال أسفل العنوان ----
st.markdown(
    """
    <div class='example-hint'>
        👇 <b>مثال:</b> <b>وجبة غداء نباتية</b> أو <b>ما هي مكونات المنسف؟</b>
    </div>
    """,
    unsafe_allow_html=True
)

# ==== سجل المحادثة ====
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
            answer = ask_ai(msgs)
        st.session_state.history.append(("الزبون", final_input))
        st.session_state.history.append(("SmartServe", answer))

# ---- عرض المحادثة ----
for sender, text in st.session_state.history[-8:]:
    if sender == "الزبون":
        st.markdown(f"<div class='bubble-user'><b>👤 الزبون:</b><br>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-bot'><b>🤖 SmartServe:</b><br>{text}</div>", unsafe_allow_html=True)

# ---- إخراج صوتي ----
if st.session_state.history and st.session_state.history[-1][0] == "SmartServe":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")
