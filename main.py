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

# Client singleton optimization
client = genai.Client(api_key=API_KEY)

def generate_script_with_fallback(topic: str) -> str:
    """Gemini 2.5 standard aur 1.5 flash backup capability ke sath script generation logic."""
    print(f"[⚙️] Prompt processing initiated for topic: {topic}")
    prompt = (
        f"Write a short, engaging 20-second video script about '{topic}' in Hinglish. "
        "Keep it punchy and optimized for Shorts. Do not include scene descriptions, only spoken text."
    )
    
    # Tier 1 Option: Naya optimized engine
    try:
        print("[⚡] Attempting script generation via gemini-2.5-flash...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except APIError as e:
        if e.code == 503:
            print("[⚠️] Gemini 2.5 is currently overloaded. Switching to stable backup cluster...")
            try:
                # Tier 2 Option: Highly available legacy flash backup core
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                )
                return response.text
            except Exception as backup_error:
                print(f"[❌] Fatal: Both primary and backup models failed: {backup_error}")
                sys.exit(1)
        else:
            print(f"[❌] API Error encountered: {e}")
            sys.exit(1)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    """Edge-TTS synchronous stream writer context encapsulation helper."""
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
    """Advanced audio tracking and multi-stream sub-process rendering module."""
    print("[🎬] Re-muxing video pipeline container...")
    video_clip = None
    audio_clip = None
    final_video = None
    try:
        video_clip = VideoFileClip(video_input)
        audio_clip = AudioFileClip(audio_input)
        
        # Audio length synchronization parameters tracking
        final_video = video_clip.set_duration(audio_clip.duration)
        final_video = final_video.set_audio(audio_clip)
        
        # Advanced rendering settings - Low Memory footprints for GitHub actions
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="1200k",
            threads=2, # Thread safety locks avoid crashing
            logger=None # Removes verbosity bottlenecks in console logs
        )
        print("[✅] Video engine render cycle completed.")
        return True
    except Exception as e:
        print(f"[❌] Compositor Pipeline crash: {e}")
        return False
    finally:
        # Context closures to safely unlock resources under all circumstances
        if video_clip: video_clip.close()
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def dispatch_telegram_media(video_path: str, caption_text: str) -> None:
    """Network request context handling stream chunk media transport protocol."""
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
                'supports_streaming': True,
                'parse_mode': 'Markdown'
            }
            files = {'video': video_file}
            
            # Request wrapper configured with precise connection barriers
            response = requests.post(url, data=payload, files=files, timeout=45)
            
        if response.status_code == 200:
            print("[🎉] Payload packet fully standard delivered to peer.")
        else:
            print(f"[❌] Transport rejection notice: {response.text}")
    except requests.exceptions.Timeout:
        print("[❌] Gateway connection timeout exceeded.")
    except Exception as e:
        print(f"[❌] Unidentified communication failure packet: {e}")

async def main():
    # Dynamic runtime dynamic string topics logic allocation layer
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    # Structural functional sequences execution
    script_content = generate_script_with_fallback(video_topic)
    print(f"\n--- Verified Script Target ---\n{script_content}\n-----------------------------\n")
    
    await generate_audio_stream(script_content, "voice.mp3")
    
    if os.path.exists("background.mp4") and os.path.exists("voice.mp3"):
        export_status = compile_production_video("background.mp4", "voice.mp3", "output_short.mp4")
        if export_status:
            formatted_caption = f"🤖 *{video_topic}*\n\n{script_content}\n\n#ai #facts #shorts"
            dispatch_telegram_media("output_short.mp4", formatted_caption)
    else:
        print("[❌] Critical Operational Disruption: Dependency components file assets not found.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
                                                 
