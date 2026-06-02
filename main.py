import asyncio
import os
import sys
import requests
from google import genai
from moviepy.editor import ColorClip, AudioFileClip

# Environment Credentials and Tokens Setup
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

def generate_script_with_fallback(topic: str) -> str:
    """Multi-cluster API backup logic to bypass overloaded status errors."""
    print(f"[⚙️] Executing prompt processing pipeline for: {topic}")
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
        print("[🔄] Primary engine busy. Shifting execution load to backup node...")
        response = client.models.generate_content(
            model='gemini-2.5-flash-8b',
            contents=prompt,
        )
        return response.text

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    """Asynchronous TTS engine setup for Native Madhur Indian Voice."""
    import edge_tts
    print("[🎙️] Synthesizing core textual blocks to speech container...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"[💾] Sound track safely compiled as: {output_filename}")

def compile_production_video(audio_input: str, video_output: str) -> bool:
    """Renders a full 1080x1920 portrait background matching the exact length of the speech stream."""
    print("[🎬] Rendering high-definition vertical video matrix layout...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        
        # Generates the target solid dark premium container background requested (Color Code: RGB 15, 23, 42)
        bg_clip = ColorClip(size=(1080, 1920), color=(15, 23, 42), duration=audio_clip.duration)
        
        # Hard alignment of audio data track onto visual frame segments
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
        print("[✅] Multiplexing render run successfully terminated.")
        return True
    except Exception as e:
        print(f"[❌] Structural breakdown in rendering module: {e}")
        return False
    finally:
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_audio_to_telegram(audio_path: str, caption_text: str):
    """Pushes standalone audio file directly via Telegram API."""
    print("[🚀] Transport layer initiating audio packet upload...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    try:
        with open(audio_path, 'rb') as audio_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': f"🎵 *Audio Voiceover Only*\n\n{caption_text}",
                'title': 'voiceover.mp3',
                'parse_mode': 'Markdown'
            }
            files = {'audio': audio_file}
            requests.post(url, data=payload, files=files, timeout=45)
        print("[✅] Audio track uploaded successfully.")
    except Exception as e:
        print(f"[❌] Connection barrier on audio block transfer: {e}")

def send_video_to_telegram(video_path: str, caption_text: str):
    """Pushes compiled MP4 stream containing audio context layers via Telegram API."""
    print("[🚀] Transport layer initiating full video packet stream...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as video_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': f"🎬 *Full Video with Audio*\n\n{caption_text}",
                'supports_streaming': True,
                'parse_mode': 'Markdown'
            }
            files = {'video': video_file}
            response = requests.post(url, data=payload, files=files, timeout=60)
            
        if response.status_code == 200:
            print("[🎉] System complete delivery confirmation received!")
        else:
            print(f"[❌] Gateway server rejected payload transfer: {response.text}")
    except Exception as e:
        print(f"[❌] Network interface timeout on binary push: {e}")

async def main():
    # Targeted context payload requested by user
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    # Custom structure provided directly to override any default AI variance text
    custom_caption = (
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Har din, aap AI use karte ho! Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!\n\n"
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai. Socho, kitna smart hai!\n\n"
        "Fact 3: AI sirf data process nahi karta, ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?\n\n"
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    )
    
    # Step 1: Content verification and speech engine streaming activation
    await generate_audio_stream(custom_caption, "voice.mp3")
    
    if os.path.exists("voice.mp3"):
        # Step 2: Push independent vocal layer first
        send_audio_to_telegram("voice.mp3", custom_caption)
        
        # Step 3: Trigger core dynamic overlay rendering pipeline
        render_status = compile_production_video("voice.mp3", "output_short.mp4")
        
        # Step 4: Dispatch full layout package straight to channel endpoint
        if render_status and os.path.exists("output_short.mp4"):
            send_video_to_telegram("output_short.mp4", custom_caption)
    else:
        print("[❌] System runtime failure: Operational buffers tracking empty.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
    
