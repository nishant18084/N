import asyncio
import os
import sys
import requests
import numpy as np
from google import genai
from moviepy.editor import VideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

# Environment variables fetch
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Dispatching TTS vocal matrix...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"[💾] Audio array registered: {output_filename}")

def compile_production_video(audio_input: str, video_output: str, script_text: str) -> bool:
    print("[🎬] Constructing full motion dynamic textual matrix...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        duration = audio_clip.duration
        
        # Paragraph parsing setup
        raw_lines = [line.strip() for line in script_text.split('\n') if line.strip()]
        
        # System font backup routing path
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "LiberationSans-Bold.ttf"
        ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, 50)
                    print(f"[🔤] Font node locked: {path}")
                    break
                except:
                    continue
        if not font:
            font = ImageFont.load_default()
            print("[⚠️] Using low-tier default system font cluster.")

        def make_frame(t):
            # Dynamic vibrant matrix loop calculation
            r = int(20 + (t * 8) % 30)
            g = int(30 + (t * 12) % 40)
            b = int(60 + (t * 15) % 50)
            
            img = Image.new('RGB', (1080, 1920), color=(r, g, b))
            draw = ImageDraw.Draw(img)
            
            # Subtle moving scanner bar to secure video stream metadata validation
            bar_y = int((t * 180) % 1920)
            draw.rectangle([(0, bar_y), (1080, bar_y + 15)], fill=(r+20, g+20, b+30))
            
            # Smart active text-tracking block logic (Line tracking via timeline index)
            total_lines = len(raw_lines)
            if total_lines > 0:
                line_duration = duration / total_lines
                current_index = min(int(t / line_duration), total_lines - 1)
                active_text = raw_lines[current_index]
                
                # Word wrapping module for screen layout bounding box
                words = active_text.split()
                wrapped_lines = []
                chunk = []
                for w in words:
                    if len(" ".join(chunk + [w])) * 18 > 880:
                        wrapped_lines.append(" ".join(chunk))
                        chunk = [w]
                    else:
                        chunk.append(w)
                if chunk:
                    wrapped_lines.append(" ".join(chunk))
                
                # Render engine block drawing
                y_offset = 850 - (len(wrapped_lines) * 45)
                for wl in wrapped_lines:
                    # Clear white tracking text with black border definition
                    draw.text((95, y_offset), wl, fill=(255, 255, 0), font=font, stroke_width=3, stroke_fill=(0,0,0))
                    y_offset += 100
                    
            return np.array(img)
            
        video_clip = VideoClip(make_frame, duration=duration)
        final_video = video_clip.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="1800k",
            threads=2,
            logger=None
        )
        print("[✅] Multiplex cluster compilation executed.")
        return True
    except Exception as e:
        print(f"[❌] Operational drop in rendering sequence: {e}")
        return False
    finally:
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_payloads_to_telegram(audio_path: str, video_path: str, caption: str):
    print("[🚀] Initiating binary cluster distribution channel to Telegram...")
    
    # 1. Dispatch Audio File Layer First
    audio_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    try:
        with open(audio_path, 'rb') as f:
            requests.post(audio_url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': f"🎵 *Voice Track Only*\n\n{caption}", 'parse_mode': 'Markdown'}, files={'audio': f}, timeout=40)
        print("[✅] Audio cluster dispatched.")
    except Exception as e:
        print(f"[❌] Audio transit barrier: {e}")
        
    # 2. Dispatch Fully Rendered Subtitled Shorts Video
    video_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as f:
            response = requests.post(video_url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': f"🎬 *AI Rendered Subtitle Short*\n\n{caption}", 'supports_streaming': True, 'parse_mode': 'Markdown'}, files={'video': f}, timeout=60)
        print(f"[🎉] Video transit completed. Gateway callback status: {response.status_code}")
    except Exception as e:
        print(f"[❌] Video transit barrier: {e}")

async def main():
    custom_caption = (
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Har din, aap AI use karte ho! Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!\n\n"
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai. Socho, kitna smart hai!\n\n"
        "Fact 3: AI sirf data process nahi karta, ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?\n\n"
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    )
    
    await generate_audio_stream(custom_caption, "voice.mp3")
    
    if os.path.exists("voice.mp3"):
        render_success = compile_production_video("voice.mp3", "output_short.mp4", custom_caption)
        if render_success and os.path.exists("output_short.mp4"):
            send_payloads_to_telegram("voice.mp3", "output_short.mp4", custom_caption)
    else:
        print("[❌] System exit: Base audio track creation error.")

if __name__ == "__main__":
    asyncio.run(main())
