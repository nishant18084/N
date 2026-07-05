import streamlit as ui
import google.generativeai as genai
import os

# पेज की सेटिंग और टाइटल
ui.set_page_config(page_title="Simple AI Chatbot", page_icon="🤖")
ui.title("🤖 मेरा सिंपल AI चैटबॉट")
ui.write("GitHub रिपॉजिटरी से बना एक आसान चैटबॉट।")

# GitHub/Deployment प्लेटफॉर्म पर Secrets में GEMINI_API_KEY सेट करें
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    ui.warning("कृपया अपने एनवायरनमेंट वेरिएबल्स (Secrets) में GEMINI_API_KEY सेट करें।")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # चैट हिस्ट्री को स्टोर करने के लिए सेशन स्टेट
    if "messages" not in ui.session_state:
        ui.session_state.messages = []

    # पुरानी बातचीत को स्क्रीन पर दिखाना
    for message in ui.session_state.messages:
        with ui.chat_message(message["role"]):
            ui.markdown(message["content"])

    # यूज़र से इनपुट लेना
    if user_input := ui.chat_input("आप मुझसे क्या पूछना चाहते हैं?"):
        with ui.chat_message("user"):
            ui.markdown(user_input)
        ui.session_state.messages.append({"role": "user", "content": user_input})

        # AI से जवाब जनरेट करना
        with ui.chat_message("assistant"):
            try:
                response = model.generate_content(user_input)
                ai_response = response.text
                ui.markdown(ai_response)
                ui.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                ui.error(f"कुछ गड़बड़ हुई: {e}")
              
