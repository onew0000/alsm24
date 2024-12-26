import os
import queue
import threading
import time
from datetime import datetime
import wave
import pyaudio
import speech_recognition as sr
from hanspell import spell_checker

VOICE_DIR = "voice"
os.makedirs(VOICE_DIR, exist_ok=True)

audio_queue = queue.Queue()
is_recording = False
record_thread = None
process_thread = None

def record_audio():
    global is_recording

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("음성 인식 시작...")

    while is_recording:
        frames = []
        for _ in range(0, int(RATE / CHUNK * 3)):
            if not is_recording:
                break
            data = stream.read(CHUNK)
            frames.append(data)

        if frames:
            audio_queue.put(frames)

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("녹음 종료")

def process_audio():
    r = sr.Recognizer()

    while is_recording:
        if not audio_queue.empty():
            frames = audio_queue.get()

            audio_filename = os.path.join(VOICE_DIR, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            wf = wave.open(audio_filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
            wf.close()

            try:
                with sr.AudioFile(audio_filename) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio, language='ko-KR')
                    if text.strip():
                        print(f"\n인식된 텍스트: {text}")

                        grammar_check = check_grammar(text)
                        result = {
                            'original_text': text,
                            'corrected_text': grammar_check['corrected'] if grammar_check else text,
                            'has_errors': bool(grammar_check)
                        }
                        print(result)

            except sr.UnknownValueError:
                print('음성을 인식할 수 없습니다.')
            except sr.RequestError as e:
                print(f'음성 인식 서비스 오류: {str(e)}')
            finally:
                os.remove(audio_filename)

        time.sleep(0.1)

def check_grammar(text):
    """한국어 문장의 맞춤법과 문법을 검사하고 교정"""
    try:
        result = spell_checker.check(text)
        if result.checked != text:
            return {
                'original': text,
                'corrected': result.checked,
                'errors': len(result.errors),
                'errors_detail': result.errors
            }
        return None
    except Exception as e:
        return None

def start_recording():
    global is_recording, record_thread, process_thread

    if not is_recording:
        is_recording = True
        record_thread = threading.Thread(target=record_audio)
        process_thread = threading.Thread(target=process_audio)

        record_thread.start()
        process_thread.start()

def stop_recording():
    global is_recording

    if is_recording:
        is_recording = False
        if record_thread:
            record_thread.join()
        if process_thread:
            process_thread.join()

if __name__ == '__main__':
    print("녹음을 시작하려면 'start_recording()'을 호출하세요.")
    print("녹음을 중지하려면 'stop_recording()'을 호출하세요.")

    start_recording()
