import asyncio
import os
import sys
import requests
from google import genai
from moviepy.editor import ColorClip, AudioFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

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
    print(f"[💾] Sound track saved as: {output_filename}")

def create_text_image(text: str, size=(1080, 1920)):
    """Video ke center mein text generate karne ke liye PIL framework"""
    img = Image.new('RGBA', size, color=(15, 23, 42, 255)) # Premium Dark Blue
    draw = ImageDraw.Draw(img)
    
    # Text wrapping logic for smartphone screens
    words = text.split()
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
        
    # Standard baseline drawing
    y = 500
    for line in lines:
        # Bina external ttf dependency ke clean crisp blocks create karna
        draw.text((90, y), line, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0,0,0))
        y += 80
        
    img.save("text_frame.png")

def compile_production_video(audio_input: str, video_output: str, script_text: str) -> bool:
    print("[🎬] Generating text overlay and rendering layout...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        
        # Frame dynamic generation trigger
        create_text_image(script_text)
        
        # Continuous visual static image clip layout alignment
        video_clip = ImageClip("text_frame.png").set_duration(audio_clip.duration)
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
        print("[✅] Multiplexing video render successfully completed.")
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
        print(f"[❌] Audio send failed: {e}")

def send_video_to_telegram(video_path: str, caption_text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as video_file:
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': f"🎬 *Full Video with Text Overlay*\n\n{caption_text}",
                'supports_streaming': True,
                'parse_mode': 'Markdown'
            }
            files = {'video': video_file}
            response = requests.post(url, data=payload, files=files, timeout=60)
            
        if response.status_code == 200:
            print("[🎉] Video delivered successfully!")
        else:
            print(f"[❌] Telegram error: {response.text}")
    except Exception as e:
        print(f"[❌] Video send failed: {e}")

async def main():
    video_topic = "Top 3 Amazing Facts about Artificial Intelligence"
    
    custom_caption = (
        "AI ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Har din, aap AI use karte ho! Google Maps, Netflix suggestions, ya Siri. Yeah, sab AI hai!\n\n"
        "Fact 2: AI ne chess, Go, aur poker mein world champions ko haraya hai. Socho, kitna smart hai!\n\n"
        "Fact 3: AI sirf data process nahi karta, ye original music aur paintings bhi bana sakta hai. Kitna creative hai na?\n\n"
        "Hai na amazing? AI ki duniya mein aur kya jaanna chahte ho? Comments mein batao!"
    )
    
    # 1. Voiceover generate karein
    await generate_audio_stream(custom_caption, "voice.mp3")
    
    if os.path.exists("voice.mp3"):
        # 2. Pehle Audio track bhejein
        send_audio_to_telegram("voice.mp3", custom_caption)
        
        # 3. Text Overlay ke sath video compile karein
        render_status = compile_production_video("voice.mp3", "output_short.mp4", custom_caption)
        
        # 4. Final Video track bhejein
        if render_status and os.path.exists("output_short.mp4"):
            send_video_to_telegram("output_short.mp4", custom_caption)

if __name__ == "__main__":
    asyncio.run(main())
    
