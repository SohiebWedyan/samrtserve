import streamlit as st
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os

# إعدادات النموذج
HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "NousResearch/Hermes-3-Llama-3.1-8B"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3075/3075977.png"

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

st.set_page_config(layout="centered", page_title="SmartServe - مساعد الطلبات الذكي")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700;900&family=Tajawal:wght@400;700&display=swap');
    body, .stApp {
        background: url('https://wallpapers.com/images/featured/restaurant-background-2ez77umko2vj5w02.jpg') no-repeat center center fixed !important;
        background-size: cover !important;
        font-family: 'Cairo', 'Tajawal', sans-serif !important;
    }
    .main {background: rgba(30, 29, 29, 0.84) !important;}
    .bubble-user {
        background: linear-gradient(90deg, #e3eaffb9 70%, #fff9e3a1 100%);
        border-radius: 16px 0 16px 16px;
        box-shadow: 0 2px 10px #0002;
        margin-bottom: 6px; padding: 14px 17px 9px 14px; font-size:18px; text-align:right;
        color:#232323;direction:rtl; max-width:77%; margin-left:auto; margin-right:3px;
    }
    .bubble-bot  {
        background: linear-gradient(270deg, #fff9e3e7 70%, #e3eaff95 100%);
        border-radius: 0 16px 16px 16px;
        box-shadow: 0 2px 13px #0002;
        margin-bottom: 10px; padding: 14px 17px 12px 14px; font-size:18px;
        font-weight:600;text-align:right;color:#2d2210;direction:rtl; max-width:77%; margin-right:auto; margin-left:3px;
    }
    .stTextInput input { font-size:19px; text-align:right; border-radius:8px;}
    .stButton>button {
        background: linear-gradient(90deg,#ffd95b 50%, #fae18c 100%);
        color: #232323; font-size:19px; font-weight:bold; border-radius:10px; padding:7px 0;
        border: 1.3px solid #e7cf7b; box-shadow:0 2px 7px #c9ad5b40;
    }
    .stButton>button:hover { background: #ffebaf !important; color: #a87e00;}
    .icon-mic {
        font-size: 30px !important;
        margin-left: -6px;
        color: #F9E27B;
        filter: drop-shadow(1px 1px 3px #4447);
        cursor:pointer;
    }
    /* Mobile */
    @media only screen and (max-width: 600px) {
        .bubble-user, .bubble-bot {font-size:15px; padding: 10px 6px;}
        .main {border-radius:0;}
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
    <div style='text-align:center;margin-bottom:1px;'>
        <img src="{LOGO_URL}" style="width:73px; margin-bottom:-14px;" />
        <div style='font-size:29px; font-weight:900; color:#F9E27B; letter-spacing:1px; margin-bottom:4px; margin-top:10px;'>SmartServe</div>
        <div style='font-size:17px;color:#faf4ce;margin-bottom:12px;'>مساعد ذكي لطلبات الطعام والمشروبات</div>
    </div>
""", unsafe_allow_html=True)

# --- Animated Example ---
st.markdown("""
<div style='font-size:15px; color:#F9E27B; margin-bottom:13px;text-align:right;animation:fadein 1.5s;'>
    <span style='animation:bounce 1s infinite alternate;display:inline-block;'>👇</span>
    <b>مثال:</b>
    <span style="background:#fff9e3aa;padding:2px 8px;border-radius:7px;">وجبة غداء نباتية</span>
    أو
    <span style="background:#e3eaffad;padding:2px 8px;border-radius:7px;">ما هي مكونات المنسف؟</span>
</div>
<style>
@keyframes bounce { 0%{transform:translateY(0);} 100%{transform:translateY(6px);} }
@keyframes fadein { from{opacity:0;} to{opacity:1;} }
</style>
""", unsafe_allow_html=True)

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

# --- عرض المحادثة بشكل فقاعات ---
for sender, text in st.session_state.history[-8:]:
    if sender == "الزبون":
        st.markdown(f"<div class='bubble-user'><b>👤 الزبون:</b><br>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bubble-bot'><b>🤖 SmartServe:</b><br>{text}</div>", unsafe_allow_html=True)

# --- إخراج صوتي ---
if st.session_state.history and st.session_state.history[-1][0] == "SmartServe":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")

# --- Footer بسيط ---
st.markdown("""
<div style='text-align:center; color:#ffe187; font-size:13px; margin-top:30px;'>
    تصميم <a href="https://github.com/sohiebwedyan" style="color:#fff9e3;text-decoration:underline;font-weight:700;" target="_blank">Sohieb Wedyan</a>
    | Powered by Hermes-Llama3 | <a href='https://github.com/sohiebwedyan' style="color:#bdbdbd;" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
