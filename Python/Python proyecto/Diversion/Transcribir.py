import whisper
from pytube import YouTube
import os

# 👉 URL del video
video_url = "https://www.youtube.com/watch?v=VIDEO_ID"

# 🔽 Descarga el video
yt = YouTube(video_url)
audio_stream = yt.streams.filter(only_audio=True).first()
output_path = audio_stream.download(filename="audio.mp4")

# 🎙️ Cargar el modelo Whisper
model = whisper.load_model("base")  # Puedes probar con "medium" o "large" si quieres más precisión

# 🎧 Transcribir el audio
result = model.transcribe(output_path)

# 📝 Mostrar la transcripción
print("\nTRANSCRIPCIÓN:")
print(result["text"])

# 🧹 Limpiar archivo descargado
os.remove(output_path)