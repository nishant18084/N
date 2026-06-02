import asyncio
import os
import sys
import requests
from google import genai

# Environment Variables
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

def generate_script_with_fallback(topic: str) -> str:
    print(f"[⚙️] Script generation started for: {topic}")
    prompt = (
        f"Write a short, engaging 20-second video script about '{topic}' in Hinglish. "
        "Keep it punchy and optimized for Shorts. Do not include scene descriptions, only spoken text."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[⚠️] Switching to backup model due to: {e}")
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-8b',
                contents=prompt,
            )
            return response.text
        except Exception as err:
            print(f"[❌] Both models failed: {err}")
            sys.exit(1)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Generating voiceover...")
    voice = "hi-IN-MadhurNeural" 
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_filename)
        print(f"[💾] Audio saved as: {output_filename}")
    except Exception as e:
        print(f"[❌] TTS Error: {e}")
        sys.exit(1)

def send_audio_to_telegram(audio_path: str, caption_text: str):
    print("[🚀] Sending audio package to Telegram...")
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[❌] Missing Telegram Credentials.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    
    try:
        with open(audio_path, 'rb') as audio_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption_text,
                'title': 'AI_Voiceover.mp3'
            }
            files = {'audio': audio_file}
            response = requests.post(url, data=payload, files=files, timeout=45)
            
        if response.status_code == 200:
            print("[🎉] Audio delivered successfully to Telegram!")
        else:
            print(f"[❌] Telegram error: {response.text}")
    except Exception as e:
        print(f"[❌] Network failure: {e}")

async def main():
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    # 1. Script Layein
    script_content = generate_script_with_fallback(video_topic)
    print(f"\n--- Script ---\n{script_content}\n--------------\n")
    
    # 2. Audio Banayein
    await generate_audio_stream(script_content, "voice.mp3")
    
    # 3. Bina Video Check Kiye Direct Telegram Par Bhejein
    if os.path.exists("voice.mp3"):
        formatted_caption = f"🤖 *{video_topic}*\n\n{script_content}"
        send_audio_to_telegram("voice.mp3", formatted_caption)
    else:
        print("[❌] voice.mp3 not found!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
                
