from dotenv import load_dotenv
from groq import Groq
import os
import glob
from pydub import AudioSegment
import math

# constants
AUDIO_EXTENSIONS = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
RECORDING_FOLDER = 'recording'
TRANSCRIPT_FOLDER = 'transcript'
WHISPER_MODEL = 'whisper-large-v3'
LANGUAGE = 'ko'
CHUNK_SIZE = 5 * 1024 * 1024 # 5MB in bytes

# load environment variables
load_dotenv()

# STT : Groq API
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_audio_file_path():
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(glob.glob(os.path.join(RECORDING_FOLDER, f'*.{ext}')))

    if not audio_files:
        print('Can\'t find any audio file in the recording folder')
        return None

    print('select audio file you want to convert to text')
    for i, file in enumerate(audio_files, 1):
        print(f'[{i}] {file}')

    while True:
        try:
            choice = int(input('Enter the number: '))
            if 1 <= choice <= len(audio_files):
                return audio_files[choice - 1]
            else:
                print('Try Again.')
        except ValueError:
            print('Please enter a number.')

def split_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    chunk_duration_ms = (CHUNK_SIZE / len(audio.raw_data)) * duration_ms
    chunks = math.ceil(duration_ms / chunk_duration_ms)
    audio_format = os.path.splitext(file_path)[1][1:].lower()
    
    return [audio[i*chunk_duration_ms:(i+1)*chunk_duration_ms] for i in range(chunks)], audio_format

def transcribe_audio_chunk(chunk, file_name, audio_format):
    try:
        temp_file = f"temp_{file_name}.wav"  # Export as WAV
        chunk.export(temp_file, format='wav')  # Specify 'wav' format
        
        with open(temp_file, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            api_file_name = os.path.basename(temp_file)

            transcription = groq_client.audio.transcriptions.create(
                file=(api_file_name, audio_bytes),
                model=WHISPER_MODEL,
                language=LANGUAGE,
                temperature=0.0,
            )
            chunk_text = transcription.text.strip()
        
        os.remove(temp_file)
        return chunk_text
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        print(f"Error in chunk STT: {e}")
        return ''

def transcribe_audio(audio_file_path):
    file_name = os.path.basename(audio_file_path)
    chunks, audio_format = split_audio(audio_file_path)
    full_transcription = []

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}/{len(chunks)} processing...")
        chunk_text = transcribe_audio_chunk(chunk, f"{file_name}_chunk_{i}", audio_format)
        full_transcription.append(chunk_text)

    return ' '.join(full_transcription)

def main():
    audio_file_path = get_audio_file_path()
    if not audio_file_path:
        return

    print('Start STT...')
    result = transcribe_audio(audio_file_path)
    base_name = os.path.basename(audio_file_path)
    output_file_path = os.path.join(TRANSCRIPT_FOLDER, f'{base_name}.txt')

    output_index = 0
    while os.path.exists(output_file_path):
        output_index += 1
        base, ext = os.path.splitext(output_file_path)
        output_file_path = f"{base}-{output_index}{ext}"
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(result)

    print(f'Transcribed text has been saved to {output_file_path}')


if __name__ == "__main__":
    main()
