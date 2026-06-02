import asyncio
import os
import sys
import requests
from google import genai
from moviepy.editor import VideoFileClip, AudioFileClip

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

def download_auto_background(output_path: str = "background.mp4"):
    """Internet se ek standard vertical background video auto-download karne ke liye"""
    print("[📥] Downloading automatic background video from cloud...")
    # Ek stable vertical abstract space/nature video ka direct link
    video_url = "https://assets.mixkit.co/videos/preview/mixkit-abstract-laser-lights-background-42171-large.mp4"
    
    try:
        response = requests.get(video_url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            print("[✅] Background video auto-downloaded successfully.")
            return True
        else:
            print("[❌] Download failed, server response error.")
            return False
    except Exception as e:
        print(f"[❌] Network error while downloading video: {e}")
        return False

def compile_production_video(video_input: str, audio_input: str, video_output: str) -> bool:
    print("[🎬] Merging downloaded video and generated audio...")
    video_clip = None
    audio_clip = None
    final_video = None
    try:
        video_clip = VideoFileClip(video_input)
        audio_clip = AudioFileClip(audio_input)
        
        # Video loop ya trim parameters
        if video_clip.duration < audio_clip.duration:
            # Agar background chhota hai toh loop karein
            from moviepy.video.fx.all import loop
            video_clip = loop(video_clip, duration=audio_clip.duration)
        
        final_video = video_clip.set_duration(audio_clip.duration)
        final_video = final_video.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="1200k",
            threads=2,
            logger=None
        )
        print("[✅] Video render cycle completed.")
        return True
    except Exception as e:
        print(f"[❌] Rendering failure: {e}")
        return False
    finally:
        if video_clip: video_clip.close()
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_video_to_telegram(video_path: str, caption_text: str):
    print("[🚀] Sending full video to Telegram...")
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
            print("[🎉] Complete Video delivered to Telegram!")
        else:
            print(f"[❌] Telegram push failed: {response.text}")
    except Exception as e:
        print(f"[❌] Network failure: {e}")

async def main():
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    # 1. AI Script
    script_content = generate_script_with_fallback(video_topic)
    
    # 2. Audio Voiceover
    await generate_audio_stream(script_content, "voice.mp3")
    
    # 3. Auto Background Download (No manual upload needed)
    download_success = download_auto_background("background.mp4")
    
    # 4. Mix & Send
    if download_success and os.path.exists("voice.mp3"):
        render_success = compile_production_video("background.mp4", "voice.mp3", "output_short.mp4")
        if render_success:
            formatted_caption = f"🤖 *{video_topic}*\n\n{script_content}\n\n#ai #shorts"
            send_video_to_telegram("output_short.mp4", formatted_caption)
    else:
        print("[❌] Setup failed due to missing dynamic assets.")

if __name__ == "__main__":
    asyncio.run(main())
    
