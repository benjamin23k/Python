# lenguaje.py
import subprocess, shlex, threading

OLLAMA_MODEL = "gpt-oss:20b"

def enviar_a_llm(prompt, timeout=30):
    # Ejecuta Ollama y devuelve la respuesta (texto)
    try:
        proc = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, prompt],
            capture_output=True, text=True, timeout=timeout
        )
        out = proc.stdout.strip()
        return out
    except subprocess.TimeoutExpired:
        return "Lo siento, la respuesta tomó demasiado tiempo."
    except Exception as e:
        return f"Error LLM: {e}"