# voz.py
import sounddevice as sd
import soundfile as sf
import numpy as np
import pyttsx3
import whisper
from resemblyzer import VoiceEncoder, preprocess_wav

# === Config ===
PERFIL_FNAME = "perfil_voz.npy"
THRESHOLD = 0.78   # ajusta entre 0.7-0.85 según pruebas
WHISPER_MODEL = "base"  # puedes usar "small" si quieres más rapidez

# === Init ===
engine = pyttsx3.init()
engine.setProperty("rate", 150)
encoder = VoiceEncoder()
perfil = np.load(PERFIL_FNAME)
whisper_model = whisper.load_model(WHISPER_MODEL)

def grabar_audio_seg(duracion=4, fs=16000):
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten(), fs

def guardar_wav(audio, fs, fname="temp_input.wav"):
    sf.write(fname, audio, fs)
    return fname

def verificar_voz_por_audio(audio):
    # audio: numpy 1D array a 16k
    try:
        emb = encoder.embed_utterance(audio)
        sim = np.dot(emb, perfil) / (np.linalg.norm(emb) * np.linalg.norm(perfil))
        return float(sim)
    except Exception as e:
        print("Error verificación voz:", e)
        return 0.0

def transcribir_de_wav(fname="temp_input.wav"):
    res = whisper_model.transcribe(fname)
    return res.get("text","").strip()

def hablar(texto):
    engine.say(texto)
    engine.runAndWait()