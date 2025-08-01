import os
import subprocess
import sys
from google.cloud import speech

def check_ffmpeg_installed():
    """Check if ffmpeg is available in the system"""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except FileNotFoundError:
        return False

def install_instructions():
    """Print instructions for installing ffmpeg"""
    print("FFmpeg is not installed. Please install it using one of the following methods:")
    print("\nFor ARM Mac (M1/M2/M3):")
    print("  1. Install Homebrew:")
    print('     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    print("  2. Follow the post-installation instructions to add Homebrew to your PATH")
    print("  3. Install FFmpeg:")
    print("     brew install ffmpeg")
    print("\nFor Intel Mac:")
    print("  brew install ffmpeg")
    
    print("\nAlternatively, you can convert your MP3 file to WAV format using an online converter")
    print("and place the WAV file in the same directory with the name 'converted.wav'.")
    
def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using ffmpeg command-line tool"""
    # Check if input file exists
    if not os.path.exists(mp3_path):
        print(f"Error: Input file '{mp3_path}' does not exist.")
        user_input = input("Do you want to proceed with a pre-converted WAV file? (y/n): ")
        if user_input.lower() == 'y':
            if os.path.exists(wav_path):
                print(f"Using existing WAV file: {wav_path}")
                return
            else:
                print(f"Error: {wav_path} not found. Please provide a valid audio file.")
                sys.exit(1)
        else:
            sys.exit(1)
            
    if not check_ffmpeg_installed():
        install_instructions()
        user_input = input("\nDo you want to proceed with a pre-converted WAV file? (y/n): ")
        if user_input.lower() == 'y':
            if os.path.exists(wav_path):
                print(f"Using existing WAV file: {wav_path}")
                return
            else:
                print(f"Error: {wav_path} not found. Please convert your audio file manually.")
                sys.exit(1)
        else:
            sys.exit(1)
    
    try:
        # Run ffmpeg command with more verbose output - CHANGED to mono (ac=1)
        process = subprocess.run(
            ["ffmpeg", "-i", mp3_path, "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", wav_path],
            check=False,  # Don't raise exception, handle it manually
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if process.returncode != 0:
            error_message = process.stderr.decode('utf-8', errors='replace')
            print(f"FFmpeg Error (code {process.returncode}):")
            print(error_message)
            
            # Ask user if they want to try a different approach
            user_input = input("Do you want to try using a pre-converted WAV file? (y/n): ")
            if user_input.lower() == 'y':
                if os.path.exists(wav_path):
                    print(f"Using existing WAV file: {wav_path}")
                    return
                else:
                    print(f"Error: {wav_path} not found.")
                    print("Please convert your audio file manually using an online converter")
                    print("or provide a valid audio file in the correct format.")
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            print(f"Successfully converted {mp3_path} to {wav_path}")
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

def transcribe_speech(wav_path):
    if not os.path.exists(wav_path):
        print(f"Error: WAV file '{wav_path}' not found. Please provide a valid WAV file.")
        sys.exit(1)
        
    client = speech.SpeechClient()

    with open(wav_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,  # 根据实际音频采样率调整
        language_code="en-US",    # 可改为 "zh-CN" 中文
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)

    full_text = ""
    for result in response.results:
        full_text += result.alternatives[0].transcript + "\n"

    return full_text.strip()

if __name__ == "__main__":
    mp3_file = "Record_test.mp3"
    wav_file = "converted.wav"
    output_file = "transcribed_text.txt"

    # 步骤1：mp3 转 wav
    convert_mp3_to_wav(mp3_file, wav_file)

    # 步骤2：调用 API 进行转录
    transcript = transcribe_speech(wav_file)

    # 步骤3：写入 TXT 文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print("Transcript successfully saved to transcribed_text.txt")