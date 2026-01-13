from pydub import AudioSegment

# Cargar el archivo original
cancion = AudioSegment.from_mp3(r"C:\Users\wilson\Desktop\Programar\Full Stack\Lenguajes Programacion\Python\Archivos\Consume.mp3")

# Recortar: desde el segundo 30 hasta el 50
fragmento = cancion[30*1000:50*1000]  # milisegundos

# Exportar el fragmento como nuevo archivo
fragmento.export("Consume_recortado.mp3", format="mp3")