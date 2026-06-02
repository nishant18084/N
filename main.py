import asyncio
import os
import sys
import requests
from google import genai
from moviepy.editor import VideoClip, AudioFileClip
from PIL import Image, ImageDraw

# Environment Credentials Setup
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Generating voiceover...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"[💾] Audio saved as: {output_filename}")

def compile_production_video(audio_input: str, video_output: str, script_text: str) -> bool:
    print("[🎬] Generating moving text background network layout...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        duration = audio_clip.duration
        
        # Text wrapping logic for smartphone screen matrix
        words = script_text.split()
        lines = []
        current_line = []
        for word in words:
            if len(" ".join(current_line + [word])) * 15 > 900:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(" ".join(current_line))

        def make_frame(t):
            """Har frame par background color aur wave opacity badal kar video ko animate karne ke liye"""
            # Frame animation wave sequence
            color_shift = int(15 + (t * 5) % 20)
            img = Image.new('RGB', (1080, 1920), color=(15, color_shift, 42))
            draw = ImageDraw.Draw(img)
            
            # Dynamic moving visual lines to force players to read as video stream
            line_y = int((t * 60) % 1920)
            draw.line([(0, line_y), (1080, line_y)], fill=(30, 41, 59), width=5)
            
            y = 450
            for line in lines:
                draw.text((90, y), line, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0,0,0))
                y += 85
            import numpy as np
            return np.array(img)
            
        # Continuous mathematical frames generate karne ke liye VideoClip configuration
        video_clip = VideoClip(make_frame, duration=duration)
        final_video = video_clip.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="1500k",
            threads=2,
            logger=None
        )
        print("[✅] Complete interactive render cycle completed.")
        return True
    except Exception as e:
        print(f"[❌] Error during rendering: {e}")
        return False
    finally:
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_audio_to_telegram(audio_path: str, caption_text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
    try:
        with open(audio_path, 'rb') as audio_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': f"🎵 *Audio Voiceover Only*\n\n{caption_text}",
                'parse_mode': 'Markdown'
            }
            files = {'audio': audio_file}
            requests.post(url, data=payload, files=files, timeout=45)
    except Exception as e:
        print(f"[❌] Audio push failed: {e}")

def send_video_to_telegram(video_path: str, caption_text: str):
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
            print(f"[🎉] Telegram Gateway Status: {response.status_code}")
    except Exception as e:
        print(f"[❌] Video stream dispatch failed: {e}")

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
        send_audio_to_telegram("voice.mp3", custom_caption)
        
        render_status = compile_production_video("voice.mp3", "output_short.mp4", custom_caption)
        
        if render_status and os.path.exists("output_short.mp4"):
            send_video_to_telegram("output_short.mp4", custom_caption)

if __name__ == "__main__":
    asyncio.run(main())
            
