import asyncio
import os
import sys
import requests
import numpy as np
from google import genai
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# Environment Credentials Setup
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Generating voiceover track...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"[💾] Audio array registered: {output_filename}")

def download_live_background_clip(output_path="real_bg.mp4"):
    """Internet se ek real chalti hui vertical shorts background video clip auto-download karne ke liye"""
    print("[📥] Downloading real live video clip from cloud network...")
    
    # Ek standard vertical satisfying/nature/relaxing high-quality stock video link
    video_url = "https://v1.assets.mixkit.co/videos/preview/mixkit-vertical-shot-of-a-beautiful-waterfall-41525-large.mp4"
    
    try:
        response = requests.get(video_url, stream=True, timeout=45)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            print("[✅] Live background video downloaded successfully.")
            return True
        else:
            print("[❌] Direct cloud source link failed.")
            return False
    except Exception as e:
        print(f"[❌] Network error while downloading video asset: {e}")
        return False

def compile_production_video(video_input: str, audio_input: str, video_output: str, script_text: str) -> bool:
    print("[🎬] Rendering real live video with word-synced tracking overlay...")
    video_clip = None
    audio_clip = None
    final_video = None
    try:
        video_clip = VideoFileClip(video_input)
        audio_clip = AudioFileClip(audio_input)
        duration = audio_clip.duration
        
        # Audio ke length ke hisab se background video ko auto-loop ya trim karna
        if video_clip.duration < duration:
            from moviepy.video.fx.all import loop
            video_clip = loop(video_clip, duration=duration)
        else:
            video_clip = video_clip.subclip(0, duration)
            
        # Target Vertical Size ensure karna (1080x1920 layout shorts check)
        video_clip = video_clip.resize(newsize=(1080, 1920))

        raw_lines = [line.strip() for line in script_text.split('\n') if line.strip()]
        total_lines = len(raw_lines)
        time_per_line = duration / total_lines if total_lines > 0 else duration

        from PIL import Image, ImageDraw, ImageFont
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "LiberationSans-Bold.ttf"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 52)
                break
        if not font:
            font = ImageFont.load_default()

        def make_frame(t):
            # Base real video frame extract karna
            frame = video_clip.get_frame(t)
            img = Image.fromarray(frame)
            draw = ImageDraw.Draw(img)
            
            # Active tracking text dynamically find karna
            current_index = min(int(t / time_per_line), total_lines - 1) if total_lines > 0 else 0
            active_text = raw_lines[current_index]
            
            # Word wrapping engine for screen limits
            words = active_text.split()
            wrapped_lines = []
            chunk = []
            for w in words:
                if len(" ".join(chunk + [w])) * 18 > 850:
                    wrapped_lines.append(" ".join(chunk))
                    chunk = [w]
                else:
                    chunk.append(w)
            if chunk:
                wrapped_lines.append(" ".join(chunk))
                
            # Text container center overlay screen render
            y_offset = 950 - (len(wrapped_lines) * 45)
            for wl in wrapped_lines:
                # High-contrast bold yellow titles look exactly like reference link
                draw.text((104, y_offset + 3), wl, fill=(0, 0, 0), font=font) # shadow
                draw.text((100, y_offset), wl, fill=(255, 234, 0), font=font) # main yellow text
                y_offset += 95
                
            return np.array(img)

        # Video clip create karke audio mix karna
        animated_clip = VideoClip(make_frame, duration=duration)
        final_video = animated_clip.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="2200k",
            threads=2,
            logger=None
        )
        return True
    except Exception as e:
        print(f"[❌] Error during production rendering: {e}")
        return False
    finally:
        if video_clip: video_clip.close()
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_video_to_telegram(video_path: str, caption_text: str):
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
            response = requests.post(url, data=payload, files=files, timeout=90)
            print(f"[🎉] Video successfully deployed to channel: {response.status_code}")
    except Exception as e:
        print(f"[❌] Telegram transport layer failure: {e}")

async def main():
    telegram_caption = (
        "🎬 *AI Rendered Short Video with Real Background*\n\n"
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Har din, aap AI use karte ho! Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!\n\n"
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai. Socho, kitna smart hai!\n\n"
        "Fact 3: AI sirf data process nahi karta, ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?\n\n"
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    )
    
    # Line by line split tracking logic
    script_lines = (
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n"
        "Fact 1: Har din, aap AI use karte ho!\n"
        "Google Maps, Netflix suggestions, ya Siri. Yeh sab AI hai!\n"
        "Fact 2: AI ne world champions ko haraya hai.\n"
        "Chess, Go, aur Poker mein! Socho kitna smart hai!\n"
        "Fact 3: AI original music aur paintings bhi bana sakta hai.\n"
        "Kitna creative hai na? Comments mein batao!"
    )
    
    await generate_audio_stream(telegram_caption, "voice.mp3")
    
    if os.path.exists("voice.mp3"):
        # Real background automatically cloud se download hoga
        if download_live_background_clip("real_bg.mp4"):
            render_success = compile_production_video("real_bg.mp4", "voice.mp3", "output_short.mp4", script_lines)
            if render_success and os.path.exists("output_short.mp4"):
                send_video_to_telegram("output_short.mp4", telegram_caption)
    else:
        print("[❌] Asset verification error.")

if __name__ == "__main__":
    asyncio.run(main())
    
