import asyncio
import os
import sys
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip

# Environment Credentials Fetch
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def generate_audio_stream(text: str, output_filename: str = "voice.mp3") -> None:
    import edge_tts
    print("[🎙️] Generating Clear AI Voiceover...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)

def compile_production_video(audio_input: str, video_output: str, script_words: list) -> bool:
    print("[🎬] Rendering high-engagement word-sync animation...")
    audio_clip = None
    final_video = None
    try:
        audio_clip = AudioFileClip(audio_input)
        duration = audio_clip.duration
        
        # System Font setup for Linux Container
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "LiberationSans-Bold.ttf"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 80)  
                break
        if not font:
            font = ImageFont.load_default()

        total_words = len(script_words)
        time_per_word = duration / total_words

        def make_frame(t):
            # NEW: Mysterious Deep Violet & Cyber Punk Background
            r = int(20 + np.sin(t * 0.6) * 5)
            g = int(10 + np.cos(t * 0.4) * 3)
            b = int(40 + np.sin(t * 0.8) * 8)
            img = Image.new('RGB', (1080, 1920), color=(r, g, b))
            draw = ImageDraw.Draw(img)
            
            # Rotating Cyber Diamond Lines in background (Motion Graphics Effect)
            angle = t * 0.5
            center_x, center_y = 540, 960
            for size in range(200, 1200, 250):
                current_size = size + int(np.sin(t * 2) * 30)
                points = [
                    (center_x + current_size * np.cos(angle), center_y + current_size * np.sin(angle)),
                    (center_x + current_size * np.cos(angle + np.pi/2), center_y + current_size * np.sin(angle + np.pi/2)),
                    (center_x + current_size * np.cos(angle + np.pi), center_y + current_size * np.sin(angle + np.pi)),
                    (center_x + current_size * np.cos(angle + 3*np.pi/2), center_y + current_size * np.sin(angle + 3*np.pi/2))
                ]
                draw.polygon(points, outline=(r + 25, g + 15, b + 35), width=4)
                
            # Word Sync Logic
            current_index = min(int(t / time_per_word), total_words - 1)
            word = script_words[current_index].upper()
            
            text_w = len(word) * 46
            text_x = 540 - (text_w // 2)
            text_y = 920 
            
            # Thick Shadow Border for High Contrast
            draw.text((text_x + 6, text_y + 6), word, fill=(0, 0, 0), font=font)
            draw.text((text_x - 3, text_y - 3), word, fill=(0, 0, 0), font=font)
            
            # HIGHLIGHT COLOR SCHEME: Bright Orange and Neon Yellow
            if any(x in word for x in ["BRAIN", "1", "2", "3", "SHOCK", "FACT", "TRICK", "PROVED"]):
                draw.text((text_x, text_y), word, fill=(255, 102, 0), font=font) # Neon Orange
            else:
                draw.text((text_x, text_y), word, fill=(255, 255, 0), font=font) # Pure Yellow
            
            return np.array(img)
            
        video_clip = VideoClip(make_frame, duration=duration)
        final_video = video_clip.set_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="2500k",
            threads=2,
            logger=None
        )
        return True
    except Exception as e:
        print(f"[❌] Error: {e}")
        return False
    finally:
        if audio_clip: audio_clip.close()
        if final_video: final_video.close()

def send_video_to_telegram(video_path: str, caption_text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as video_file:
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption_text, 'supports_streaming': True, 'parse_mode': 'Markdown'}
            requests.post(url, data=payload, files={'video': video_file}, timeout=90)
            print("[🎉] New Psychology Video sent to Telegram successfully!")
    except Exception as e:
        print(f"[❌] Telegram failed: {e}")

async def main():
    # New Psychology Caption for Telegram Channel
    telegram_caption = (
        "🎬 *Human Brain & Psychology Facts*\n\n"
        "Human Brain ke baare mein Top 3 amazing facts jo aapko shock kar denge!\n\n"
        "Fact 1: Jab aap kuch naya seekhte hain, toh aapke brain ka structure badal jata hai! Isey neuroplasticity kehte hain.\n\n"
        "Fact 2: Hamara dimaag hamesha boring cheezon ko automatic customize karke unhe interesting banane ki koshish karta hai.\n\n"
        "Fact 3: Yeh scientifically proved hai ki creative log raat mein zyada active aur dimaag se tez hote hain!\n\n"
        "Hai na amazing? Comments mein batao!"
    )
    
    # Word-by-word Array
    script_words = [
        "Top", "3", "Amazing", "Facts", "About", "Human", "Brain",
        "Fact", "1:", "Jab", "aap", "kuch", "naya", "seekhte", "hain,",
        "toh", "aapke", "brain", "ka", "structure", "change", "ho", "jata", "hai!",
        "Fact", "2:", "Hamara", "dimaag", "boring", "cheezon", "ko", "automatic", "interesting", "bana", "deta", "hai.",
        "Fact", "3:", "Yeh", "fact", "scientifically", "proved", "hai", "ki",
        "creative", "log", "raat", "mein", "zyada", "active", "aur", "tez", "hote", "hain!",
        "Hai", "na", "amazing?", "Comments", "mein", "batao!"
    ]
    
    await generate_audio_stream(telegram_caption, "voice.mp3")
    if os.path.exists("voice.mp3"):
        if compile_production_video("voice.mp3", "tg_short.mp4", script_words):
            send_video_to_telegram("tg_short.mp4", telegram_caption)

if __name__ == "__main__":
    asyncio.run(main())
    
