import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

from farming_kb import setup_knowledge_base
from translator import (
    detect_language,
    translate_to_english,
    translate_from_english,
    get_language_name
)

from retriever import (
    retrieve_documents,
    build_context
)

from llm import ask_llm

from safety import (
    apply_safety_rules,
    safety_message
)

# New import for government schemes
from govt_schemes import (
    setup_schemes_knowledge_base,
    retrieve_schemes,
    build_schemes_context
)

# New import for weather
from weather import get_weather



st.set_page_config(
    page_title="KrishiMitra AI",
    page_icon="🌾",
    layout="centered"
)



st.title("🌾 KrishiMitra AI")
st.subheader("Multilingual Agricultural Assistant")
st.write("தமிழ் • हिंदी • English")



@st.cache_resource
def initialize_agri_kb():
    return setup_knowledge_base()

@st.cache_resource
def initialize_schemes_kb():
    return setup_schemes_knowledge_base()


agri_collection = initialize_agri_kb()
schemes_collection = initialize_schemes_kb()



with st.sidebar:
    st.header("📍 Location (for weather)")
    
    if 'latitude' not in st.session_state:
        st.session_state.latitude = 13.0827  # Default: Chennai
    if 'longitude' not in st.session_state:
        st.session_state.longitude = 80.2707

    lat_input = st.number_input(
        "Latitude",
        value=st.session_state.latitude,
        format="%.6f",
        step=0.000001,
        help="Enter latitude (e.g., 13.0827 for Chennai)"
    )
    lon_input = st.number_input(
        "Longitude",
        value=st.session_state.longitude,
        format="%.6f",
        step=0.000001,
        help="Enter longitude (e.g., 80.2707 for Chennai)"
    )

    
    if lat_input != st.session_state.latitude or lon_input != st.session_state.longitude:
        st.session_state.latitude = lat_input
        st.session_state.longitude = lon_input

    if st.button("🌤️ Get Current Weather"):
        with st.spinner("Fetching weather data..."):
            weather_info = get_weather(st.session_state.latitude, st.session_state.longitude)
            st.session_state.weather_info = weather_info
            st.success("Weather updated!")

    
    if 'weather_info' in st.session_state:
        st.info(f"**Weather:** {st.session_state.weather_info}")

    st.divider()
    st.header("🎤 Voice Settings")
    use_voice_input = st.checkbox("Enable voice input (speech-to-text)", value=False)
    use_voice_output = st.checkbox("Enable voice output (text-to-speech)", value=False)



language = st.selectbox(
    "Language / மொழி / भाषा",
    options=["ta", "hi", "en"],
    format_func=lambda code: {
        "ta": "🇮🇳 தமிழ்",
        "hi": "🇮🇳 हिंदी",
        "en": "🇬🇧 English"
    }[code]
)



crop = st.selectbox(
    "Crop / பயிர் / फसल",
    options=["rice", "tomato", "cotton"],
    format_func=lambda value: {
        "rice": "🌾 Rice / நெல் / धान",
        "tomato": "🍅 Tomato / தக்காளி / टमाटर",
        "cotton": "🌱 Cotton / பருத்தி / कपास"
    }[value]
)


# Initialize question in session state if not present
if 'question' not in st.session_state:
    st.session_state.question = ""

question = st.text_area(
    "Your Question / உங்கள் கேள்வি / आपका प्रश्न",
    value=st.session_state.question,
    height=150,
    placeholder=(
        "Example:\n"
        "என் நீல்풀이 노랗게 변했어요. 무엇을 해야 할까요?"
    )
)

if use_voice_input:
    if st.button("🎤 Record Voice"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now.")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                st.info("Processing speech...")
                # Recognize speech using Google Web Speech API (free)
                voice_text = recognizer.recognize_google(audio)
                st.session_state.question = voice_text
                st.success(f"Recognized: {voice_text}")
                # Rerun to update text area
                st.experimental_rerun()
            except sr.WaitTimeoutError:
                st.error("Listening timed out. Please try again.")
            except sr.UnknownValueError:
                st.error("Sorry, could not understand audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from speech service; {e}")
            except Exception as e:
                st.error(f"Error: {e}")



ask_button = st.button(
    "🌾 Get Agricultural Advice",
    use_container_width=True
)

if ask_button:

    st.session_state.question = question

    if not st.session_state.question.strip():
        st.warning("Please enter your agricultural question.")
        st.stop()

    question = st.session_state.question

    with st.spinner("Detecting language..."):
        try:
            detected_language = detect_language(question)
        except Exception as error:
            st.error(f"Language detection error: {error}")
            st.stop()

    st.info(f"Detected language: **{get_language_name(detected_language)}**")

    with st.spinner("Processing your question..."):
        try:
            english_question = translate_to_english(
                question, detected_language
            )
        except Exception as error:
            st.error(f"Translation error: {error}")
            st.stop()

    with st.spinner("Searching agricultural knowledge..."):
        try:
            agri_retrieved_documents = retrieve_documents(
                english_question, crop=crop, top_k=3
            )
        except Exception as error:
            st.error(f"Knowledge search error: {error}")
            st.stop()

    with st.spinner("Searching government schemes..."):
        try:
            schemes_retrieved = retrieve_schemes(
                english_question, crop=crop, top_k=3
            )
        except Exception as error:
            st.error(f"Schemes search error: {error}")
            st.stop()

    weather_context = ""
    if 'weather_info' in st.session_state:
        weather_context = f"LOCAL WEATHER INFORMATION:\n{st.session_state.weather_info}\n"


    safety = apply_safety_rules(english_question, agri_retrieved_documents)


    if not safety["safe"]:

        english_answer = safety_message(detected_language)

        st.warning(english_answer)
        st.metric("Confidence", f"{safety['confidence'] * 100:.0f}%")
        st.info("👨‍🔬 Expert verification recommended.")
        st.stop()


    agri_context = build_context(agri_retrieved_documents)
    schemes_context = build_schemes_context(schemes_retrieved)

    # Combine contexts
    combined_context = agri_context + "\n\n---\n\n" + schemes_context
    if weather_context:
        combined_context = weather_context + "\n\n---\n\n" + combined_context


    with st.spinner("Generating agricultural answer..."):
        try:
            english_answer = ask_llm(
                question=english_question,
                context=combined_context,
                crop=crop
            )
        except Exception as error:
            st.error(f"AI error: {error}")
            st.stop()


    with st.spinner("Preparing answer..."):
        try:
            final_answer = translate_from_english(
                english_answer, detected_language
            )
        except Exception as error:
            st.error(f"Answer translation error: {error}")
            st.stop()


    st.success("🌾 Agricultural advice")
    st.write(final_answer)

    confidence = safety["confidence"]
    st.metric("Knowledge confidence", f"{confidence * 100:.0f}%")
    if schemes_retrieved:
        st.info(f"💡 Also included {len(schemes_retrieved)} relevant government scheme(s).")
    if use_voice_output:
        try:
            tts = gTTS(text=final_answer, lang=detected_language, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
                tts.save(temp_path)
            st.audio(temp_path, format="audio/mp3")
        except Exception as e:
            st.error(f"Voice generation error: {e}")

    with st.expander("📚 Retrieved agricultural sources"):
        for item in agri_retrieved_documents:
            st.write(f"**Crop:** {item['crop']}")
            st.write(f"**Source:** {item['source']}")
            st.write(item["document"])
            st.divider()

    with st.expander("🏛️ Retrieved government schemes"):
        for item in schemes_retrieved:
            st.write(f"**Scheme:** {item['scheme_name']}")
            st.write(f"**Crop:** {item['crop']}")
            st.write(f"**Source:** {item['source']}")
            st.write(item["document"])
            st.divider()

    with st.expander("🌤️ Weather Information"):
        if 'weather_info' in st.session_state:
            st.write(st.session_state.weather_info)
        else:
            st.write("No weather data available. Click 'Get Current Weather' in sidebar.")