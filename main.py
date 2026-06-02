import asyncio
import os
import sys
import requests
import numpy as np
from google import genai
from moviepy.editor import VideoClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont

API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Generating speech track...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"[💾] Audio saved as: {output_filename}")

def compile_production_video(audio_input: str, video_output: str, sub_segments: list) -> bool:
    print("[🎬] Rendering video with word-synced subtitles...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        duration = audio_clip.duration
        
        # System font backup configuration
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "LiberationSans-Bold.ttf"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 55)
                break
        if not font:
            font = ImageFont.load_default()

        # Har segment ka timing automatically breakdown karne ke liye layout calculation
        total_segments = len(sub_segments)
        time_per_segment = duration / total_segments

        def make_frame(t):
            # Dynamic animated subtle gradient layout background
            bg_v = int(25 + (t * 4) % 15)
            img = Image.new('RGB', (1080, 1920), color=(15, 23, bg_v))
            draw = ImageDraw.Draw(img)
            
            # Subtitle segment detection based on current timestamp
            current_index = min(int(t / time_per_segment), total_segments - 1)
            current_text = sub_segments[current_index]
            
            # Word wrap configuration for vertical shorts block layout
            words = current_text.split()
            wrapped_lines = []
            chunk = []
            for w in words:
                if len(" ".join(chunk + [w])) * 20 > 900:
                    wrapped_lines.append(" ".join(chunk))
                    chunk = [w]
                else:
                    chunk.append(w)
            if chunk:
                wrapped_lines.append(" ".join(chunk))
            
            # Active box render mapping
            y_offset = 900 - (len(wrapped_lines) * 50)
            for line in wrapped_lines:
                # Text shadow effect
                draw.text((94, y_offset + 4), line, fill=(0, 0, 0), font=font)
                # Highlighted dynamic subtitles layout (Yellow color font)
                draw.text((90, y_offset), line, fill=(255, 255, 0), font=font)
                y_offset += 110
                
            return np.array(img)
            
        video_clip = VideoClip(make_frame, duration=duration)
        final_video = video_clip.set_audio(audio_clip)
        
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
        print(f"[❌] Rendering failure: {e}")
        return False
    finally:
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
            requests.post(url, data=payload, files=files, timeout=60)
            print("[🎉] Dynamic short video dispatched successfully!")
    except Exception as e:
        print(f"[❌] Telegram distribution crashed: {e}")

async def main():
    # Structural presentation mapping
    full_caption = (
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Har din, aap AI use karte ho! Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!\n\n"
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai. Socho, kitna smart hai!\n\n"
        "Fact 3: AI sirf data process nahi karta, ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?\n\n"
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    )
    
    # Subtitle layers to sync step-by-step
    sub_segments = [
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!",
        "Fact 1: Har din, aap AI use karte ho!",
        "Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!",
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai.",
        "Socho, kitna smart hai!",
        "Fact 3: AI sirf data process nahi karta,",
        "ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?",
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    ]
    
    await generate_audio_stream(full_caption, "voice.mp3")
    
    if os.path.exists("voice.mp3"):
        render_success = compile_production_video("voice.mp3", "output_short.mp4", sub_segments)
        if render_success and os.path.exists("output_short.mp4"):
            send_video_to_telegram("output_short.mp4", full_caption)

if __name__ == "__main__":
    asyncio.run(main())
            
