import asyncio
import os
import sys
import requests
from google import genai
from moviepy.editor import ColorClip, AudioFileClip

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
    except Exception:
        print("[🔄] Switching to backup model...")
        response = client.models.generate_content(
            model='gemini-2.5-flash-8b',
            contents=prompt,
        )
        return response.text

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Generating voiceover...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"[💾] Audio saved as: {output_filename}")

def compile_production_video(audio_input: str, video_output: str) -> bool:
    print("[🎬] Generating auto-background and rendering video...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        
        # Python khud ek premium dark-blue vertical background generate karega (Shorts size: 1080x1920)
        bg_clip = ColorClip(size=(1080, 1920), color=(15, 23, 42), duration=audio_clip.duration)
        
        # Audio aur background ko combine karna
        final_video = bg_clip.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="1200k",
            threads=2,
            logger=None
        )
        print("[✅] Video render completed successfully.")
        return True
    except Exception as e:
        print(f"[❌] Rendering failure: {e}")
        return False
    finally:
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_video_to_telegram(video_path: str, caption_text: str):
    print("[🚀] Sending video to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as video_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption_text,
                'supports_streaming': True
            }
            files = {'video': video_file}
            response = requests.post(url, data=payload, files=files, timeout=60)
            
        if response.status_code == 200:
            print("[🎉] Video delivered to Telegram!")
        else:
            print(f"[❌] Telegram error: {response.text}")
    except Exception as e:
        print(f"[❌] Network failure: {e}")

async def main():
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    # 1. AI Script
    script_content = generate_script_with_fallback(video_topic)
    print(f"Script: {script_content}")
    
    # 2. Audio Voiceover
    await generate_audio_stream(script_content, "voice.mp3")
    
    # 3. Create Video & Send
    if os.path.
    
