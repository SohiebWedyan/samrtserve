import streamlit as st
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os

# إعداد API
HF_TOKEN = "hf_..."  # ضع التوكن الخاص بك هنا أو استخدم open access إن أردت
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

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

st.set_page_config(layout="centered", page_title="مساعد SmartServe الذكي")
st.markdown("""
    <style>
    .stTextInput input { font-size:18px; direction:rtl; text-align:right; }
    .stButton>button { font-size:18px; border-radius:8px; }
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

# --- واجهة الإدخال في صف واحد ---
st.markdown("<h2 style='text-align:right;'>👇 اسأل صوتيًا أو نصيًا</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    user_input = st.text_input("سؤالك أو طلبك:", key="input", placeholder="مثال: وجبة غداء نباتية ...", label_visibility="collapsed")
with col2:
    audio = audio_recorder("🎤", icon_size="1.5x")
with col3:
    submit = st.button("إرسال", use_container_width=True)

# --- معالجة الصوت ---
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

# --- المنطق عند الإرسال ---
if submit and final_input:
    menu_results = search_menu(final_input)
    if menu_results:
        msg = "إليك بعض الخيارات من المنيو لدينا:\n"
        for item in menu_results:
            msg += f"- **{item['name']}**: {item['desc']}\n"
        st.session_state.history.append(("أنت", final_input))
        st.session_state.history.append(("المساعد", msg))
    else:
        msgs = [{"role": "system", "content": "أنت مساعد مطاعم ذكي ترد بالعربية الفصحى وتوضح اقتراحات الطعام أو أي معلومات غذائية أو نصائح حول المنيو."}]
        for s, m in st.session_state.history[-6:]:
            msgs.append({"role": "user" if s == "أنت" else "assistant", "content": m})
        msgs.append({"role": "user", "content": final_input})
        with st.spinner("جاري البحث الذكي عبر الذكاء الاصطناعي ..."):
            answer = ask_ai(msgs)
        st.session_state.history.append(("أنت", final_input))
        st.session_state.history.append(("المساعد", answer))

# --- عرض الرسائل بشكل أنيق ---
for sender, text in st.session_state.history[-8:]:
    if sender == "أنت":
        st.markdown(f"<div style='background:#e9f1ff; border-radius:14px; padding:10px; margin-bottom:4px; text-align:right'><b>🧑‍💼</b> {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#fff8d6; border-radius:14px; padding:11px; margin-bottom:8px; font-weight:600; text-align:right'><b>🤖</b> {text}</div>", unsafe_allow_html=True)

# --- إخراج صوتي ---
if st.session_state.history and st.session_state.history[-1][0] == "المساعد":
    last_response = st.session_state.history[-1][1]
    tts = gTTS(last_response, lang="ar")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")
