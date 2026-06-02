import asyncio
import os
import edge_tts
import requests
from google import genai
# Naye version ke mutabik direct moviepy se import kar rahe hain
from moviepy import VideoFileClip, AudioFileClip

# API & Bot Setup
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=API_KEY)

def generate_script(topic):
    print(f"Generating script for: {topic}...")
    prompt = f"Write a short, engaging 20-second video script about '{topic}' in Hinglish. Keep it punchy and optimized for Shorts. Do not include scene descriptions, only spoken text."
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

async def generate_audio(text, output_filename="voice.mp3"):
    print("Generating natural voiceover...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)
    print(f"Audio saved successfully as {output_filename}")

def create_video(video_input, audio_input, video_output):
    print("Merging Audio and Video...")
    try:
        video_clip = VideoFileClip(video_input)
        audio_clip = AudioFileClip(audio_input)
        
        final_video = video_clip.with_duration(audio_clip.duration)
        final_video = final_video.with_audio(audio_clip)
        
        final_video.write_videofile(
            video_output, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="1500k"
        )
        
        video_clip.close()
        audio_clip.close()
        final_video.close()
        print(f"Video created successfully.")
        return True
    except Exception as e:
        print(f"Error in video creation: {e}")
        return False

def send_to_telegram(video_path, caption_text):
    print("Sending video to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': caption_text,
            'supports_streaming': True
        }
        files = {
            'video': video_file
        }
        response = requests.post(url, data=payload, files=files)
        
    if response.status_code == 200:
        print("Video sent successfully to Telegram!")
    else:
        print(f"Failed to send video: {response.text}")

async def main():
    video_topic = "Top 3 Amazing Facts about AI"
    
    script_text = generate_script(video_topic)
    await generate_audio(script_text)
    
    if os.path.exists("background.mp4") and os.path.exists("voice.mp3"):
        success = create_video("background.mp4", "voice.mp3", "output_short.mp4")
        if success:
            caption = f"🤖 {video_topic}\n\n#ai #facts #shorts"
            send_to_telegram("output_short.mp4", caption)
    else:
        print("Error: background.mp4 ya voice.mp3 missing hai!")

if __name__ == "__main__":
    asyncio.run(main())
    
