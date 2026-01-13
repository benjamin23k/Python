import sounddevice as sd
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import soundfile as sf

print("🎙️ Grabando tu voz para crear tu perfil...")
print("Habla normalmente durante 5 segundos...")

fs = 16000
duracion = 5
audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1)
sd.wait()

sf.write("tu_voz.wav", audio, fs)
print("✅ Audio grabado: tu_voz.wav")

# Procesar e incrustar tu voz
encoder = VoiceEncoder()
wav = preprocess_wav("tu_voz.wav")
embedding = encoder.embed_utterance(wav)

np.save("perfil_voz.npy", embedding)
print("✅ Perfil de voz creado y guardado como 'perfil_voz.npy'")
