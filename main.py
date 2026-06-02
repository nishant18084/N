import asyncio
import os
import sys
import requests
from google import genai
from google.genai.errors import APIError
from moviepy.editor import VideoFileClip, AudioFileClip

# Global configurations aur environment initializations
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Client singleton initialization
client = genai.Client(api_key=API_KEY)

def generate_script_with_fallback(topic: str) -> str:
    """Gemini 2.5 standard aur naye SDK compatible 1.5 flash backup logic."""
    print(f"[⚙️] Prompt processing initiated for topic: {topic}")
    prompt = (
        f"Write a short, engaging 20-second video script about '{topic}' in Hinglish. "
        "Keep it punchy and optimized for Shorts. Do not include scene descriptions, only the spoken text."
    )
    
    # Tier 1 Option: Primary Model
    try:
        print("[⚡] Attempting script generation via gemini-2.5-flash...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[⚠️] Gemini 2.5 is busy or failed. Error: {e}")
        print("[🔄] Switching to highly-available backup cluster (gemini-2.5-flash-8b)...")
        try:
            # Tier 2 Option: 2.5 ka lightweight variant (Highly stable fallback)
            response = client.models.generate_content(
                model='gemini-2.5-flash-8b',
                contents=prompt,
            )
            return response.text
        except Exception as backup_error:
            print("[⚠️] Backup Tier 2 failed. Trying Tier 3 (gemini-1.5-pro)...")
            try:
                # Tier 3 Option: Pro Engine for strict availability
                response = client.models.generate_content(
                    model='gemini-1.5-pro',
                    contents=prompt,
                )
                return response.text
            except Exception as critical_error:
                print(f"[❌] Fatal Core Crash: All cluster pools exhausted: {critical_error}")
                sys.exit(1)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    """Edge-TTS layer implementation context."""
    import edge_tts
    print("[🎙️] Dispatching text-to-speech renderer...")
    voice = "hi-IN-MadhurNeural" 
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_filename)
        print(f"[💾] Audio compilation finalized and stored as: {output_filename}")
    except Exception as e:
        print(f"[❌] Native TTS Exception: {e}")
        sys.exit(1)

def compile_production_video(video_input: str, audio_input: str, video_output: str) -> bool:
    """Audio alignment and re-muxing compilation interface."""
    print("[🎬] Re-muxing video pipeline container...")
    video_clip = None
    audio_clip = None
    final_video = None
    try:
        video_clip = VideoFileClip(video_input)
        audio_clip = AudioFileClip(audio_input)
        
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
        print("[✅] Video engine render cycle completed.")
        return True
    except Exception as e:
        print(f"[❌] Compositor Pipeline crash: {e}")
        return False
    finally:
        if video_clip: video_clip.close()
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def dispatch_telegram_media(video_path: str, caption_text: str) -> None:
    """Network connection management module for clean delivery."""
    print("[🚀] Transport layer initializing media export to Telegram network...")
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[❌] Network Exception: Missing authorization tokens.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    
    try:
        with open(video_path, 'rb') as video_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption_text,
                'supports_streaming': True
            }
            files = {'video': video_file}
            response = requests.post(url, data=payload, files=files, timeout=45)
            
        if response.status_code == 200:
            print("[🎉] Payload packet fully standard delivered to peer.")
        else:
            print(f"[❌] Transport rejection notice: {response.text}")
    except Exception as e:
        print(f"[❌] Communication failure packet: {e}")

async def main():
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    # Sequences control execution flow
    script_content = generate_script_with_fallback(video_topic)
    print(f"\n--- Verified Script Target ---\n{script_content}\n-----------------------------\n")
    
    await generate_audio_stream(script_content, "voice.mp3")
    
    if os.path.exists("background.mp4") and os.path.exists("voice.mp3"):
        export_status = compile_production_video("background.mp4", "voice.mp3", "output_short.mp4")
        if export_status:
            formatted_caption = f"🤖 {video_topic}\n\n{script_content}\n\n#ai #facts #shorts"
            dispatch_telegram_media("output_short.mp4", formatted_caption)
    else:
        print("[❌] Critical Operational Disruption: Target file assets not found.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
        
