import asyncio
import os
import sys
import requests
import numpy as np
from google import genai
from moviepy.editor import VideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

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

def compile_production_video(audio_input: str, video_output: str, script_text: str) -> bool:
    print("[🎬] Generating moving cinematic background with text synchronization...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        duration = audio_clip.duration
        
        # Line wise split for subtitle transitions
        raw_lines = [line.strip() for line in script_text.split('\n') if line.strip()]
        total_lines = len(raw_lines)
        time_per_line = duration / total_lines if total_lines > 0 else duration

        # System Font setup for Linux Container
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
            # 1. GENERATE MOVING BACKGROUND ANIMATION (No internet required)
            # Dheere-dheere badalta hua premium deep background color loop
            r = int(15 + np.sin(t * 0.5) * 5)
            g = int(23 + np.cos(t * 0.5) * 5)
            b = int(42 + np.sin(t * 0.3) * 10)
            img = Image.new('RGB', (1080, 1920), color=(r, g, b))
            draw = ImageDraw.Draw(img)
            
            # Subtitle background subtle glowing circles to show heavy video movement
            for i in range(3):
                radius = int(200 + np.sin(t * 2 + i) * 50)
                center_x = int(540 + np.cos(t + i) * 100)
                center_y = int(960 + np.sin(t + i) * 150)
                draw.ellipse(
                    [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], 
                    outline=(r+15, g+20, b+35), width=4
                )
            
            # 2. SUBTITLE SYNCHRONIZATION LOGIC
            current_index = min(int(t / time_per_line), total_lines - 1) if total_lines > 0 else 0
            active_text = raw_lines[current_index]
            
            # Word wrapping for safe screen bounds
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
                
            # Render Text onto the live frame matrix
            y_offset = 950 - (len(wrapped_lines) * 45)
            for wl in wrapped_lines:
                # Heavy Drop Shadow for premium YouTube Shorts look
                draw.text((104, y_offset + 4), wl, fill=(0, 0, 0), font=font)
                # Vibrant Yellow Main Text
                draw.text((100, y_offset), wl, fill=(255, 234, 0), font=font)
                y_offset += 95
                
            return np.array(img)

        # Build real full-motion mp4 file container
        animated_clip = VideoClip(make_frame, duration=duration)
        final_video = animated_clip.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="2000k",
            threads=2,
            logger=None
        )
        return True
    except Exception as e:
        print(f"[❌] Rendering failed at core layer: {e}")
        return False
    finally:
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_video_to_telegram(video_path: str, caption_text: str):
    print("[🚀] Transporting compiled short video package to Telegram...")
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
            print(f"[🎉] Telegram Gateway Response Code: {response.status_code}")
    except Exception as e:
        print(f"[❌] Critical network push failure: {e}")

async def main():
    telegram_caption = (
        "🎬 *AI Rendered Short Video with Moving Background*\n\n"
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Har din, aap AI use karte ho! Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!\n\n"
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai. Socho, kitna smart hai!\n\n"
        "Fact 3: AI sirf data process nahi karta, ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?\n\n"
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    )
    
    # Exact subtitle line sequencing for the reference look
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
        render_success = compile_production_video("voice.mp3", "output_short.mp4", script_lines)
        if render_success and os.path.exists("output_short.mp4"):
            send_video_to_telegram("output_short.mp4", telegram_caption)
    else:
        print("[❌] Voice track buffer initialization failed.")

if __name__ == "__main__":
    asyncio.run(main())
    
